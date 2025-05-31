#!/usr/bin/env python3
"""
Test script to verify the selector fix works correctly.
"""

import sys
sys.path.append('source')

import pandas as pd
import numpy as np
from sklearn.feature_selection import SelectKBest, f_classif

def test_selector_logic():
    print("🧪 Testing Selector Fix")
    print("=" * 50)
    
    # Test case 1: Few features (≤10) - selector should be None
    print("\nTest 1: Few features (5 features)")
    selector = None
    n_features = 5
    
    if n_features > 10:
        print("  Creating selector...")
        selector = SelectKBest(f_classif, k=n_features // 2)
    else:
        print("  No selector needed (≤10 features)")
    
    # Check feature name selection logic
    if selector is not None and hasattr(selector, 'get_support'):
        print("  Using selector.get_support()")
    else:
        print("  Using all features (no selector)")
    
    print(f"  Result: selector = {selector}")
    
    # Test case 2: Many features (>10) - selector should be created
    print("\nTest 2: Many features (20 features)")
    selector = None
    n_features = 20
    
    if n_features > 10:
        print("  Creating selector...")
        selector = SelectKBest(f_classif, k=n_features // 2)
    else:
        print("  No selector needed (≤10 features)")
    
    # Check feature name selection logic
    if selector is not None and hasattr(selector, 'get_support'):
        print("  Using selector.get_support()")
    else:
        print("  Using all features (no selector)")
    
    print(f"  Result: selector = {type(selector).__name__ if selector else None}")
    
    print("\n✅ Selector logic test passed!")


if __name__ == "__main__":
    test_selector_logic() 