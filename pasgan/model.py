"""
PassGAN Model Architecture
Generator and Discriminator for password generation with 12+ character constraint
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class Generator(nn.Module):
    """
    Generator network for PassGAN
    Generates passwords of length 12 or more characters
    """
    
    def __init__(self, latent_dim=128, seq_len=16, vocab_size=95, embed_dim=128):
        """
        Args:
            latent_dim: Dimension of the latent noise vector
            seq_len: Length of generated password sequences (minimum 12)
            vocab_size: Size of character vocabulary (printable ASCII)
            embed_dim: Embedding dimension
        """
        super(Generator, self).__init__()
        self.latent_dim = latent_dim
        self.seq_len = max(seq_len, 12)  # Ensure minimum 12 characters
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        
        # Initial projection
        self.fc1 = nn.Linear(latent_dim, 256)
        self.bn1 = nn.BatchNorm1d(256)
        
        # LSTM layers for sequence generation
        self.lstm1 = nn.LSTM(256, 512, batch_first=True, dropout=0.3)
        self.lstm2 = nn.LSTM(512, 512, batch_first=True, dropout=0.3)
        self.lstm3 = nn.LSTM(512, 256, batch_first=True, dropout=0.3)
        
        # Output projection to vocabulary
        self.fc_out = nn.Linear(256, vocab_size)
        
    def forward(self, z):
        """
        Forward pass
        Args:
            z: Latent noise vector (batch_size, latent_dim)
        Returns:
            Generated character probabilities (batch_size, seq_len, vocab_size)
        """
        batch_size = z.size(0)
        
        # Project and reshape
        x = F.leaky_relu(self.bn1(self.fc1(z)), 0.2)
        x = x.unsqueeze(1).repeat(1, self.seq_len, 1)  # (batch, seq_len, 256)
        
        # LSTM layers
        x, _ = self.lstm1(x)
        x, _ = self.lstm2(x)
        x, _ = self.lstm3(x)
        
        # Output projection
        x = self.fc_out(x)  # (batch, seq_len, vocab_size)
        
        return x


class Discriminator(nn.Module):
    """
    Discriminator network for PassGAN
    Classifies whether a password is real or generated
    """
    
    def __init__(self, seq_len=16, vocab_size=95, embed_dim=128):
        """
        Args:
            seq_len: Length of password sequences
            vocab_size: Size of character vocabulary
            embed_dim: Embedding dimension
        """
        super(Discriminator, self).__init__()
        self.seq_len = max(seq_len, 12)
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        
        # Embedding layer
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        
        # Convolutional layers for feature extraction
        self.conv1 = nn.Conv1d(embed_dim, 256, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(256, 512, kernel_size=3, padding=1)
        self.conv3 = nn.Conv1d(512, 512, kernel_size=3, padding=1)
        
        # Batch normalization
        self.bn1 = nn.BatchNorm1d(256)
        self.bn2 = nn.BatchNorm1d(512)
        self.bn3 = nn.BatchNorm1d(512)
        
        # Dropout for regularization
        self.dropout = nn.Dropout(0.3)
        
        # LSTM for sequential processing
        self.lstm = nn.LSTM(512, 256, batch_first=True, bidirectional=True)
        
        # Final classification layers
        self.fc1 = nn.Linear(512, 256)
        self.fc2 = nn.Linear(256, 1)
        
    def forward(self, x):
        """
        Forward pass
        Args:
            x: Input character sequences (batch_size, seq_len) - integer indices
        Returns:
            Probability that input is real (batch_size, 1)
        """
        # Handle both integer indices and one-hot encoded inputs
        if x.dtype == torch.float:
            # One-hot encoded input
            x = torch.argmax(x, dim=-1)
        
        # Embedding
        x = self.embedding(x)  # (batch, seq_len, embed_dim)
        x = x.transpose(1, 2)  # (batch, embed_dim, seq_len)
        
        # Convolutional layers
        x = F.leaky_relu(self.bn1(self.conv1(x)), 0.2)
        x = self.dropout(x)
        x = F.leaky_relu(self.bn2(self.conv2(x)), 0.2)
        x = self.dropout(x)
        x = F.leaky_relu(self.bn3(self.conv3(x)), 0.2)
        
        # Transpose for LSTM
        x = x.transpose(1, 2)  # (batch, seq_len, 512)
        
        # LSTM layer
        x, (h_n, c_n) = self.lstm(x)
        
        # Use last hidden state
        x = torch.cat([h_n[-2], h_n[-1]], dim=1)  # (batch, 512)
        
        # Classification
        x = F.leaky_relu(self.fc1(x), 0.2)
        x = self.dropout(x)
        x = self.fc2(x)
        
        return x


class ResidualBlock(nn.Module):
    """Residual block for improved gradient flow"""
    
    def __init__(self, channels):
        super(ResidualBlock, self).__init__()
        self.conv1 = nn.Conv1d(channels, channels, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm1d(channels)
        self.conv2 = nn.Conv1d(channels, channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm1d(channels)
        
    def forward(self, x):
        residual = x
        x = F.leaky_relu(self.bn1(self.conv1(x)), 0.2)
        x = self.bn2(self.conv2(x))
        x = x + residual
        x = F.leaky_relu(x, 0.2)
        return x


def weights_init(m):
    """Initialize network weights"""
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        nn.init.normal_(m.weight.data, 0.0, 0.02)
    elif classname.find('BatchNorm') != -1:
        nn.init.normal_(m.weight.data, 1.0, 0.02)
        nn.init.constant_(m.bias.data, 0)
    elif classname.find('Linear') != -1:
        nn.init.xavier_uniform_(m.weight.data)
        if m.bias is not None:
            nn.init.constant_(m.bias.data, 0)
