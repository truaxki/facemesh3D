#!/usr/bin/env python3
"""Test Interactive Animation Player

Simple test script to verify the new interactive animation player works correctly.
"""

import numpy as np
import sys
from pathlib import Path

# Add source to path
sys.path.insert(0, str(Path(__file__).parent / "source"))

from animation_player import play_animation_interactive


def create_test_animation(num_frames=24, num_points=1000):
    """Create a simple test animation - a rotating sphere."""
    print(f"🎲 Creating test animation: {num_frames} frames, {num_points} points each")
    
    frames_data = []
    
    for frame in range(num_frames):
        # Create sphere points
        phi = np.random.uniform(0, 2*np.pi, num_points)
        costheta = np.random.uniform(-1, 1, num_points)
        u = np.random.uniform(0, 1, num_points)
        
        theta = np.arccos(costheta)
        r = u ** (1/3)
        
        # Add rotation over time
        rotation_angle = 2 * np.pi * frame / num_frames
        
        x = r * np.sin(theta) * np.cos(phi + rotation_angle)
        y = r * np.sin(theta) * np.sin(phi + rotation_angle)
        z = r * np.cos(theta)
        
        points = np.column_stack([x, y, z])
        
        # Color based on frame (creates a color transition)
        hue = frame / num_frames
        colors = np.column_stack([
            np.ones(num_points) * hue,
            (phi / (2*np.pi)),
            np.ones(num_points) * 0.8
        ])
        
        frames_data.append({
            'points': points,
            'colors': colors
        })
    
    print(f"✅ Created {len(frames_data)} frames")
    return frames_data


def main():
    """Main test function."""
    print("🧪 Testing Interactive Animation Player")
    print("=" * 50)
    
    try:
        # Create test animation
        frames_data = create_test_animation(num_frames=36, num_points=2000)
        
        # Test the interactive player
        print("🎬 Launching interactive animation player...")
        print("💡 All controls work directly in the 3D window:")
        print("   SPACEBAR - Play/pause")
        print("   N/P - Next/previous frame")
        print("   R - Reverse direction")
        print("   =/- - Speed up/down")
        print("   B - Change background")
        print("   S - Screenshot")
        print("   H - Help")
        print("   Q - Quit")
        print("🎮 Focus the 3D window and press SPACEBAR to start!")
        print()
        
        success = play_animation_interactive(frames_data, fps=12)
        
        if success:
            print("✅ Interactive animation player test completed successfully!")
        else:
            print("❌ Interactive animation player test failed")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 