"""
Quick Start Script for PassGAN Password Cracker
Simplified interface for running the complete pipeline
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import main

if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              PassGAN Password Cracker v1.0                   ║
║     GAN-based Password Generation & File Cracking            ║
║                                                              ║
║  Features:                                                   ║
║    • Deep Learning Password Generation (12+ chars)           ║
║    • PDF, DOCX, PPTX, ZIP Support                           ║
║    • Parallel Processing                                     ║
║    • Diverse Password Patterns                               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Run main function
    main()
