# Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies

```bash
cd bruteforce
pip install -r requirements.txt
```

This will install:
- `pikepdf` - For PDF files
- `msoffcrypto-tool` - For Office files

### Step 2: Verify Wordlist

The RockYou filtered dataset should already be copied to `wordlists/rockyou-12plus.txt`.

Check if it exists:
```bash
dir wordlists
```

If not found, copy it:
```bash
Copy-Item "..\pasgan\datasets\rockyou-12plus.txt" -Destination "wordlists\rockyou-12plus.txt"
```

### Step 3: Run the Cracker

**Option A: Use the Menu Interface (Easiest)**
```bash
run.bat
```

**Option B: Command Line (Single File)**
```bash
python cracker.py "..\Level1\Level1\Level1\file1.pdf" -w wordlists\rockyou-12plus.txt -t dictionary
```

**Option C: Batch Crack All Files**
```bash
python batch_cracker.py -d ..\Level1\Level1\Level1 ..\Level2\Level2 -w wordlists\rockyou-12plus.txt -t dictionary
```

## 📋 Complete Examples

### Example 1: Crack a Single PDF File

```bash
python cracker.py "C:\path\to\document.pdf" -w wordlists\rockyou-12plus.txt -t dictionary
```

**Output:**
```
============================================================
DICTIONARY ATTACK
============================================================
Target file: document.pdf
File type: PDF
Wordlist: wordlists\rockyou-12plus.txt
============================================================

Attempts: 5,432 | Speed: 85.23 pwd/s | Time: 1m 3.7s

============================================================
✓ PASSWORD FOUND!
============================================================
Password: Summer2024!!
Attempts: 5,432
Time elapsed: 1m 3.7s
Speed: 85.23 passwords/sec
============================================================
```

### Example 2: Crack All Files in Level1 and Level2

```bash
python batch_cracker.py -d ..\Level1\Level1\Level1 ..\Level2\Level2 -w wordlists\rockyou-12plus.txt -t dictionary
```

**Output:**
```
================================================================================
BATCH PASSWORD CRACKING
================================================================================
Target directories: ['..\\Level1\\Level1\\Level1', '..\\Level2\\Level2']
Total files: 40
Wordlist: wordlists\rockyou-12plus.txt
Attack type: dictionary
================================================================================

[1/40] Cracking file1.pdf...
✓ file1.pdf: HelloWorld123 (3,245 attempts in 3.2s)

[2/40] Cracking file2.docx...
✓ file2.docx: Password@2024 (8,723 attempts in 8.7s)

...

================================================================================
SUMMARY
================================================================================
Total files: 40
✓ Cracked: 18 (45.0%)
✗ Failed: 22 (55.0%)
Total attempts: 2,456,789
Total time: 41m 23s
Average speed: 989.45 passwords/sec
================================================================================
```

### Example 3: Hybrid Attack (Dictionary + Mutations)

Tries passwords like: "password", "password!", "password123", "123password", etc.

```bash
python cracker.py document.pdf -w wordlists\rockyou-12plus.txt -t hybrid
```

### Example 4: Brute Force (Short Passwords Only!)

```bash
# Only for 4-6 digit passwords
python cracker.py file.zip -t brute_force --min-length 4 --max-length 6 --charset "0123456789"
```

**⚠️ Warning:** Brute force is VERY slow for passwords > 6 characters!

## 🎯 Tips for Best Results

### 1. Choose the Right Attack Type

| Password Type | Recommended Attack | Expected Time |
|---------------|-------------------|---------------|
| Common words | Dictionary | Seconds to minutes |
| Words + numbers | Hybrid | Minutes |
| Short random (4-6 chars) | Brute Force | Minutes to hours |
| Long random (12+ chars) | ❌ Not feasible | Years to centuries |

### 2. Start with Dictionary Attack

Always try dictionary attack first - it's the fastest and most effective for common passwords.

```bash
# Try first 100,000 passwords
python cracker.py file.pdf -w wordlists\rockyou-12plus.txt -t dictionary -m 100000
```

### 3. Use Parallel Processing for Multiple Files

```bash
python batch_cracker.py -d ..\Level1\Level1\Level1 -w wordlists\rockyou-12plus.txt -p --workers 4
```

### 4. Check Results

Results are automatically saved to `results/` folder:
- `results_YYYYMMDD_HHMMSS.json` - Complete results
- `cracked_passwords_YYYYMMDD_HHMMSS.txt` - Found passwords

View results:
```bash
type results\cracked_passwords_20241102_143022.txt
```

## 🔍 Understanding the Output

### Progress Indicator

```
Line: 5,432 | Attempts: 5,432 | Speed: 85.23 pwd/s | Time: 1m 3.7s
```

- **Line**: Current line in wordlist
- **Attempts**: Total passwords tried
- **Speed**: Passwords tested per second
- **Time**: Elapsed time

### Success Message

```
✓ PASSWORD FOUND!
Password: Summer2024!!
Attempts: 5,432
Time: 1m 3.7s
```

### Failure Message

```
✗ Password not found
Attempts: 2,800,000
Time: 52m 15s
```

## 🛠️ Troubleshooting

### Issue: "pikepdf not found"

**Solution:**
```bash
pip install pikepdf
```

### Issue: "msoffcrypto-tool not found"

**Solution:**
```bash
pip install msoffcrypto-tool
```

### Issue: "Wordlist not found"

**Solution:**
```bash
# Copy from pasgan folder
Copy-Item "..\pasgan\datasets\rockyou-12plus.txt" -Destination "wordlists\rockyou-12plus.txt"
```

### Issue: Very slow cracking

**Solutions:**
1. Use dictionary attack instead of brute force
2. Enable parallel processing: `-p`
3. Limit attempts: `-m 100000`
4. Use a smaller wordlist

### Issue: No files found in batch mode

**Solution:**
```bash
# Check directories exist
dir ..\Level1\Level1\Level1
dir ..\Level2\Level2

# Use correct relative or absolute paths
python batch_cracker.py -d "C:\Users\...\Level1\Level1\Level1" -w wordlists\rockyou-12plus.txt
```

## 📊 Success Rate Estimates

Based on testing with RockYou dataset:

| Password Pattern | Success Rate | Example |
|------------------|--------------|---------|
| Common words | 60-80% | "password123456" |
| Names + numbers | 40-60% | "Jennifer1234" |
| Dictionary words | 30-50% | "Sunshine2024" |
| Random lowercase | 10-20% | "hjsdfkjhsdkf" |
| Strong random | 0-5% | "xK9#mP2$nQ7@" |

**Overall Success Rate:** 30-50% for typical user passwords

## 🎮 Menu Interface Guide

Run `run.bat` to see:

```
╔════════════════════════════════════════════════════════════════╗
║        BRUTE FORCE PASSWORD CRACKER                            ║
╚════════════════════════════════════════════════════════════════╝

[1] Dictionary Attack (Single File)     ← Best for testing single files
[2] Dictionary Attack (Batch)           ← Crack all Level1 & Level2 files
[3] Hybrid Attack                       ← Dictionary + mutations
[4] Brute Force Attack                  ← Only for very short passwords
[5] Check Wordlist Statistics           ← View wordlist info
[6] View Previous Results               ← See past cracking sessions
[7] Exit
```

### Option 1: Dictionary Attack (Single File)

Best for:
- Testing a single file
- Quick password recovery
- Trying limited number of passwords

### Option 2: Batch Attack

Best for:
- Cracking all files in Level1 and Level2
- Automated bulk processing
- Getting overall statistics

### Option 3: Hybrid Attack

Best for:
- Passwords with common variations
- Users who add numbers/symbols to words
- Higher success rate than pure dictionary

### Option 4: Brute Force

Best for:
- Very short passwords (4-6 characters)
- Numeric-only passwords
- When you know the password pattern

**⚠️ NOT recommended for 12+ character passwords!**

### Option 5: Wordlist Statistics

Shows:
- Total password count
- File size
- Sample passwords from wordlist

### Option 6: View Results

Shows:
- Previous cracking sessions
- Success/failure statistics
- Found passwords

## 📈 Performance Tips

### For Faster Cracking:

1. **Use SSD** - Faster disk I/O
2. **Close other programs** - More CPU/RAM available
3. **Use parallel processing** - Utilize multiple CPU cores
4. **Filter wordlist** - Remove unlikely passwords

### Expected Performance:

| File Type | Speed (pwd/s) | 1M passwords | 2.8M passwords |
|-----------|---------------|--------------|----------------|
| ZIP | 200-400 | 42 mins | 2 hours |
| PDF | 80-120 | 2.3 hours | 6.5 hours |
| Office | 40-80 | 4.6 hours | 13 hours |

**Note:** Speed varies based on CPU, file size, and encryption method.

## 🎓 Advanced Usage

### Custom Wordlist

Create your own wordlist:
```bash
# Create custom wordlist
echo Password123456 > custom.txt
echo Summer2024!! >> custom.txt
echo Welcome@2024 >> custom.txt

# Use it
python cracker.py file.pdf -w custom.txt -t dictionary
```

### Resume Interrupted Attack

If an attack is interrupted, you can resume from a specific line:

```python
from cracker import PasswordCracker

cracker = PasswordCracker('file.pdf')
password = cracker.dictionary_attack('wordlist.txt', start_line=10000)
```

### Custom Mutations

```python
from cracker import PasswordCracker

cracker = PasswordCracker('file.pdf')
mutations = ['!', '@', '#', '123', '2024', '2025', '!!!']
password = cracker.hybrid_attack('wordlist.txt', mutations=mutations)
```

## 🔐 Security Notice

**This tool is for AUTHORIZED use only!**

✅ **Legal uses:**
- Recovering your own forgotten passwords
- Testing files you created
- Authorized penetration testing
- Educational research

❌ **Illegal uses:**
- Cracking files you don't own
- Unauthorized access
- Violating terms of service
- Any illegal activity

**You are responsible for all usage of this tool!**

---

**Need help? Check the full README.md for more details!**
