"""
Example Usage Script
Demonstrates various ways to use PassGAN components
"""

import os
import sys

# Add pasgan to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def example_1_basic_usage():
    """Example 1: Basic usage - complete pipeline"""
    print("="*60)
    print("EXAMPLE 1: Basic Complete Pipeline")
    print("="*60)
    
    from main import train_model, generate_passwords, crack_files
    
    # Train model
    config = {'num_epochs': 10, 'min_password_len': 12}  # Small for demo
    checkpoint = train_model(config)
    
    # Generate passwords
    password_file = generate_passwords(checkpoint, num_passwords=1000, min_length=12)
    
    # Crack files
    targets = ['Level1/Level1/Level1']
    crack_files(password_file, targets)


def example_2_custom_generation():
    """Example 2: Custom password generation"""
    print("="*60)
    print("EXAMPLE 2: Custom Password Generation")
    print("="*60)
    
    from generate import PasswordGenerator
    
    checkpoint = 'pasgan/checkpoints/final_model.pth'
    
    if os.path.exists(checkpoint):
        # Create generator
        generator = PasswordGenerator(checkpoint)
        
        # Generate with different temperatures
        print("\nLow temperature (focused):")
        passwords = generator.generate(10, min_length=12, temperature=0.5)
        for pwd in passwords:
            print(f"  {pwd}")
        
        print("\nHigh temperature (diverse):")
        passwords = generator.generate(10, min_length=12, temperature=1.5)
        for pwd in passwords:
            print(f"  {pwd}")
        
        # Generate with patterns
        print("\nWith uppercase, lowercase, and digits:")
        passwords = generator.generate_with_patterns(
            10, 
            patterns=['uppercase', 'lowercase', 'digits'],
            min_length=12
        )
        for pwd in passwords:
            print(f"  {pwd}")
    else:
        print("Model checkpoint not found. Train the model first.")


def example_3_direct_cracking():
    """Example 3: Direct file cracking"""
    print("="*60)
    print("EXAMPLE 3: Direct File Cracking")
    print("="*60)
    
    from cracker import FileCracker
    
    # Create custom password list
    passwords = [
        'Password1234',
        'Admin@123456',
        'Welcome2024!',
        'P@ssw0rd2024',
        'Qwerty123456',
    ]
    
    # Create cracker
    cracker = FileCracker(passwords=passwords, max_workers=2)
    
    # Try to crack a single file
    test_file = 'Level1/Level1/Level1/GC_PS7_S1_L1-1.docx'
    if os.path.exists(test_file):
        result = cracker.crack_file(test_file)
        print(f"\nResult: {result}")
    else:
        print(f"Test file not found: {test_file}")


def example_4_dataset_usage():
    """Example 4: Working with password datasets"""
    print("="*60)
    print("EXAMPLE 4: Password Dataset Usage")
    print("="*60)
    
    from dataset import PasswordDataset, create_dataloader, augment_passwords
    
    # Create dataset with synthetic passwords
    dataset = PasswordDataset(seq_len=16, min_len=12)
    
    print(f"\nDataset size: {len(dataset)}")
    print(f"Vocabulary size: {dataset.vocab_size}")
    print(f"Character set: {dataset.charset[:20]}...")
    
    # Get some samples
    print("\nSample passwords from dataset:")
    for i in range(5):
        indices = dataset[i]
        password = dataset.decode(indices)
        print(f"  {i+1}. {password}")
    
    # Augmentation
    original = ['Password123', 'Admin456789']
    augmented = augment_passwords(original, augment_factor=3)
    print(f"\nOriginal: {len(original)} passwords")
    print(f"Augmented: {len(augmented)} passwords")
    print("Samples:")
    for pwd in augmented[:10]:
        print(f"  {pwd}")


def example_5_model_inspection():
    """Example 5: Inspect model architecture"""
    print("="*60)
    print("EXAMPLE 5: Model Architecture")
    print("="*60)
    
    from model import Generator, Discriminator
    import torch
    
    # Create models
    generator = Generator(latent_dim=128, seq_len=16, vocab_size=95)
    discriminator = Discriminator(seq_len=16, vocab_size=95)
    
    print("\nGenerator Architecture:")
    print(generator)
    print(f"\nTotal parameters: {sum(p.numel() for p in generator.parameters()):,}")
    
    print("\n" + "-"*60)
    print("\nDiscriminator Architecture:")
    print(discriminator)
    print(f"\nTotal parameters: {sum(p.numel() for p in discriminator.parameters()):,}")
    
    # Test forward pass
    print("\n" + "-"*60)
    print("\nTesting forward pass...")
    
    # Generator
    noise = torch.randn(4, 128)  # Batch of 4
    gen_output = generator(noise)
    print(f"Generator input shape: {noise.shape}")
    print(f"Generator output shape: {gen_output.shape}")
    
    # Discriminator
    passwords = torch.randint(0, 95, (4, 16))  # Batch of 4
    disc_output = discriminator(passwords)
    print(f"Discriminator input shape: {passwords.shape}")
    print(f"Discriminator output shape: {disc_output.shape}")


def main():
    """Run examples"""
    print("\n" + "="*60)
    print("PassGAN Usage Examples")
    print("="*60)
    
    examples = {
        '1': ('Basic Complete Pipeline', example_1_basic_usage),
        '2': ('Custom Password Generation', example_2_custom_generation),
        '3': ('Direct File Cracking', example_3_direct_cracking),
        '4': ('Password Dataset Usage', example_4_dataset_usage),
        '5': ('Model Architecture Inspection', example_5_model_inspection),
    }
    
    print("\nAvailable examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print("  0. Run all examples")
    print("  q. Quit")
    
    choice = input("\nSelect example to run: ").strip()
    
    if choice == 'q':
        print("Goodbye!")
        return
    
    if choice == '0':
        for name, func in examples.values():
            print("\n\n")
            try:
                func()
            except Exception as e:
                print(f"Error in {name}: {e}")
            input("\nPress Enter to continue...")
    elif choice in examples:
        name, func = examples[choice]
        try:
            func()
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Invalid choice")


if __name__ == '__main__':
    main()
