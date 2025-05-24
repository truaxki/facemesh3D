#!/usr/bin/env python3
"""
Simple launcher script for the Zoetrope Point Cloud Viewer
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit application"""
    app_path = os.path.join("source", "zoetrope_app.py")
    
    if not os.path.exists(app_path):
        print(f"Error: Could not find {app_path}")
        print("Make sure you're running this from the project root directory.")
        sys.exit(1)
    
    print("🎬 Starting Zoetrope Point Cloud Viewer...")
    print(f"Running: streamlit run {app_path}")
    
    try:
        subprocess.run(["streamlit", "run", app_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: Streamlit not found. Please install it with:")
        print("pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main() 