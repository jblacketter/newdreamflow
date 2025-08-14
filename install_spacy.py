#!/usr/bin/env python
"""
Cross-platform spaCy installer for the Dream Journal project.
Handles Windows-specific issues with spaCy installation.
"""

import subprocess
import sys
import platform

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    print("=" * 60)
    print("spaCy Installation for Dream Journal Semantic Analysis")
    print("=" * 60)
    
    is_windows = platform.system() == "Windows"
    
    # Upgrade pip first
    if not run_command(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        "Upgrading pip"
    ):
        print("Warning: pip upgrade failed, continuing anyway...")
    
    # Install setuptools and wheel for Windows
    if is_windows:
        run_command(
            [sys.executable, "-m", "pip", "install", "--upgrade", "setuptools", "wheel"],
            "Installing build tools"
        )
    
    # Install spaCy
    print("\nInstalling spaCy (this may take a few minutes)...")
    spacy_install_cmd = [sys.executable, "-m", "pip", "install", "--no-cache-dir", "spacy==3.7.6"]
    
    if not run_command(spacy_install_cmd, "Installing spaCy"):
        print("\n" + "!" * 60)
        print("spaCy installation failed!")
        print("\nFor Windows users:")
        print("1. Install Microsoft C++ Build Tools:")
        print("   https://visualstudio.microsoft.com/visual-cpp-build-tools/")
        print("2. Restart your command prompt")
        print("3. Run this script again")
        print("!" * 60)
        sys.exit(1)
    
    # Download language model
    if not run_command(
        [sys.executable, "-m", "spacy", "download", "en_core_web_sm"],
        "Downloading English language model"
    ):
        print("Failed to download language model")
        sys.exit(1)
    
    # Verify installation
    print("\nVerifying installation...")
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp("Dreams are windows to the soul.")
        print(f"✓ spaCy version {spacy.__version__} installed successfully!")
        print(f"✓ Language model 'en_core_web_sm' loaded successfully!")
        print(f"✓ Test sentence processed: {len(doc)} tokens found")
        print("\n" + "=" * 60)
        print("SUCCESS: Semantic analysis is now available!")
        print("=" * 60)
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()