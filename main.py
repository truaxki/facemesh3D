#!/usr/bin/env python3
"""main.py

Main launcher for the Open3D Point Cloud Visualization System
============================================================

This launches the web-based control panel that lets you:
1. Configure point cloud settings
2. Generate or upload point cloud data  
3. Launch the interactive Open3D desktop viewer

The version you liked from http://localhost:8501/

Usage: python main.py
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Launch the Open3D Streamlit control panel."""
    print("🚀 Starting Open3D Point Cloud Visualization System...")
    print("   Web interface: Configure settings, upload files")
    print("   Desktop viewer: Full Open3D interactivity")
    print()
    
    # Path to the main app
    app_path = Path(__file__).parent / "source" / "streamlit_open3d_launcher.py"
    
    if not app_path.exists():
        print(f"❌ Error: Could not find {app_path}")
        print("   Make sure you're running from the project root directory.")
        sys.exit(1)
    
    try:
        # Launch Streamlit
        print(f"📂 Launching: {app_path}")
        print("🌐 Opening web interface...")
        print()
        print("   The app will open in your browser automatically.")
        print("   If not, go to: http://localhost:8501")
        print()
        print("   Press Ctrl+C to stop the server.")
        print()
        
        subprocess.run([
            "streamlit", "run", str(app_path),
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down Open3D launcher. Goodbye!")
    except Exception as e:
        print(f"❌ Error launching app: {e}")
        print("   Try running manually: streamlit run source/streamlit_open3d_launcher.py")
        sys.exit(1)

if __name__ == "__main__":
    main() 