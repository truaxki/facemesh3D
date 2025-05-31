#!/usr/bin/env python3
"""
Test script to verify feature file discovery for model training.
"""

import sys
sys.path.append('source')

from pathlib import Path
from session_state_manager import SessionStateManager

def test_file_discovery():
    print("🧪 Testing Feature File Discovery")
    print("=" * 50)
    
    # Simulate what happens in the UI
    data_write_dir = Path("data/write")
    
    # Test 1: Check if write directory exists
    if not data_write_dir.exists():
        print("❌ data/write directory doesn't exist!")
        return
    
    print("✅ data/write directory exists")
    
    # Test 2: Look for experiment folders
    experiments = list(data_write_dir.glob("*"))
    experiment_dirs = [d for d in experiments if d.is_dir()]
    
    print(f"\n📁 Found {len(experiment_dirs)} experiment directories:")
    for exp_dir in experiment_dirs:
        print(f"  - {exp_dir.name}")
    
    # Test 3: Look for feature files in each experiment
    all_feature_files = []
    
    for exp_dir in experiment_dirs:
        csv_files = list(exp_dir.glob("*.csv"))
        feature_files = []
        
        for csv_file in csv_files:
            try:
                # Quick check if it's a feature file
                import pandas as pd
                df = pd.read_csv(csv_file, nrows=1)
                
                # Check for derived features
                has_displacement = any(col.startswith('displacement_') for col in df.columns)
                has_quaternion = any(col.startswith('quaternion_') for col in df.columns)
                
                if has_displacement or has_quaternion:
                    feature_files.append({
                        'path': str(csv_file),
                        'name': csv_file.name,
                        'experiment': exp_dir.name,
                        'has_displacement': has_displacement,
                        'has_quaternion': has_quaternion
                    })
                    
            except Exception as e:
                print(f"    ⚠️ Error reading {csv_file.name}: {e}")
        
        if feature_files:
            print(f"\n  📊 {exp_dir.name}: {len(feature_files)} feature files")
            for ff in feature_files:
                features = []
                if ff['has_displacement']:
                    features.append("displacement")
                if ff['has_quaternion']:
                    features.append("quaternion")
                print(f"     • {ff['name']} [{', '.join(features)}]")
            
            all_feature_files.extend(feature_files)
    
    # Test 4: Summary
    print(f"\n📈 Summary:")
    print(f"  Total feature files found: {len(all_feature_files)}")
    
    if all_feature_files:
        print(f"\n✅ Model training should be able to find these files!")
        print("\n💡 If files aren't showing in the UI:")
        print("   1. Click the '🔄 Refresh Files' button in Model Training tab")
        print("   2. Or switch to File Overview tab and back to Model Training")
    else:
        print(f"\n❌ No feature files found!")
        print("💡 Make sure to extract features first:")
        print("   1. Go to Analysis → Feature Analysis → Feature Extraction")
        print("   2. Select files and extract features")
        print("   3. Then return to Model Training")


if __name__ == "__main__":
    test_file_discovery() 