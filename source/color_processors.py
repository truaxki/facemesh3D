"""Color Processors Module

Handles all color processing methods for point cloud visualization.
Modularizes the various coloring strategies from the main interface.
"""

import numpy as np
import streamlit as st
from typing import List, Dict, Any
from data_filters import DataFilters
from facial_clusters import FACIAL_CLUSTERS


class ColorProcessor:
    """Base class for color processing strategies."""
    
    @staticmethod
    def apply_none_coloring(frames_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply white/neutral coloring to all points."""
        for frame in frames_data:
            num_points = len(frame['points'])
            frame['colors'] = np.ones((num_points, 3)) * 0.9  # Light gray/white
        return frames_data
    
    @staticmethod
    def apply_point_cloud_continuous_coloring(frames_data: List[Dict[str, Any]], 
                                            baseline_frames: int) -> List[Dict[str, Any]]:
        """Apply coloring based on continuous distance from baseline (for microexpressions)."""
        if len(frames_data) < baseline_frames:
            print("⚠️ Not enough frames for baseline calculation")
            return frames_data
        
        # Calculate baseline as average of first N frames
        baseline_frames_data = frames_data[:baseline_frames]
        num_points = len(baseline_frames_data[0]['points'])
        
        # Compute average baseline points
        baseline_points = np.zeros((num_points, 3))
        for frame in baseline_frames_data:
            baseline_points += frame['points']
        baseline_points /= len(baseline_frames_data)
        
        # Apply continuous distance coloring to all frames
        frames_data = DataFilters.generate_continuous_distance_colors(
            frames_data, baseline_points, 'point_cloud'
        )
        
        return frames_data
    
    @staticmethod
    def apply_point_cloud_sd_coloring(frames_data: List[Dict[str, Any]], 
                                    baseline_frames: int) -> List[Dict[str, Any]]:
        """Apply coloring based on standard deviation from baseline."""
        if len(frames_data) < baseline_frames:
            print("⚠️ Not enough frames for baseline calculation")
            return frames_data
        
        # Calculate baseline statistics
        baseline_frames_data = frames_data[:baseline_frames]
        num_points = len(baseline_frames_data[0]['points'])
        
        # Compute baseline mean and std for each point
        baseline_points_all = np.array([frame['points'] for frame in baseline_frames_data])
        baseline_mean = np.mean(baseline_points_all, axis=0)
        baseline_std = np.std(baseline_points_all, axis=0)
        
        # Apply SD coloring
        frames_data = DataFilters.generate_sd_distance_colors(
            frames_data, baseline_mean, baseline_std, 'point_cloud'
        )
        
        return frames_data
    
    @staticmethod
    def apply_clusters_continuous_coloring(frames_data: List[Dict[str, Any]], 
                                         baseline_frames: int) -> List[Dict[str, Any]]:
        """Apply coloring based on cluster mean continuous distance from baseline."""
        if len(frames_data) < baseline_frames:
            print("⚠️ Not enough frames for baseline calculation")
            return frames_data
        
        # Calculate baseline cluster means
        baseline_frames_data = frames_data[:baseline_frames]
        baseline_cluster_means = DataFilters.calculate_baseline_cluster_means(baseline_frames_data)
        
        # Apply continuous distance coloring for clusters
        frames_data = DataFilters.generate_continuous_distance_colors(
            frames_data, baseline_cluster_means, 'clusters'
        )
        
        return frames_data
    
    @staticmethod
    def apply_clusters_sd_coloring(frames_data: List[Dict[str, Any]], 
                                 baseline_frames: int) -> List[Dict[str, Any]]:
        """Apply coloring based on cluster standard deviation from baseline."""
        if len(frames_data) < baseline_frames:
            print("⚠️ Not enough frames for baseline calculation")
            return frames_data
        
        # Calculate baseline cluster statistics
        baseline_frames_data = frames_data[:baseline_frames]
        baseline_stats = DataFilters.calculate_baseline_cluster_stats(baseline_frames_data)
        
        # Apply SD coloring for clusters
        frames_data = DataFilters.generate_sd_distance_colors(
            frames_data, baseline_stats['means'], baseline_stats['stds'], 'clusters'
        )
        
        return frames_data
    
    @staticmethod
    def apply_coloring(frames_data: List[Dict[str, Any]], color_mode: str, 
                      baseline_frames: int) -> List[Dict[str, Any]]:
        """Apply the specified coloring mode to frames data."""
        coloring_methods = {
            'none': lambda fd: ColorProcessor.apply_none_coloring(fd),
            'point_cloud_continuous': lambda fd: ColorProcessor.apply_point_cloud_continuous_coloring(fd, baseline_frames),
            'point_cloud_sd': lambda fd: ColorProcessor.apply_point_cloud_sd_coloring(fd, baseline_frames),
            'clusters_continuous': lambda fd: ColorProcessor.apply_clusters_continuous_coloring(fd, baseline_frames),
            'clusters_sd': lambda fd: ColorProcessor.apply_clusters_sd_coloring(fd, baseline_frames)
        }
        
        if color_mode in coloring_methods:
            return coloring_methods[color_mode](frames_data)
        else:
            print(f"⚠️ Unknown color mode: {color_mode}")
            return ColorProcessor.apply_none_coloring(frames_data) 