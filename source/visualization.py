"""Visualization Module

Handles matplotlib-based preview plotting for point clouds.
Clean separation from the main UI logic.
Enhanced with proper camera orientation for facial landmark data.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math


class PointCloudVisualizer:
    """Handles matplotlib visualization for point cloud previews."""
    
    @staticmethod
    def create_preview_plot(points, colors=None, title_prefix="Preview"):
        """Create matplotlib preview plot for point cloud."""
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        if colors is not None:
            ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                      c=colors, s=1, alpha=0.7)
        else:
            ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                      c=points[:, 2], cmap='viridis', s=1, alpha=0.7)
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(f'{title_prefix} ({len(points)} points)\nThis is the LIMITED matplotlib view')
        
        # Equal aspect ratio
        max_range = np.max(np.ptp(points, axis=0)) / 2
        mid = np.mean(points, axis=0)
        ax.set_xlim(mid[0] - max_range, mid[0] + max_range)
        ax.set_ylim(mid[1] - max_range, mid[1] + max_range)
        ax.set_zlim(mid[2] - max_range, mid[2] + max_range)
        
        # Fix orientation - proper front-facing view for facial data
        # elev=20 (slightly above), azim=30 (angled view), roll=0 (upright)
        # Changed to azim=30 for better depth perception while keeping face visible
        ax.view_init(elev=20, azim=30, roll=0)
        
        return fig
    
    @staticmethod
    def create_animation_frame_plot(frame_data, frame_idx, total_frames, bounds=None):
        """Create plot for a single animation frame."""
        points = frame_data['points']
        colors = frame_data['colors']
        filename = frame_data['filename']
        
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        if colors is not None:
            ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                      c=colors, s=1, alpha=0.7)
        else:
            ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                      c=points[:, 2], cmap='viridis', s=1, alpha=0.7)
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        # Clean title without emoji to prevent matplotlib issues
        ax.set_title(f'Frame {frame_idx+1}/{total_frames}: {filename}\nAnimation Preview ({len(points)} points)')
        
        # Apply bounds if provided
        if bounds:
            ax.set_xlim(bounds['xlim'])
            ax.set_ylim(bounds['ylim'])
            ax.set_zlim(bounds['zlim'])
        else:
            # Calculate bounds for this frame
            max_range = np.max(np.ptp(points, axis=0)) / 2
            mid = np.mean(points, axis=0)
            ax.set_xlim(mid[0] - max_range, mid[0] + max_range)
            ax.set_ylim(mid[1] - max_range, mid[1] + max_range)
            ax.set_zlim(mid[2] - max_range, mid[2] + max_range)
        
        # Fix orientation - proper front-facing view for facial data
        # Changed to azim=30 for better depth perception while keeping face visible
        ax.view_init(elev=20, azim=30, roll=0)
        
        return fig
    
    @staticmethod
    def create_animation_thumbnail_grid(frames_data, max_frames=16, grid_cols=4):
        """Create a grid of thumbnail plots for animation frames."""
        total_frames = len(frames_data)
        
        # Limit number of frames to display
        if total_frames > max_frames:
            # Sample frames evenly across the animation
            indices = np.linspace(0, total_frames - 1, max_frames, dtype=int)
            display_frames = [frames_data[i] for i in indices]
            frame_numbers = indices
        else:
            display_frames = frames_data
            frame_numbers = list(range(total_frames))
        
        num_frames = len(display_frames)
        grid_rows = math.ceil(num_frames / grid_cols)
        
        # Calculate consistent bounds for all frames
        all_points = np.vstack([f['points'] for f in frames_data])
        max_range = np.max(np.ptp(all_points, axis=0)) / 2 * 1.1
        mid = np.mean(all_points, axis=0)
        bounds = {
            'xlim': [mid[0] - max_range, mid[0] + max_range],
            'ylim': [mid[1] - max_range, mid[1] + max_range],
            'zlim': [mid[2] - max_range, mid[2] + max_range]
        }
        
        # Create figure with subplots
        fig = plt.figure(figsize=(grid_cols * 3, grid_rows * 2.5))
        fig.suptitle(f'Animation Overview: {total_frames} Frames Total', fontsize=14)
        
        for i, (frame_data, frame_num) in enumerate(zip(display_frames, frame_numbers)):
            ax = fig.add_subplot(grid_rows, grid_cols, i + 1, projection='3d')
            
            points = frame_data['points']
            colors = frame_data['colors']
            
            # Smaller point size for thumbnails
            if colors is not None:
                ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                          c=colors, s=0.5, alpha=0.8, edgecolors='none')
            else:
                ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                          c=points[:, 2], cmap='viridis', s=0.5, alpha=0.8, edgecolors='none')
            
            # Apply consistent bounds
            ax.set_xlim(bounds['xlim'])
            ax.set_ylim(bounds['ylim'])
            ax.set_zlim(bounds['zlim'])
            
            # Minimal labels for thumbnails
            ax.set_title(f'Frame {frame_num + 1}', fontsize=10)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_zticks([])
            
            # Remove axis labels for clean look
            ax.set_xlabel('')
            ax.set_ylabel('')
            ax.set_zlabel('')
            
            # Fix orientation for thumbnails - consistent view
            # Changed to azim=30 for better depth perception while keeping face visible
            ax.view_init(elev=20, azim=30, roll=0)
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def create_animation_strip(frames_data, max_frames=12):
        """Create a horizontal strip of animation frames."""
        total_frames = len(frames_data)
        
        # Sample frames if too many
        if total_frames > max_frames:
            indices = np.linspace(0, total_frames - 1, max_frames, dtype=int)
            display_frames = [frames_data[i] for i in indices]
            frame_numbers = indices
        else:
            display_frames = frames_data
            frame_numbers = list(range(total_frames))
        
        num_frames = len(display_frames)
        
        # Calculate consistent bounds
        all_points = np.vstack([f['points'] for f in frames_data])
        max_range = np.max(np.ptp(all_points, axis=0)) / 2 * 1.1
        mid = np.mean(all_points, axis=0)
        bounds = {
            'xlim': [mid[0] - max_range, mid[0] + max_range],
            'ylim': [mid[1] - max_range, mid[1] + max_range],
            'zlim': [mid[2] - max_range, mid[2] + max_range]
        }
        
        # Create horizontal strip
        fig = plt.figure(figsize=(num_frames * 2, 3))
        fig.suptitle(f'Animation Timeline: {total_frames} Frames', fontsize=12)
        
        for i, (frame_data, frame_num) in enumerate(zip(display_frames, frame_numbers)):
            ax = fig.add_subplot(1, num_frames, i + 1, projection='3d')
            
            points = frame_data['points']
            colors = frame_data['colors']
            
            if colors is not None:
                ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                          c=colors, s=0.3, alpha=0.9, edgecolors='none')
            else:
                ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                          c=points[:, 2], cmap='viridis', s=0.3, alpha=0.9, edgecolors='none')
            
            # Apply bounds
            ax.set_xlim(bounds['xlim'])
            ax.set_ylim(bounds['ylim'])
            ax.set_zlim(bounds['zlim'])
            
            # Clean minimal appearance
            ax.set_title(f'{frame_num + 1}', fontsize=8)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_zticks([])
            ax.set_xlabel('')
            ax.set_ylabel('')
            ax.set_zlabel('')
            
            # Fix orientation for strip view
            # Changed to azim=30 for better depth perception while keeping face visible
            ax.view_init(elev=20, azim=30, roll=0)
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def calculate_animation_bounds(frames_data):
        """Calculate consistent bounds for animation frames."""
        all_points = np.vstack([f['points'] for f in frames_data])
        max_range = np.max(np.ptp(all_points, axis=0)) / 2
        mid = np.mean(all_points, axis=0)
        
        return {
            'xlim': [mid[0] - max_range, mid[0] + max_range],
            'ylim': [mid[1] - max_range, mid[1] + max_range],
            'zlim': [mid[2] - max_range, mid[2] + max_range]
        }
    
    @staticmethod
    def get_plot_info():
        """Get information about matplotlib plotting capabilities."""
        return {
            'type': 'matplotlib',
            'limitations': [
                'Limited interactivity',
                'Slow rotation',
                'Basic lighting',
                'Browser-based only'
            ],
            'advantages': [
                'Quick preview',
                'Web-based',
                'Good for static views',
                'Easy integration'
            ],
            'recommendation': 'Use desktop viewer for full interactivity',
            'orientation_fix': 'Added proper camera angles (elev=20, azim=45) for facial data'
        }
    
    @staticmethod
    def create_orientation_comparison_plot(points, colors=None):
        """Create a comparison plot showing different orientations."""
        fig = plt.figure(figsize=(15, 5))
        
        # Original (problematic) view
        ax1 = fig.add_subplot(131, projection='3d')
        if colors is not None:
            ax1.scatter(points[:, 0], points[:, 1], points[:, 2], c=colors, s=1, alpha=0.7)
        else:
            ax1.scatter(points[:, 0], points[:, 1], points[:, 2], c=points[:, 2], cmap='viridis', s=1, alpha=0.7)
        ax1.set_title('Original View\n(Often upside-down)')
        # Default matplotlib view (often problematic)
        
        # Fixed front view
        ax2 = fig.add_subplot(132, projection='3d')
        if colors is not None:
            ax2.scatter(points[:, 0], points[:, 1], points[:, 2], c=colors, s=1, alpha=0.7)
        else:
            ax2.scatter(points[:, 0], points[:, 1], points[:, 2], c=points[:, 2], cmap='viridis', s=1, alpha=0.7)
        ax2.set_title('Fixed Front View\n(elev=20, azim=30)')
        ax2.view_init(elev=20, azim=30, roll=0)
        
        # Side view
        ax3 = fig.add_subplot(133, projection='3d')
        if colors is not None:
            ax3.scatter(points[:, 0], points[:, 1], points[:, 2], c=colors, s=1, alpha=0.7)
        else:
            ax3.scatter(points[:, 0], points[:, 1], points[:, 2], c=points[:, 2], cmap='viridis', s=1, alpha=0.7)
        ax3.set_title('Side View\n(elev=0, azim=0)')
        ax3.view_init(elev=0, azim=0, roll=0)
        
        # Set consistent bounds for all
        max_range = np.max(np.ptp(points, axis=0)) / 2
        mid = np.mean(points, axis=0)
        for ax in [ax1, ax2, ax3]:
            ax.set_xlim(mid[0] - max_range, mid[0] + max_range)
            ax.set_ylim(mid[1] - max_range, mid[1] + max_range)
            ax.set_zlim(mid[2] - max_range, mid[2] + max_range)
        
        plt.tight_layout()
        return fig 