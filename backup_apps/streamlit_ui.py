import streamlit as st
import time
import os
from PIL import Image
from point_cloud import PointCloudZoetrope, ZoetropeAnimator


class ZoetropeApp:
    """Streamlit app for the Zoetrope Point Cloud Viewer."""
    
    def __init__(self):
        st.set_page_config(
            page_title="Zoetrope Point Cloud Viewer",
            page_icon="🎬",
            layout="wide"
        )
    
    def render_sidebar(self):
        """Render sidebar controls and return parameters."""
        st.sidebar.header("Controls")
        
        params = {
            'num_points': st.sidebar.slider("Number of Points", 50, 500, 100),
            'radius': st.sidebar.slider("Cloud Radius", 1, 10, 5),
            'num_frames': st.sidebar.slider("Number of Frames", 12, 72, 36),
            'fps': st.sidebar.slider("Video FPS", 1, 10, 1)
        }
        
        return params
    
    def progress_callback(self, progress, current_frame, total_frames, angle):
        """Progress callback for frame generation."""
        if hasattr(self, '_progress_bar'):
            self._progress_bar.progress(progress)
        if hasattr(self, '_status_text'):
            self._status_text.text(f"Frame {current_frame}/{total_frames} - {angle:.1f}°")
    
    def generate_frames(self, params):
        """Generate frames using the point cloud logic."""
        with st.spinner("Generating point cloud and frames..."):
            self._progress_bar = st.progress(0)
            self._status_text = st.empty()
            
            # Create point cloud and animator
            point_cloud = PointCloudZoetrope(params['num_points'], params['radius'])
            animator = ZoetropeAnimator(point_cloud)
            
            # Generate frames
            frame_paths = animator.generate_frames(
                num_frames=params['num_frames'],
                progress_callback=self.progress_callback
            )
            
            # Clean up progress indicators
            self._progress_bar.empty()
            self._status_text.empty()
            
            return point_cloud, frame_paths, animator
    
    def display_thumbnails(self, frame_paths, cols=6):
        """Display thumbnails in a grid."""
        if not frame_paths:
            st.warning("No frames to display")
            return
        
        st.subheader("Generated Frames")
        
        for i in range(0, len(frame_paths), cols):
            columns = st.columns(cols)
            for j, col in enumerate(columns):
                if i + j < len(frame_paths):
                    with col:
                        image = Image.open(frame_paths[i + j])
                        st.image(image, caption=f"Frame {i+j+1}", use_column_width=True)
    
    def render_animation_tab(self, frame_paths, fps):
        """Render the animation preview tab."""
        st.subheader("Animation Preview")
        if frame_paths and st.button("Play Animation"):
            frame_placeholder = st.empty()
            for frame_path in frame_paths:
                image = Image.open(frame_path)
                frame_placeholder.image(image, caption="Rotating Point Cloud", width=400)
                time.sleep(1.0 / fps)
    
    def render_video_tab(self, frame_paths, animator, fps):
        """Render the video generation tab."""
        st.subheader("Video Generation")
        if st.button("Create Video"):
            with st.spinner("Creating video..."):
                video_path = animator.create_video(frame_paths, fps=fps)
                
                if video_path and os.path.exists(video_path):
                    st.success("Video created successfully!")
                    
                    with open(video_path, 'rb') as video_file:
                        video_bytes = video_file.read()
                        st.video(video_bytes)
                    
                    st.download_button(
                        label="Download Video",
                        data=video_bytes,
                        file_name="zoetrope_video.mp4",
                        mime="video/mp4"
                    )
    
    def render_info_section(self):
        """Render info when no frames are available."""
        st.info("Click 'Generate New Point Cloud & Frames' to start!")
        
        st.subheader("What this app does:")
        st.markdown("""
        1. **Generates random 3D point clouds** - Creates a sphere of random points in 3D space
        2. **Rotates around Y-axis** - Each frame shows the point cloud rotated by a specific angle
        3. **Creates PNG thumbnails** - Saves each rotation as a PNG image in the data folder
        4. **Blends into video** - Combines all frames into a smooth rotating animation
        5. **Zoetrope effect** - Like the classic optical toy, creates the illusion of motion
        """)
    
    def run(self):
        """Main method to run the Streamlit application."""
        st.title("🎬 Zoetrope Point Cloud Viewer")
        st.markdown("Generate rotating 3D point clouds and create zoetrope-like animations!")
        
        # Sidebar controls
        params = self.render_sidebar()
        
        # Generate button
        if st.sidebar.button("Generate New Point Cloud & Frames"):
            point_cloud, frame_paths, animator = self.generate_frames(params)
            
            # Store in session state
            st.session_state.frame_paths = frame_paths
            st.session_state.animator = animator
            
            st.success(f"Generated {len(frame_paths)} frames!")
        
        # Display content
        if 'frame_paths' in st.session_state:
            frame_paths = st.session_state.frame_paths
            animator = st.session_state.animator
            
            # Create tabs
            tab1, tab2, tab3 = st.tabs(["Thumbnails", "Animation Preview", "Video"])
            
            with tab1:
                self.display_thumbnails(frame_paths)
            
            with tab2:
                self.render_animation_tab(frame_paths, params['fps'])
            
            with tab3:
                self.render_video_tab(frame_paths, animator, params['fps'])
        else:
            self.render_info_section()


def main():
    """Entry point for the Streamlit application."""
    app = ZoetropeApp()
    app.run()


if __name__ == "__main__":
    main() 