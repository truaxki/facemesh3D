#!/usr/bin/env python3
"""
Facial Microexpression Analysis - Main Entry Point

This script launches the Streamlit web interface for facial microexpression analysis.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Launch the Streamlit interface."""
    print("🎭 Starting Facial Microexpression Analysis...")
    print("📊 Launching Streamlit interface...")
    
    # Get the path to the streamlit interface
    source_dir = Path(__file__).parent / "source"
    interface_file = source_dir / "streamlit_interface.py"
    
    if not interface_file.exists():
        print(f"❌ Error: Interface file not found at {interface_file}")
        sys.exit(1)
    
    try:
        # Launch streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(interface_file),
            "--server.port", "8507",
            "--server.address", "localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application closed by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 