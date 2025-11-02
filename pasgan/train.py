"""
PassGAN Training Script
Trains Generator and Discriminator networks for password generation
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.tensorboard import SummaryWriter
import numpy as np
import os
from datetime import datetime
import json

from model import Generator, Discriminator, weights_init
from dataset import create_dataloader, augment_passwords, COMMON_PATTERNS


class PassGANTrainer:
    """
    Trainer class for PassGAN
    """
    
    def __init__(self, config):
        """
        Args:
            config: Dictionary with training configuration
        """
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        
        # Create models
        self.generator = Generator(
            latent_dim=config['latent_dim'],
            seq_len=config['seq_len'],
            vocab_size=config['vocab_size'],
            embed_dim=config['embed_dim']
        ).to(self.device)
        
        self.discriminator = Discriminator(
            seq_len=config['seq_len'],
            vocab_size=config['vocab_size'],
            embed_dim=config['embed_dim']
        ).to(self.device)
        
        # Initialize weights
        self.generator.apply(weights_init)
        self.discriminator.apply(weights_init)
        
        # Optimizers
        self.g_optimizer = optim.Adam(
            self.generator.parameters(),
            lr=config['g_lr'],
            betas=(config['beta1'], config['beta2'])
        )
        
        self.d_optimizer = optim.Adam(
            self.discriminator.parameters(),
            lr=config['d_lr'],
            betas=(config['beta1'], config['beta2'])
        )
        
        # Loss function
        self.criterion = nn.BCEWithLogitsLoss()
        
        # Create save directory
        self.save_dir = config['save_dir']
        os.makedirs(self.save_dir, exist_ok=True)
        
        # Tensorboard writer
        log_dir = os.path.join(self.save_dir, 'logs', 
                              datetime.now().strftime('%Y%m%d_%H%M%S'))
        self.writer = SummaryWriter(log_dir)
        
        # Training stats
        self.epoch = 0
        self.g_losses = []
        self.d_losses = []
        
    def train_discriminator(self, real_data, batch_size):
        """
        Train discriminator for one step
        
        Args:
            real_data: Real password data (batch_size, seq_len)
            batch_size: Batch size
            
        Returns:
            Discriminator loss
        """
        self.discriminator.zero_grad()
        
        # Real data
        real_data = real_data.to(self.device)
        real_labels = torch.ones(batch_size, 1).to(self.device)
        
        real_output = self.discriminator(real_data)
        d_loss_real = self.criterion(real_output, real_labels)
        
        # Fake data
        noise = torch.randn(batch_size, self.config['latent_dim']).to(self.device)
        fake_data = self.generator(noise)
        fake_data_indices = torch.argmax(fake_data, dim=-1)
        fake_labels = torch.zeros(batch_size, 1).to(self.device)
        
        fake_output = self.discriminator(fake_data_indices.detach())
        d_loss_fake = self.criterion(fake_output, fake_labels)
        
        # Total discriminator loss
        d_loss = d_loss_real + d_loss_fake
        d_loss.backward()
        self.d_optimizer.step()
        
        return d_loss.item()
    
    def train_generator(self, batch_size):
        """
        Train generator for one step
        
        Args:
            batch_size: Batch size
            
        Returns:
            Generator loss
        """
        self.generator.zero_grad()
        
        # Generate fake data
        noise = torch.randn(batch_size, self.config['latent_dim']).to(self.device)
        fake_data = self.generator(noise)
        fake_data_indices = torch.argmax(fake_data, dim=-1)
        
        # Labels for generator (want discriminator to classify as real)
        real_labels = torch.ones(batch_size, 1).to(self.device)
        
        # Get discriminator's opinion
        fake_output = self.discriminator(fake_data_indices)
        g_loss = self.criterion(fake_output, real_labels)
        
        g_loss.backward()
        self.g_optimizer.step()
        
        return g_loss.item()
    
    def train_epoch(self, dataloader):
        """
        Train for one epoch
        
        Args:
            dataloader: DataLoader with password data
            
        Returns:
            Average generator loss, average discriminator loss
        """
        self.generator.train()
        self.discriminator.train()
        
        g_losses = []
        d_losses = []
        
        for i, real_data in enumerate(dataloader):
            batch_size = real_data.size(0)
            
            # Train Discriminator
            for _ in range(self.config['d_steps']):
                d_loss = self.train_discriminator(real_data, batch_size)
                d_losses.append(d_loss)
            
            # Train Generator
            for _ in range(self.config['g_steps']):
                g_loss = self.train_generator(batch_size)
                g_losses.append(g_loss)
            
            # Log progress
            if i % 50 == 0:
                print(f"  Batch {i}/{len(dataloader)} - "
                      f"D Loss: {np.mean(d_losses[-10:]):.4f}, "
                      f"G Loss: {np.mean(g_losses[-10:]):.4f}")
        
        return np.mean(g_losses), np.mean(d_losses)
    
    def generate_samples(self, num_samples=10, dataset=None):
        """
        Generate sample passwords
        
        Args:
            num_samples: Number of samples to generate
            dataset: Dataset object for decoding
            
        Returns:
            List of generated passwords
        """
        self.generator.eval()
        
        with torch.no_grad():
            noise = torch.randn(num_samples, self.config['latent_dim']).to(self.device)
            fake_data = self.generator(noise)
            fake_data_indices = torch.argmax(fake_data, dim=-1)
            
        if dataset:
            passwords = dataset.decode_batch(fake_data_indices)
        else:
            passwords = fake_data_indices.cpu().numpy().tolist()
        
        return passwords
    
    def save_checkpoint(self, filename='checkpoint.pth'):
        """
        Save model checkpoint
        
        Args:
            filename: Checkpoint filename
        """
        checkpoint = {
            'epoch': self.epoch,
            'generator_state_dict': self.generator.state_dict(),
            'discriminator_state_dict': self.discriminator.state_dict(),
            'g_optimizer_state_dict': self.g_optimizer.state_dict(),
            'd_optimizer_state_dict': self.d_optimizer.state_dict(),
            'g_losses': self.g_losses,
            'd_losses': self.d_losses,
            'config': self.config
        }
        
        filepath = os.path.join(self.save_dir, filename)
        torch.save(checkpoint, filepath)
        print(f"Checkpoint saved to {filepath}")
    
    def load_checkpoint(self, filepath):
        """
        Load model checkpoint
        
        Args:
            filepath: Path to checkpoint file
        """
        checkpoint = torch.load(filepath, map_location=self.device)
        
        self.epoch = checkpoint['epoch']
        self.generator.load_state_dict(checkpoint['generator_state_dict'])
        self.discriminator.load_state_dict(checkpoint['discriminator_state_dict'])
        self.g_optimizer.load_state_dict(checkpoint['g_optimizer_state_dict'])
        self.d_optimizer.load_state_dict(checkpoint['d_optimizer_state_dict'])
        self.g_losses = checkpoint['g_losses']
        self.d_losses = checkpoint['d_losses']
        
        print(f"Checkpoint loaded from {filepath}")
    
    def train(self, dataloader, num_epochs, dataset=None):
        """
        Main training loop
        
        Args:
            dataloader: DataLoader with password data
            num_epochs: Number of epochs to train
            dataset: Dataset object for sample generation
        """
        print(f"\nStarting training for {num_epochs} epochs...")
        print(f"Generator parameters: {sum(p.numel() for p in self.generator.parameters())}")
        print(f"Discriminator parameters: {sum(p.numel() for p in self.discriminator.parameters())}")
        
        for epoch in range(num_epochs):
            self.epoch = epoch
            print(f"\nEpoch {epoch+1}/{num_epochs}")
            
            # Train for one epoch
            g_loss, d_loss = self.train_epoch(dataloader)
            
            self.g_losses.append(g_loss)
            self.d_losses.append(d_loss)
            
            # Log to tensorboard
            self.writer.add_scalar('Loss/Generator', g_loss, epoch)
            self.writer.add_scalar('Loss/Discriminator', d_loss, epoch)
            
            print(f"Epoch {epoch+1} - G Loss: {g_loss:.4f}, D Loss: {d_loss:.4f}")
            
            # Generate sample passwords
            if (epoch + 1) % 5 == 0:
                print("\nSample generated passwords:")
                samples = self.generate_samples(10, dataset)
                for i, pwd in enumerate(samples):
                    print(f"  {i+1}. {pwd}")
            
            # Save checkpoint
            if (epoch + 1) % 10 == 0:
                self.save_checkpoint(f'checkpoint_epoch_{epoch+1}.pth')
        
        # Save final model
        self.save_checkpoint('final_model.pth')
        self.writer.close()
        print("\nTraining completed!")


def get_default_config():
    """
    Get default training configuration
    
    Returns:
        Configuration dictionary
    """
    return {
        'latent_dim': 128,
        'seq_len': 16,
        'vocab_size': 95,
        'embed_dim': 128,
        'g_lr': 0.0002,
        'd_lr': 0.0002,
        'beta1': 0.5,
        'beta2': 0.999,
        'batch_size': 64,
        'num_epochs': 100,
        'd_steps': 3,  # Train discriminator 3 times per generator step
        'g_steps': 1,
        'save_dir': 'pasgan/checkpoints',
        'min_password_len': 12
    }


def main():
    """Main training function"""
    
    # Configuration
    config = get_default_config()
    
    # Save configuration
    os.makedirs(config['save_dir'], exist_ok=True)
    with open(os.path.join(config['save_dir'], 'config.json'), 'w') as f:
        json.dump(config, f, indent=4)
    
    # Create dataset and dataloader
    print("Creating dataset...")
    
    # Use common patterns and synthetic data for initial training
    initial_passwords = COMMON_PATTERNS.copy()
    initial_passwords = augment_passwords(initial_passwords, augment_factor=5)
    
    dataloader, dataset = create_dataloader(
        passwords=initial_passwords,
        batch_size=config['batch_size'],
        seq_len=config['seq_len'],
        min_len=config['min_password_len'],
        shuffle=True
    )
    
    # Create trainer
    trainer = PassGANTrainer(config)
    
    # Train
    trainer.train(dataloader, config['num_epochs'], dataset)


if __name__ == '__main__':
    main()
