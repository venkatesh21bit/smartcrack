"""
Brute Force and Dictionary Attack Password Cracker
Supports PDF, DOCX, PPTX, and ZIP files
"""

import os
import sys
import time
import string
import itertools
from pathlib import Path
from typing import List, Optional, Tuple
import multiprocessing as mp
from functools import partial

# File format libraries
try:
    import pikepdf
except ImportError:
    pikepdf = None

try:
    import msoffcrypto
except ImportError:
    msoffcrypto = None

import zipfile


class PasswordCracker:
    """Multi-format password cracker with dictionary and brute force attacks"""
    
    def __init__(self, target_file: str, verbose: bool = True):
        """
        Initialize the password cracker
        
        Args:
            target_file: Path to the password-protected file
            verbose: Whether to print progress information
        """
        self.target_file = Path(target_file)
        self.verbose = verbose
        self.attempts = 0
        self.start_time = None
        
        if not self.target_file.exists():
            raise FileNotFoundError(f"Target file not found: {target_file}")
        
        # Detect file type
        self.file_type = self._detect_file_type()
        
    def _detect_file_type(self) -> str:
        """Detect the type of password-protected file"""
        suffix = self.target_file.suffix.lower()
        
        if suffix == '.pdf':
            if pikepdf is None:
                raise ImportError("pikepdf is required for PDF files. Install: pip install pikepdf")
            return 'pdf'
        elif suffix in ['.docx', '.xlsx', '.pptx']:
            if msoffcrypto is None:
                raise ImportError("msoffcrypto-tool is required for Office files. Install: pip install msoffcrypto-tool")
            return 'office'
        elif suffix == '.zip':
            return 'zip'
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
    
    def try_password(self, password: str) -> bool:
        """
        Try a single password on the target file
        
        Args:
            password: Password to try
            
        Returns:
            True if password is correct, False otherwise
        """
        self.attempts += 1
        
        try:
            if self.file_type == 'pdf':
                return self._try_pdf_password(password)
            elif self.file_type == 'office':
                return self._try_office_password(password)
            elif self.file_type == 'zip':
                return self._try_zip_password(password)
        except Exception:
            return False
        
        return False
    
    def _try_pdf_password(self, password: str) -> bool:
        """Try password on PDF file"""
        try:
            with pikepdf.open(self.target_file, password=password):
                return True
        except pikepdf.PasswordError:
            return False
    
    def _try_office_password(self, password: str) -> bool:
        """Try password on Office file"""
        try:
            import io
            with open(self.target_file, 'rb') as f:
                file_obj = msoffcrypto.OfficeFile(f)
                file_obj.load_key(password=password)
                # Try to decrypt to memory to verify password
                output = io.BytesIO()
                file_obj.decrypt(output)
                return True
        except Exception:
            return False
    
    def _try_zip_password(self, password: str) -> bool:
        """Try password on ZIP file"""
        try:
            with zipfile.ZipFile(self.target_file, 'r') as zf:
                # Get first file in archive
                first_file = zf.namelist()[0]
                # Try to extract with password
                zf.read(first_file, pwd=password.encode('utf-8'))
                return True
        except (RuntimeError, zipfile.BadZipFile, KeyError):
            return False
    
    def dictionary_attack(self, wordlist_path: str, start_line: int = 0, 
                         max_passwords: Optional[int] = None) -> Optional[str]:
        """
        Perform dictionary attack using a wordlist
        
        Args:
            wordlist_path: Path to wordlist file
            start_line: Line number to start from (for resuming)
            max_passwords: Maximum number of passwords to try
            
        Returns:
            Correct password if found, None otherwise
        """
        wordlist = Path(wordlist_path)
        if not wordlist.exists():
            raise FileNotFoundError(f"Wordlist not found: {wordlist_path}")
        
        self.start_time = time.time()
        self.attempts = 0
        
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"DICTIONARY ATTACK")
            print(f"{'='*60}")
            print(f"Target file: {self.target_file}")
            print(f"File type: {self.file_type.upper()}")
            print(f"Wordlist: {wordlist}")
            print(f"Starting from line: {start_line + 1}")
            if max_passwords:
                print(f"Max attempts: {max_passwords:,}")
            print(f"{'='*60}\n")
        
        try:
            with open(wordlist, 'r', encoding='utf-8', errors='ignore') as f:
                # Skip to start line
                for _ in range(start_line):
                    next(f)
                
                for line_num, line in enumerate(f, start=start_line + 1):
                    password = line.strip()
                    
                    if not password:
                        continue
                    
                    if self.try_password(password):
                        self._print_success(password)
                        return password
                    
                    if self.verbose and self.attempts % 1000 == 0:
                        self._print_progress(line_num)
                    
                    if max_passwords and self.attempts >= max_passwords:
                        if self.verbose:
                            print(f"\n✗ Reached maximum attempts ({max_passwords:,})")
                        break
        
        except KeyboardInterrupt:
            if self.verbose:
                print(f"\n\n⚠ Attack interrupted by user")
                print(f"Stopped at line: {line_num}")
                print(f"Resume with: start_line={line_num}")
        
        if self.verbose:
            elapsed = time.time() - self.start_time
            print(f"\n{'='*60}")
            print(f"✗ Password not found")
            print(f"Attempts: {self.attempts:,}")
            print(f"Time elapsed: {self._format_time(elapsed)}")
            print(f"Speed: {self.attempts / elapsed:.2f} passwords/sec")
            print(f"{'='*60}\n")
        
        return None
    
    def brute_force_attack(self, charset: str = None, min_length: int = 1, 
                          max_length: int = 6) -> Optional[str]:
        """
        Perform brute force attack
        
        Args:
            charset: Character set to use (default: digits + lowercase + uppercase)
            min_length: Minimum password length
            max_length: Maximum password length
            
        Returns:
            Correct password if found, None otherwise
        """
        if charset is None:
            charset = string.digits + string.ascii_lowercase + string.ascii_uppercase
        
        self.start_time = time.time()
        self.attempts = 0
        
        # Calculate total combinations
        total = sum(len(charset) ** length for length in range(min_length, max_length + 1))
        
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"BRUTE FORCE ATTACK")
            print(f"{'='*60}")
            print(f"Target file: {self.target_file}")
            print(f"File type: {self.file_type.upper()}")
            print(f"Character set: {charset}")
            print(f"Character set size: {len(charset)}")
            print(f"Length range: {min_length}-{max_length}")
            print(f"Total combinations: {total:,}")
            print(f"{'='*60}\n")
        
        try:
            for length in range(min_length, max_length + 1):
                if self.verbose:
                    print(f"\nTrying passwords of length {length}...")
                
                for combo in itertools.product(charset, repeat=length):
                    password = ''.join(combo)
                    
                    if self.try_password(password):
                        self._print_success(password)
                        return password
                    
                    if self.verbose and self.attempts % 1000 == 0:
                        self._print_progress()
        
        except KeyboardInterrupt:
            if self.verbose:
                print(f"\n\n⚠ Attack interrupted by user")
        
        if self.verbose:
            elapsed = time.time() - self.start_time
            print(f"\n{'='*60}")
            print(f"✗ Password not found")
            print(f"Attempts: {self.attempts:,}")
            print(f"Time elapsed: {self._format_time(elapsed)}")
            print(f"Speed: {self.attempts / elapsed:.2f} passwords/sec")
            print(f"{'='*60}\n")
        
        return None
    
    def hybrid_attack(self, wordlist_path: str, mutations: List[str] = None) -> Optional[str]:
        """
        Perform hybrid attack: dictionary + common mutations
        
        Args:
            wordlist_path: Path to wordlist file
            mutations: List of common mutations (suffixes/prefixes)
            
        Returns:
            Correct password if found, None otherwise
        """
        if mutations is None:
            mutations = ['', '!', '123', '1', '12', '2024', '2025', '!@#']
        
        wordlist = Path(wordlist_path)
        if not wordlist.exists():
            raise FileNotFoundError(f"Wordlist not found: {wordlist_path}")
        
        self.start_time = time.time()
        self.attempts = 0
        
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"HYBRID ATTACK")
            print(f"{'='*60}")
            print(f"Target file: {self.target_file}")
            print(f"File type: {self.file_type.upper()}")
            print(f"Wordlist: {wordlist}")
            print(f"Mutations: {mutations}")
            print(f"{'='*60}\n")
        
        try:
            with open(wordlist, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, start=1):
                    base_password = line.strip()
                    
                    if not base_password:
                        continue
                    
                    # Try base password + all mutations
                    for mutation in mutations:
                        password = base_password + mutation
                        
                        if self.try_password(password):
                            self._print_success(password)
                            return password
                        
                        # Also try mutation as prefix
                        password = mutation + base_password
                        if self.try_password(password):
                            self._print_success(password)
                            return password
                    
                    if self.verbose and self.attempts % 1000 == 0:
                        self._print_progress(line_num)
        
        except KeyboardInterrupt:
            if self.verbose:
                print(f"\n\n⚠ Attack interrupted by user")
        
        if self.verbose:
            elapsed = time.time() - self.start_time
            print(f"\n{'='*60}")
            print(f"✗ Password not found")
            print(f"Attempts: {self.attempts:,}")
            print(f"Time elapsed: {self._format_time(elapsed)}")
            print(f"Speed: {self.attempts / elapsed:.2f} passwords/sec")
            print(f"{'='*60}\n")
        
        return None
    
    def _print_progress(self, line_num: Optional[int] = None):
        """Print progress information"""
        elapsed = time.time() - self.start_time
        speed = self.attempts / elapsed if elapsed > 0 else 0
        
        progress = f"Attempts: {self.attempts:,} | Speed: {speed:.2f} pwd/s | Time: {self._format_time(elapsed)}"
        if line_num:
            progress = f"Line: {line_num:,} | {progress}"
        
        print(f"\r{progress}", end='', flush=True)
    
    def _print_success(self, password: str):
        """Print success message"""
        elapsed = time.time() - self.start_time
        
        print(f"\n\n{'='*60}")
        print(f"✓ PASSWORD FOUND!")
        print(f"{'='*60}")
        print(f"Password: {password}")
        print(f"Attempts: {self.attempts:,}")
        print(f"Time elapsed: {self._format_time(elapsed)}")
        print(f"Speed: {self.attempts / elapsed:.2f} passwords/sec")
        print(f"{'='*60}\n")
    
    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format elapsed time"""
        if seconds < 60:
            return f"{seconds:.2f}s"
        elif seconds < 3600:
            mins = int(seconds // 60)
            secs = seconds % 60
            return f"{mins}m {secs:.1f}s"
        else:
            hours = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            secs = seconds % 60
            return f"{hours}h {mins}m {secs:.0f}s"


def crack_file(target_file: str, wordlist: str = None, attack_type: str = 'dictionary',
               max_passwords: Optional[int] = None, **kwargs) -> Optional[str]:
    """
    Convenience function to crack a password-protected file
    
    Args:
        target_file: Path to the password-protected file
        wordlist: Path to wordlist file (for dictionary/hybrid attacks)
        attack_type: Type of attack ('dictionary', 'brute_force', 'hybrid')
        max_passwords: Maximum number of passwords to try
        **kwargs: Additional arguments for specific attack types
        
    Returns:
        Correct password if found, None otherwise
    """
    cracker = PasswordCracker(target_file)
    
    if attack_type == 'dictionary':
        if wordlist is None:
            raise ValueError("Wordlist required for dictionary attack")
        return cracker.dictionary_attack(wordlist, max_passwords=max_passwords)
    
    elif attack_type == 'brute_force':
        min_length = kwargs.get('min_length', 1)
        max_length = kwargs.get('max_length', 6)
        charset = kwargs.get('charset', None)
        return cracker.brute_force_attack(charset, min_length, max_length)
    
    elif attack_type == 'hybrid':
        if wordlist is None:
            raise ValueError("Wordlist required for hybrid attack")
        mutations = kwargs.get('mutations', None)
        return cracker.hybrid_attack(wordlist, mutations)
    
    else:
        raise ValueError(f"Unknown attack type: {attack_type}")


if __name__ == '__main__':
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description='Password cracker for PDF, Office, and ZIP files')
    parser.add_argument('file', help='Target file to crack')
    parser.add_argument('-w', '--wordlist', help='Path to wordlist file')
    parser.add_argument('-t', '--type', choices=['dictionary', 'brute_force', 'hybrid'], 
                       default='dictionary', help='Attack type')
    parser.add_argument('-m', '--max', type=int, help='Maximum passwords to try')
    parser.add_argument('--min-length', type=int, default=1, help='Minimum password length (brute force)')
    parser.add_argument('--max-length', type=int, default=6, help='Maximum password length (brute force)')
    parser.add_argument('--charset', help='Character set for brute force')
    
    args = parser.parse_args()
    
    result = crack_file(
        args.file,
        wordlist=args.wordlist,
        attack_type=args.type,
        max_passwords=args.max,
        min_length=args.min_length,
        max_length=args.max_length,
        charset=args.charset
    )
    
    if result:
        print(f"\n✓ Success! Password: {result}")
        sys.exit(0)
    else:
        print(f"\n✗ Failed to crack password")
        sys.exit(1)
