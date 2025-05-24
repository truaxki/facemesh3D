#!/usr/bin/env python3
"""test_troubleshooting.py

Comprehensive troubleshooting script for Open3D and MP4 export issues.
This will help diagnose and fix common problems.

Run: python test_troubleshooting.py
"""

import os
import sys
import subprocess
import tempfile
import time

def test_imports():
    """Test if all required packages are available."""
    print("🔍 Testing Python Package Imports")
    print("=" * 50)
    
    packages = [
        ('numpy', 'np'),
        ('open3d', 'o3d'),
        ('cv2', 'cv2'),
        ('matplotlib.pyplot', 'plt'),
        ('streamlit', 'st')
    ]
    
    all_good = True
    
    for package, alias in packages:
        try:
            if package == 'numpy':
                import numpy as np
                print(f"✅ numpy {np.__version__}")
            elif package == 'open3d':
                import open3d as o3d
                print(f"✅ open3d {o3d.__version__}")
            elif package == 'cv2':
                import cv2
                print(f"✅ opencv {cv2.__version__}")
            elif package == 'matplotlib.pyplot':
                import matplotlib.pyplot as plt
                import matplotlib
                print(f"✅ matplotlib {matplotlib.__version__}")
            elif package == 'streamlit':
                import streamlit as st
                print(f"✅ streamlit {st.__version__}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            all_good = False
        except Exception as e:
            print(f"⚠️ {package}: {e}")
            all_good = False
    
    return all_good

def test_open3d_basic():
    """Test basic Open3D functionality."""
    print("\n🔺 Testing Open3D Basic Functionality")
    print("=" * 50)
    
    try:
        import open3d as o3d
        import numpy as np
        
        # Create simple point cloud
        points = np.random.rand(100, 3)
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        
        # Test file I/O
        temp_file = tempfile.mktemp(suffix=".ply")
        success = o3d.io.write_point_cloud(temp_file, pcd)
        
        if success:
            # Try to read it back
            pcd2 = o3d.io.read_point_cloud(temp_file)
            if len(pcd2.points) == 100:
                print("✅ Open3D file I/O working")
                os.unlink(temp_file)
                return True
            else:
                print("❌ Open3D read/write mismatch")
                return False
        else:
            print("❌ Open3D write failed")
            return False
            
    except Exception as e:
        print(f"❌ Open3D test failed: {e}")
        return False

def test_open3d_viewer():
    """Test Open3D viewer launch."""
    print("\n🎮 Testing Open3D Viewer")
    print("=" * 50)
    
    try:
        # Create test point cloud file
        import open3d as o3d
        import numpy as np
        
        points = np.random.rand(500, 3)
        colors = np.random.rand(500, 3)
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        pcd.colors = o3d.utility.Vector3dVector(colors)
        
        test_file = "test_viewer.ply"
        o3d.io.write_point_cloud(test_file, pcd)
        
        print(f"📁 Created test file: {test_file}")
        print("🚀 Launching Open3D viewer for 5 seconds...")
        
        # Launch viewer
        cmd = [sys.executable, "source/open3d_desktop_viewer.py", "--file", test_file]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a few seconds
        time.sleep(3)
        
        # Check if still running
        if process.poll() is None:
            print("✅ Open3D viewer launched successfully!")
            process.terminate()
            process.wait()
            
            # Clean up
            if os.path.exists(test_file):
                os.unlink(test_file)
            
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Viewer failed to launch")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Viewer test failed: {e}")
        return False

def test_opencv_codecs():
    """Test OpenCV video codec support."""
    print("\n🎥 Testing OpenCV Video Codecs")
    print("=" * 50)
    
    try:
        import cv2
        import numpy as np
        
        # Create test frames
        width, height = 640, 480
        test_frames = []
        
        for i in range(5):
            frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
            test_frames.append(frame)
        
        codecs_to_test = [
            ('mp4v', '.mp4'),
            ('XVID', '.avi'),
            ('MJPG', '.avi'),
            ('H264', '.mp4')
        ]
        
        working_codecs = []
        
        for codec, ext in codecs_to_test:
            try:
                temp_video = tempfile.mktemp(suffix=ext)
                fourcc = cv2.VideoWriter_fourcc(*codec)
                
                video_writer = cv2.VideoWriter(temp_video, fourcc, 10, (width, height))
                
                if video_writer.isOpened():
                    for frame in test_frames:
                        video_writer.write(frame)
                    video_writer.release()
                    
                    # Check if file was created and has content
                    if os.path.exists(temp_video) and os.path.getsize(temp_video) > 1000:
                        print(f"✅ {codec} codec working")
                        working_codecs.append((codec, ext))
                        os.unlink(temp_video)
                    else:
                        print(f"❌ {codec} codec created empty file")
                else:
                    print(f"❌ {codec} codec failed to open")
                    
            except Exception as e:
                print(f"❌ {codec} codec error: {e}")
        
        if working_codecs:
            print(f"\n✅ Working codecs: {[c[0] for c in working_codecs]}")
            return True
        else:
            print("\n❌ No working video codecs found!")
            return False
            
    except Exception as e:
        print(f"❌ Codec test failed: {e}")
        return False

def test_animation_files():
    """Test animation file loading."""
    print("\n🎬 Testing Animation Files")
    print("=" * 50)
    
    animations_dir = "animations"
    if not os.path.exists(animations_dir):
        print(f"❌ Animations folder not found: {animations_dir}")
        return False
    
    subfolders = [f for f in os.listdir(animations_dir) 
                  if os.path.isdir(os.path.join(animations_dir, f))]
    
    if not subfolders:
        print("❌ No animation subfolders found")
        return False
    
    print(f"📁 Found {len(subfolders)} animation folders:")
    
    all_good = True
    for folder in subfolders:
        folder_path = os.path.join(animations_dir, folder)
        ply_files = [f for f in os.listdir(folder_path) if f.endswith('.ply')]
        
        if ply_files:
            print(f"✅ {folder}: {len(ply_files)} PLY files")
        else:
            print(f"❌ {folder}: No PLY files found")
            all_good = False
    
    return all_good

def run_streamlit_test():
    """Test Streamlit interface."""
    print("\n🌐 Testing Streamlit Interface")
    print("=" * 50)
    
    try:
        # Check if Streamlit is already running
        import requests
        try:
            response = requests.get("http://localhost:8501", timeout=2)
            print("✅ Streamlit already running on port 8501")
            return True
        except:
            pass
        
        print("🚀 Starting Streamlit interface...")
        cmd = [sys.executable, "-m", "streamlit", "run", "source/streamlit_open3d_launcher.py", "--server.headless", "true"]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for startup
        time.sleep(5)
        
        try:
            response = requests.get("http://localhost:8501", timeout=5)
            if response.status_code == 200:
                print("✅ Streamlit interface accessible")
                process.terminate()
                return True
            else:
                print(f"❌ Streamlit returned status {response.status_code}")
                process.terminate()
                return False
        except Exception as e:
            print(f"❌ Could not connect to Streamlit: {e}")
            process.terminate()
            return False
            
    except Exception as e:
        print(f"❌ Streamlit test failed: {e}")
        return False

def print_solutions():
    """Print common solutions."""
    print("\n🔧 Common Solutions")
    print("=" * 50)
    
    print("""
**Open3D Window Not Appearing:**
1. Check your taskbar - Windows often opens it in background
2. Try: Alt+Tab to cycle through windows
3. The script will try to bring window to front automatically
4. Restart your terminal/IDE if needed

**MP4 Export Issues:**
1. Install additional codecs: `pip install opencv-python-headless`
2. Try different video formats (AVI fallback available)
3. Reduce frame count for testing
4. Use individual frame download as backup

**Animation Playback Problems:**
1. Ensure animation folder contains PLY files
2. Check file naming: frame_000_*.ply, frame_001_*.ply, etc.
3. Try creating test animation: `python rotate_pointcloud.py --sample torus test.ply test_anim/ --frames 12`
4. Use desktop viewer for smoother playback

**General Troubleshooting:**
1. Restart Python/Anaconda environment
2. Update packages: `pip install --upgrade open3d streamlit opencv-python`
3. Check Windows permissions
4. Try running as Administrator if needed
""")

def main():
    """Run comprehensive diagnostics."""
    print("🔧 Open3D & Animation Troubleshooting")
    print("=" * 60)
    print("This will test all components and identify issues.\n")
    
    tests = [
        ("Package Imports", test_imports),
        ("Open3D Basic", test_open3d_basic),
        ("OpenCV Codecs", test_opencv_codecs),
        ("Animation Files", test_animation_files),
        ("Open3D Viewer", test_open3d_viewer),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your system should work perfectly.")
        print("\n🚀 Quick Start:")
        print("1. Run: python main.py")
        print("2. Select '🎬 Animation Folder'")
        print("3. Choose an animation from the dropdown")
        print("4. Click 'Load Animation Frames'")
        print("5. Use frame slider or export video!")
    else:
        print(f"\n⚠️ {total - passed} tests failed. See solutions below:")
        print_solutions()

if __name__ == "__main__":
    main() 