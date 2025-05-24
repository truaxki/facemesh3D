#!/usr/bin/env python3
"""
Zoetrope Point Cloud Viewer - Main Application Entry Point

This is the main entry point for the Streamlit application.
The logic has been separated into:
- point_cloud.py: Point cloud generation and manipulation
- streamlit_ui.py: Streamlit user interface components
"""

from streamlit_ui import main

if __name__ == "__main__":
    main() 