import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
import time
from PIL import Image
import io
import cv2
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="Zoetrope Point Cloud Viewer",
    page_icon="🎬",
    layout="wide"
)

class PointCloudZoetrope:
    def __init__(self, num_points=100, radius=5):
        self.num_points = num_points
        self.radius = radius
        self.points = self.generate_random_point_cloud()
        
    def generate_random_point_cloud(self):
        """Generate a random 3D point cloud"""
        # Create random points in a sphere
        phi = np.random.uniform(0, 2*np.pi, self.num_points)
        costheta = np.random.uniform(-1, 1, self.num_points)
        u = np.random.uniform(0, 1, self.num_points)
        
        theta = np.arccos(costheta)
        r = self.radius * (u ** (1/3))
        
        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)
        
        return np.column_stack([x, y, z])
    
    def rotate_y(self, angle_degrees):
        """Rotate points around Y-axis"""
        angle_rad = np.radians(angle_degrees)
        rotation_matrix = np.array([
            [np.cos(angle_rad), 0, np.sin(angle_rad)],
            [0, 1, 0],
            [-np.sin(angle_rad), 0, np.cos(angle_rad)]
        ])
        return np.dot(self.points, rotation_matrix.T)
    
    def create_frame(self, angle_degrees, figsize=(8, 8)):
        """Create a single frame of the rotating point cloud"""
        rotated_points = self.rotate_y(angle_degrees)
        
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot points with color based on z-coordinate for depth perception
        colors = rotated_points[:, 2]  # Use z-coordinate for coloring
        scatter = ax.scatter(rotated_points[:, 0], 
                           rotated_points[:, 1], 
                           rotated_points[:, 2], 
                           c=colors, 
                           cmap='viridis', 
                           s=50, 
                           alpha=0.7)
        
        # Set equal aspect ratio and limits
        max_range = self.radius * 1.2
        ax.set_xlim([-max_range, max_range])
        ax.set_ylim([-max_range, max_range])
        ax.set_zlim([-max_range, max_range])
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(f'Point Cloud - Rotation: {angle_degrees:.1f}°')
        
        # Remove axes for cleaner look
        ax.grid(False)
        ax.set_facecolor('black')
        
        return fig
    
    def save_frame_as_png(self, angle_degrees, filepath):
        """Save a frame as PNG"""
        fig = self.create_frame(angle_degrees)
        fig.savefig(filepath, dpi=100, bbox_inches='tight', 
                   facecolor='black', edgecolor='none')
        plt.close(fig)
        return filepath

def generate_frames(point_cloud, num_frames=36, data_dir="data"):
    """Generate all frames for the zoetrope"""
    os.makedirs(data_dir, exist_ok=True)
    
    frame_paths = []
    angles = np.linspace(0, 360, num_frames, endpoint=False)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, angle in enumerate(angles):
        filename = f"frame_{i:03d}_{angle:.1f}deg.png"
        filepath = os.path.join(data_dir, filename)
        
        point_cloud.save_frame_as_png(angle, filepath)
        frame_paths.append(filepath)
        
        # Update progress
        progress = (i + 1) / num_frames
        progress_bar.progress(progress)
        status_text.text(f"Generating frame {i+1}/{num_frames} - {angle:.1f}°")
    
    progress_bar.empty()
    status_text.empty()
    
    return frame_paths

def create_video_from_frames(frame_paths, output_path="data/zoetrope_video.mp4", fps=1):
    """Create a video from the generated frames"""
    if not frame_paths:
        return None
    
    # Read first frame to get dimensions
    first_frame = cv2.imread(frame_paths[0])
    height, width, layers = first_frame.shape
    
    # Define codec and create VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    for frame_path in frame_paths:
        frame = cv2.imread(frame_path)
        video.write(frame)
    
    video.release()
    return output_path

def display_thumbnails(frame_paths, cols=6):
    """Display thumbnails in a grid"""
    if not frame_paths:
        st.warning("No frames to display")
        return
    
    st.subheader("Generated Frames")
    
    # Create columns for thumbnail grid
    for i in range(0, len(frame_paths), cols):
        columns = st.columns(cols)
        for j, col in enumerate(columns):
            if i + j < len(frame_paths):
                frame_path = frame_paths[i + j]
                with col:
                    image = Image.open(frame_path)
                    st.image(image, caption=f"Frame {i+j+1}", use_column_width=True)

def main():
    st.title("🎬 Zoetrope Point Cloud Viewer")
    st.markdown("Generate rotating 3D point clouds and create zoetrope-like animations!")
    
    # Sidebar controls
    st.sidebar.header("Controls")
    
    # Point cloud parameters
    num_points = st.sidebar.slider("Number of Points", 50, 500, 100)
    radius = st.sidebar.slider("Cloud Radius", 1, 10, 5)
    num_frames = st.sidebar.slider("Number of Frames", 12, 72, 36)
    fps = st.sidebar.slider("Video FPS", 1, 10, 1)
    
    # Generate button
    if st.sidebar.button("Generate New Point Cloud & Frames"):
        with st.spinner("Generating point cloud and frames..."):
            # Create point cloud
            point_cloud = PointCloudZoetrope(num_points=num_points, radius=radius)
            
            # Generate frames
            frame_paths = generate_frames(point_cloud, num_frames=num_frames)
            
            # Store in session state
            st.session_state.frame_paths = frame_paths
            st.session_state.point_cloud = point_cloud
            
            st.success(f"Generated {len(frame_paths)} frames!")
    
    # Display existing frames if available
    if 'frame_paths' in st.session_state:
        frame_paths = st.session_state.frame_paths
        
        # Create tabs
        tab1, tab2, tab3 = st.tabs(["Thumbnails", "Animation Preview", "Video"])
        
        with tab1:
            display_thumbnails(frame_paths)
        
        with tab2:
            st.subheader("Animation Preview")
            if frame_paths:
                # Create a simple animation using Streamlit
                frame_placeholder = st.empty()
                
                if st.button("Play Animation"):
                    for frame_path in frame_paths:
                        image = Image.open(frame_path)
                        frame_placeholder.image(image, caption="Rotating Point Cloud", width=400)
                        time.sleep(1.0 / fps)
        
        with tab3:
            st.subheader("Video Generation")
            if st.button("Create Video"):
                with st.spinner("Creating video..."):
                    video_path = create_video_from_frames(frame_paths, fps=fps)
                    if video_path and os.path.exists(video_path):
                        st.success("Video created successfully!")
                        
                        # Display video
                        with open(video_path, 'rb') as video_file:
                            video_bytes = video_file.read()
                            st.video(video_bytes)
                        
                        # Download button
                        st.download_button(
                            label="Download Video",
                            data=video_bytes,
                            file_name="zoetrope_video.mp4",
                            mime="video/mp4"
                        )
    else:
        st.info("Click 'Generate New Point Cloud & Frames' to start!")
        
        # Show example of what the app does
        st.subheader("What this app does:")
        st.markdown("""
        1. **Generates random 3D point clouds** - Creates a sphere of random points in 3D space
        2. **Rotates around Y-axis** - Each frame shows the point cloud rotated by a specific angle
        3. **Creates PNG thumbnails** - Saves each rotation as a PNG image in the data folder
        4. **Blends into video** - Combines all frames into a smooth rotating animation
        5. **Zoetrope effect** - Like the classic optical toy, creates the illusion of motion
        """)

if __name__ == "__main__":
    main() 