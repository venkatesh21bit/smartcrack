"""
Password Generation Script
Generates passwords using trained PassGAN model
Enforces minimum 12 character constraint
"""

import torch
import numpy as np
import os
import json
import argparse
from datetime import datetime

from model import Generator
from dataset import PasswordDataset


class PasswordGenerator:
    """
    Password generator using trained PassGAN model
    """
    
    def __init__(self, checkpoint_path, device=None):
        """
        Args:
            checkpoint_path: Path to trained model checkpoint
            device: Device to use (cuda/cpu)
        """
        self.device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load checkpoint
        print(f"Loading checkpoint from {checkpoint_path}")
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        
        self.config = checkpoint['config']
        
        # Create generator
        self.generator = Generator(
            latent_dim=self.config['latent_dim'],
            seq_len=self.config['seq_len'],
            vocab_size=self.config['vocab_size'],
            embed_dim=self.config['embed_dim']
        ).to(self.device)
        
        # Load weights
        self.generator.load_state_dict(checkpoint['generator_state_dict'])
        self.generator.eval()
        
        # Create dataset for decoding
        self.dataset = PasswordDataset(seq_len=self.config['seq_len'])
        
        print(f"Generator loaded successfully on {self.device}")
        print(f"Vocabulary size: {self.dataset.vocab_size}")
        print(f"Sequence length: {self.config['seq_len']}")
    
    def generate(self, num_passwords, min_length=12, temperature=1.0, unique=True):
        """
        Generate passwords
        
        Args:
            num_passwords: Number of passwords to generate
            min_length: Minimum password length
            temperature: Sampling temperature (higher = more diverse)
            unique: Return only unique passwords
            
        Returns:
            List of generated passwords
        """
        passwords = []
        generated_set = set()
        
        batch_size = 128
        attempts = 0
        max_attempts = num_passwords * 10  # Prevent infinite loop
        
        with torch.no_grad():
            while len(passwords) < num_passwords and attempts < max_attempts:
                attempts += 1
                
                # Generate noise
                noise = torch.randn(batch_size, self.config['latent_dim']).to(self.device)
                
                # Generate passwords
                logits = self.generator(noise) / temperature
                
                # Sample from distribution
                probs = torch.softmax(logits, dim=-1)
                indices = torch.multinomial(probs.view(-1, self.dataset.vocab_size), 1)
                indices = indices.view(batch_size, self.config['seq_len'])
                
                # Decode passwords
                batch_passwords = self.dataset.decode_batch(indices)
                
                # Filter by length and uniqueness
                for pwd in batch_passwords:
                    if len(pwd) >= min_length:
                        if unique:
                            if pwd not in generated_set:
                                passwords.append(pwd)
                                generated_set.add(pwd)
                        else:
                            passwords.append(pwd)
                    
                    if len(passwords) >= num_passwords:
                        break
        
        return passwords[:num_passwords]
    
    def generate_with_patterns(self, num_passwords, patterns=None, min_length=12):
        """
        Generate passwords with specific patterns
        
        Args:
            num_passwords: Number of passwords to generate
            patterns: List of pattern constraints (e.g., 'uppercase', 'digits', 'special')
            min_length: Minimum password length
            
        Returns:
            List of generated passwords matching patterns
        """
        if patterns is None:
            patterns = []
        
        passwords = []
        attempts = 0
        max_attempts = num_passwords * 20
        
        while len(passwords) < num_passwords and attempts < max_attempts:
            # Generate batch
            batch = self.generate(100, min_length=min_length, unique=False)
            
            # Filter by patterns
            for pwd in batch:
                if self._matches_patterns(pwd, patterns):
                    passwords.append(pwd)
                    if len(passwords) >= num_passwords:
                        break
            
            attempts += 1
        
        return passwords[:num_passwords]
    
    def _matches_patterns(self, password, patterns):
        """
        Check if password matches required patterns
        
        Args:
            password: Password string
            patterns: List of pattern names
            
        Returns:
            True if password matches all patterns
        """
        for pattern in patterns:
            if pattern == 'uppercase' and not any(c.isupper() for c in password):
                return False
            if pattern == 'lowercase' and not any(c.islower() for c in password):
                return False
            if pattern == 'digits' and not any(c.isdigit() for c in password):
                return False
            if pattern == 'special' and not any(not c.isalnum() for c in password):
                return False
        
        return True
    
    def save_passwords(self, passwords, output_file):
        """
        Save passwords to file
        
        Args:
            passwords: List of passwords
            output_file: Output file path
        """
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for pwd in passwords:
                f.write(pwd + '\n')
        
        print(f"Saved {len(passwords)} passwords to {output_file}")
    
    def generate_diverse_batch(self, num_passwords, min_length=12, 
                              temperature_range=(0.8, 1.5)):
        """
        Generate diverse batch with varying temperatures
        
        Args:
            num_passwords: Number of passwords to generate
            min_length: Minimum password length
            temperature_range: Range of temperatures to use
            
        Returns:
            List of generated passwords
        """
        passwords = []
        temps = np.linspace(temperature_range[0], temperature_range[1], 5)
        
        per_temp = num_passwords // len(temps)
        
        for temp in temps:
            batch = self.generate(per_temp, min_length=min_length, 
                                temperature=temp, unique=True)
            passwords.extend(batch)
        
        # Fill remaining
        if len(passwords) < num_passwords:
            remaining = num_passwords - len(passwords)
            batch = self.generate(remaining, min_length=min_length, unique=True)
            passwords.extend(batch)
        
        return passwords[:num_passwords]


def main():
    """Main generation function"""
    parser = argparse.ArgumentParser(description='Generate passwords using PassGAN')
    parser.add_argument('--checkpoint', type=str, 
                       default='pasgan/checkpoints/final_model.pth',
                       help='Path to model checkpoint')
    parser.add_argument('--num', type=int, default=10000,
                       help='Number of passwords to generate')
    parser.add_argument('--min-length', type=int, default=12,
                       help='Minimum password length')
    parser.add_argument('--output', type=str, 
                       default='pasgan/generated_passwords.txt',
                       help='Output file path')
    parser.add_argument('--temperature', type=float, default=1.0,
                       help='Sampling temperature')
    parser.add_argument('--diverse', action='store_true',
                       help='Use diverse temperature sampling')
    parser.add_argument('--patterns', type=str, nargs='+',
                       help='Required patterns (uppercase, lowercase, digits, special)')
    
    args = parser.parse_args()
    
    # Check if checkpoint exists
    if not os.path.exists(args.checkpoint):
        print(f"Error: Checkpoint not found at {args.checkpoint}")
        print("Please train the model first using train.py")
        return
    
    # Create generator
    generator = PasswordGenerator(args.checkpoint)
    
    # Generate passwords
    print(f"\nGenerating {args.num} passwords (min length: {args.min_length})...")
    
    if args.patterns:
        passwords = generator.generate_with_patterns(
            args.num, 
            patterns=args.patterns,
            min_length=args.min_length
        )
    elif args.diverse:
        passwords = generator.generate_diverse_batch(
            args.num,
            min_length=args.min_length
        )
    else:
        passwords = generator.generate(
            args.num,
            min_length=args.min_length,
            temperature=args.temperature
        )
    
    print(f"Generated {len(passwords)} unique passwords")
    
    # Show samples
    print("\nSample passwords:")
    for i, pwd in enumerate(passwords[:20]):
        print(f"  {i+1}. {pwd} (length: {len(pwd)})")
    
    # Save to file
    generator.save_passwords(passwords, args.output)
    
    # Statistics
    lengths = [len(pwd) for pwd in passwords]
    print(f"\nStatistics:")
    print(f"  Total passwords: {len(passwords)}")
    print(f"  Min length: {min(lengths)}")
    print(f"  Max length: {max(lengths)}")
    print(f"  Average length: {np.mean(lengths):.2f}")


if __name__ == '__main__':
    main()
