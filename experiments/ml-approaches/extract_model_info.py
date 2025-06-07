#!/usr/bin/env python3
"""
Extract trained model information for pure Python implementation
"""

import sys
import os
sys.path.append('ml-solution')

import joblib
import json
import numpy as np

def extract_model_info():
    """Extract key information from the trained ML model."""
    
    # Load the trained model
    try:
        model = joblib.load('ml-solution/best_model.pkl')
        
        # Load feature names
        with open('ml-solution/feature_names.json', 'r') as f:
            feature_names = json.load(f)
            
        print("🔍 TRAINED MODEL ANALYSIS")
        print("="*40)
        print(f"Model type: {type(model).__name__}")
        print(f"Number of estimators: {model.n_estimators}")
        print(f"Max depth: {model.max_depth}")
        print(f"Features used: {len(feature_names)}")
        
        print(f"\n📊 FEATURE IMPORTANCE:")
        importances = model.feature_importances_
        
        for i, (name, importance) in enumerate(zip(feature_names, importances)):
            if i < 15:  # Top 15 features
                print(f"  {i+1:2d}. {name:25} {importance:.4f}")
        
        # Test on the problematic case
        print(f"\n🧪 TESTING PROBLEMATIC CASE:")
        print("Input: 14 days, 1056 miles, $2489.69 receipts")
        print("Expected: $1894.16")
        
        # We need to reconstruct the input features
        # This would require the full feature engineering pipeline
        print("\n⚠️  Need to test with actual feature engineering...")
        
        return model, feature_names, importances
        
    except Exception as e:
        print(f"Error loading model: {e}")
        return None, None, None

if __name__ == "__main__":
    extract_model_info() 