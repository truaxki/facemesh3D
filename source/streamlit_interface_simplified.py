"""Simplified Model Training Interface

Streamlined interface focused on Random Forest model training with data verification.
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
import matplotlib.pyplot as plt

from model_training import ModelTraining
from session_state_manager import SessionStateManager


class SimplifiedModelTraining:
    """Simplified model training interface focused on Random Forest."""
    
    @staticmethod
    def render():
        """Render the simplified model training interface."""
        st.subheader("🎯 Model Training")
        
        # Add refresh button
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("🔄 Refresh Files", help="Click to refresh the file list"):
                # Clear cached file info
                if 'available_files_info' in st.session_state:
                    del st.session_state['available_files_info']
                st.rerun()
        
        # Initialize trainer
        if 'model_trainer' not in st.session_state:
            st.session_state.model_trainer = ModelTraining()
        
        trainer = st.session_state.model_trainer
        
        # Get available feature files
        available_files = SessionStateManager.get('available_files_info', [])
        feature_files = [f for f in available_files if f['Source'] == 'WRITE' and f['Derived Features'] > 0]
        
        if not feature_files:
            st.warning("⚠️ No feature files found. Please extract features first.")
            st.stop()
        
        # STEP 1: Data Selection (Simplified)
        st.markdown("### 1️⃣ Select Training Data")
        
        # Auto-select all feature files
        selected_files = []
        file_selection_container = st.container()
        
        with file_selection_container:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"Found {len(feature_files)} feature files")
            with col2:
                select_all = st.checkbox("Select All", value=True)
        
        # Simple file list
        for file_info in feature_files:
            if select_all or st.checkbox(file_info['File Name'], 
                                        value=True,
                                        key=f"file_{file_info['File Name']}"):
                selected_files.append(file_info['Path'])
        
        if not selected_files:
            st.stop()
        
        # STEP 2: Data Verification
        st.markdown("### 2️⃣ Data Health Check")
        
        if st.button("🔍 Verify Data", type="secondary"):
            with st.spinner("Checking data quality..."):
                try:
                    # Load data
                    combined_df = trainer.load_extracted_features(selected_files)
                    combined_df = trainer.create_labels_from_filenames(combined_df)
                    
                    # Store in session
                    st.session_state.verified_data = combined_df
                    st.session_state.data_verified = True
                    
                    # Show verification results
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("✅ Total Samples", len(combined_df))
                    
                    with col2:
                        unique_subjects = combined_df['subject'].nunique()
                        st.metric("👥 Subjects", unique_subjects, 
                                 help=f"Found: {', '.join(combined_df['subject'].unique())}")
                    
                    with col3:
                        unique_tests = combined_df['test'].nunique()
                        st.metric("🧪 Test Types", unique_tests,
                                 help=f"Found: {', '.join(combined_df['test'].unique())}")
                    
                    with col4:
                        feature_types = trainer.separate_feature_types(combined_df)
                        total_features = len(feature_types['displacement']) + len(feature_types['quaternion'])
                        st.metric("📊 Features", total_features)
                    
                    # Data balance check
                    st.markdown("**Class Distribution:**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        subject_counts = combined_df['subject'].value_counts()
                        fig, ax = plt.subplots(figsize=(4, 3))
                        subject_counts.plot(kind='bar', ax=ax, color='steelblue')
                        ax.set_title("Samples per Subject")
                        ax.set_xlabel("Subject")
                        ax.set_ylabel("Count")
                        plt.tight_layout()
                        st.pyplot(fig)
                    
                    with col2:
                        test_counts = combined_df['test'].value_counts()
                        fig, ax = plt.subplots(figsize=(4, 3))
                        test_counts.plot(kind='bar', ax=ax, color='darkorange')
                        ax.set_title("Samples per Test")
                        ax.set_xlabel("Test")
                        ax.set_ylabel("Count")
                        plt.tight_layout()
                        st.pyplot(fig)
                    
                    # Feature availability
                    with st.expander("📋 Feature Details", expanded=False):
                        st.write(f"**Displacement Features ({len(feature_types['displacement'])}):**")
                        st.code(", ".join(feature_types['displacement'][:10]) + 
                               ("..." if len(feature_types['displacement']) > 10 else ""))
                        
                        st.write(f"**Quaternion Features ({len(feature_types['quaternion'])}):**")
                        st.code(", ".join(feature_types['quaternion']))
                    
                except Exception as e:
                    st.error(f"❌ Data verification failed: {str(e)}")
                    st.session_state.data_verified = False
        
        # STEP 3: Random Forest Training (Simplified)
        if st.session_state.get('data_verified', False):
            st.markdown("### 3️⃣ Train Random Forest Model")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                feature_set = st.selectbox(
                    "Features",
                    ["combined", "displacement", "quaternion"],
                    help="Which features to use"
                )
            
            with col2:
                target = st.selectbox(
                    "Predict",
                    ["subject", "test"],
                    help="What to predict"
                )
            
            with col3:
                n_trees = st.selectbox(
                    "Trees",
                    [50, 100, 200, 500],
                    index=1,
                    help="Number of trees in forest"
                )
            
            # Single train button
            if st.button("🌳 Train Random Forest", type="primary", use_container_width=True):
                with st.spinner("Training Random Forest..."):
                    try:
                        # Get data
                        data = st.session_state.verified_data
                        
                        # Modify the training to use only Random Forest
                        from sklearn.ensemble import RandomForestClassifier
                        
                        # Use the trainer but override to use only RF
                        original_pipeline = trainer.train_model_pipeline
                        
                        # Temporarily modify to use only RF
                        def rf_only_pipeline(df, model_type, target, test_size, random_state):
                            # Call original but capture internals
                            from sklearn.model_selection import train_test_split
                            from sklearn.preprocessing import StandardScaler, LabelEncoder
                            from sklearn.feature_selection import SelectKBest, f_classif
                            
                            # Get features
                            feature_types = trainer.separate_feature_types(df)
                            
                            if model_type == 'displacement':
                                selected_features = feature_types['displacement']
                            elif model_type == 'quaternion':
                                selected_features = feature_types['quaternion']
                            else:
                                selected_features = feature_types['displacement'] + feature_types['quaternion']
                            
                            # Prepare data
                            X = df[selected_features].fillna(0)
                            y = df[target]
                            
                            # Encode labels
                            if y.dtype == 'object':
                                le = LabelEncoder()
                                y_encoded = le.fit_transform(y)
                                trainer.label_encoders[f"{model_type}_{target}"] = le
                            else:
                                y_encoded = y.values
                            
                            # Split
                            X_train, X_test, y_train, y_test = train_test_split(
                                X, y_encoded, test_size=test_size, random_state=random_state,
                                stratify=y_encoded
                            )
                            
                            # Scale
                            scaler = StandardScaler()
                            X_train_scaled = scaler.fit_transform(X_train)
                            X_test_scaled = scaler.transform(X_test)
                            
                            # Feature selection
                            selector = None  # Initialize selector
                            if X_train_scaled.shape[1] > 10:
                                k = max(5, X_train_scaled.shape[1] // 2)
                                selector = SelectKBest(f_classif, k=k)
                                X_train_selected = selector.fit_transform(X_train_scaled, y_train)
                                X_test_selected = selector.transform(X_test_scaled)
                            else:
                                X_train_selected = X_train_scaled
                                X_test_selected = X_test_scaled
                            
                            # Train ONLY Random Forest
                            rf = RandomForestClassifier(
                                n_estimators=n_trees,
                                random_state=random_state,
                                n_jobs=-1  # Use all cores
                            )
                            
                            rf.fit(X_train_selected, y_train)
                            
                            # Get predictions
                            y_pred = rf.predict(X_test_selected)
                            train_score = rf.score(X_train_selected, y_train)
                            test_score = rf.score(X_test_selected, y_test)
                            
                            # Feature importance
                            if selector is not None and hasattr(selector, 'get_support'):
                                selected_feature_names = [f for f, s in zip(selected_features, selector.get_support()) if s]
                            else:
                                selected_feature_names = selected_features
                            
                            importances = rf.feature_importances_
                            
                            return {
                                'model': rf,
                                'train_accuracy': train_score,
                                'test_accuracy': test_score,
                                'predictions': y_pred,
                                'y_test': y_test,
                                'feature_importances': importances,
                                'feature_names': selected_feature_names,
                                'scaler': scaler,
                                'selector': selector,  # This can be None if no feature selection was done
                                'n_features_used': X_train_selected.shape[1],
                                'n_features_total': len(selected_features)
                            }
                        
                        # Train model
                        results = rf_only_pipeline(
                            data,
                            model_type=feature_set,
                            target=target,
                            test_size=0.2,
                            random_state=42
                        )
                        
                        # Store results
                        st.session_state.rf_results = results
                        st.session_state.rf_config = {
                            'feature_set': feature_set,
                            'target': target,
                            'n_trees': n_trees
                        }
                        
                        # Show results
                        st.success("✅ Training Complete!")
                        
                    except Exception as e:
                        st.error(f"❌ Training failed: {str(e)}")
        
        # STEP 4: Results (Clean and Focused)
        if 'rf_results' in st.session_state:
            st.markdown("### 4️⃣ Results")
            
            results = st.session_state.rf_results
            config = st.session_state.rf_config
            
            # Key metrics in a clean layout
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                accuracy = results['test_accuracy']
                delta = results['train_accuracy'] - results['test_accuracy']
                st.metric("Test Accuracy", f"{accuracy:.1%}", 
                         delta=f"{delta:+.1%} vs train",
                         delta_color="inverse")
            
            with col2:
                st.metric("Features Used", 
                         f"{results['n_features_used']}/{results['n_features_total']}")
            
            with col3:
                st.metric("Model", "Random Forest")
            
            with col4:
                st.metric("Trees", config['n_trees'])
            
            # Feature importance plot
            st.markdown("**📊 Top Important Features**")
            
            # Get top 10 features
            importances = results['feature_importances']
            feature_names = results['feature_names']
            
            # Sort by importance
            indices = np.argsort(importances)[::-1][:10]
            top_features = [feature_names[i] for i in indices]
            top_importances = [importances[i] for i in indices]
            
            # Create horizontal bar plot
            fig, ax = plt.subplots(figsize=(8, 4))
            y_pos = np.arange(len(top_features))
            ax.barh(y_pos, top_importances, color='forestgreen', alpha=0.8)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(top_features)
            ax.set_xlabel('Importance Score')
            ax.set_title(f'Top 10 Features for {config["target"].title()} Prediction')
            ax.grid(axis='x', alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)
            
            # Simple confusion matrix
            from sklearn.metrics import confusion_matrix
            
            cm = confusion_matrix(results['y_test'], results['predictions'])
            
            # Get class names
            if f"{config['feature_set']}_{config['target']}" in trainer.label_encoders:
                encoder = trainer.label_encoders[f"{config['feature_set']}_{config['target']}"]
                if encoder:
                    class_names = encoder.classes_
                else:
                    class_names = [str(i) for i in range(cm.shape[0])]
            else:
                class_names = [str(i) for i in range(cm.shape[0])]
            
            # Create confusion matrix
            fig, ax = plt.subplots(figsize=(6, 5))
            im = ax.imshow(cm, interpolation='nearest', cmap='Blues')
            ax.figure.colorbar(im, ax=ax)
            
            # Labels
            ax.set(xticks=np.arange(cm.shape[1]),
                   yticks=np.arange(cm.shape[0]),
                   xticklabels=class_names,
                   yticklabels=class_names,
                   xlabel='Predicted',
                   ylabel='Actual')
            
            # Add numbers
            for i in range(cm.shape[0]):
                for j in range(cm.shape[1]):
                    text = ax.text(j, i, cm[i, j],
                                 ha="center", va="center",
                                 color="white" if cm[i, j] > cm.max() / 2 else "black")
            
            ax.set_title(f'Confusion Matrix: {config["target"].title()} Prediction')
            plt.tight_layout()
            st.pyplot(fig)
            
            # Quick actions
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Model", type="secondary"):
                    try:
                        save_path = f"models/rf_{config['feature_set']}_{config['target']}"
                        Path(save_path).mkdir(parents=True, exist_ok=True)
                        
                        import joblib
                        joblib.dump(results['model'], f"{save_path}/model.joblib")
                        joblib.dump(results['scaler'], f"{save_path}/scaler.joblib")
                        if results['selector']:
                            joblib.dump(results['selector'], f"{save_path}/selector.joblib")
                        
                        st.success(f"✅ Model saved to {save_path}/")
                    except Exception as e:
                        st.error(f"Failed to save: {e}")
            
            with col2:
                if st.button("🔄 Train New Model", type="secondary"):
                    for key in ['rf_results', 'rf_config', 'verified_data', 'data_verified']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun() 