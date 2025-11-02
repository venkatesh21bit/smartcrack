"""
File Cracker Utility
Attempts to crack password-protected files using generated passwords
Supports PDF, DOCX, PPTX, ZIP files
"""

import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json

try:
    import pikepdf
except ImportError:
    pikepdf = None

try:
    import msoffcrypto
except ImportError:
    msoffcrypto = None

try:
    import zipfile
except ImportError:
    zipfile = None


class FileCracker:
    """
    File cracker for password-protected files
    """
    
    def __init__(self, password_file=None, passwords=None, max_workers=4):
        """
        Args:
            password_file: Path to password list file
            passwords: List of passwords
            max_workers: Number of parallel workers
        """
        self.max_workers = max_workers
        
        # Load passwords
        if password_file and os.path.exists(password_file):
            self.passwords = self._load_passwords(password_file)
        elif passwords:
            self.passwords = passwords
        else:
            self.passwords = []
        
        print(f"Loaded {len(self.passwords)} passwords for cracking")
        
        # Statistics
        self.attempts = 0
        self.successes = 0
        self.failures = 0
        self.results = {}
        
    def _load_passwords(self, filepath):
        """Load passwords from file"""
        passwords = []
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                pwd = line.strip()
                if pwd:
                    passwords.append(pwd)
        return passwords
    
    def crack_pdf(self, pdf_path, passwords):
        """
        Attempt to crack a PDF file
        
        Args:
            pdf_path: Path to PDF file
            passwords: List of passwords to try
            
        Returns:
            Correct password or None
        """
        if pikepdf is None:
            print("Warning: pikepdf not installed. Cannot crack PDF files.")
            print("Install with: pip install pikepdf")
            return None
        
        for pwd in passwords:
            try:
                with pikepdf.open(pdf_path, password=pwd):
                    return pwd
            except pikepdf.PasswordError:
                self.attempts += 1
                continue
            except Exception as e:
                continue
        
        return None
    
    def crack_docx(self, docx_path, passwords):
        """
        Attempt to crack a DOCX file
        
        Args:
            docx_path: Path to DOCX file
            passwords: List of passwords to try
            
        Returns:
            Correct password or None
        """
        if msoffcrypto is None:
            print("Warning: msoffcrypto-tool not installed. Cannot crack Office files.")
            print("Install with: pip install msoffcrypto-tool")
            return None
        
        for pwd in passwords:
            try:
                with open(docx_path, 'rb') as f:
                    file = msoffcrypto.OfficeFile(f)
                    file.load_key(password=pwd)
                    
                    # Try to decrypt to verify password
                    import io
                    decrypted = io.BytesIO()
                    file.decrypt(decrypted)
                    
                    return pwd
            except Exception as e:
                self.attempts += 1
                continue
        
        return None
    
    def crack_pptx(self, pptx_path, passwords):
        """
        Attempt to crack a PPTX file
        
        Args:
            pptx_path: Path to PPTX file
            passwords: List of passwords to try
            
        Returns:
            Correct password or None
        """
        # PPTX uses same encryption as DOCX
        return self.crack_docx(pptx_path, passwords)
    
    def crack_zip(self, zip_path, passwords):
        """
        Attempt to crack a ZIP file
        
        Args:
            zip_path: Path to ZIP file
            passwords: List of passwords to try
            
        Returns:
            Correct password or None
        """
        if zipfile is None:
            print("Warning: zipfile module not available.")
            return None
        
        for pwd in passwords:
            try:
                with zipfile.ZipFile(zip_path) as zf:
                    # Get first file in archive
                    first_file = zf.namelist()[0]
                    # Try to extract with password
                    zf.read(first_file, pwd=pwd.encode('utf-8'))
                    return pwd
            except (RuntimeError, zipfile.BadZipFile):
                self.attempts += 1
                continue
            except Exception as e:
                continue
        
        return None
    
    def crack_file(self, filepath, passwords=None):
        """
        Attempt to crack a single file
        
        Args:
            filepath: Path to file
            passwords: List of passwords (uses self.passwords if None)
            
        Returns:
            Dict with result information
        """
        if passwords is None:
            passwords = self.passwords
        
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filepath)[1].lower()
        
        print(f"\nAttempting to crack: {filename}")
        start_time = time.time()
        
        password = None
        
        # Try appropriate cracking method based on extension
        if ext == '.pdf':
            password = self.crack_pdf(filepath, passwords)
        elif ext in ['.docx', '.doc']:
            password = self.crack_docx(filepath, passwords)
        elif ext in ['.pptx', '.ppt']:
            password = self.crack_pptx(filepath, passwords)
        elif ext == '.zip':
            password = self.crack_zip(filepath, passwords)
        else:
            print(f"Unsupported file type: {ext}")
            return {
                'file': filename,
                'status': 'unsupported',
                'password': None,
                'time': 0
            }
        
        elapsed = time.time() - start_time
        
        if password:
            print(f"✓ SUCCESS! Password found: {password} (Time: {elapsed:.2f}s)")
            self.successes += 1
            status = 'success'
        else:
            print(f"✗ FAILED! No password found (Time: {elapsed:.2f}s)")
            self.failures += 1
            status = 'failed'
        
        result = {
            'file': filename,
            'path': filepath,
            'status': status,
            'password': password,
            'time': elapsed,
            'attempts': len(passwords)
        }
        
        self.results[filename] = result
        return result
    
    def crack_directory(self, directory, recursive=True, extensions=None):
        """
        Crack all files in a directory
        
        Args:
            directory: Directory path
            recursive: Search subdirectories
            extensions: List of file extensions to process
            
        Returns:
            List of results
        """
        if extensions is None:
            extensions = ['.pdf', '.docx', '.doc', '.pptx', '.ppt', '.zip']
        
        # Find all files
        files = []
        if recursive:
            for root, dirs, filenames in os.walk(directory):
                for filename in filenames:
                    ext = os.path.splitext(filename)[1].lower()
                    if ext in extensions:
                        files.append(os.path.join(root, filename))
        else:
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                if os.path.isfile(filepath):
                    ext = os.path.splitext(filename)[1].lower()
                    if ext in extensions:
                        files.append(filepath)
        
        print(f"\nFound {len(files)} files to crack in {directory}")
        
        # Crack files
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.crack_file, f): f for f in files}
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        
        return results
    
    def save_results(self, output_file='crack_results.json'):
        """
        Save cracking results to file
        
        Args:
            output_file: Output file path
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_attempts': self.attempts,
            'successes': self.successes,
            'failures': self.failures,
            'results': self.results
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=4)
        
        print(f"\nResults saved to {output_file}")
    
    def print_summary(self):
        """Print summary of cracking results"""
        print("\n" + "="*60)
        print("CRACKING SUMMARY")
        print("="*60)
        print(f"Total files processed: {len(self.results)}")
        print(f"Successful cracks: {self.successes}")
        print(f"Failed cracks: {self.failures}")
        print(f"Total password attempts: {self.attempts}")
        
        if self.successes > 0:
            print("\nSuccessfully cracked files:")
            for filename, result in self.results.items():
                if result['status'] == 'success':
                    print(f"  ✓ {filename}: {result['password']}")
        
        print("="*60 + "\n")


def main():
    """Main cracking function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Crack password-protected files')
    parser.add_argument('--target', type=str, required=True,
                       help='Target file or directory to crack')
    parser.add_argument('--passwords', type=str,
                       default='pasgan/generated_passwords.txt',
                       help='Password list file')
    parser.add_argument('--recursive', action='store_true',
                       help='Search directories recursively')
    parser.add_argument('--workers', type=int, default=4,
                       help='Number of parallel workers')
    parser.add_argument('--output', type=str, default='crack_results.json',
                       help='Output results file')
    
    args = parser.parse_args()
    
    # Check if password file exists
    if not os.path.exists(args.passwords):
        print(f"Error: Password file not found: {args.passwords}")
        print("Please generate passwords first using generate.py")
        return
    
    # Create cracker
    cracker = FileCracker(password_file=args.passwords, max_workers=args.workers)
    
    # Crack files
    if os.path.isfile(args.target):
        # Single file
        cracker.crack_file(args.target)
    elif os.path.isdir(args.target):
        # Directory
        cracker.crack_directory(args.target, recursive=args.recursive)
    else:
        print(f"Error: Target not found: {args.target}")
        return
    
    # Print summary and save results
    cracker.print_summary()
    cracker.save_results(args.output)


if __name__ == '__main__':
    main()
