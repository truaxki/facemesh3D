#!/usr/bin/env python3
"""open3d_basic_test.py

Quick sanity-check that Open3D is installed and working.

Usage
-----
    python source/open3d_basic_test.py [path/to/points.txt]

If a path is provided, the file should contain a comma- or whitespace-separated
list of XYZ coordinates, one point per line.  If no file is provided, the
script generates a random spherical point cloud instead.

Controls (Open3D viewer)
-----------------------
    Left-drag   : rotate camera
    Right-drag  : translate camera
    Mouse wheel : zoom in/out
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import open3d as o3d


def _load_points_from_txt(path: str | Path) -> np.ndarray:
    """Load an Nx3 ASCII point list (csv or whitespace separated)."""
    arr = np.loadtxt(path, delimiter=",")
    if arr.ndim == 1:
        # Single point
        arr = arr.reshape(1, -1)
    if arr.shape[1] != 3:
        raise ValueError("Input file must have exactly 3 columns (XYZ)")
    return arr.astype(np.float64)


def _random_sphere(num_points: int = 1000, radius: float = 1.0) -> np.ndarray:
    """Uniformly sample *num_points* inside a sphere of given *radius*."""
    phi = np.random.uniform(0.0, 2.0 * np.pi, num_points)
    costheta = np.random.uniform(-1.0, 1.0, num_points)
    u = np.random.uniform(0.0, 1.0, num_points)

    theta = np.arccos(costheta)
    r = radius * (u ** (1.0 / 3.0))

    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)
    return np.column_stack((x, y, z)).astype(np.float64)


def make_open3d_point_cloud(points: np.ndarray) -> o3d.geometry.PointCloud:
    """Convert an (N,3) array to an Open3D PointCloud object."""
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError("points must be an Nx3 array of XYZ coordinates")
    pc = o3d.geometry.PointCloud()
    pc.points = o3d.utility.Vector3dVector(points)
    # Estimate normals so we can enable nicer shading in the viewer
    pc.estimate_normals()
    return pc


def main() -> None:
    # ------------------------------
    # 1. Get data
    # ------------------------------
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        if not path.exists():
            sys.exit(f"File not found: {path}")
        points = _load_points_from_txt(path)
        print(f"Loaded {points.shape[0]} points from {path}")
    else:
        points = _random_sphere()
        print(f"Generated {points.shape[0]} random points inside a sphere")

    # ------------------------------
    # 2. Convert & show
    # ------------------------------
    pcd = make_open3d_point_cloud(points)
    print("Opening Open3D visualiser… (close the window to finish)")
    o3d.visualization.draw_geometries([pcd])


if __name__ == "__main__":
    main() 