import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
import cv2


class PointCloudZoetrope:
    """A class for generating and manipulating 3D point clouds for zoetrope animations."""
    
    def __init__(self, num_points=100, radius=5):
        self.num_points = num_points
        self.radius = radius
        self.points = self._generate_sphere_points()
        
    def _generate_sphere_points(self):
        """Generate random points distributed within a sphere using spherical coordinates."""
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
        """Rotate points around Y-axis by specified angle."""
        angle_rad = np.radians(angle_degrees)
        rotation_matrix = np.array([
            [np.cos(angle_rad), 0, np.sin(angle_rad)],
            [0, 1, 0],
            [-np.sin(angle_rad), 0, np.cos(angle_rad)]
        ])
        return np.dot(self.points, rotation_matrix.T)
    
    def create_frame(self, angle_degrees, figsize=(8, 8)):
        """Create a matplotlib figure of the rotated point cloud."""
        rotated_points = self.rotate_y(angle_degrees)
        
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot with depth-based coloring
        ax.scatter(rotated_points[:, 0], rotated_points[:, 1], rotated_points[:, 2], 
                  c=rotated_points[:, 2], cmap='viridis', s=50, alpha=0.7)
        
        # Set limits and styling
        max_range = self.radius * 1.2
        ax.set_xlim([-max_range, max_range])
        ax.set_ylim([-max_range, max_range])
        ax.set_zlim([-max_range, max_range])
        ax.set_title(f'Point Cloud - Rotation: {angle_degrees:.1f}°')
        ax.grid(False)
        ax.set_facecolor('black')
        
        return fig
    
    def save_frame(self, angle_degrees, filepath):
        """Save a frame as PNG file."""
        fig = self.create_frame(angle_degrees)
        fig.savefig(filepath, dpi=100, bbox_inches='tight', 
                   facecolor='black', edgecolor='none')
        plt.close(fig)
        return filepath


class ZoetropeAnimator:
    """Creates animations from point clouds."""
    
    def __init__(self, point_cloud):
        self.point_cloud = point_cloud
    
    def generate_frames(self, num_frames=36, data_dir="data", progress_callback=None):
        """Generate all frames for the animation."""
        os.makedirs(data_dir, exist_ok=True)
        
        frame_paths = []
        angles = np.linspace(0, 360, num_frames, endpoint=False)
        
        for i, angle in enumerate(angles):
            filename = f"frame_{i:03d}_{angle:.1f}deg.png"
            filepath = os.path.join(data_dir, filename)
            
            self.point_cloud.save_frame(angle, filepath)
            frame_paths.append(filepath)
            
            if progress_callback:
                progress_callback((i + 1) / num_frames, i + 1, num_frames, angle)
        
        return frame_paths
    
    def create_video(self, frame_paths, output_path="data/zoetrope_video.mp4", fps=1):
        """Create a video from frames."""
        if not frame_paths:
            return None
        
        first_frame = cv2.imread(frame_paths[0])
        if first_frame is None:
            return None
            
        height, width, layers = first_frame.shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        for frame_path in frame_paths:
            frame = cv2.imread(frame_path)
            if frame is not None:
                video.write(frame)
        
        video.release()
        return output_path


# Convenience functions
def create_point_cloud(num_points=100, radius=5):
    """Create a random point cloud."""
    return PointCloudZoetrope(num_points, radius)


def create_animation(num_points=100, radius=5, num_frames=36, 
                    data_dir="data", fps=1, progress_callback=None):
    """Complete workflow to generate a zoetrope animation."""
    cloud = create_point_cloud(num_points, radius)
    animator = ZoetropeAnimator(cloud)
    
    frame_paths = animator.generate_frames(num_frames, data_dir, progress_callback)
    video_path = animator.create_video(frame_paths, f"{data_dir}/zoetrope_video.mp4", fps)
    
    return frame_paths, video_path