# PassGAN Password Cracker - Getting Started Guide

## Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
cd c:\Users\91902\Documents\smartcrack
pip install -r pasgan\requirements.txt
```

### Step 2: Run Complete Pipeline
```bash
python pasgan\main.py --all --targets Level1\Level1\Level1 Level2\Level2
```

OR use the Windows batch script:
```bash
pasgan\run.bat
```

### Step 3: Check Results
Results will be saved in:
- `pasgan/checkpoints/` - Trained model
- `pasgan/generated_passwords.txt` - Generated passwords
- `crack_results_*.json` - Cracking results

---

## What Was Created

### 🗂️ File Structure
```
smartcrack/
└── pasgan/
    ├── model.py              # GAN architecture (Generator + Discriminator)
    ├── dataset.py            # Password dataset handler
    ├── train.py              # Model training script
    ├── generate.py           # Password generation script
    ├── cracker.py            # File cracking utility
    ├── main.py               # Main orchestration script
    ├── run.py                # Quick start script
    ├── run.bat               # Windows batch script
    ├── examples.py           # Usage examples
    ├── requirements.txt      # Python dependencies
    ├── README.md             # Full documentation
    └── __init__.py           # Package initialization
```

### 🎯 Key Features

1. **PassGAN Model** (model.py)
   - Generator: Creates passwords using LSTM layers
   - Discriminator: Classifies real vs. generated passwords
   - Enforces 12+ character minimum
   - 95-character vocabulary (printable ASCII)

2. **Training System** (train.py)
   - Adversarial training with Generator vs Discriminator
   - TensorBoard logging for monitoring
   - Checkpoint saving every 10 epochs
   - Supports custom datasets or synthetic data

3. **Password Generation** (generate.py)
   - Multiple temperature sampling for diversity
   - Pattern-based generation (uppercase, digits, special chars)
   - Batch generation with uniqueness filtering
   - Export to text file

4. **File Cracker** (cracker.py)
   - Multi-threaded cracking
   - Supports: PDF, DOCX, PPTX, ZIP
   - Progress tracking and statistics
   - JSON result export

5. **Main Orchestration** (main.py)
   - Complete pipeline automation
   - Dependency checking
   - Flexible step selection
   - Error handling

---

## Target Files

### Level 1 Files (Level1/Level1/Level1/)
- 20 files: GC_PS7_S1_L1-1.docx through GC_PS7_S1_L1-20.pdf
- Mix of DOCX and PDF files

### Level 2 Files (Level2/Level2/)
- 20 files: GC_PS7_S1_L2-1.docx through GC_PS7_S1_L2-20.pdf
- Mix of DOCX, PPTX, and PDF files

---

## Usage Options

### Option 1: One Command (Recommended)
```bash
python pasgan\main.py --all --targets Level1\Level1\Level1 Level2\Level2
```

### Option 2: Step-by-Step
```bash
# Train
python pasgan\main.py --train --epochs 100

# Generate
python pasgan\main.py --generate --num-passwords 10000

# Crack
python pasgan\main.py --crack --targets Level1\Level1\Level1 Level2\Level2
```

### Option 3: Individual Scripts
```bash
# Train model
python pasgan\train.py

# Generate passwords
python pasgan\generate.py --checkpoint pasgan\checkpoints\final_model.pth --num 10000

# Crack files
python pasgan\cracker.py --target Level1\Level1\Level1 --passwords pasgan\generated_passwords.txt
```

### Option 4: Windows Batch Script
```bash
# Double-click or run:
pasgan\run.bat
```

### Option 5: Python API
```python
from pasgan import PasswordGenerator, FileCracker

# Generate passwords
generator = PasswordGenerator('pasgan/checkpoints/final_model.pth')
passwords = generator.generate(1000, min_length=12)

# Crack files
cracker = FileCracker(passwords=passwords)
result = cracker.crack_file('path/to/file.pdf')
```

---

## Configuration

Edit default settings in `train.py`:
```python
config = {
    'latent_dim': 128,          # Noise vector dimension
    'seq_len': 16,              # Max password length
    'vocab_size': 95,           # Character vocabulary
    'batch_size': 64,           # Training batch size
    'num_epochs': 100,          # Training epochs
    'min_password_len': 12,     # Minimum password length
    'g_lr': 0.0002,            # Generator learning rate
    'd_lr': 0.0002,            # Discriminator learning rate
}
```

---

## Expected Timeline

1. **Installation**: 2-5 minutes
2. **Training**: 10-60 minutes (depends on hardware & epochs)
3. **Generation**: 30 seconds - 2 minutes
4. **Cracking**: Variable (depends on password complexity)

**Total for complete pipeline**: 30-90 minutes

---

## Dependencies Installed

```
torch>=2.0.0              # Deep learning framework
numpy>=1.24.0             # Numerical computing
tensorboard>=2.14.0       # Training visualization
pikepdf>=8.0.0           # PDF cracking
msoffcrypto-tool>=5.0.0  # Office file cracking
tqdm>=4.65.0             # Progress bars
```

---

## Troubleshooting

### Issue: Import errors
**Solution**: Install dependencies
```bash
pip install torch numpy pikepdf msoffcrypto-tool
```

### Issue: CUDA not available
**Solution**: System will use CPU automatically (slower but works)

### Issue: Out of memory
**Solution**: Reduce batch size in config (e.g., 32 instead of 64)

### Issue: No passwords found
**Solution**: 
- Train longer (more epochs)
- Generate more passwords
- Try different temperature values

---

## Output Examples

### Generated Passwords
```
Password1234!
Admin@123456
Welcome2024#
P@ssw0rd2024
Qwerty123456789
Summer2024!!
Abc123XYZ789
```

### Cracking Results
```json
{
    "timestamp": "2024-11-02T10:30:00",
    "successes": 5,
    "failures": 15,
    "results": {
        "GC_PS7_S1_L1-1.docx": {
            "status": "success",
            "password": "Password1234!",
            "time": 12.5
        }
    }
}
```

---

## Next Steps

1. **Run the system**:
   ```bash
   python pasgan\main.py --all --targets Level1\Level1\Level1 Level2\Level2
   ```

2. **Monitor training**:
   ```bash
   tensorboard --logdir pasgan\checkpoints\logs
   ```

3. **Check results**:
   - View `crack_results_*.json` for success/failure statistics
   - Successful passwords will be listed in the results

4. **Improve results** (if needed):
   - Train longer: `--epochs 200`
   - Generate more: `--num-passwords 50000`
   - Use custom password list if you have one

---

## Tips for Success

✅ **Start with quick test**: 10 epochs, 1000 passwords on 1 file
✅ **Use GPU**: Much faster training if available
✅ **Be patient**: Training takes time but runs automatically
✅ **Check samples**: Review generated passwords during training
✅ **Parallel cracking**: Speeds up multi-file cracking

---

## Support

For detailed documentation, see: `pasgan\README.md`
For usage examples, run: `python pasgan\examples.py`

---

**You're all set! The PassGAN system is ready to use.** 🚀
