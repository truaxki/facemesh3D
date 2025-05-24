#!/usr/bin/env python3
"""main.py

Streamlined launcher for the Open3D Point Cloud Visualization application.
Now uses modular architecture for better maintainability.

Run: python main.py
"""

import subprocess
import sys
import os
from pathlib import Path


def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'streamlit',
        'open3d', 
        'numpy',
        'matplotlib',
        'opencv-python',
        'pandas'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'opencv-python':
                import cv2
            else:
                __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("❌ Missing required packages:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\n💡 Install with: pip install " + " ".join(missing))
        return False
    
    return True


def main():
    """Main launcher function."""
    print("🚀 Open3D Point Cloud Visualization Launcher")
    print("=" * 50)
    
    # Check dependencies
    print("📦 Checking dependencies...")
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first.")
        return 1
    
    print("✅ All dependencies available")
    
    # Check if application files exist
    source_dir = Path(__file__).parent / "source"
    interface_file = source_dir / "streamlit_interface.py"
    
    if not interface_file.exists():
        print(f"❌ Interface file not found: {interface_file}")
        print("   Make sure the source/ directory contains the application files.")
        return 1
    
    # Launch the new modular interface
    print("\n🌐 Starting Streamlit application...")
    print("   URL: http://localhost:8507")
    print("   Press Ctrl+C to stop")
    print("\n" + "=" * 50)
    
    try:
        # Use the new modular interface
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            str(interface_file), 
            "--server.port", "8507",
            "--server.headless", "false"
        ]
        
        # Launch Streamlit
        result = subprocess.run(cmd)
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 