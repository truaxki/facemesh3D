# 🎯 Model Training Guide

Comprehensive guide for training machine learning models on facial microexpression data with your feature extraction system.

## 📋 Overview

Your model training pipeline supports **three distinct model types** and **two prediction targets**, giving you multiple approaches to analyze facial microexpression data:

### 🎯 Model Types
1. **Displacement Only** - Frame-to-frame movement patterns
2. **Quaternion Only** - Head rotation/orientation patterns  
3. **Combined** - Both displacement + quaternion features

### 🎯 Prediction Targets
1. **Subject Prediction** - Identify which person (e.g., "e1", "e4", "e6")
2. **Test Prediction** - Classify test type (e.g., "baseline", "session1", "session2")

## 🚀 Quick Start

### Method 1: Streamlit Interface (Recommended)
1. **Extract Features** (if not done):
   ```
   Go to: Analysis → Feature Analysis → Feature Extraction
   Select files → Configure features → Extract
   ```

2. **Train Models**:
   ```
   Go to: Analysis → Model Training
   Select feature files → Run correlation analysis → Train models
   ```

### Method 2: Command Line Demo
```bash
python demo_model_training.py
```

## 🔗 Correlation Analysis

### Purpose
- **Identify important features** for prediction
- **Visualize relationships** between features and targets
- **Guide feature selection** for model training

### Correlation Types
- **Feature-to-Target**: Which features best predict subjects/tests?
- **Feature-to-Feature**: Which features are redundant/complementary?

### Interpretation
- **High correlation (|r| > 0.7)**: Strong predictive relationship
- **Moderate correlation (0.3 < |r| < 0.7)**: Useful feature
- **Low correlation (|r| < 0.3)**: Weak predictive power

## 🎯 Confusion Matrix Analysis

### What They Show
- **True vs Predicted** classifications
- **Per-class accuracy** (diagonal elements)
- **Common misclassifications** (off-diagonal elements)

### Key Metrics
- **Overall Accuracy**: Correct predictions / Total predictions
- **Per-class Precision**: True positives / (True positives + False positives)
- **Per-class Recall**: True positives / (True positives + False negatives)

### Example Interpretation
```
Subject Confusion Matrix:
     e1  e4  e6
e1   45   2   1    # e1 mostly correctly classified
e4    3  42   3    # e4 sometimes confused with e6
e6    1   5  44    # e6 sometimes confused with e4

Accuracy: 89.1%
```

## 🤖 Model Training Options

### 1. Individual Model Training

**Configure and train one specific model:**

```python
from model_training import ModelTraining

trainer = ModelTraining()
results = trainer.train_model_pipeline(
    data,
    model_type='combined',      # 'displacement', 'quaternion', 'combined'
    target='subject',           # 'subject', 'test'
    test_size=0.2,             # 20% for testing
    random_state=42            # Reproducible results
)
```

### 2. Batch Training

**Train all combinations automatically:**

- 3 model types × 2 targets = **6 total configurations**
- Automatic comparison and ranking
- Identifies best performing setup

### 3. Cross-Validation

**All models use 5-fold stratified cross-validation:**
- Data split into 5 equal parts
- Train on 4 parts, test on 1 part
- Repeat 5 times with different test parts
- Average results for robust performance estimates

## 📊 Model Performance Comparison

### Expected Performance Patterns

**Subject Prediction** (typically easier):
- **Combined models**: Usually best (0.85-0.95 accuracy)
- **Displacement models**: Good baseline (0.75-0.90 accuracy)
- **Quaternion models**: Moderate (0.60-0.80 accuracy)

**Test Prediction** (typically harder):
- **Combined models**: Best overall (0.70-0.85 accuracy)
- **Displacement models**: Task-dependent (0.60-0.80 accuracy)
- **Quaternion models**: Lower but informative (0.50-0.70 accuracy)

### Factors Affecting Performance

1. **Data Quality**:
   - More frames per test → Better performance
   - Consistent experimental conditions → Better performance
   - Clear differences between classes → Better performance

2. **Feature Engineering**:
   - Raw displacement: Baseline performance
   - Head-corrected displacement: Usually better
   - Combined features: Often best

3. **Class Balance**:
   - Equal samples per subject/test → Better performance
   - Imbalanced data → May favor majority classes

## 🎯 Model Selection Guidelines

### Choose Displacement Models When:
- ✅ Focus on facial movement patterns
- ✅ Head movement is minimal or corrected
- ✅ Interested in microexpression dynamics
- ✅ Need interpretable features

### Choose Quaternion Models When:
- ✅ Head movement is significant
- ✅ Orientation patterns are important
- ✅ Working with unconstrained recordings
- ✅ Studying head pose relationships

### Choose Combined Models When:
- ✅ Want maximum performance
- ✅ Have sufficient training data
- ✅ Both movement and orientation matter
- ✅ Model interpretability is less critical

## 📈 Performance Optimization

### 1. Feature Selection
```python
# Automatic feature selection (current default)
# Keeps top 50% most important features
# Minimum 5 features retained

# Custom feature selection
from sklearn.feature_selection import SelectKBest, f_classif
selector = SelectKBest(f_classif, k=20)  # Keep top 20 features
```

### 2. Preprocessing Options
```python
# Current pipeline:
# 1. Fill missing values with 0
# 2. Standard scaling (mean=0, std=1)
# 3. Feature selection
# 4. Model training

# Optional enhancements:
# - Outlier detection/removal
# - Principal Component Analysis (PCA)
# - Feature engineering (ratios, differences)
```

### 3. Model Hyperparameters
```python
# Current models with default parameters:
'RandomForest': RandomForestClassifier(n_estimators=100)
'LogisticRegression': LogisticRegression(max_iter=1000)
'SVM': SVC(probability=True)

# For better performance, consider hyperparameter tuning:
# - Grid search over parameters
# - Random search for efficiency
# - Bayesian optimization for advanced tuning
```

## 🔍 Results Interpretation

### 1. Training vs Test Accuracy
- **Similar scores**: Good generalization
- **Training >> Test**: Overfitting (reduce model complexity)
- **Both low**: Underfitting (increase model complexity)

### 2. Cross-Validation Scores
- **Low std**: Consistent performance across folds
- **High std**: Performance varies with data split
- **Mean close to test**: Good validation strategy

### 3. Confusion Matrix Patterns
- **Diagonal dominance**: Good overall performance
- **Specific confusions**: Systematic classification errors
- **Random scatter**: Poor feature discrimination

## 💾 Model Persistence

### Saving Models
```python
# Automatic saving includes:
# - Trained models (.joblib)
# - Feature scalers (.joblib)
# - Label encoders (.joblib)
# - Feature selectors (.joblib)

trainer.save_models("models/experiment_name")
```

### Loading Models
```python
# Load for prediction on new data
trainer.load_models("models/experiment_name")

# Use for inference
predictions = trainer.predict(new_features)
```

## 🚀 Advanced Workflows

### 1. Time-Series Cross-Validation
```python
# For temporal data, consider time-aware splits
from sklearn.model_selection import TimeSeriesSplit

cv = TimeSeriesSplit(n_splits=5)
scores = cross_val_score(model, X, y, cv=cv)
```

### 2. Subject-Specific Models
```python
# Train separate models for each subject
for subject in unique_subjects:
    subject_data = data[data['subject'] == subject]
    model = train_model_pipeline(subject_data, target='test')
    save_model(f"models/subject_{subject}")
```

### 3. Ensemble Methods
```python
# Combine multiple model types for better performance
displacement_pred = displacement_model.predict_proba(X_disp)
quaternion_pred = quaternion_model.predict_proba(X_quat)

# Weighted average
ensemble_pred = 0.6 * displacement_pred + 0.4 * quaternion_pred
final_pred = np.argmax(ensemble_pred, axis=1)
```

## 🎯 Troubleshooting

### Common Issues

**Low Accuracy (< 0.6)**:
- Check data quality and preprocessing
- Verify feature extraction worked correctly
- Consider different model types
- Check for class imbalance

**Overfitting (Train >> Test)**:
- Reduce feature count
- Increase training data
- Use simpler models
- Add regularization

**Memory Issues**:
- Process data in batches
- Use feature selection
- Consider dimensionality reduction
- Use more efficient models

**Inconsistent Results**:
- Fix random seeds
- Use stratified splits
- Check for data leakage
- Verify preprocessing consistency

### Getting Help

1. **Check feature extraction**: Ensure derived features were created properly
2. **Verify data format**: Confirm CSV structure and column names
3. **Review error messages**: Often indicate specific issues
4. **Start simple**: Begin with single model type before batch training

## 📚 References

- **Scikit-learn Documentation**: https://scikit-learn.org/
- **Confusion Matrix Guide**: https://en.wikipedia.org/wiki/Confusion_matrix
- **Cross-Validation**: https://scikit-learn.org/stable/modules/cross_validation.html
- **Feature Selection**: https://scikit-learn.org/stable/modules/feature_selection.html 