#!/usr/bin/env python3
"""
Test Desktop Launcher
Tests the fixed desktop launcher functionality.
"""

from source.desktop_launcher import DesktopLauncher
from source.point_cloud_generator import PointCloudGenerator

def test_desktop_launcher():
    """Test the desktop launcher."""
    print("🧪 Testing Desktop Launcher")
    print("=" * 40)
    
    try:
        # Generate test data
        print("📊 Generating test point cloud...")
        points, colors = PointCloudGenerator.generate('Sphere', 500)
        print(f"✅ Generated {len(points)} points")
        
        # Test launcher
        print("\n🚀 Testing desktop viewer launch...")
        config = {
            'shape_type': 'Sphere',
            'num_points': 500,
            'test': True
        }
        
        success, message = DesktopLauncher.launch_single_viewer(points, colors, config)
        
        if success:
            print(f"✅ {message}")
            print("🎮 Desktop viewer should have opened in a new window!")
            print("   Check your taskbar if you don't see it.")
            print("   Close the 3D window when done testing.")
        else:
            print(f"❌ Launch failed: {message}")
            
        return success
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run the test."""
    success = test_desktop_launcher()
    
    if success:
        print("\n🎉 Desktop launcher is working!")
        print("   The Open3D capabilities should now work in the Streamlit app.")
    else:
        print("\n❌ Desktop launcher has issues.")
        print("   This explains why Open3D capabilities weren't working.")

if __name__ == "__main__":
    main() 