"""Model Training Module

Provides machine learning training capabilities for facial microexpression analysis.
Supports three model types: displacement-only, quaternion-only, and combined features.
Includes correlation analysis, confusion matrices, and cross-validation.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False
    print("⚠️ Seaborn not available - using matplotlib for visualizations")

from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from sklearn.feature_selection import SelectKBest, f_classif
import joblib
import warnings
warnings.filterwarnings('ignore')
import streamlit as st


class ModelTraining:
    """Comprehensive model training for facial microexpression analysis."""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.feature_selectors = {}
        self.training_history = []
    
    @staticmethod
    def load_extracted_features(file_paths: List[str]) -> pd.DataFrame:
        """
        Load and combine extracted features from multiple CSV files.
        
        Args:
            file_paths: List of paths to extracted feature CSV files
            
        Returns:
            Combined DataFrame with all features and labels
        """
        all_dataframes = []
        
        for file_path in file_paths:
            try:
                df = pd.read_csv(file_path)
                all_dataframes.append(df)
                print(f"✅ Loaded {len(df)} samples from {Path(file_path).name}")
            except Exception as e:
                print(f"❌ Error loading {file_path}: {str(e)}")
        
        if not all_dataframes:
            raise ValueError("No valid feature files could be loaded")
        
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        print(f"📊 Combined dataset: {len(combined_df)} total samples")
        
        return combined_df
    
    @staticmethod
    def create_labels_from_filenames(df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract subject and test labels from source filenames.
        
        Args:
            df: DataFrame with 'source_file' column
            
        Returns:
            DataFrame with added 'subject' and 'test' columns
        """
        if 'source_file' not in df.columns:
            raise ValueError("DataFrame must have 'source_file' column")
        
        subjects = []
        tests = []
        
        for filename in df['source_file']:
            # Remove .csv extension
            name_without_ext = filename.replace('.csv', '')
            
            # Split by dash: e.g., "e4-session1" -> ["e4", "session1"]
            parts = name_without_ext.split('-')
            
            if len(parts) >= 2:
                subject = parts[0]  # e.g., "e4"
                test = '-'.join(parts[1:])  # e.g., "session1" or "session1-part2"
            else:
                # Fallback if no dash found
                subject = name_without_ext
                test = "unknown"
            
            subjects.append(subject)
            tests.append(test)
        
        df_with_labels = df.copy()
        df_with_labels['subject'] = subjects
        df_with_labels['test'] = tests
        
        print(f"📋 Found {len(set(subjects))} unique subjects: {sorted(set(subjects))}")
        print(f"📋 Found {len(set(tests))} unique tests: {sorted(set(tests))}")
        
        return df_with_labels
    
    @staticmethod
    def separate_feature_types(df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Identify and separate different feature types.
        
        Args:
            df: DataFrame with extracted features
            
        Returns:
            Dictionary mapping feature types to column names
        """
        displacement_cols = [col for col in df.columns if col.startswith('displacement_')]
        quaternion_cols = [col for col in df.columns if col.startswith('quaternion_')]
        
        # Identify point feature columns (feat_N_x/y/z pattern)
        point_feature_cols = [col for col in df.columns if 
                             col.startswith('feat_') and ('_x' in col or '_y' in col or '_z' in col)]
        
        feature_types = {
            'displacement': displacement_cols,
            'quaternion': quaternion_cols,
            'point_features': point_feature_cols,
            'metadata': ['source_file', 'frame_index', 'time_seconds', 'subject', 'test']
        }
        
        print(f"🎯 Feature type breakdown:")
        for feat_type, cols in feature_types.items():
            if cols:
                print(f"   {feat_type}: {len(cols)} features")
        
        return feature_types
    
    @staticmethod
    def compute_correlation_matrix(df: pd.DataFrame, feature_cols: List[str], 
                                 target_col: str = 'subject') -> Tuple[np.ndarray, List[str]]:
        """
        Compute correlation matrix between features and target.
        
        Args:
            df: DataFrame with features and target
            feature_cols: List of feature column names
            target_col: Target column name
            
        Returns:
            Correlation matrix and feature names
        """
        # Select only numeric features
        numeric_features = []
        for col in feature_cols:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                numeric_features.append(col)
        
        if not numeric_features:
            raise ValueError("No numeric features found for correlation analysis")
        
        # Create feature matrix
        X = df[numeric_features].fillna(0)  # Fill NaN with 0
        
        # Encode target if it's categorical
        if df[target_col].dtype == 'object':
            le = LabelEncoder()
            y = le.fit_transform(df[target_col])
        else:
            y = df[target_col].values
        
        # Compute correlation matrix
        feature_data = X.values
        target_data = y.reshape(-1, 1)
        
        # Combine features and target for correlation
        combined_data = np.hstack([feature_data, target_data])
        correlation_matrix = np.corrcoef(combined_data.T)
        
        # Extract correlations with target (last column)
        target_correlations = correlation_matrix[:-1, -1]
        
        return correlation_matrix, numeric_features, target_correlations
    
    def train_model_pipeline(self, df: pd.DataFrame, model_type: str = 'combined', 
                           target: str = 'subject', test_size: float = 0.2, 
                           random_state: int = 42) -> Dict[str, Any]:
        """
        Train a complete model pipeline with the specified configuration.
        
        Args:
            df: DataFrame with features and labels
            model_type: 'displacement', 'quaternion', or 'combined'
            target: Target column ('subject' or 'test')
            test_size: Fraction of data for testing
            random_state: Random seed for reproducibility
            
        Returns:
            Training results dictionary
        """
        print(f"🚀 Starting {model_type} model training for {target} prediction...")
        
        # Separate feature types
        feature_types = self.separate_feature_types(df)
        
        # Select features based on model type
        if model_type == 'displacement':
            selected_features = feature_types['displacement']
        elif model_type == 'quaternion':
            selected_features = feature_types['quaternion']
        elif model_type == 'combined':
            selected_features = feature_types['displacement'] + feature_types['quaternion']
        else:
            raise ValueError(f"Invalid model_type: {model_type}")
        
        if not selected_features:
            raise ValueError(f"No features found for model type: {model_type}")
        
        print(f"📊 Using {len(selected_features)} features: {selected_features[:5]}{'...' if len(selected_features) > 5 else ''}")
        
        # Prepare data
        X = df[selected_features].fillna(0)  # Fill NaN with 0
        y = df[target]
        
        # Encode labels if categorical
        if y.dtype == 'object':
            le = LabelEncoder()
            y_encoded = le.fit_transform(y)
            self.label_encoders[f"{model_type}_{target}"] = le
        else:
            y_encoded = y.values
            self.label_encoders[f"{model_type}_{target}"] = None
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=test_size, random_state=random_state, 
            stratify=y_encoded if len(set(y_encoded)) > 1 else None
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers[f"{model_type}_{target}"] = scaler
        
        # Feature selection (keep top 50% most important features)
        if X_train_scaled.shape[1] > 10:  # Only if we have many features
            k = max(5, X_train_scaled.shape[1] // 2)  # Keep at least 5 features
            selector = SelectKBest(f_classif, k=k)
            X_train_selected = selector.fit_transform(X_train_scaled, y_train)
            X_test_selected = selector.transform(X_test_scaled)
            self.feature_selectors[f"{model_type}_{target}"] = selector
            print(f"🔍 Feature selection: {X_train_scaled.shape[1]} → {k} features")
        else:
            X_train_selected = X_train_scaled
            X_test_selected = X_test_scaled
            self.feature_selectors[f"{model_type}_{target}"] = None
        
        # Train multiple models
        models_to_try = {
            'RandomForest': RandomForestClassifier(n_estimators=100, random_state=random_state),
            'LogisticRegression': LogisticRegression(random_state=random_state, max_iter=1000),
            'SVM': SVC(random_state=random_state, probability=True)
        }
        
        results = {}
        best_model = None
        best_score = 0
        
        for model_name, model in models_to_try.items():
            print(f"🔄 Training {model_name}...")
            
            # Train model
            model.fit(X_train_selected, y_train)
            
            # Evaluate
            train_score = model.score(X_train_selected, y_train)
            test_score = model.score(X_test_selected, y_test)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train_selected, y_train, 
                                      cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state))
            
            # Predictions
            y_pred = model.predict(X_test_selected)
            
            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred)
            
            # Classification report
            if self.label_encoders[f"{model_type}_{target}"] is not None:
                target_names = self.label_encoders[f"{model_type}_{target}"].classes_
            else:
                target_names = None
                
            class_report = classification_report(y_test, y_pred, target_names=target_names, output_dict=True)
            
            model_results = {
                'model': model,
                'train_accuracy': train_score,
                'test_accuracy': test_score,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'confusion_matrix': cm,
                'classification_report': class_report,
                'predictions': y_pred,
                'y_test': y_test
            }
            
            results[model_name] = model_results
            
            print(f"   ✅ {model_name}: Test accuracy = {test_score:.3f}, CV = {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
            
            # Track best model
            if test_score > best_score:
                best_score = test_score
                best_model = model_name
        
        # Store best model
        self.models[f"{model_type}_{target}"] = results[best_model]['model']
        
        # Create summary
        training_summary = {
            'model_type': model_type,
            'target': target,
            'best_model': best_model,
            'best_accuracy': best_score,
            'feature_count': len(selected_features),
            'selected_feature_count': X_train_selected.shape[1],
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'results': results,
            'selected_features': selected_features
        }
        
        self.training_history.append(training_summary)
        
        print(f"🎉 Training complete! Best model: {best_model} (accuracy: {best_score:.3f})")
        
        return training_summary
    
    @staticmethod
    def plot_confusion_matrix(cm: np.ndarray, class_names: List[str], 
                            title: str = "Confusion Matrix") -> plt.Figure:
        """
        Create a confusion matrix plot.
        
        Args:
            cm: Confusion matrix
            class_names: List of class names
            title: Plot title
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Create heatmap
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=class_names, yticklabels=class_names, ax=ax)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylabel('True Label', fontsize=12)
        ax.set_xlabel('Predicted Label', fontsize=12)
        
        # Add accuracy information
        accuracy = np.trace(cm) / np.sum(cm)
        ax.text(0.5, -0.1, f'Overall Accuracy: {accuracy:.3f}', 
               transform=ax.transAxes, ha='center', fontsize=10)
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def plot_feature_correlations(correlation_matrix: np.ndarray, feature_names: List[str],
                                target_correlations: np.ndarray, target_name: str = "Target") -> plt.Figure:
        """
        Create correlation analysis plots.
        
        Args:
            correlation_matrix: Full correlation matrix
            feature_names: List of feature names
            target_correlations: Correlations with target variable
            target_name: Name of target variable
            
        Returns:
            Matplotlib figure with correlation plots
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot 1: Feature correlations with target
        sorted_indices = np.argsort(np.abs(target_correlations))[::-1]
        top_features = min(20, len(feature_names))  # Show top 20 features
        
        top_indices = sorted_indices[:top_features]
        top_correlations = target_correlations[top_indices]
        top_names = [feature_names[i] for i in top_indices]
        
        # Truncate long feature names
        display_names = []
        for name in top_names:
            if len(name) > 20:
                display_names.append(name[:17] + "...")
            else:
                display_names.append(name)
        
        colors = ['red' if corr < 0 else 'blue' for corr in top_correlations]
        
        bars = ax1.barh(range(len(top_correlations)), top_correlations, color=colors, alpha=0.7)
        ax1.set_yticks(range(len(top_correlations)))
        ax1.set_yticklabels(display_names, fontsize=8)
        ax1.set_xlabel(f'Correlation with {target_name}', fontsize=10)
        ax1.set_title(f'Top {top_features} Feature Correlations', fontsize=12, fontweight='bold')
        ax1.axvline(x=0, color='black', linestyle='-', alpha=0.3)
        ax1.grid(True, alpha=0.3)
        
        # Add correlation values on bars
        for i, (bar, corr) in enumerate(zip(bars, top_correlations)):
            ax1.text(corr + 0.01 if corr >= 0 else corr - 0.01, i, f'{corr:.3f}', 
                    va='center', ha='left' if corr >= 0 else 'right', fontsize=8)
        
        # Plot 2: Correlation matrix heatmap (subset for readability)
        if len(feature_names) > 20:
            # Show correlation matrix for top features only
            subset_matrix = correlation_matrix[np.ix_(top_indices, top_indices)]
            subset_names = display_names
        else:
            subset_matrix = correlation_matrix[:-1, :-1]  # Exclude target column
            subset_names = display_names if len(feature_names) <= 20 else [f"F{i}" for i in range(len(feature_names))]
        
        im = ax2.imshow(subset_matrix, cmap='RdBu_r', vmin=-1, vmax=1)
        ax2.set_xticks(range(len(subset_names)))
        ax2.set_yticks(range(len(subset_names)))
        ax2.set_xticklabels(subset_names, rotation=45, ha='right', fontsize=8)
        ax2.set_yticklabels(subset_names, fontsize=8)
        ax2.set_title('Feature Correlation Matrix', fontsize=12, fontweight='bold')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax2, shrink=0.8)
        cbar.set_label('Correlation Coefficient', fontsize=10)
        
        plt.tight_layout()
        return fig
    
    def save_models(self, save_dir: str = "models"):
        """
        Save trained models and preprocessing objects.
        
        Args:
            save_dir: Directory to save models
        """
        save_path = Path(save_dir)
        save_path.mkdir(exist_ok=True)
        
        # Save models
        for model_name, model in self.models.items():
            model_file = save_path / f"{model_name}_model.joblib"
            joblib.dump(model, model_file)
            print(f"💾 Saved {model_name} model to {model_file}")
        
        # Save scalers
        for scaler_name, scaler in self.scalers.items():
            scaler_file = save_path / f"{scaler_name}_scaler.joblib"
            joblib.dump(scaler, scaler_file)
        
        # Save label encoders
        for encoder_name, encoder in self.label_encoders.items():
            if encoder is not None:
                encoder_file = save_path / f"{encoder_name}_encoder.joblib"
                joblib.dump(encoder, encoder_file)
        
        # Save feature selectors
        for selector_name, selector in self.feature_selectors.items():
            if selector is not None:
                selector_file = save_path / f"{selector_name}_selector.joblib"
                joblib.dump(selector, selector_file)
        
        print(f"✅ All models saved to {save_path}")
    
    def load_models(self, save_dir: str = "models"):
        """
        Load trained models and preprocessing objects.
        
        Args:
            save_dir: Directory containing saved models
        """
        save_path = Path(save_dir)
        
        if not save_path.exists():
            raise ValueError(f"Model directory {save_path} does not exist")
        
        # Load all .joblib files
        for file_path in save_path.glob("*.joblib"):
            name = file_path.stem
            obj = joblib.load(file_path)
            
            if "_model" in name:
                self.models[name.replace("_model", "")] = obj
            elif "_scaler" in name:
                self.scalers[name.replace("_scaler", "")] = obj
            elif "_encoder" in name:
                self.label_encoders[name.replace("_encoder", "")] = obj
            elif "_selector" in name:
                self.feature_selectors[name.replace("_selector", "")] = obj
        
        print(f"✅ Loaded models from {save_path}")
        print(f"   Models: {list(self.models.keys())}")
        print(f"   Scalers: {list(self.scalers.keys())}") 