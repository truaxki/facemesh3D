#!/usr/bin/env python3
"""
Debug script to check file paths for feature extraction and model training.
"""

from pathlib import Path
import os

def check_paths():
    print("🔍 Debugging File Paths for Feature Extraction and Model Training")
    print("=" * 60)
    
    # Check current working directory
    print(f"\n📁 Current working directory: {os.getcwd()}")
    
    # Check if data directories exist
    data_dir = Path("data")
    read_dir = data_dir / "read"
    write_dir = data_dir / "write"
    
    print(f"\n📂 Directory structure:")
    print(f"  data/ exists: {data_dir.exists()}")
    print(f"  data/read/ exists: {read_dir.exists()}")
    print(f"  data/write/ exists: {write_dir.exists()}")
    
    # List experiments in read directory
    if read_dir.exists():
        print(f"\n📊 Experiments in data/read/:")
        for exp in read_dir.iterdir():
            if exp.is_dir():
                csv_count = len(list(exp.glob("*.csv")))
                print(f"  - {exp.name}: {csv_count} CSV files")
    
    # List experiments in write directory and their feature files
    if write_dir.exists():
        print(f"\n📊 Experiments in data/write/:")
        total_feature_files = 0
        
        for exp in write_dir.iterdir():
            if exp.is_dir():
                # Look for feature files
                feature_files = list(exp.glob("extracted_features_*.csv"))
                other_csv = list(exp.glob("*.csv"))
                
                print(f"\n  - {exp.name}:")
                print(f"      Feature files: {len(feature_files)}")
                print(f"      Total CSV files: {len(other_csv)}")
                
                # List actual feature files
                if feature_files:
                    for ff in feature_files[:3]:  # Show first 3
                        print(f"        • {ff.name}")
                    if len(feature_files) > 3:
                        print(f"        • ... and {len(feature_files) - 3} more")
                
                total_feature_files += len(feature_files)
        
        print(f"\n✅ Total feature files found: {total_feature_files}")
    
    # Check what the model training demo looks for
    print(f"\n🔍 Model training looks for:")
    print(f"  Pattern: data/write/*/extracted_features_*.csv")
    
    # Actually search like the demo does
    found_files = []
    for exp_dir in write_dir.glob("*"):
        if exp_dir.is_dir():
            for csv_file in exp_dir.glob("extracted_features_*.csv"):
                found_files.append(str(csv_file))
    
    print(f"  Found: {len(found_files)} files")
    if found_files:
        for f in found_files[:5]:
            print(f"    • {f}")
        if len(found_files) > 5:
            print(f"    • ... and {len(found_files) - 5} more")
    
    # Check file accessibility
    if found_files:
        print(f"\n📋 Checking first feature file:")
        first_file = Path(found_files[0])
        print(f"  Path: {first_file}")
        print(f"  Exists: {first_file.exists()}")
        print(f"  Readable: {os.access(first_file, os.R_OK)}")
        print(f"  Size: {first_file.stat().st_size / 1024:.1f} KB")
        
        # Try to read first few lines
        try:
            import pandas as pd
            df = pd.read_csv(first_file, nrows=5)
            print(f"  Columns: {list(df.columns)[:10]}")
            if len(df.columns) > 10:
                print(f"           ... and {len(df.columns) - 10} more columns")
        except Exception as e:
            print(f"  ❌ Error reading file: {e}")


if __name__ == "__main__":
    check_paths() 