#!/usr/bin/env python3
"""Test Facial Landmark CSV Import

Test script to verify the new facial landmark import functionality.
"""

import sys
import pandas as pd
from pathlib import Path
from io import StringIO
import numpy as np

# Add source to path
sys.path.insert(0, str(Path(__file__).parent / "source"))

from file_manager import FileManager


def test_facial_csv_detection():
    """Test facial landmark CSV detection."""
    print("🧪 Testing Facial Landmark CSV Detection")
    print("=" * 50)
    
    # Test with the provided CSV file
    csv_path = "e4_processed/1_Facial_Processed/e4-baseline.csv"
    
    if Path(csv_path).exists():
        try:
            # Read the CSV
            df = pd.read_csv(csv_path)
            print(f"📁 Loading: {csv_path}")
            print(f"📊 Shape: {df.shape}")
            print(f"📋 Columns: {len(df.columns)}")
            
            # Test detection
            is_facial = FileManager._is_facial_landmark_csv(df)
            print(f"🎭 Is facial landmark CSV: {is_facial}")
            
            if is_facial:
                print("✅ CSV format detected correctly!")
                
                # Show some details
                feat_x_cols = [col for col in df.columns if col.startswith('feat_') and col.endswith('_x')]
                feat_y_cols = [col for col in df.columns if col.startswith('feat_') and col.endswith('_y')]
                feat_z_cols = [col for col in df.columns if col.startswith('feat_') and col.endswith('_z')]
                xdiff_cols = [col for col in df.columns if col.startswith('feat_') and col.endswith('_xdiff')]
                
                print(f"📍 X coordinates: {len(feat_x_cols)}")
                print(f"📍 Y coordinates: {len(feat_y_cols)}")
                print(f"📍 Z coordinates: {len(feat_z_cols)}")
                print(f"📐 Movement data: {len(xdiff_cols)} xdiff columns")
                
                # Test parsing
                print("\n🎨 Testing parsing with movement colors...")
                frames_data = FileManager._parse_facial_landmark_csv(df, color_mode='movement')
                
                if frames_data:
                    first_frame = frames_data[0]
                    print(f"✅ First frame parsed:")
                    print(f"   Points: {len(first_frame['points'])}")
                    print(f"   Colors: {first_frame['colors'].shape}")
                    print(f"   Timestamp: {first_frame['timestamp']}")
                    print(f"   Movement data: {len(first_frame['movement_data'])}")
                    
                    # Show movement intensity range for first frame
                    movement_data = first_frame['movement_data']
                    intensities = []
                    for move in movement_data:
                        xdiff = move.get('xdiff', 0)
                        ydiff = move.get('ydiff', 0)
                        zdiff = move.get('zdiff', 0)
                        intensity = (xdiff**2 + ydiff**2 + zdiff**2)**0.5
                        intensities.append(intensity)
                    
                    intensities = np.array(intensities)
                    print(f"📊 Movement intensities: {np.min(intensities):.4f} to {np.max(intensities):.4f}")
                    
                    print(f"\n✅ Parsed {len(frames_data)} total frames successfully!")
                    
            else:
                print("❌ CSV format not detected")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ File not found: {csv_path}")


def test_z_scaling():
    """Test Z-axis scaling functionality."""
    print("\n📏 Testing Z-Axis Scaling")
    print("=" * 50)
    
    csv_path = "e4_processed/1_Facial_Processed/e4-baseline.csv"
    
    if Path(csv_path).exists():
        try:
            df = pd.read_csv(csv_path)
            
            # Test much higher Z scales for facial data
            z_scales = [1.0, 25.0, 50.0, 100.0]
            
            for z_scale in z_scales:
                print(f"\n🎯 Testing Z-scale: {z_scale}x")
                if z_scale == 25.0:
                    print("   ⭐ OPTIMAL VALUE (user-tested)")
                frames_data = FileManager._parse_facial_landmark_csv(df, color_mode='movement', z_scale=z_scale)
                
                if frames_data:
                    first_frame = frames_data[0]
                    points = first_frame['points']
                    
                    # Analyze Z coordinate distribution
                    z_values = points[:, 2]  # Z coordinates
                    z_min, z_max = np.min(z_values), np.max(z_values)
                    z_range = z_max - z_min
                    
                    print(f"   📊 Z range: {z_min:.4f} to {z_max:.4f} (range: {z_range:.4f})")
                    
                    # Show proportion to X,Y coordinates
                    x_range = np.max(points[:, 0]) - np.min(points[:, 0])
                    y_range = np.max(points[:, 1]) - np.min(points[:, 1])
                    print(f"   📐 X range: {x_range:.4f}, Y range: {y_range:.4f}")
                    print(f"   📊 Z/X ratio: {z_range/x_range:.3f}, Z/Y ratio: {z_range/y_range:.3f}")
                    
                    # Assessment
                    z_x_ratio = z_range/x_range
                    if z_x_ratio < 0.1:
                        print(f"   ⚠️ Still quite flat - consider higher scaling")
                    elif z_x_ratio < 0.3:
                        print(f"   ✅ Good proportions for analysis")
                    else:
                        print(f"   🚀 Excellent 3D depth!")
                    
            print("\n✅ Z-scaling tests completed!")
            
        except Exception as e:
            print(f"❌ Error testing Z-scaling: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ File not found: {csv_path}")


def test_animation_creation():
    """Test creating an animation folder."""
    print("\n🎬 Testing Animation Creation")
    print("=" * 50)
    
    csv_path = "e4_processed/1_Facial_Processed/e4-baseline.csv"
    
    if Path(csv_path).exists():
        try:
            # Create a mock uploaded file
            class MockUploadedFile:
                def __init__(self, file_path):
                    self.name = Path(file_path).name
                    with open(file_path, 'rb') as f:
                        self._content = f.read()
                
                def getvalue(self):
                    return self._content
            
            mock_file = MockUploadedFile(csv_path)
            
            # Test creating animation folder with Z-scaling
            z_scale = 25.0
            print(f"🎭 Creating facial animation with Z-scale {z_scale}x (optimal value - limited to 10 frames for testing)...")
            
            folder_path, saved_frames, metadata = FileManager.create_facial_animation_folder(
                mock_file,
                folder_name="test_facial_animation_optimal_scale",
                color_mode='movement',
                max_frames=10,
                z_scale=z_scale
            )
            
            print(f"✅ Animation created!")
            print(f"📁 Folder: {folder_path}")
            print(f"📊 Frames saved: {saved_frames}")
            print(f"🎯 Z-scale applied: {metadata['z_scale']}x")
            print(f"🎭 Metadata: {metadata}")
            
            # Verify files exist
            folder = Path(folder_path)
            ply_files = list(folder.glob("*.ply"))
            print(f"📄 PLY files created: {len(ply_files)}")
            
            metadata_file = folder / "metadata.json"
            if metadata_file.exists():
                print("✅ Metadata file created")
            
        except Exception as e:
            print(f"❌ Error creating animation: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ File not found: {csv_path}")


def main():
    """Main test function."""
    print("🧪 Facial Landmark CSV Import Tests")
    print("=" * 60)
    
    test_facial_csv_detection()
    test_z_scaling()
    test_animation_creation()
    
    print("\n" + "=" * 60)
    print("🎉 Tests completed!")


if __name__ == "__main__":
    main() 