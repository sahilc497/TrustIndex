"""
Reproduction Entry Point: TRUST Index Verification Layer Validation.

Usage:
    python run_trust_validation.py
"""

import os
import sys

# Ensure root directory is on Python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from src.validate_detector import main

if __name__ == "__main__":
    main()
