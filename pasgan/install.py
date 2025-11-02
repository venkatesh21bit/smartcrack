"""
Installation and Verification Script
Checks system requirements and installs dependencies
"""

import sys
import os
import subprocess
import platform


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def check_python_version():
    """Check if Python version is compatible"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required")
        return False
    
    print("✓ Python version is compatible")
    return True


def check_pip():
    """Check if pip is available"""
    print_header("Checking pip")
    
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"],
                              capture_output=True, text=True)
        print(f"pip version: {result.stdout.strip()}")
        print("✓ pip is available")
        return True
    except Exception as e:
        print(f"❌ Error: pip is not available - {e}")
        return False


def install_dependencies():
    """Install required dependencies"""
    print_header("Installing Dependencies")
    
    requirements_file = os.path.join('pasgan', 'requirements.txt')
    
    if not os.path.exists(requirements_file):
        print(f"❌ Error: Requirements file not found: {requirements_file}")
        return False
    
    print(f"Installing from {requirements_file}...")
    print("This may take several minutes...\n")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", requirements_file],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            print("✓ Dependencies installed successfully")
            return True
        else:
            print("❌ Error installing dependencies:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def verify_imports():
    """Verify that all required packages can be imported"""
    print_header("Verifying Installations")
    
    packages = {
        'torch': 'PyTorch',
        'numpy': 'NumPy',
        'pikepdf': 'pikepdf (PDF support)',
        'msoffcrypto': 'msoffcrypto-tool (Office support)',
    }
    
    all_ok = True
    
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"✓ {name} - OK")
        except ImportError:
            print(f"❌ {name} - NOT FOUND")
            all_ok = False
    
    return all_ok


def check_cuda():
    """Check if CUDA is available for GPU acceleration"""
    print_header("Checking GPU Support")
    
    try:
        import torch
        
        if torch.cuda.is_available():
            device_count = torch.cuda.device_count()
            device_name = torch.cuda.get_device_name(0)
            print(f"✓ CUDA is available!")
            print(f"  Devices: {device_count}")
            print(f"  Device 0: {device_name}")
            print("  → Training will use GPU (much faster)")
        else:
            print("ℹ CUDA is not available")
            print("  → Training will use CPU (slower but works)")
    except Exception as e:
        print(f"ℹ Could not check CUDA: {e}")


def check_disk_space():
    """Check available disk space"""
    print_header("Checking Disk Space")
    
    try:
        import shutil
        
        total, used, free = shutil.disk_usage(os.getcwd())
        
        free_gb = free / (1024**3)
        print(f"Free disk space: {free_gb:.2f} GB")
        
        if free_gb < 1:
            print("⚠ Warning: Low disk space (< 1 GB)")
            print("  Model checkpoints and logs may require ~500 MB")
        else:
            print("✓ Sufficient disk space available")
    except Exception as e:
        print(f"ℹ Could not check disk space: {e}")


def verify_targets():
    """Verify target files exist"""
    print_header("Checking Target Files")
    
    targets = [
        'Level1/Level1/Level1',
        'Level2/Level2'
    ]
    
    total_files = 0
    
    for target in targets:
        if os.path.exists(target):
            files = [f for f in os.listdir(target) if os.path.isfile(os.path.join(target, f))]
            print(f"✓ {target}: {len(files)} files found")
            total_files += len(files)
        else:
            print(f"❌ {target}: Directory not found")
    
    print(f"\nTotal target files: {total_files}")


def print_next_steps():
    """Print next steps for the user"""
    print_header("Installation Complete!")
    
    print("\n📋 Next Steps:")
    print("\n1. Run the complete pipeline:")
    print("   python pasgan\\main.py --all --targets Level1\\Level1\\Level1 Level2\\Level2")
    
    print("\n2. Or run individual steps:")
    print("   python pasgan\\main.py --train")
    print("   python pasgan\\main.py --generate")
    print("   python pasgan\\main.py --crack --targets Level1\\Level1\\Level1")
    
    print("\n3. Or use the Windows batch script:")
    print("   pasgan\\run.bat")
    
    print("\n📚 Documentation:")
    print("   - Quick Start: pasgan\\GETTING_STARTED.md")
    print("   - Full Docs: pasgan\\README.md")
    print("   - Architecture: pasgan\\ARCHITECTURE.txt")
    print("   - Examples: python pasgan\\examples.py")
    
    print("\n⏱️ Expected Time:")
    print("   - Training: 10-60 minutes")
    print("   - Generation: 30 seconds - 2 minutes")
    print("   - Cracking: Varies by complexity")
    print("   - Total: 30-90 minutes for complete pipeline")
    
    print("\n" + "="*60)


def main():
    """Main installation and verification function"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  PassGAN Password Cracker - Installation & Verification  ".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    print(f"\nSystem: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    
    # Step 1: Check Python
    if not check_python_version():
        print("\n❌ Installation cannot continue - Python version too old")
        return False
    
    # Step 2: Check pip
    if not check_pip():
        print("\n❌ Installation cannot continue - pip not available")
        return False
    
    # Step 3: Check disk space
    check_disk_space()
    
    # Step 4: Install dependencies
    print("\n📦 Ready to install dependencies")
    response = input("Continue with installation? (y/n): ").strip().lower()
    
    if response != 'y':
        print("Installation cancelled")
        return False
    
    if not install_dependencies():
        print("\n❌ Installation failed")
        print("\nTry manual installation:")
        print("  pip install torch numpy pikepdf msoffcrypto-tool")
        return False
    
    # Step 5: Verify installations
    if not verify_imports():
        print("\n⚠ Warning: Some packages could not be imported")
        print("You may need to reinstall them manually")
    
    # Step 6: Check CUDA
    check_cuda()
    
    # Step 7: Verify targets
    verify_targets()
    
    # Step 8: Print next steps
    print_next_steps()
    
    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
