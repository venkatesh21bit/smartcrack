"""
Main Orchestration Script
Coordinates training, password generation, and file cracking
"""

import os
import sys
import argparse
from datetime import datetime
import json


def check_dependencies():
    """Check if required packages are installed"""
    missing = []
    
    try:
        import torch
    except ImportError:
        missing.append('torch')
    
    try:
        import numpy
    except ImportError:
        missing.append('numpy')
    
    try:
        import pikepdf
    except ImportError:
        missing.append('pikepdf')
    
    try:
        import msoffcrypto
    except ImportError:
        missing.append('msoffcrypto-tool')
    
    if missing:
        print("Missing dependencies:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\nInstall with:")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    return True


def train_model(config):
    """Train PassGAN model"""
    print("\n" + "="*60)
    print("STEP 1: TRAINING PASGAN MODEL")
    print("="*60)
    
    from train import PassGANTrainer, get_default_config
    from dataset import create_dataloader, augment_passwords, COMMON_PATTERNS
    
    # Use provided config or default
    train_config = get_default_config()
    if config:
        train_config.update(config)
    
    # Save configuration
    os.makedirs(train_config['save_dir'], exist_ok=True)
    with open(os.path.join(train_config['save_dir'], 'config.json'), 'w') as f:
        json.dump(train_config, f, indent=4)
    
    # Create dataset
    print("\nPreparing training data...")
    initial_passwords = COMMON_PATTERNS.copy()
    initial_passwords = augment_passwords(initial_passwords, augment_factor=5)
    
    dataloader, dataset = create_dataloader(
        passwords=initial_passwords,
        batch_size=train_config['batch_size'],
        seq_len=train_config['seq_len'],
        min_len=train_config['min_password_len'],
        shuffle=True
    )
    
    # Train model
    trainer = PassGANTrainer(train_config)
    trainer.train(dataloader, train_config['num_epochs'], dataset)
    
    print("\n✓ Training completed!")
    return os.path.join(train_config['save_dir'], 'final_model.pth')


def generate_passwords(checkpoint_path, num_passwords=10000, min_length=12):
    """Generate passwords using trained model"""
    print("\n" + "="*60)
    print("STEP 2: GENERATING PASSWORDS")
    print("="*60)
    
    from generate import PasswordGenerator
    
    if not os.path.exists(checkpoint_path):
        print(f"Error: Checkpoint not found at {checkpoint_path}")
        return None
    
    # Create generator
    generator = PasswordGenerator(checkpoint_path)
    
    # Generate passwords with diversity
    print(f"\nGenerating {num_passwords} passwords (min length: {min_length})...")
    passwords = generator.generate_diverse_batch(num_passwords, min_length=min_length)
    
    print(f"Generated {len(passwords)} unique passwords")
    
    # Show samples
    print("\nSample passwords:")
    for i, pwd in enumerate(passwords[:20]):
        print(f"  {i+1}. {pwd} (length: {len(pwd)})")
    
    # Save passwords
    output_file = 'pasgan/generated_passwords.txt'
    generator.save_passwords(passwords, output_file)
    
    print(f"\n✓ Password generation completed!")
    return output_file


def crack_files(password_file, targets):
    """Crack target files"""
    print("\n" + "="*60)
    print("STEP 3: CRACKING FILES")
    print("="*60)
    
    from cracker import FileCracker
    
    if not os.path.exists(password_file):
        print(f"Error: Password file not found: {password_file}")
        return
    
    # Create cracker
    cracker = FileCracker(password_file=password_file, max_workers=4)
    
    # Crack each target
    for target in targets:
        print(f"\nTarget: {target}")
        
        if os.path.isfile(target):
            cracker.crack_file(target)
        elif os.path.isdir(target):
            cracker.crack_directory(target, recursive=True)
        else:
            print(f"Warning: Target not found: {target}")
    
    # Print summary and save results
    cracker.print_summary()
    
    output_file = f'crack_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    cracker.save_results(output_file)
    
    print(f"\n✓ File cracking completed!")


def main():
    """Main orchestration function"""
    parser = argparse.ArgumentParser(
        description='PassGAN Password Cracker - Complete Pipeline'
    )
    
    parser.add_argument('--train', action='store_true',
                       help='Train PassGAN model')
    parser.add_argument('--generate', action='store_true',
                       help='Generate passwords')
    parser.add_argument('--crack', action='store_true',
                       help='Crack files')
    parser.add_argument('--all', action='store_true',
                       help='Run complete pipeline (train + generate + crack)')
    
    parser.add_argument('--checkpoint', type=str,
                       default='pasgan/checkpoints/final_model.pth',
                       help='Path to model checkpoint')
    parser.add_argument('--num-passwords', type=int, default=10000,
                       help='Number of passwords to generate')
    parser.add_argument('--min-length', type=int, default=12,
                       help='Minimum password length')
    parser.add_argument('--epochs', type=int, default=100,
                       help='Number of training epochs')
    
    parser.add_argument('--targets', type=str, nargs='+',
                       help='Target files or directories to crack')
    
    parser.add_argument('--skip-deps', action='store_true',
                       help='Skip dependency check')
    
    args = parser.parse_args()
    
    # Check dependencies
    if not args.skip_deps:
        print("Checking dependencies...")
        if not check_dependencies():
            print("\nPlease install missing dependencies and try again.")
            return
        print("✓ All dependencies satisfied\n")
    
    # Determine what to run
    run_train = args.train or args.all
    run_generate = args.generate or args.all
    run_crack = args.crack or args.all
    
    # If nothing specified, show help
    if not (run_train or run_generate or run_crack):
        parser.print_help()
        print("\n" + "="*60)
        print("QUICK START:")
        print("="*60)
        print("1. Run complete pipeline:")
        print("   python pasgan/main.py --all --targets Level1 Level2")
        print("\n2. Or run steps individually:")
        print("   python pasgan/main.py --train")
        print("   python pasgan/main.py --generate")
        print("   python pasgan/main.py --crack --targets Level1 Level2")
        print("="*60)
        return
    
    checkpoint_path = args.checkpoint
    password_file = 'pasgan/generated_passwords.txt'
    
    # Run pipeline
    try:
        # Step 1: Train model
        if run_train:
            config = {
                'num_epochs': args.epochs,
                'min_password_len': args.min_length
            }
            checkpoint_path = train_model(config)
        
        # Step 2: Generate passwords
        if run_generate:
            password_file = generate_passwords(
                checkpoint_path,
                num_passwords=args.num_passwords,
                min_length=args.min_length
            )
            if password_file is None:
                print("Error: Password generation failed")
                return
        
        # Step 3: Crack files
        if run_crack:
            if not args.targets:
                print("Error: No targets specified for cracking")
                print("Use --targets to specify files or directories")
                return
            
            crack_files(password_file, args.targets)
        
        print("\n" + "="*60)
        print("PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
