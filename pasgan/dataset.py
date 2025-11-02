"""
Password Dataset Handler
Loads and preprocesses password data for PassGAN training
"""

import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import string
import os


class PasswordDataset(Dataset):
    """
    Dataset class for password data
    Filters passwords to be 12 characters or longer
    """
    
    def __init__(self, password_file=None, passwords=None, seq_len=16, min_len=12):
        """
        Args:
            password_file: Path to password list file (one password per line)
            passwords: List of passwords (alternative to file)
            seq_len: Maximum sequence length
            min_len: Minimum password length (default 12)
        """
        self.seq_len = seq_len
        self.min_len = min_len
        
        # Define character vocabulary (printable ASCII)
        self.charset = string.printable[:95]  # Excludes some control characters
        self.char_to_idx = {char: idx for idx, char in enumerate(self.charset)}
        self.idx_to_char = {idx: char for char, idx in self.char_to_idx.items()}
        self.vocab_size = len(self.charset)
        
        # Load passwords
        if password_file and os.path.exists(password_file):
            self.passwords = self._load_from_file(password_file)
        elif passwords:
            self.passwords = self._filter_passwords(passwords)
        else:
            # Generate synthetic training data if no file provided
            self.passwords = self._generate_synthetic_passwords(10000)
            
        print(f"Loaded {len(self.passwords)} passwords (min length: {min_len}, max length: {seq_len})")
        
    def _load_from_file(self, filepath):
        """Load passwords from file and filter by length"""
        passwords = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    pwd = line.strip()
                    if self.min_len <= len(pwd) <= self.seq_len:
                        # Check if all characters are in vocabulary
                        if all(c in self.char_to_idx for c in pwd):
                            passwords.append(pwd)
        except Exception as e:
            print(f"Error loading password file: {e}")
        return passwords
    
    def _filter_passwords(self, passwords):
        """Filter passwords by length and character set"""
        filtered = []
        for pwd in passwords:
            if self.min_len <= len(pwd) <= self.seq_len:
                if all(c in self.char_to_idx for c in pwd):
                    filtered.append(pwd)
        return filtered
    
    def _generate_synthetic_passwords(self, count):
        """
        Generate synthetic passwords for training
        Uses common password patterns with 12+ characters
        """
        passwords = []
        patterns = [
            lambda: ''.join(np.random.choice(list(string.ascii_letters + string.digits), 
                                            np.random.randint(12, self.seq_len + 1))),
            lambda: ''.join(np.random.choice(list(string.ascii_letters), 
                                            np.random.randint(8, 12))) + 
                   ''.join(np.random.choice(list(string.digits), 
                                          np.random.randint(4, 8))),
            lambda: ''.join(np.random.choice(list(string.ascii_uppercase), 
                                            np.random.randint(4, 8))) +
                   ''.join(np.random.choice(list(string.ascii_lowercase), 
                                          np.random.randint(4, 8))) +
                   ''.join(np.random.choice(list(string.digits + string.punctuation), 
                                          np.random.randint(4, 8))),
        ]
        
        for _ in range(count):
            pattern = np.random.choice(patterns)
            pwd = pattern()
            if len(pwd) >= self.min_len:
                passwords.append(pwd[:self.seq_len])
                
        return passwords
    
    def __len__(self):
        return len(self.passwords)
    
    def __getitem__(self, idx):
        """
        Get a password and convert to indices
        Returns:
            Tensor of character indices, padded to seq_len
        """
        password = self.passwords[idx]
        
        # Convert to indices
        indices = [self.char_to_idx[c] for c in password]
        
        # Pad to seq_len
        if len(indices) < self.seq_len:
            indices += [0] * (self.seq_len - len(indices))  # Pad with index 0
            
        return torch.tensor(indices, dtype=torch.long)
    
    def decode(self, indices):
        """
        Convert indices back to password string
        Args:
            indices: Tensor or list of character indices
        Returns:
            Password string
        """
        if isinstance(indices, torch.Tensor):
            indices = indices.cpu().numpy()
        
        # Stop at padding (index 0) or end of sequence
        chars = []
        for idx in indices:
            if idx == 0:
                break
            if idx < self.vocab_size:
                chars.append(self.idx_to_char[idx])
        
        return ''.join(chars)
    
    def decode_batch(self, batch_indices):
        """
        Decode a batch of password indices
        Args:
            batch_indices: Tensor of shape (batch_size, seq_len)
        Returns:
            List of password strings
        """
        return [self.decode(indices) for indices in batch_indices]


def create_dataloader(password_file=None, passwords=None, batch_size=64, 
                     seq_len=16, min_len=12, shuffle=True, num_workers=0):
    """
    Create DataLoader for password dataset
    
    Args:
        password_file: Path to password list file
        passwords: List of passwords
        batch_size: Batch size
        seq_len: Maximum sequence length
        min_len: Minimum password length
        shuffle: Whether to shuffle data
        num_workers: Number of worker processes
        
    Returns:
        DataLoader, PasswordDataset
    """
    dataset = PasswordDataset(password_file=password_file, 
                             passwords=passwords,
                             seq_len=seq_len,
                             min_len=min_len)
    
    dataloader = DataLoader(dataset, 
                           batch_size=batch_size,
                           shuffle=shuffle,
                           num_workers=num_workers,
                           pin_memory=True)
    
    return dataloader, dataset


# Common password patterns for augmentation
COMMON_PATTERNS = [
    "Password123!",
    "Welcome2024!",
    "Admin@123456",
    "P@ssw0rd2024",
    "Qwerty123456",
    "Abc123456789",
    "Summer2024!!",
    "Winter2024##",
    "Spring202401",
    "Autumn202402",
]


def augment_passwords(passwords, augment_factor=2):
    """
    Augment password list with variations
    
    Args:
        passwords: List of passwords
        augment_factor: How many variations to create per password
        
    Returns:
        Augmented list of passwords
    """
    augmented = list(passwords)
    
    for pwd in passwords:
        for _ in range(augment_factor):
            # Random case changes
            if np.random.random() < 0.3:
                pwd_aug = ''.join([c.swapcase() if np.random.random() < 0.3 else c 
                                  for c in pwd])
                augmented.append(pwd_aug)
            
            # Add numbers at end
            if np.random.random() < 0.3 and len(pwd) < 14:
                pwd_aug = pwd + str(np.random.randint(10, 999))
                augmented.append(pwd_aug)
            
            # Add special characters
            if np.random.random() < 0.3 and len(pwd) < 15:
                special = np.random.choice(['!', '@', '#', '$', '%'])
                pwd_aug = pwd + special
                augmented.append(pwd_aug)
    
    return augmented
