#!/usr/bin/env python3
"""test_mp4_export.py

Quick test script for MP4 export functionality.
This will test the video creation without needing the full Streamlit interface.

Run: python test_mp4_export.py
"""

import numpy as np
import open3d as o3d
import cv2
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import tempfile
import os
import time

def create_test_animation():
    """Create a simple test animation with 6 frames."""
    print("🎬 Creating test animation (6 frames)...")
    
    frames_data = []
    
    # Create a simple rotating cube animation
    for i in range(6):
        angle = i * np.pi / 3  # 60 degrees per frame
        
        # Create cube points
        cube_points = np.array([
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],  # bottom
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]       # top
        ])
        
        # Add more points by subdividing
        additional_points = []
        for _ in range(100):
            x = np.random.uniform(-1, 1)
            y = np.random.uniform(-1, 1) 
            z = np.random.uniform(-1, 1)
            additional_points.append([x, y, z])
        
        all_points = np.vstack([cube_points, additional_points])
        
        # Rotate around Z axis
        rotation_matrix = np.array([
            [np.cos(angle), -np.sin(angle), 0],
            [np.sin(angle), np.cos(angle), 0],
            [0, 0, 1]
        ])
        
        rotated_points = all_points @ rotation_matrix.T
        
        # Create colors (rainbow based on height)
        colors = np.zeros_like(rotated_points)
        colors[:, 0] = (rotated_points[:, 2] + 1) / 2  # Red
        colors[:, 1] = (rotated_points[:, 0] + 1) / 2  # Green
        colors[:, 2] = (rotated_points[:, 1] + 1) / 2  # Blue
        colors = np.clip(colors, 0, 1)
        
        frames_data.append({
            'points': rotated_points,
            'colors': colors,
            'filename': f'test_frame_{i:03d}.ply'
        })
    
    print(f"✅ Created {len(frames_data)} test frames")
    return frames_data

def test_video_export(frames_data, fps=5):
    """Test video export functionality."""
    print(f"\n🎥 Testing video export ({len(frames_data)} frames at {fps} FPS)...")
    
    try:
        # Create temp directory
        temp_dir = tempfile.mkdtemp(prefix="test_mp4_")
        print(f"📁 Working directory: {temp_dir}")
        
        # Generate frame images
        frame_paths = []
        print("🖼️ Rendering frames...")
        
        # Calculate bounds once
        all_points = np.vstack([f['points'] for f in frames_data])
        max_range = np.max(np.ptp(all_points, axis=0)) / 2 * 1.1
        mid = np.mean(all_points, axis=0)
        xlim = [mid[0] - max_range, mid[0] + max_range]
        ylim = [mid[1] - max_range, mid[1] + max_range]
        zlim = [mid[2] - max_range, mid[2] + max_range]
        
        for i, frame_data in enumerate(frames_data):
            points = frame_data['points']
            colors = frame_data['colors']
            
            print(f"   Frame {i+1}/{len(frames_data)}")
            
            fig = plt.figure(figsize=(8, 6), facecolor='black', dpi=100)
            ax = fig.add_subplot(111, projection='3d', facecolor='black')
            
            ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                      c=colors, s=20, alpha=0.8, edgecolors='none')
            
            ax.set_xlabel('X', color='white')
            ax.set_ylabel('Y', color='white')
            ax.set_zlabel('Z', color='white')
            ax.tick_params(colors='white')
            ax.set_title(f'Test Frame {i+1}/{len(frames_data)}', color='white')
            
            ax.set_xlim(xlim)
            ax.set_ylim(ylim)
            ax.set_zlim(zlim)
            
            frame_path = os.path.join(temp_dir, f"frame_{i:04d}.png")
            plt.savefig(frame_path, dpi=100, bbox_inches='tight', 
                       facecolor='black', edgecolor='none')
            plt.close()
            
            if not os.path.exists(frame_path):
                raise ValueError(f"Frame {i+1} failed to save")
            
            frame_paths.append(frame_path)
        
        print(f"✅ All {len(frame_paths)} frames rendered")
        
        # Test video creation
        first_frame = cv2.imread(frame_paths[0])
        if first_frame is None:
            raise ValueError("Could not read first frame")
        
        height, width, layers = first_frame.shape
        print(f"🖼️ Video resolution: {width}x{height}")
        
        # Test different codecs
        codecs_to_test = [
            ('mp4v', '.mp4', 'MP4V'),
            ('XVID', '.avi', 'XVID'),
            ('MJPG', '.avi', 'MJPG'),
        ]
        
        successful_videos = []
        
        for codec, ext, name in codecs_to_test:
            print(f"\n🔄 Testing {name} codec...")
            
            try:
                video_path = os.path.join(temp_dir, f"test_video_{codec}{ext}")
                fourcc = cv2.VideoWriter_fourcc(*codec)
                video_writer = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
                
                if not video_writer.isOpened():
                    print(f"❌ {name}: Writer failed to open")
                    continue
                
                # Write frames
                for frame_path in frame_paths:
                    frame = cv2.imread(frame_path)
                    if frame is not None:
                        video_writer.write(frame)
                
                video_writer.release()
                
                # Check result
                if os.path.exists(video_path):
                    file_size = os.path.getsize(video_path)
                    if file_size > 1000:
                        print(f"✅ {name}: Success! ({file_size / 1024:.1f} KB)")
                        successful_videos.append((name, video_path, file_size))
                    else:
                        print(f"❌ {name}: File too small ({file_size} bytes)")
                else:
                    print(f"❌ {name}: No file created")
                    
            except Exception as e:
                print(f"❌ {name}: Error - {e}")
        
        # Summary
        print(f"\n📊 TEST RESULTS:")
        print(f"   Frames rendered: {len(frame_paths)}")
        print(f"   Successful codecs: {len(successful_videos)}")
        
        if successful_videos:
            print("\n✅ WORKING CODECS:")
            for name, path, size in successful_videos:
                print(f"   {name}: {os.path.basename(path)} ({size / 1024:.1f} KB)")
                
            # Test the first successful video
            best_video = successful_videos[0]
            print(f"\n🎬 Testing playback of {best_video[0]} video...")
            print(f"   File: {best_video[1]}")
            print(f"   You can try opening this file manually to verify it works!")
            
            return True
        else:
            print("\n❌ NO WORKING CODECS FOUND!")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the MP4 export test."""
    print("🧪 MP4 Export Test")
    print("=" * 50)
    
    # Test 1: Check OpenCV
    print("1️⃣ Testing OpenCV installation...")
    try:
        import cv2
        print(f"✅ OpenCV {cv2.__version__} installed")
    except ImportError:
        print("❌ OpenCV not available - install with: pip install opencv-python")
        return
    
    # Test 2: Create test data
    print("\n2️⃣ Creating test animation...")
    frames_data = create_test_animation()
    
    # Test 3: Export video
    print("\n3️⃣ Testing video export...")
    success = test_video_export(frames_data, fps=5)
    
    # Final result
    print("\n" + "=" * 50)
    if success:
        print("🎉 MP4 EXPORT TEST: PASSED!")
        print("✅ Your system can create videos successfully")
        print("🚀 The Streamlit interface should work for video export")
    else:
        print("❌ MP4 EXPORT TEST: FAILED!")
        print("⚠️ Video export may not work in Streamlit interface")
        print("🔧 Try installing additional codecs or use frame download instead")
    
    print("\n💡 Next steps:")
    print("   - Run: python main.py")
    print("   - Load an animation")  
    print("   - Try the 'Export Video' button")

if __name__ == "__main__":
    main() 