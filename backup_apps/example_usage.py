#!/usr/bin/env python3
"""
Example usage of the point cloud module without Streamlit.

This demonstrates how to use the separated point cloud logic
for other applications or testing.
"""

from point_cloud import PointCloudZoetrope, ZoetropeAnimator, create_point_cloud, create_animation
import matplotlib.pyplot as plt


def basic_example():
    """Basic point cloud creation and visualization."""
    print("Example 1: Basic point cloud creation")
    
    # Create and visualize a point cloud
    cloud = PointCloudZoetrope(num_points=200, radius=3)
    fig = cloud.create_frame(45)  # 45 degree rotation
    plt.show()
    
    # Save a frame
    cloud.save_frame(90, "example_frame.png")
    print("Saved frame to example_frame.png")


def animation_example():
    """Generate frames and create video."""
    print("\nExample 2: Generate animation")
    
    # Create point cloud and animator
    cloud = create_point_cloud(num_points=150, radius=4)
    animator = ZoetropeAnimator(cloud)
    
    # Progress callback
    def progress_callback(progress, current, total, angle):
        if current % 6 == 0:  # Print every 6th frame
            print(f"Progress: {progress:.1%} - Frame {current}/{total}")
    
    # Generate frames and video
    frame_paths = animator.generate_frames(
        num_frames=12, 
        data_dir="example_data",
        progress_callback=progress_callback
    )
    
    video_path = animator.create_video(frame_paths, "example_data/example_video.mp4", fps=2)
    
    print(f"Generated {len(frame_paths)} frames")
    if video_path:
        print(f"Created video: {video_path}")


def complete_workflow_example():
    """Complete workflow using convenience function."""
    print("\nExample 3: Complete workflow")
    
    def progress_callback(progress, current, total, angle):
        if current % 8 == 0:  # Print every 8th frame
            print(f"Generating frame {current}/{total}...")
    
    # Generate complete animation
    frame_paths, video_path = create_animation(
        num_points=100,
        radius=5,
        num_frames=24,
        data_dir="complete_example",
        fps=3,
        progress_callback=progress_callback
    )
    
    print(f"Complete! Generated {len(frame_paths)} frames and video: {video_path}")


def custom_angles_example():
    """Custom rotation angles."""
    print("\nExample 4: Custom rotation angles")
    
    cloud = PointCloudZoetrope(num_points=100, radius=2)
    custom_angles = [0, 30, 60, 90, 120, 150, 180]
    
    for i, angle in enumerate(custom_angles):
        filename = f"custom_frame_{i:02d}_{angle}deg.png"
        cloud.save_frame(angle, filename)
        print(f"Saved {filename}")


if __name__ == "__main__":
    print("🎬 Point Cloud Module Examples")
    print("=" * 40)
    
    try:
        basic_example()
        animation_example()
        complete_workflow_example()
        custom_angles_example()
        
        print("\n✅ All examples completed successfully!")
        print("\nFiles created:")
        print("- example_frame.png")
        print("- example_data/ (folder with frames and video)")
        print("- complete_example/ (folder with frames and video)")
        print("- custom_frame_*.png (custom angle frames)")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        print("Make sure all dependencies are installed (see requirements.txt)") 