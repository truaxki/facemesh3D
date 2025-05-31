#!/usr/bin/env python3
"""
Demo: Model Training Pipeline for Facial Microexpression Analysis

This script demonstrates how to use the ModelTraining class to:
1. Load extracted features
2. Perform correlation analysis
3. Train the three model types (displacement, quaternion, combined)
4. Generate confusion matrices
5. Compare model performance

Run this script after extracting features via the Streamlit interface.
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Add source directory to path
sys.path.append('source')

from model_training import ModelTraining

def demo_model_training():
    """Demonstrate the complete model training pipeline."""
    
    print("🎭 Facial Microexpression Model Training Demo")
    print("=" * 50)
    
    # Initialize trainer
    trainer = ModelTraining()
    
    # 1. FIND EXTRACTED FEATURE FILES
    print("\n📁 Looking for extracted feature files...")
    
    write_dir = Path("data/write")
    feature_files = []
    
    # Search for extracted feature files
    for exp_dir in write_dir.glob("*"):
        if exp_dir.is_dir():
            for csv_file in exp_dir.glob("extracted_features_*.csv"):
                feature_files.append(str(csv_file))
    
    if not feature_files:
        print("❌ No extracted feature files found!")
        print("💡 Please run feature extraction first using the Streamlit interface:")
        print("   1. Go to Analysis → Feature Analysis → Feature Extraction")
        print("   2. Extract features from your CSV files")
        print("   3. Then run this demo script")
        return
    
    print(f"✅ Found {len(feature_files)} feature files:")
    for file in feature_files:
        print(f"   📄 {Path(file).name}")
    
    # 2. LOAD AND PREPARE DATA
    print(f"\n📊 Loading and preparing data...")
    
    try:
        # Load extracted features
        combined_df = trainer.load_extracted_features(feature_files)
        
        # Create labels from filenames
        combined_df = trainer.create_labels_from_filenames(combined_df)
        
        print(f"✅ Data loaded successfully!")
        print(f"   📈 Total samples: {len(combined_df)}")
        print(f"   👥 Subjects: {sorted(combined_df['subject'].unique())}")
        print(f"   🧪 Test types: {sorted(combined_df['test'].unique())}")
        
        # Show feature breakdown
        feature_types = trainer.separate_feature_types(combined_df)
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    # 3. CORRELATION ANALYSIS
    print(f"\n🔗 Performing correlation analysis...")
    
    try:
        # Analyze correlation with subject prediction
        all_features = feature_types['displacement'] + feature_types['quaternion']
        
        if all_features:
            correlation_matrix, feature_names, target_correlations = trainer.compute_correlation_matrix(
                combined_df, all_features, 'subject'
            )
            
            # Show top correlations
            sorted_indices = np.argsort(np.abs(target_correlations))[::-1]
            print(f"🏆 Top 5 features correlated with subject:")
            for i in range(min(5, len(sorted_indices))):
                idx = sorted_indices[i]
                print(f"   {i+1}. {feature_names[idx]}: {target_correlations[idx]:.3f}")
            
            # Create correlation plot
            fig = trainer.plot_feature_correlations(
                correlation_matrix, feature_names, target_correlations, "Subject"
            )
            
            # Save plot
            plot_path = "correlation_analysis.png"
            fig.savefig(plot_path, dpi=150, bbox_inches='tight')
            print(f"💾 Correlation plot saved to {plot_path}")
            plt.close(fig)
        
    except Exception as e:
        print(f"⚠️ Correlation analysis failed: {e}")
    
    # 4. TRAIN ALL THREE MODEL TYPES
    print(f"\n🎯 Training all three model types...")
    
    model_types = ["displacement", "quaternion", "combined"]
    targets = ["subject", "test"]
    
    all_results = {}
    
    for target in targets:
        print(f"\n📊 Training models for {target} prediction:")
        
        for model_type in model_types:
            print(f"   🔄 Training {model_type} model...")
            
            try:
                results = trainer.train_model_pipeline(
                    combined_df,
                    model_type=model_type,
                    target=target,
                    test_size=0.2,
                    random_state=42
                )
                
                all_results[f"{model_type}_{target}"] = results
                print(f"   ✅ {model_type}: Best accuracy = {results['best_accuracy']:.3f} ({results['best_model']})")
                
            except Exception as e:
                print(f"   ❌ {model_type} training failed: {e}")
    
    # 5. GENERATE CONFUSION MATRICES
    print(f"\n🎯 Generating confusion matrices...")
    
    for config_name, results in all_results.items():
        print(f"   📊 Creating confusion matrix for {config_name}...")
        
        try:
            # Get best model results
            best_model_name = results['best_model']
            best_results = results['results'][best_model_name]
            cm = best_results['confusion_matrix']
            
            # Get class names
            model_key = f"{results['model_type']}_{results['target']}"
            if trainer.label_encoders[model_key]:
                class_names = trainer.label_encoders[model_key].classes_
            else:
                class_names = [str(i) for i in range(cm.shape[0])]
            
            # Create confusion matrix plot
            fig = trainer.plot_confusion_matrix(
                cm, 
                class_names, 
                title=f"{best_model_name} - {results['model_type'].title()} Model ({results['target'].title()} Prediction)"
            )
            
            # Save plot
            plot_path = f"confusion_matrix_{config_name}_{best_model_name}.png"
            fig.savefig(plot_path, dpi=150, bbox_inches='tight')
            print(f"      💾 Saved to {plot_path}")
            plt.close(fig)
            
        except Exception as e:
            print(f"      ❌ Failed to create confusion matrix: {e}")
    
    # 6. PERFORMANCE SUMMARY
    print(f"\n📈 Model Performance Summary:")
    print("=" * 60)
    
    summary_data = []
    for config_name, results in all_results.items():
        summary_data.append({
            'Configuration': config_name.replace('_', ' → ').title(),
            'Best Model': results['best_model'],
            'Test Accuracy': f"{results['best_accuracy']:.3f}",
            'Features Used': results['selected_feature_count'],
            'Training Samples': results['train_samples']
        })
    
    # Sort by accuracy
    summary_data.sort(key=lambda x: float(x['Test Accuracy']), reverse=True)
    
    for i, data in enumerate(summary_data):
        print(f"{i+1:2d}. {data['Configuration']:<20} | {data['Best Model']:<15} | "
              f"Acc: {data['Test Accuracy']} | Features: {data['Features Used']:2d} | "
              f"Samples: {data['Training Samples']}")
    
    # 7. SAVE MODELS
    print(f"\n💾 Saving trained models...")
    
    try:
        trainer.save_models("models/demo_training")
        print(f"✅ All models saved to models/demo_training/")
    except Exception as e:
        print(f"❌ Error saving models: {e}")
    
    # 8. RECOMMENDATIONS
    print(f"\n💡 Recommendations:")
    
    if all_results:
        # Find best overall configuration
        best_config = max(all_results.items(), key=lambda x: x[1]['best_accuracy'])
        best_name, best_result = best_config
        
        print(f"🏆 Best performing configuration: {best_name}")
        print(f"   Model: {best_result['best_model']}")
        print(f"   Accuracy: {best_result['best_accuracy']:.3f}")
        print(f"   Features: {best_result['selected_feature_count']}")
        
        # Subject vs test prediction comparison
        subject_accuracies = [r['best_accuracy'] for k, r in all_results.items() if 'subject' in k]
        test_accuracies = [r['best_accuracy'] for k, r in all_results.items() if 'test' in k]
        
        if subject_accuracies and test_accuracies:
            avg_subject_acc = np.mean(subject_accuracies)
            avg_test_acc = np.mean(test_accuracies)
            
            if avg_subject_acc > avg_test_acc:
                print(f"📊 Subject prediction performs better on average ({avg_subject_acc:.3f} vs {avg_test_acc:.3f})")
            else:
                print(f"📊 Test prediction performs better on average ({avg_test_acc:.3f} vs {avg_subject_acc:.3f})")
        
        # Feature type recommendations
        displacement_accuracies = [r['best_accuracy'] for k, r in all_results.items() if 'displacement' in k]
        quaternion_accuracies = [r['best_accuracy'] for k, r in all_results.items() if 'quaternion' in k]
        combined_accuracies = [r['best_accuracy'] for k, r in all_results.items() if 'combined' in k]
        
        feature_performance = {
            'Displacement': np.mean(displacement_accuracies) if displacement_accuracies else 0,
            'Quaternion': np.mean(quaternion_accuracies) if quaternion_accuracies else 0,
            'Combined': np.mean(combined_accuracies) if combined_accuracies else 0
        }
        
        best_feature_type = max(feature_performance.items(), key=lambda x: x[1])
        print(f"🎯 Best feature type: {best_feature_type[0]} (avg accuracy: {best_feature_type[1]:.3f})")
    
    print(f"\n🎉 Demo completed! Check the generated plots and model files.")
    print(f"📁 Outputs:")
    print(f"   📊 correlation_analysis.png")
    print(f"   🎯 confusion_matrix_*.png")
    print(f"   🤖 models/demo_training/")


if __name__ == "__main__":
    demo_model_training() 