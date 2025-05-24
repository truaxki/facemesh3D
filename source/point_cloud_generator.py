"""Point Cloud Generator Module

Clean, focused module for generating various 3D point cloud shapes.
Extracted from the main application for better modularity.
"""

import numpy as np


class PointCloudGenerator:
    """Generates various types of 3D point clouds with colors."""
    
    @staticmethod
    def sphere(num_points=2000, radius=1.0):
        """Generate points uniformly distributed within a sphere."""
        phi = np.random.uniform(0, 2*np.pi, num_points)
        costheta = np.random.uniform(-1, 1, num_points)
        u = np.random.uniform(0, 1, num_points)
        
        theta = np.arccos(costheta)
        r = radius * (u ** (1/3))
        
        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)
        points = np.column_stack([x, y, z])
        
        # Color by height
        colors = np.column_stack([
            (z + radius) / (2*radius),
            np.zeros_like(z),
            1 - (z + radius) / (2*radius)
        ])
        
        return points, colors
    
    @staticmethod
    def torus(num_points=2000, major_radius=1.0, minor_radius=0.3):
        """Generate points on a torus surface."""
        u = np.random.uniform(0, 2*np.pi, num_points)
        v = np.random.uniform(0, 2*np.pi, num_points)
        
        x = (major_radius + minor_radius * np.cos(v)) * np.cos(u)
        y = (major_radius + minor_radius * np.cos(v)) * np.sin(u)
        z = minor_radius * np.sin(v)
        points = np.column_stack([x, y, z])
        
        colors = np.column_stack([
            (np.sin(u) + 1) / 2,
            (np.cos(u) + 1) / 2,
            (np.sin(v) + 1) / 2
        ])
        
        return points, colors
    
    @staticmethod
    def helix(num_points=2000, turns=3, height=2.0, radius=1.0):
        """Generate points along a helical path."""
        t = np.linspace(0, turns * 2*np.pi, num_points)
        x = radius * np.cos(t)
        y = radius * np.sin(t)
        z = height * t / (turns * 2*np.pi)
        points = np.column_stack([x, y, z])
        
        colors = np.column_stack([
            t / (turns * 2*np.pi),
            0.5 * np.ones_like(t),
            1 - t / (turns * 2*np.pi)
        ])
        
        return points, colors
    
    @staticmethod
    def cube(num_points=2000, side_length=2.0):
        """Generate points uniformly distributed within a cube."""
        points = np.random.uniform(-side_length/2, side_length/2, (num_points, 3))
        
        # Color by distance from center
        dist = np.linalg.norm(points, axis=1)
        max_dist = np.max(dist)
        colors = np.column_stack([
            dist / max_dist,
            0.5 * np.ones_like(dist),
            1 - dist / max_dist
        ])
        
        return points, colors
    
    @staticmethod
    def random(num_points=2000):
        """Generate random point cloud."""
        points = np.random.randn(num_points, 3)
        colors = np.random.rand(num_points, 3)
        return points, colors
    
    @classmethod
    def generate(cls, shape_type, num_points, **kwargs):
        """Generate a point cloud of the specified type."""
        generators = {
            "Sphere": cls.sphere,
            "Torus": cls.torus,
            "Helix": cls.helix,
            "Cube": cls.cube,
            "Random": cls.random
        }
        
        if shape_type not in generators:
            raise ValueError(f"Unknown shape type: {shape_type}")
        
        return generators[shape_type](num_points, **kwargs)


def get_shape_parameters():
    """Get the parameter definitions for each shape type."""
    return {
        "Sphere": [
            {"name": "radius", "min": 0.5, "max": 3.0, "default": 1.0}
        ],
        "Torus": [
            {"name": "major_radius", "min": 0.5, "max": 2.0, "default": 1.0},
            {"name": "minor_radius", "min": 0.1, "max": 0.8, "default": 0.3}
        ],
        "Helix": [
            {"name": "turns", "min": 1, "max": 8, "default": 3, "type": "int"},
            {"name": "height", "min": 1.0, "max": 5.0, "default": 2.0},
            {"name": "radius", "min": 0.5, "max": 2.0, "default": 1.0}
        ],
        "Cube": [
            {"name": "side_length", "min": 1.0, "max": 4.0, "default": 2.0}
        ],
        "Random": []
    } 