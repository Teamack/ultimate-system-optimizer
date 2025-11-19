#!/usr/bin/env python3
"""
Ultimate System Optimizer - Main Entry Point

AI-Powered Predictive System Management

Features:
- Feature #15: One-Click Boost
- Feature #25: Transparent Optimization
- Feature #14: Context-Aware Resource Allocation
- Feature #6: Predictive Disk Space Manager

Author: Ultimate System Optimizer Team
License: MIT
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_python_version():
    """Verify Python version is 3.6+."""
    if sys.version_info < (3, 6):
        print("Error: Python 3.6 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)


def check_dependencies():
    """Verify required dependencies are installed."""
    missing = []

    try:
        import psutil
    except ImportError:
        missing.append('psutil')

    try:
        import tkinter
    except ImportError:
        missing.append('tkinter')

    if missing:
        print("Missing required dependencies:")
        for dep in missing:
            print(f"  - {dep}")

        print("\nInstalling missing dependencies...")
        import subprocess

        for dep in missing:
            if dep == 'tkinter':
                print("\ntkinter installation:")
                print("  Ubuntu/Debian: sudo apt-get install python3-tk")
                print("  Fedora: sudo dnf install python3-tkinter")
                print("  macOS: Included with Python")
                print("  Windows: Included with Python")
                sys.exit(1)
            else:
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                except subprocess.CalledProcessError:
                    print(f"Failed to install {dep}. Please install manually:")
                    print(f"  pip install {dep}")
                    sys.exit(1)

    return True


def main():
    """Main application entry point."""
    print("=" * 60)
    print("Ultimate System Optimizer")
    print("AI-Powered Predictive System Management")
    print("=" * 60)
    print()

    # Check Python version
    print("Checking Python version...", end=" ")
    check_python_version()
    print(f"OK ({sys.version.split()[0]})")

    # Check dependencies
    print("Checking dependencies...", end=" ")
    check_dependencies()
    print("OK")

    print("\nLoading application...")

    # Import after dependency check
    from gui.main_window import MainApplication
    from config.config_manager import ConfigManager

    # Load configuration
    config = ConfigManager()
    print(f"Configuration loaded from: {config.config_path}")

    print("\nStarting application...")
    print()

    # Create and run application
    try:
        app = MainApplication(config)
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
