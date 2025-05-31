"""
Script to comprehensively clean all derived feature columns from facial landmark CSVs.
Keeps only basic coordinates (feat_N_x, feat_N_y, feat_N_z) and core metadata.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import shutil

def comprehensive_clean(file_path: Path) -> pd.DataFrame:
    """
    Remove all derived feature columns, keeping only basic coordinates and metadata.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        DataFrame with only essential columns
    """
    # Read the CSV
    df = pd.read_csv(file_path)
    
    # Define columns to keep
    core_metadata = ['Unnamed: 0', 'Subject Name', 'Test Name', 'Time (s)', 'Face Depth (cm)']
    
    # Find basic coordinate columns (feat_N_x, feat_N_y, feat_N_z)
    coordinate_cols = []
    for col in df.columns:
        if (col.startswith('feat_') and 
            (col.endswith('_x') or col.endswith('_y') or col.endswith('_z')) and
            not any(suffix in col for suffix in ['diff', 'tot', 'norm', 'mag', 'dist'])):
            coordinate_cols.append(col)
    
    # Sort coordinate columns numerically by feature number
    def sort_key(col_name):
        # Extract the feature number from feat_N_x/y/z
        parts = col_name.split('_')
        if len(parts) >= 3 and parts[0] == 'feat':
            try:
                feat_num = int(parts[1])
                coord_type = parts[2]  # x, y, or z
                # Sort by feature number first, then by coordinate type (x, y, z)
                coord_order = {'x': 0, 'y': 1, 'z': 2}
                return (feat_num, coord_order.get(coord_type, 3))
            except ValueError:
                return (999999, 0)  # Put invalid ones at the end
        return (999999, 0)
    
    coordinate_cols = sorted(coordinate_cols, key=sort_key)
    
    # Columns to keep: metadata + basic coordinates
    keep_cols = []
    for col in core_metadata:
        if col in df.columns:
            keep_cols.append(col)
    keep_cols.extend(coordinate_cols)
    
    # Count removed columns
    removed_cols = [col for col in df.columns if col not in keep_cols]
    
    print(f"    Keeping {len(keep_cols)} columns ({len(coordinate_cols)} coordinates + {len(keep_cols) - len(coordinate_cols)} metadata)")
    print(f"    Removing {len(removed_cols)} derived feature columns")
    
    # Return cleaned dataframe
    return df[keep_cols]

def process_experiment(exp_dir: Path):
    """Process all CSV files in an experiment directory."""
    print(f"\n🔍 Processing experiment: {exp_dir.name}")
    
    # Process each CSV file
    csv_files = list(exp_dir.glob("*.csv"))
    if not csv_files:
        print(f"⚠️ No CSV files found in {exp_dir.name}")
        return
    
    for csv_file in csv_files:
        print(f"  📄 Processing {csv_file.name}...")
        try:
            # Comprehensive clean
            df = comprehensive_clean(csv_file)
            
            # Save back to file
            df.to_csv(csv_file, index=False)
            print(f"    ✅ Successfully cleaned {csv_file.name}")
            
        except Exception as e:
            print(f"    ❌ Error processing {csv_file.name}: {str(e)}")

def main():
    """Main function to process all experiments."""
    # Setup paths
    root_dir = Path("data/read")
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    backup_dir = root_dir.parent / f"backup_comprehensive_{timestamp}"
    backup_dir.mkdir(exist_ok=True)
    print(f"📁 Created backup directory: {backup_dir}")
    
    # Process each experiment directory
    exp_dirs = [d for d in root_dir.glob("e*") if d.is_dir()]
    
    for exp_dir in exp_dirs:
        # Create backup of experiment
        exp_backup_dir = backup_dir / exp_dir.name
        exp_backup_dir.mkdir(exist_ok=True)
        
        # Backup all CSV files
        for csv_file in exp_dir.glob("*.csv"):
            shutil.copy2(csv_file, exp_backup_dir / csv_file.name)
        
        # Process the experiment
        process_experiment(exp_dir)
    
    print("\n✨ Done! All CSV files comprehensively cleaned.")
    print("\nYour files now contain only:")
    print("- Core metadata: Subject Name, Test Name, Time (s), Face Depth (cm)")
    print("- Basic coordinates: feat_N_x, feat_N_y, feat_N_z (for 478 landmarks)")

if __name__ == "__main__":
    main() 