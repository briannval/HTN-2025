#!/usr/bin/env python3
"""
Setup script for the HTN (Hear, Take, Narrate) project.
This script helps set up the environment and install dependencies.
"""

import os
import subprocess
import sys
import logging

logger = logging.getLogger(__name__)


def install_requirements():
    logger.info("Installing required packages...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )
        logger.info("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error installing packages: {e}")
        return False


def check_cohere_api_key():
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key:
        logger.warning("⚠️  COHERE_API_KEY environment variable not set.")
        logger.info("To enable image analysis, you need to:")
        logger.info("1. Get a Cohere API key from https://cohere.com/")
        logger.info("2. Set the environment variable:")
        logger.info("   export COHERE_API_KEY='your_api_key_here'")
        logger.info("   (Add this to your ~/.zshrc or ~/.bashrc for persistence)")
        return False
    else:
        logger.info("✅ Cohere API key found!")
        return True


def main():
    logger.info("🎯 HTN (Hear, Take, Narrate) Setup")
    logger.info("=" * 40)

    if not install_requirements():
        logger.error("Setup failed. Please check the error messages above.")
        return

    cohere_available = check_cohere_api_key()

    logger.info("\n🚀 Setup complete!")
    logger.info("\nTo run the application:")
    logger.info("python main.py")

    if not cohere_available:
        logger.warning("\nNote: Image analysis will not be available without a Cohere API key.")
    else:
        logger.info("\n✅ Image analysis is ready!")


if __name__ == "__main__":
    main()
