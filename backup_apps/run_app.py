#!/usr/bin/env python3
"""Simple launcher for the Zoetrope Point Cloud Viewer"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit application"""
    app_path = "source/zoetrope_app.py"
    
    if not os.path.exists(app_path):
        print(f"❌ Error: Could not find {app_path}")
        print("Make sure you're running this from the project root directory.")
        return
    
    print("🎬 Starting Zoetrope Point Cloud Viewer...")
    
    try:
        subprocess.run(["streamlit", "run", app_path], check=True)
    except FileNotFoundError:
        print("❌ Error: Streamlit not found. Install it with: pip install streamlit")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")

if __name__ == "__main__":
    main() 