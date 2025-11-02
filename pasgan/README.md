# PassGAN Password Cracker

A GAN-based password cracking system that generates passwords of 12+ characters to crack password-protected files.

## Features

- **PassGAN Model**: Deep learning-based password generation using Generative Adversarial Networks
- **12+ Character Constraint**: Enforces minimum password length of 12 characters
- **Multi-Format Support**: Cracks PDF, DOCX, PPTX, and ZIP files
- **Parallel Processing**: Multi-threaded file cracking for improved performance
- **Diverse Generation**: Multiple temperature sampling for password diversity

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
pasgan/
├── model.py          # Generator and Discriminator architectures
├── dataset.py        # Password dataset handler
├── train.py          # Training script
├── generate.py       # Password generation script
├── cracker.py        # File cracking utility
├── main.py           # Main orchestration script
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Usage

### Quick Start - Complete Pipeline

Run the entire pipeline (train, generate, crack):

```bash
cd c:\Users\91902\Documents\smartcrack
python pasgan/main.py --all --targets Level1/Level1/Level1 Level2/Level2
```

### Step-by-Step Usage

#### 1. Train the Model

```bash
python pasgan/main.py --train --epochs 100
```

Options:
- `--epochs`: Number of training epochs (default: 100)
- `--min-length`: Minimum password length (default: 12)

#### 2. Generate Passwords

```bash
python pasgan/main.py --generate --num-passwords 10000
```

Options:
- `--num-passwords`: Number of passwords to generate (default: 10000)
- `--min-length`: Minimum password length (default: 12)
- `--checkpoint`: Path to model checkpoint

#### 3. Crack Files

```bash
python pasgan/main.py --crack --targets Level1 Level2
```

Options:
- `--targets`: Target files or directories to crack
- `--checkpoint`: Path to model checkpoint

### Advanced Usage

#### Generate Passwords with Specific Patterns

```bash
python pasgan/generate.py --checkpoint pasgan/checkpoints/final_model.pth \
                          --num 10000 \
                          --min-length 12 \
                          --patterns uppercase lowercase digits \
                          --output my_passwords.txt
```

#### Crack Specific File

```bash
python pasgan/cracker.py --target "Level1/Level1/Level1/GC_PS7_S1_L1-1.docx" \
                         --passwords pasgan/generated_passwords.txt
```

#### Train with Custom Configuration

```python
python pasgan/train.py
```

Edit the `get_default_config()` function in `train.py` to customize training parameters.

## Model Architecture

### Generator
- **Input**: Random latent vector (128 dimensions)
- **Architecture**: 
  - Fully connected layer with batch normalization
  - 3-layer LSTM (256, 512, 512, 256)
  - Output projection to vocabulary size (95 characters)
- **Output**: Password sequence (12-16 characters)

### Discriminator
- **Input**: Password sequence (character indices)
- **Architecture**:
  - Character embedding layer
  - 3-layer CNN with batch normalization
  - Bidirectional LSTM
  - Fully connected classification layers
- **Output**: Real/Fake probability

## Configuration

Default configuration (can be modified in `train.py`):

```python
{
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
    'd_steps': 3,
    'g_steps': 1,
    'min_password_len': 12
}
```

## Output Files

- `pasgan/checkpoints/`: Model checkpoints
- `pasgan/generated_passwords.txt`: Generated password list
- `crack_results_*.json`: Cracking results with statistics

## Supported File Types

- **PDF**: `.pdf` files (requires pikepdf)
- **Microsoft Word**: `.docx`, `.doc` (requires msoffcrypto-tool)
- **Microsoft PowerPoint**: `.pptx`, `.ppt` (requires msoffcrypto-tool)
- **ZIP Archives**: `.zip` files

## Performance Tips

1. **GPU Acceleration**: Use CUDA-enabled GPU for faster training
2. **Batch Size**: Increase batch size if you have more memory
3. **Multiple Workers**: Use `--workers` flag for parallel cracking
4. **Password Diversity**: Use `--diverse` flag for better coverage

## Targets

The system is designed to crack files in:
- `Level1/Level1/Level1/` - 20 files (DOCX and PDF)
- `Level2/Level2/` - 20 files (DOCX, PPTX, and PDF)

## Examples

### Example 1: Quick Test
```bash
# Train small model and test on one file
python pasgan/main.py --train --epochs 10
python pasgan/main.py --generate --num-passwords 1000
python pasgan/main.py --crack --targets "Level1/Level1/Level1/GC_PS7_S1_L1-1.docx"
```

### Example 2: Production Run
```bash
# Full training and cracking all files
python pasgan/main.py --all --epochs 200 --num-passwords 50000 \
                      --targets Level1/Level1/Level1 Level2/Level2
```

## Troubleshooting

### Import Errors
If you get import errors for torch, pikepdf, or msoffcrypto:
```bash
pip install torch pikepdf msoffcrypto-tool
```

### CUDA Errors
If CUDA is not available, the system will automatically use CPU.

### Memory Issues
Reduce batch size in configuration or use fewer workers for cracking.

## Notes

- Training time varies based on epochs and hardware (10-60 minutes typical)
- Password generation is fast (seconds to minutes for 10k passwords)
- Cracking time depends on password list size and number of files
- Results are saved automatically with timestamps

## License

Educational and research purposes only. Use responsibly and ethically.
