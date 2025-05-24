"""registration.py
Utility functions for estimating rigid 6-DoF motion (rotation + translation)
between two point clouds using Open3D. Designed for quick experiments with
Iterative Closest Point (ICP) and Generalized ICP (GICP).

Dependencies
------------
open3d>=0.17.0  (add this to requirements.txt)

Example
-------
>>> from point_cloud import PointCloudZoetrope
>>> from registration import estimate_rigid_transform_icp
>>> cloud = PointCloudZoetrope(num_points=500, radius=3)
>>> src = cloud.points
>>> tgt = cloud.rotate_y(30)  # ground-truth rotation
>>> result = estimate_rigid_transform_icp(src, tgt)
>>> print(result.transformation)
"""
from __future__ import annotations

from typing import Tuple, Dict
import numpy as np

try:
    import open3d as o3d  # type: ignore
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "Open3D is required for registration utilities. Install with:\n"
        "  pip install open3d"
    ) from e

__all__ = [
    "to_o3d_point_cloud",
    "estimate_rigid_transform_icp",
    "estimate_rigid_transform_gicp",
    "evaluate_registration",
]


# -----------------------------------------------------------------------------
# Helper utilities
# -----------------------------------------------------------------------------

def to_o3d_point_cloud(points: np.ndarray) -> "o3d.geometry.PointCloud":
    """Convert (N,3) numpy array to an Open3D PointCloud with normals."""
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError("points must be a Nx3 array")

    pc = o3d.geometry.PointCloud()
    pc.points = o3d.utility.Vector3dVector(points.astype(np.float64))
    pc.estimate_normals()
    return pc


# -----------------------------------------------------------------------------
# Rigid registration methods
# -----------------------------------------------------------------------------

def estimate_rigid_transform_icp(
    source_pts: np.ndarray,
    target_pts: np.ndarray,
    threshold: float = 0.05,
    init_transformation: np.ndarray | None = None,
    point_to_plane: bool = True,
) -> "o3d.pipelines.registration.RegistrationResult":
    """Run (point-to-plane) ICP to align *source* to *target*.

    Parameters
    ----------
    source_pts, target_pts : (N,3), (M,3) float arrays
        The point sets to register.
    threshold : float
        Maximum correspondence distance (in the same units as the points).
    init_transformation : 4x4 float array, optional
        Initial guess. If *None*, uses identity.
    point_to_plane : bool, default True
        Use point-to-plane ICP (needs normals). If False, uses point-to-point.

    Returns
    -------
    open3d.registration.RegistrationResult
        Contains the estimated 4×4 transformation matrix, RMSE and fitness.
    """
    if init_transformation is None:
        init_transformation = np.eye(4)

    src_pc = to_o3d_point_cloud(source_pts)
    tgt_pc = to_o3d_point_cloud(target_pts)

    if point_to_plane:
        estimation = o3d.pipelines.registration.TransformationEstimationPointToPlane()
    else:
        estimation = o3d.pipelines.registration.TransformationEstimationPointToPoint()

    result = o3d.pipelines.registration.registration_icp(
        src_pc,
        tgt_pc,
        threshold,
        init_transformation,
        estimation,
        o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=2000),
    )
    return result


def estimate_rigid_transform_gicp(
    source_pts: np.ndarray,
    target_pts: np.ndarray,
    threshold: float = 0.05,
    init_transformation: np.ndarray | None = None,
) -> "o3d.pipelines.registration.RegistrationResult":
    """Run Generalized-ICP (GICP) to align *source* to *target*.

    GICP models local plane covariance and generally converges faster and
    more robustly than standard ICP.
    """
    if init_transformation is None:
        init_transformation = np.eye(4)

    src_pc = to_o3d_point_cloud(source_pts)
    tgt_pc = to_o3d_point_cloud(target_pts)

    result = o3d.pipelines.registration.registration_generalized_icp(
        src_pc,
        tgt_pc,
        threshold,
        init_transformation,
        o3d.pipelines.registration.TransformationEstimationForGeneralizedICP(),
        o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=2000),
    )
    return result


# -----------------------------------------------------------------------------
# Evaluation utilities
# -----------------------------------------------------------------------------

def _rotation_error_deg(R_gt: np.ndarray, R_est: np.ndarray) -> float:
    """Geodesic distance between two rotation matrices in degrees."""
    val = (np.trace(R_gt.T @ R_est) - 1) / 2.0
    val = np.clip(val, -1.0, 1.0)
    return float(np.degrees(np.arccos(val)))


def evaluate_registration(
    result: "o3d.pipelines.registration.RegistrationResult",
    R_gt: np.ndarray,
    t_gt: np.ndarray,
) -> Dict[str, float]:
    """Return rotation (deg) and translation (L2) errors as a dict."""
    T_est = result.transformation
    R_est = T_est[:3, :3]
    t_est = T_est[:3, 3]

    rot_err = _rotation_error_deg(R_gt, R_est)
    trans_err = float(np.linalg.norm(t_gt - t_est))

    return {
        "rotation_error_deg": rot_err,
        "translation_error": trans_err,
        "rmse": result.inlier_rmse,
        "fitness": result.fitness,
    } 