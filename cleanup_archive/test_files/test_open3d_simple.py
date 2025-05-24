#!/usr/bin/env python3
"""
Simple Open3D Test Script
Tests Open3D capabilities to identify any issues.
"""

import sys
import traceback

def test_basic_import():
    """Test basic Open3D import."""
    try:
        import open3d as o3d
        print(f"✅ Open3D import successful - Version: {o3d.__version__}")
        return True
    except Exception as e:
        print(f"❌ Open3D import failed: {e}")
        return False

def test_geometry_creation():
    """Test Open3D geometry creation."""
    try:
        import open3d as o3d
        mesh = o3d.geometry.TriangleMesh.create_sphere()
        print(f"✅ Geometry creation working - Created sphere with {len(mesh.vertices)} vertices")
        return True
    except Exception as e:
        print(f"❌ Geometry creation failed: {e}")
        return False

def test_point_cloud_creation():
    """Test point cloud creation."""
    try:
        import open3d as o3d
        import numpy as np
        
        # Create simple point cloud
        points = np.random.rand(100, 3)
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        
        print(f"✅ Point cloud creation working - Created cloud with {len(pcd.points)} points")
        return True
    except Exception as e:
        print(f"❌ Point cloud creation failed: {e}")
        return False

def test_visualization_creation():
    """Test visualization creation (without showing)."""
    try:
        import open3d as o3d
        vis = o3d.visualization.Visualizer()
        print("✅ Visualizer creation successful")
        return True
    except Exception as e:
        print(f"❌ Visualizer creation failed: {e}")
        return False

def test_gui_backend():
    """Test GUI backend availability."""
    try:
        import open3d as o3d
        import numpy as np
        
        # Try to create a window (this might fail on headless systems)
        points = np.random.rand(100, 3)
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        
        vis = o3d.visualization.Visualizer()
        vis.create_window("Test Window", width=640, height=480, visible=False)
        vis.add_geometry(pcd)
        vis.poll_events()
        vis.update_renderer()
        vis.destroy_window()
        
        print("✅ GUI backend working - Window creation/destruction successful")
        return True
    except Exception as e:
        print(f"❌ GUI backend issue: {e}")
        traceback.print_exc()
        return False

def test_desktop_launcher():
    """Test our desktop launcher module."""
    try:
        from source.desktop_launcher import DesktopLauncher
        from source.point_cloud_generator import PointCloudGenerator
        
        # Generate test data
        points, colors = PointCloudGenerator.generate('Sphere', 100)
        print(f"✅ Generated test data: {len(points)} points")
        
        # Test desktop launcher (but don't actually launch)
        print("✅ Desktop launcher module imports successfully")
        return True
    except Exception as e:
        print(f"❌ Desktop launcher test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🔬 Testing Open3D Capabilities")
    print("=" * 50)
    
    tests = [
        ("Basic Import", test_basic_import),
        ("Geometry Creation", test_geometry_creation),
        ("Point Cloud Creation", test_point_cloud_creation),
        ("Visualizer Creation", test_visualization_creation),
        ("GUI Backend", test_gui_backend),
        ("Desktop Launcher", test_desktop_launcher),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:<10} {test_name}")
    
    failed_tests = [name for name, passed in results if not passed]
    if failed_tests:
        print(f"\n❌ {len(failed_tests)} test(s) failed: {', '.join(failed_tests)}")
        print("\nThis indicates where the Open3D issue is located.")
        return 1
    else:
        print("\n✅ All tests passed! Open3D is working correctly.")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 