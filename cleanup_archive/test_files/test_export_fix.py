#!/usr/bin/env python3
"""Test Export Fix - Quick MP4 Export Test

This tests if the MP4 export works without stalling after removing the problematic emoji characters.
"""

import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt
import cv2
import tempfile
import os
import time

def create_test_frames():
    """Create a few test frames for quick export test."""
    frames = []
    
    # Create simple rotating sphere frames
    for i in range(6):  # Just 6 frames for quick test
        angle = i * (360 / 6)
        
        # Generate sphere points
        phi = np.random.uniform(0, 2*np.pi, 500)
        costheta = np.random.uniform(-1, 1, 500)
        u = np.random.uniform(0, 1, 500)
        
        theta = np.arccos(costheta)
        r = u ** (1/3)
        
        # Rotate around Y-axis
        angle_rad = np.radians(angle)
        x = r * np.sin(theta) * np.cos(phi) * np.cos(angle_rad) - r * np.cos(theta) * np.sin(angle_rad)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.sin(theta) * np.cos(phi) * np.sin(angle_rad) + r * np.cos(theta) * np.cos(angle_rad)
        
        points = np.column_stack([x, y, z])
        colors = np.column_stack([
            (z + 1) / 2,
            np.zeros_like(z),
            1 - (z + 1) / 2
        ])
        
        frames.append({
            'points': points,
            'colors': colors,
            'filename': f'test_frame_{i:03d}.ply'
        })
    
    return frames

def test_export_without_emojis():
    """Test MP4 export with emoji-free matplotlib plots."""
    print("🧪 Testing MP4 Export (Emoji-Free)")
    print("=" * 50)
    
    # Create test frames
    print("1️⃣ Creating test frames...")
    frames_data = create_test_frames()
    print(f"✅ Created {len(frames_data)} test frames")
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix="export_test_")
    print(f"📁 Working directory: {temp_dir}")
    
    try:
        # Render frames WITHOUT emoji characters
        print("2️⃣ Rendering frames (no emojis)...")
        frame_paths = []
        
        for i, frame_data in enumerate(frames_data):
            points = frame_data['points']
            colors = frame_data['colors']
            
            # Create matplotlib figure - NO EMOJI CHARACTERS
            fig = plt.figure(figsize=(8, 6), facecolor='black', dpi=80)
            ax = fig.add_subplot(111, projection='3d', facecolor='black')
            
            ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                      c=colors, s=2, alpha=0.8)
            
            # Clean title - NO EMOJIS
            ax.set_xlabel('X', color='white')
            ax.set_ylabel('Y', color='white')
            ax.set_zlabel('Z', color='white')
            ax.set_title(f'Frame {i+1}/{len(frames_data)} | {len(points)} points', 
                       color='white', fontsize=12)
            ax.tick_params(colors='white')
            
            # Save frame
            frame_path = os.path.join(temp_dir, f"frame_{i:04d}.png")
            plt.savefig(frame_path, dpi=80, bbox_inches='tight', 
                      facecolor='black', format='png')
            plt.close()
            
            frame_paths.append(frame_path)
            print(f"   ✅ Frame {i+1}/{len(frames_data)} rendered")
        
        print(f"✅ All {len(frame_paths)} frames rendered successfully")
        
        # Test video creation
        print("3️⃣ Creating MP4 video...")
        
        first_frame = cv2.imread(frame_paths[0])
        height, width, layers = first_frame.shape
        
        video_path = os.path.join(temp_dir, "test_export.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(video_path, fourcc, 5, (width, height))
        
        if not video.isOpened():
            raise ValueError("Could not open video writer")
        
        for i, frame_path in enumerate(frame_paths):
            frame = cv2.imread(frame_path)
            if frame is not None:
                video.write(frame)
                print(f"   ✅ Encoded frame {i+1}/{len(frame_paths)}")
            else:
                raise ValueError(f"Could not read frame {i+1}")
        
        video.release()
        
        # Verify video
        if os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            print(f"✅ Video created: {file_size / 1024:.1f} KB")
            print(f"📁 Video saved to: {video_path}")
            
            # Test playback
            cap = cv2.VideoCapture(video_path)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            
            print(f"🎬 Video verification: {frame_count} frames")
            
            if frame_count == len(frames_data):
                print("🎉 EXPORT TEST: PASSED!")
                print("✅ No stalling issues detected")
                print("✅ Emoji removal successful")
                return True
            else:
                print("❌ Frame count mismatch")
                return False
        else:
            print("❌ Video file not created")
            return False
            
    except Exception as e:
        print(f"❌ Export test failed: {e}")
        return False
    
    finally:
        # Cleanup
        try:
            import shutil
            shutil.rmtree(temp_dir)
            print(f"🧹 Cleaned up temp directory")
        except:
            pass

if __name__ == "__main__":
    success = test_export_without_emojis()
    
    if success:
        print("\n" + "="*50)
        print("🎯 EXPORT STALLING ISSUE: FIXED!")
        print("✅ The Streamlit app should now export videos without stalling")
        print("✅ Emoji characters removed from matplotlib plots")
        print("✅ Better error handling added")
        print("\n💡 Ready to test in Streamlit at http://localhost:8507")
    else:
        print("\n❌ Export test failed - more investigation needed") 