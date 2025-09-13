#!/usr/bin/env python3
"""
Setup script for the HTN (Hear, Take, Narrate) project.
This script helps set up the environment and install dependencies.
"""

import os
import subprocess
import sys


def install_requirements():
    print("Installing required packages...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False


def check_cohere_api_key():
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key:
        print("⚠️  COHERE_API_KEY environment variable not set.")
        print("To enable image analysis, you need to:")
        print("1. Get a Cohere API key from https://cohere.com/")
        print("2. Set the environment variable:")
        print("   export COHERE_API_KEY='your_api_key_here'")
        print("   (Add this to your ~/.zshrc or ~/.bashrc for persistence)")
        return False
    else:
        print("✅ Cohere API key found!")
        return True


def main():
    print("🎯 HTN (Hear, Take, Narrate) Setup")
    print("=" * 40)

    if not install_requirements():
        print("Setup failed. Please check the error messages above.")
        return

    cohere_available = check_cohere_api_key()

    print("\n🚀 Setup complete!")
    print("\nTo run the application:")
    print("python main.py")

    if not cohere_available:
        print("\nNote: Image analysis will not be available without a Cohere API key.")
    else:
        print("\n✅ Image analysis is ready!")


if __name__ == "__main__":
    main()
