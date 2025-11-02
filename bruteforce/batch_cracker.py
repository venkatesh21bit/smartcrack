"""
Batch Password Cracker for Multiple Files
Cracks all files in Level1 and Level2 folders
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import concurrent.futures

from cracker import PasswordCracker


class BatchCracker:
    """Batch password cracker for multiple files"""
    
    def __init__(self, target_dirs: List[str], wordlist: str, 
                 output_dir: str = 'results', max_workers: int = 4):
        """
        Initialize batch cracker
        
        Args:
            target_dirs: List of directories containing password-protected files
            wordlist: Path to wordlist file
            output_dir: Directory to save results
            max_workers: Number of parallel workers
        """
        self.target_dirs = [Path(d) for d in target_dirs]
        self.wordlist = Path(wordlist)
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        
        # Validate inputs
        for target_dir in self.target_dirs:
            if not target_dir.exists():
                raise FileNotFoundError(f"Target directory not found: {target_dir}")
        
        if not self.wordlist.exists():
            raise FileNotFoundError(f"Wordlist not found: {wordlist}")
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Results storage
        self.results = {}
        self.start_time = None
        
    def find_target_files(self) -> List[Path]:
        """Find all password-protected files in target directories"""
        supported_extensions = ['.pdf', '.docx', '.xlsx', '.pptx', '.zip']
        target_files = []
        
        for target_dir in self.target_dirs:
            for ext in supported_extensions:
                target_files.extend(target_dir.glob(f'*{ext}'))
        
        return sorted(target_files)
    
    def crack_single_file(self, file_path: Path, attack_type: str = 'dictionary',
                         max_passwords: Optional[int] = None) -> Dict:
        """
        Crack a single file
        
        Args:
            file_path: Path to file
            attack_type: Type of attack to use
            max_passwords: Maximum passwords to try
            
        Returns:
            Dictionary with results
        """
        result = {
            'file': str(file_path),
            'filename': file_path.name,
            'success': False,
            'password': None,
            'attempts': 0,
            'time': 0,
            'error': None
        }
        
        try:
            cracker = PasswordCracker(str(file_path), verbose=False)
            start = time.time()
            
            if attack_type == 'dictionary':
                password = cracker.dictionary_attack(str(self.wordlist), max_passwords=max_passwords)
            elif attack_type == 'hybrid':
                password = cracker.hybrid_attack(str(self.wordlist))
            else:
                raise ValueError(f"Unsupported attack type: {attack_type}")
            
            elapsed = time.time() - start
            
            result['attempts'] = cracker.attempts
            result['time'] = elapsed
            
            if password:
                result['success'] = True
                result['password'] = password
                print(f"✓ {file_path.name}: {password} ({cracker.attempts:,} attempts in {elapsed:.1f}s)")
            else:
                print(f"✗ {file_path.name}: Failed ({cracker.attempts:,} attempts in {elapsed:.1f}s)")
        
        except Exception as e:
            result['error'] = str(e)
            print(f"✗ {file_path.name}: Error - {e}")
        
        return result
    
    def crack_all_files(self, attack_type: str = 'dictionary', 
                       max_passwords: Optional[int] = None,
                       parallel: bool = False) -> Dict:
        """
        Crack all files in target directories
        
        Args:
            attack_type: Type of attack to use
            max_passwords: Maximum passwords to try per file
            parallel: Whether to use parallel processing
            
        Returns:
            Dictionary with all results
        """
        target_files = self.find_target_files()
        
        if not target_files:
            print("No target files found!")
            return {}
        
        self.start_time = time.time()
        
        print(f"\n{'='*80}")
        print(f"BATCH PASSWORD CRACKING")
        print(f"{'='*80}")
        print(f"Target directories: {[str(d) for d in self.target_dirs]}")
        print(f"Total files: {len(target_files)}")
        print(f"Wordlist: {self.wordlist}")
        print(f"Attack type: {attack_type}")
        if max_passwords:
            print(f"Max passwords per file: {max_passwords:,}")
        print(f"Parallel processing: {'Yes' if parallel else 'No'}")
        if parallel:
            print(f"Workers: {self.max_workers}")
        print(f"{'='*80}\n")
        
        # Crack files
        if parallel:
            self._crack_parallel(target_files, attack_type, max_passwords)
        else:
            self._crack_sequential(target_files, attack_type, max_passwords)
        
        # Save results
        self._save_results()
        
        # Print summary
        self._print_summary()
        
        return self.results
    
    def _crack_sequential(self, target_files: List[Path], attack_type: str,
                         max_passwords: Optional[int]):
        """Crack files sequentially"""
        for i, file_path in enumerate(target_files, 1):
            print(f"\n[{i}/{len(target_files)}] Cracking {file_path.name}...")
            result = self.crack_single_file(file_path, attack_type, max_passwords)
            self.results[str(file_path)] = result
    
    def _crack_parallel(self, target_files: List[Path], attack_type: str,
                       max_passwords: Optional[int]):
        """Crack files in parallel"""
        from functools import partial
        
        crack_func = partial(self.crack_single_file, 
                           attack_type=attack_type,
                           max_passwords=max_passwords)
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(crack_func, f): f for f in target_files}
            
            for future in concurrent.futures.as_completed(futures):
                file_path = futures[future]
                try:
                    result = future.result()
                    self.results[str(file_path)] = result
                except Exception as e:
                    print(f"✗ {file_path.name}: Exception - {e}")
                    self.results[str(file_path)] = {
                        'file': str(file_path),
                        'filename': file_path.name,
                        'success': False,
                        'error': str(e)
                    }
    
    def _save_results(self):
        """Save results to JSON and text files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save JSON results
        json_file = self.output_dir / f'results_{timestamp}.json'
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Save cracked passwords to text file
        passwords_file = self.output_dir / f'cracked_passwords_{timestamp}.txt'
        with open(passwords_file, 'w') as f:
            f.write("CRACKED PASSWORDS\n")
            f.write("="*80 + "\n\n")
            
            for file_path, result in self.results.items():
                if result.get('success'):
                    f.write(f"File: {result['filename']}\n")
                    f.write(f"Password: {result['password']}\n")
                    f.write(f"Attempts: {result['attempts']:,}\n")
                    f.write(f"Time: {result['time']:.2f}s\n")
                    f.write("-" * 80 + "\n")
        
        print(f"\n✓ Results saved:")
        print(f"  - {json_file}")
        print(f"  - {passwords_file}")
    
    def _print_summary(self):
        """Print summary statistics"""
        total_time = time.time() - self.start_time
        total_files = len(self.results)
        successful = sum(1 for r in self.results.values() if r.get('success'))
        failed = total_files - successful
        total_attempts = sum(r.get('attempts', 0) for r in self.results.values())
        
        print(f"\n{'='*80}")
        print(f"SUMMARY")
        print(f"{'='*80}")
        print(f"Total files: {total_files}")
        print(f"✓ Cracked: {successful} ({successful/total_files*100:.1f}%)")
        print(f"✗ Failed: {failed} ({failed/total_files*100:.1f}%)")
        print(f"Total attempts: {total_attempts:,}")
        print(f"Total time: {self._format_time(total_time)}")
        if total_time > 0:
            print(f"Average speed: {total_attempts/total_time:.2f} passwords/sec")
        print(f"{'='*80}\n")
        
        # List cracked files
        if successful > 0:
            print(f"CRACKED FILES:")
            for result in self.results.values():
                if result.get('success'):
                    print(f"  ✓ {result['filename']}: {result['password']}")
        
        # List failed files
        if failed > 0:
            print(f"\nFAILED FILES:")
            for result in self.results.values():
                if not result.get('success'):
                    error = f" ({result['error']})" if result.get('error') else ""
                    print(f"  ✗ {result['filename']}{error}")
    
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


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch password cracker')
    parser.add_argument('-d', '--dirs', nargs='+', required=True,
                       help='Target directories containing password-protected files')
    parser.add_argument('-w', '--wordlist', required=True,
                       help='Path to wordlist file')
    parser.add_argument('-t', '--type', choices=['dictionary', 'hybrid'],
                       default='dictionary', help='Attack type')
    parser.add_argument('-m', '--max', type=int,
                       help='Maximum passwords to try per file')
    parser.add_argument('-o', '--output', default='results',
                       help='Output directory for results')
    parser.add_argument('-p', '--parallel', action='store_true',
                       help='Use parallel processing')
    parser.add_argument('--workers', type=int, default=4,
                       help='Number of parallel workers')
    
    args = parser.parse_args()
    
    cracker = BatchCracker(
        args.dirs,
        args.wordlist,
        output_dir=args.output,
        max_workers=args.workers
    )
    
    results = cracker.crack_all_files(
        attack_type=args.type,
        max_passwords=args.max,
        parallel=args.parallel
    )
    
    # Exit with success if any files were cracked
    successful = sum(1 for r in results.values() if r.get('success'))
    sys.exit(0 if successful > 0 else 1)


if __name__ == '__main__':
    main()
