"""
Dataset Download and Preparation Script
Downloads and filters popular password datasets for training
"""

import os
import sys
import urllib.request
import gzip
import shutil


def download_file(url, filename):
    """Download a file with progress"""
    print(f"Downloading {filename}...")
    
    def reporthook(blocknum, blocksize, totalsize):
        readsofar = blocknum * blocksize
        if totalsize > 0:
            percent = readsofar * 100 / totalsize
            s = f"\r{percent:5.1f}% {readsofar:,} / {totalsize:,} bytes"
            sys.stderr.write(s)
            if readsofar >= totalsize:
                sys.stderr.write("\n")
        else:
            sys.stderr.write(f"\rRead {readsofar:,} bytes")
    
    try:
        urllib.request.urlretrieve(url, filename, reporthook)
        print(f"✓ Downloaded: {filename}")
        return True
    except Exception as e:
        print(f"✗ Error downloading: {e}")
        return False


def extract_gz(gz_file, output_file):
    """Extract .gz file"""
    print(f"Extracting {gz_file}...")
    try:
        with gzip.open(gz_file, 'rb') as f_in:
            with open(output_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        print(f"✓ Extracted: {output_file}")
        os.remove(gz_file)
        return True
    except Exception as e:
        print(f"✗ Error extracting: {e}")
        return False


def filter_passwords(input_file, output_file, min_len=12, max_len=16):
    """
    Filter passwords by length (12-16 characters)
    
    Args:
        input_file: Input password file
        output_file: Output filtered file
        min_len: Minimum password length
        max_len: Maximum password length
    """
    print(f"\nFiltering passwords (length: {min_len}-{max_len})...")
    
    total = 0
    filtered = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as fin:
            with open(output_file, 'w', encoding='utf-8') as fout:
                for line in fin:
                    total += 1
                    pwd = line.strip()
                    
                    # Filter by length
                    if min_len <= len(pwd) <= max_len:
                        # Check if all ASCII printable
                        if all(32 <= ord(c) < 127 for c in pwd):
                            fout.write(pwd + '\n')
                            filtered += 1
                    
                    # Progress
                    if total % 100000 == 0:
                        print(f"  Processed: {total:,} | Filtered: {filtered:,}", end='\r')
        
        print(f"\n✓ Filtered {filtered:,} passwords from {total:,} total")
        print(f"✓ Saved to: {output_file}")
        return True
    
    except Exception as e:
        print(f"✗ Error filtering: {e}")
        return False


def download_rockyou():
    """Download RockYou dataset"""
    print("\n" + "="*60)
    print("DOWNLOADING ROCKYOU DATASET")
    print("="*60)
    
    os.makedirs('datasets', exist_ok=True)
    
    # RockYou dataset URL
    url = "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt"
    output_file = "datasets/rockyou.txt"
    
    if os.path.exists(output_file):
        print(f"✓ RockYou dataset already exists: {output_file}")
        size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"  Size: {size_mb:.2f} MB")
    else:
        if download_file(url, output_file):
            size_mb = os.path.getsize(output_file) / (1024 * 1024)
            print(f"  Size: {size_mb:.2f} MB")
        else:
            print("\n⚠ Failed to download RockYou dataset")
            print("Manual download instructions:")
            print("1. Go to: https://github.com/brannondorsey/naive-hashcat/releases/")
            print("2. Download rockyou.txt")
            print("3. Place it in: datasets/rockyou.txt")
            return False
    
    # Filter for 12+ characters
    filtered_file = "datasets/rockyou-12plus.txt"
    if not os.path.exists(filtered_file):
        print("\nFiltering for 12+ character passwords...")
        if filter_passwords(output_file, filtered_file, min_len=12, max_len=16):
            print(f"✓ Created filtered dataset: {filtered_file}")
    else:
        print(f"✓ Filtered dataset already exists: {filtered_file}")
    
    return True


def download_leaked_datasets():
    """Information about other leaked password datasets"""
    print("\n" + "="*60)
    print("OTHER PASSWORD DATASETS")
    print("="*60)
    
    datasets = [
        {
            "name": "RockYou",
            "size": "14M+ passwords",
            "year": "2009",
            "url": "https://github.com/brannondorsey/naive-hashcat/releases/",
            "description": "Most popular, real user passwords from data breach"
        },
        {
            "name": "LinkedIn",
            "size": "6.5M+ passwords",
            "year": "2012",
            "url": "Various torrent sites",
            "description": "Professional passwords, often more complex"
        },
        {
            "name": "000webhost",
            "size": "13M+ passwords",
            "year": "2015",
            "url": "Various sources",
            "description": "Web hosting service breach"
        },
        {
            "name": "Adobe",
            "size": "150M+ passwords",
            "year": "2013",
            "url": "Various sources",
            "description": "Large dataset but many encrypted"
        },
        {
            "name": "SecLists",
            "size": "Various",
            "year": "Ongoing",
            "url": "https://github.com/danielmiessler/SecLists",
            "description": "Curated lists for security testing"
        }
    ]
    
    print("\nAvailable password datasets:\n")
    for i, ds in enumerate(datasets, 1):
        print(f"{i}. {ds['name']} ({ds['year']})")
        print(f"   Size: {ds['size']}")
        print(f"   Description: {ds['description']}")
        print(f"   URL: {ds['url']}")
        print()
    
    print("Recommendation: Start with RockYou - it's the most popular and effective\n")


def create_sample_dataset():
    """Create a small sample dataset for testing"""
    print("\n" + "="*60)
    print("CREATING SAMPLE DATASET")
    print("="*60)
    
    os.makedirs('datasets', exist_ok=True)
    
    sample_passwords = [
        # Common patterns
        "Password1234", "Welcome2024!", "Admin@123456",
        "P@ssw0rd2024", "Qwerty123456", "Abc123456789",
        
        # Real-looking patterns
        "Summer2024!!", "Winter2024##", "Spring202401",
        "Football2024", "Basketball99", "Baseball2024",
        
        # More complex
        "MyP@ssword99", "SecurePass123!", "Dragon123456",
        "Monkey123456", "Master123456", "Princess2024",
        
        # Variations
        "iloveyou2024", "sunshine2024", "password1234",
        "qwerty123456", "letmein12345", "trustno12024",
        
        # With symbols
        "P@ssw0rd!234", "Adm1n@System", "User$2024Pass",
        "Login#123456", "Access@2024!", "Entry!234567",
    ]
    
    output_file = "datasets/sample-passwords.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        for pwd in sample_passwords:
            f.write(pwd + '\n')
    
    print(f"✓ Created sample dataset: {output_file}")
    print(f"  Contains {len(sample_passwords)} passwords")
    print("  Use this for quick testing before downloading larger datasets\n")


def show_dataset_stats(filename):
    """Show statistics about a password dataset"""
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return
    
    print(f"\n" + "="*60)
    print(f"DATASET STATISTICS: {filename}")
    print("="*60)
    
    total = 0
    lengths = []
    has_upper = 0
    has_lower = 0
    has_digit = 0
    has_special = 0
    
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            total += 1
            pwd = line.strip()
            lengths.append(len(pwd))
            
            if any(c.isupper() for c in pwd):
                has_upper += 1
            if any(c.islower() for c in pwd):
                has_lower += 1
            if any(c.isdigit() for c in pwd):
                has_digit += 1
            if any(not c.isalnum() for c in pwd):
                has_special += 1
            
            if total >= 100000:  # Sample first 100k for speed
                break
    
    if lengths:
        print(f"Total passwords: {total:,}")
        print(f"Average length: {sum(lengths)/len(lengths):.2f}")
        print(f"Min length: {min(lengths)}")
        print(f"Max length: {max(lengths)}")
        print(f"\nCharacter usage:")
        print(f"  Uppercase: {has_upper/total*100:.1f}%")
        print(f"  Lowercase: {has_lower/total*100:.1f}%")
        print(f"  Digits: {has_digit/total*100:.1f}%")
        print(f"  Special chars: {has_special/total*100:.1f}%")
        print()


def main():
    """Main function"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  Password Dataset Download & Preparation Tool  ".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    print("\nOptions:")
    print("  1. Download RockYou dataset (Recommended)")
    print("  2. Show other available datasets")
    print("  3. Create sample dataset (for testing)")
    print("  4. Filter existing dataset")
    print("  5. Show dataset statistics")
    print("  6. Exit")
    
    choice = input("\nSelect option (1-6): ").strip()
    
    if choice == '1':
        download_rockyou()
        print("\n✓ Done! You can now use the dataset for training:")
        print("  python pasgan/train.py")
        
    elif choice == '2':
        download_leaked_datasets()
        
    elif choice == '3':
        create_sample_dataset()
        print("✓ You can test with this sample dataset:")
        print("  python pasgan/train.py")
        
    elif choice == '4':
        input_file = input("Input file path: ").strip()
        output_file = input("Output file path (default: datasets/filtered.txt): ").strip()
        if not output_file:
            output_file = "datasets/filtered.txt"
        
        min_len = input("Minimum length (default: 12): ").strip()
        min_len = int(min_len) if min_len else 12
        
        max_len = input("Maximum length (default: 16): ").strip()
        max_len = int(max_len) if max_len else 16
        
        filter_passwords(input_file, output_file, min_len, max_len)
        
    elif choice == '5':
        filename = input("Dataset file path: ").strip()
        show_dataset_stats(filename)
        
    elif choice == '6':
        print("Goodbye!")
    else:
        print("Invalid choice")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
