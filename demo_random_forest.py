#!/usr/bin/env python3
"""
Demo: Random Forest Training for Facial Microexpression Analysis

Quick demonstration of Random Forest model training with data verification.
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, confusion_matrix
import matplotlib.pyplot as plt

# Add source directory to path
sys.path.append('source')

from model_training import ModelTraining


def quick_data_check(df):
    """Quick verification of data quality."""
    print("\n📊 DATA VERIFICATION:")
    print("=" * 50)
    
    # Basic info
    print(f"Total samples: {len(df)}")
    print(f"Subjects: {df['subject'].unique()}")
    print(f"Tests: {df['test'].unique()}")
    
    # Feature types
    displacement_features = [col for col in df.columns if col.startswith('displacement_')]
    quaternion_features = [col for col in df.columns if col.startswith('quaternion_')]
    
    print(f"\nFeatures:")
    print(f"  - Displacement: {len(displacement_features)}")
    print(f"  - Quaternion: {len(quaternion_features)}")
    print(f"  - Total: {len(displacement_features) + len(quaternion_features)}")
    
    # Class balance
    print(f"\nClass balance:")
    print("Subjects:")
    print(df['subject'].value_counts())
    print("\nTests:")
    print(df['test'].value_counts())
    
    # Missing values
    missing = df.isnull().sum().sum()
    print(f"\nMissing values: {missing}")
    
    return displacement_features, quaternion_features


def train_random_forest(X, y, feature_names, target_name, n_trees=100):
    """Train a Random Forest model and show results."""
    print(f"\n🌳 TRAINING RANDOM FOREST for {target_name}")
    print("=" * 50)
    
    # Encode labels if needed
    if y.dtype == 'object':
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        class_names = le.classes_
    else:
        y_encoded = y
        class_names = None
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest
    rf = RandomForestClassifier(n_estimators=n_trees, random_state=42, n_jobs=-1)
    rf.fit(X_train_scaled, y_train)
    
    # Evaluate
    train_acc = rf.score(X_train_scaled, y_train)
    test_acc = rf.score(X_test_scaled, y_test)
    y_pred = rf.predict(X_test_scaled)
    
    print(f"Train accuracy: {train_acc:.3f}")
    print(f"Test accuracy: {test_acc:.3f}")
    print(f"Overfitting: {train_acc - test_acc:.3f}")
    
    # Feature importance
    print(f"\nTop 10 Important Features:")
    importances = rf.feature_importances_
    indices = np.argsort(importances)[::-1][:10]
    
    for i, idx in enumerate(indices):
        print(f"{i+1:2d}. {feature_names[idx]:30s} {importances[idx]:.4f}")
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    if class_names is not None:
        print(f"\nConfusion Matrix:")
        print(f"{'':10s}", end='')
        for name in class_names:
            print(f"{name:10s}", end='')
        print()
        
        for i, name in enumerate(class_names):
            print(f"{name:10s}", end='')
            for j in range(len(class_names)):
                print(f"{cm[i,j]:10d}", end='')
            print()
    
    return rf, test_acc, importances, feature_names


def main():
    """Run the Random Forest demo."""
    print("🎯 Random Forest Demo for Facial Microexpression Analysis")
    print("=" * 60)
    
    # Initialize trainer
    trainer = ModelTraining()
    
    # Find feature files
    write_dir = Path("data/write")
    feature_files = []
    
    for exp_dir in write_dir.glob("*"):
        if exp_dir.is_dir():
            for csv_file in exp_dir.glob("extracted_features_*.csv"):
                feature_files.append(str(csv_file))
    
    if not feature_files:
        print("❌ No extracted feature files found!")
        print("Please run feature extraction first.")
        return
    
    print(f"✅ Found {len(feature_files)} feature files")
    
    # Load data
    try:
        combined_df = trainer.load_extracted_features(feature_files)
        combined_df = trainer.create_labels_from_filenames(combined_df)
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    # Data verification
    displacement_features, quaternion_features = quick_data_check(combined_df)
    
    # Train models for different feature sets
    results = {}
    
    # 1. Combined features
    print("\n" + "="*60)
    print("COMBINED FEATURES (Displacement + Quaternion)")
    all_features = displacement_features + quaternion_features
    if all_features:
        X = combined_df[all_features].fillna(0)
        
        # Subject prediction
        rf_subject, acc_subject, _, _ = train_random_forest(
            X, combined_df['subject'], all_features, "Subject Prediction"
        )
        results['combined_subject'] = acc_subject
        
        # Test prediction
        rf_test, acc_test, _, _ = train_random_forest(
            X, combined_df['test'], all_features, "Test Prediction"
        )
        results['combined_test'] = acc_test
    
    # 2. Displacement only
    if displacement_features:
        print("\n" + "="*60)
        print("DISPLACEMENT FEATURES ONLY")
        X = combined_df[displacement_features].fillna(0)
        
        rf_disp, acc_disp, _, _ = train_random_forest(
            X, combined_df['subject'], displacement_features, "Subject Prediction (Displacement)"
        )
        results['displacement_subject'] = acc_disp
    
    # 3. Quaternion only
    if quaternion_features:
        print("\n" + "="*60)
        print("QUATERNION FEATURES ONLY")
        X = combined_df[quaternion_features].fillna(0)
        
        rf_quat, acc_quat, _, _ = train_random_forest(
            X, combined_df['subject'], quaternion_features, "Subject Prediction (Quaternion)"
        )
        results['quaternion_subject'] = acc_quat
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY OF RESULTS")
    print("="*60)
    
    for config, accuracy in results.items():
        print(f"{config:25s}: {accuracy:.3f}")
    
    print("\n💡 RECOMMENDATIONS:")
    best_config = max(results.items(), key=lambda x: x[1])
    print(f"Best configuration: {best_config[0]} (accuracy: {best_config[1]:.3f})")
    
    if 'combined' in best_config[0]:
        print("✅ Combined features work best - use both displacement and quaternion")
    elif 'displacement' in best_config[0]:
        print("✅ Displacement features are most informative")
    else:
        print("✅ Quaternion features capture the key patterns")
    
    print("\n🎉 Demo completed!")


if __name__ == "__main__":
    main() 