#!/usr/bin/env python3
"""
Test script to verify model training improvements work correctly.
"""

import sys
import os
sys.path.append('source')

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        from model_training import ModelTraining
        print("✅ ModelTraining imported successfully")
    except Exception as e:
        print(f"❌ Failed to import ModelTraining: {e}")
        return False
    
    try:
        from streamlit_interface_simplified import SimplifiedModelTraining
        print("✅ SimplifiedModelTraining imported successfully")
    except Exception as e:
        print(f"❌ Failed to import SimplifiedModelTraining: {e}")
        return False
    
    try:
        import pandas as pd
        import numpy as np
        from sklearn.ensemble import RandomForestClassifier
        print("✅ All dependencies imported successfully")
    except Exception as e:
        print(f"❌ Failed to import dependencies: {e}")
        return False
    
    return True


def test_data_verification():
    """Test the data verification functionality."""
    print("\nTesting data verification...")
    
    try:
        from model_training import ModelTraining
        import pandas as pd
        
        # Create dummy data
        dummy_data = pd.DataFrame({
            'displacement_landmark_1': [0.1, 0.2, 0.3, 0.4, 0.5],
            'displacement_landmark_10': [0.2, 0.3, 0.4, 0.5, 0.6],
            'quaternion_x': [0.01, 0.02, 0.03, 0.04, 0.05],
            'quaternion_y': [0.01, 0.02, 0.03, 0.04, 0.05],
            'quaternion_z': [0.01, 0.02, 0.03, 0.04, 0.05],
            'quaternion_w': [0.99, 0.98, 0.97, 0.96, 0.95],
            'source_file': ['e1-baseline.csv'] * 5
        })
        
        trainer = ModelTraining()
        
        # Test label creation
        labeled_data = trainer.create_labels_from_filenames(dummy_data)
        
        assert 'subject' in labeled_data.columns, "Subject column not created"
        assert 'test' in labeled_data.columns, "Test column not created"
        assert labeled_data['subject'].iloc[0] == 'e1', "Subject not parsed correctly"
        assert labeled_data['test'].iloc[0] == 'baseline', "Test not parsed correctly"
        
        print("✅ Data verification tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Data verification test failed: {e}")
        return False


def test_feature_separation():
    """Test feature type separation."""
    print("\nTesting feature separation...")
    
    try:
        from model_training import ModelTraining
        import pandas as pd
        
        # Create dummy data with mixed features
        dummy_data = pd.DataFrame({
            'displacement_landmark_1': [0.1] * 5,
            'displacement_landmark_10': [0.2] * 5,
            'displacement_landmark_20': [0.3] * 5,
            'quaternion_x': [0.01] * 5,
            'quaternion_y': [0.02] * 5,
            'quaternion_z': [0.03] * 5,
            'quaternion_w': [0.99] * 5,
            'other_column': ['test'] * 5
        })
        
        trainer = ModelTraining()
        feature_types = trainer.separate_feature_types(dummy_data)
        
        assert len(feature_types['displacement']) == 3, f"Expected 3 displacement features, got {len(feature_types['displacement'])}"
        assert len(feature_types['quaternion']) == 4, f"Expected 4 quaternion features, got {len(feature_types['quaternion'])}"
        
        print("✅ Feature separation tests passed")
        print(f"   - Displacement features: {feature_types['displacement']}")
        print(f"   - Quaternion features: {feature_types['quaternion']}")
        return True
        
    except Exception as e:
        print(f"❌ Feature separation test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing Model Training Improvements")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_data_verification,
        test_feature_separation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All tests passed! Model training improvements are working correctly.")
    else:
        print("❌ Some tests failed. Please check the error messages above.")


if __name__ == "__main__":
    main() 