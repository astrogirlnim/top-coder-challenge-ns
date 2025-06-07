#!/usr/bin/env python3
"""
Extract Linear Model Coefficients that approximate ML performance

Strategy: Train a simple Linear Regression on the same features as the 
Random Forest, then extract the coefficients for dependency-free implementation.
"""

import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
import joblib

# Import our existing functions
from train_model import load_data, engineer_features

def extract_linear_approximation():
    """Extract a linear approximation of the ML model."""
    
    print("🔧 EXTRACTING LINEAR APPROXIMATION OF ML MODEL")
    print("="*60)
    
    # Load the same data used for ML training
    X_raw, y = load_data('../public_cases.json')
    X_engineered = engineer_features(X_raw)
    
    # Use same train/test split as ML model
    X_train, X_test, y_train, y_test = train_test_split(
        X_engineered, y, test_size=0.2, random_state=42
    )
    
    print(f"Training on {len(X_train)} examples with {len(X_engineered.columns)} features")
    
    # Train Linear Regression on the same features
    linear_model = LinearRegression()
    linear_model.fit(X_train, y_train)
    
    # Test performance
    y_pred = linear_model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    
    print(f"Linear Regression MAE: ${mae:.2f}")
    
    # Get coefficients
    coefficients = linear_model.coef_
    intercept = linear_model.intercept_
    feature_names = list(X_engineered.columns)
    
    print(f"Intercept: {intercept:.6f}")
    print(f"\nTop 15 coefficients by absolute value:")
    
    # Sort coefficients by absolute value
    coef_importance = [(name, coef) for name, coef in zip(feature_names, coefficients)]
    coef_importance.sort(key=lambda x: abs(x[1]), reverse=True)
    
    for i, (name, coef) in enumerate(coef_importance[:15]):
        print(f"  {i+1:2d}. {name:25} {coef:12.6f}")
    
    # Save coefficients for pure Python implementation
    linear_config = {
        'intercept': float(intercept),
        'coefficients': {name: float(coef) for name, coef in zip(feature_names, coefficients)},
        'feature_names': feature_names,
        'mae': mae,
        'model_type': 'LinearRegression'
    }
    
    with open('linear_coefficients.json', 'w') as f:
        json.dump(linear_config, f, indent=2)
    
    print(f"\n💾 Saved coefficients to linear_coefficients.json")
    
    # Test on problematic case
    print(f"\n🧪 TESTING ON PROBLEMATIC CASE:")
    problematic_input = np.array([[14, 1056, 2489.69]])  # days, miles, receipts
    problematic_features = engineer_features(problematic_input)
    predicted_value = linear_model.predict(problematic_features)[0]
    
    print(f"Input: 14 days, 1056 miles, $2489.69 receipts")
    print(f"Linear model prediction: ${predicted_value:.2f}")
    print(f"Expected: $1894.16")
    print(f"Error: ${abs(predicted_value - 1894.16):.2f}")
    
    return linear_config

def create_pure_python_from_coefficients(config):
    """Create pure Python implementation using extracted coefficients."""
    
    print(f"\n🐍 CREATING PURE PYTHON IMPLEMENTATION")
    print("="*50)
    
    # Create the feature engineering function
    feature_engineering_code = '''
def engineer_features_exact(days, miles, receipts):
    """Exact feature engineering matching ML training."""
    import math
    
    # Start with basic features
    features = {}
    features['days'] = days
    features['miles'] = miles
    features['receipts'] = receipts
    
    # Derived features
    features['miles_per_day'] = miles / days
    features['receipts_per_day'] = receipts / days
    features['receipts_per_mile'] = receipts / (miles + 1)
    
    # Mathematical transformations
    features['log_receipts'] = math.log1p(receipts)
    features['log_miles'] = math.log1p(miles)
    features['receipts_squared'] = receipts ** 2
    features['days_squared'] = days ** 2
    features['miles_squared'] = miles ** 2
    features['days_x_efficiency'] = days * features['miles_per_day']
    
    # Business logic features
    features['has_rounding_bug'] = int((receipts * 100) % 100 in [49, 99])
    features['is_short_trip'] = int(days <= 3)
    features['is_long_trip'] = int(days >= 7)
    features['is_5_day_trip'] = int(days == 5)
    
    # Efficiency zones (from interviews)
    mpd = features['miles_per_day']
    features['is_super_productivity'] = int(600 <= mpd <= 900)
    features['is_sweet_spot_efficiency'] = int(180 <= mpd <= 220)
    features['is_high_efficiency'] = int(mpd > 400)
    features['is_low_efficiency'] = int(mpd < 50)
    
    # Receipt patterns
    features['is_small_receipts'] = int(receipts < 50)
    features['is_medium_receipts'] = int(600 <= receipts <= 800)
    features['is_high_receipts'] = int(receipts > 1200)
    
    # Trip patterns
    features['is_extreme_miles'] = int(miles > 1000)
    features['is_sweet_spot_length'] = int(3 <= days <= 7)
    
    # Additional derived features (to match training exactly)
    features['efficiency_x_days'] = features['miles_per_day'] * days
    features['receipts_x_days'] = receipts * days
    features['spending_efficiency'] = features['receipts_per_day'] / (features['miles_per_day'] + 1)
    
    return features
'''
    
    # Create the main calculation function
    coefficients = config['coefficients']
    intercept = config['intercept']
    
    calculation_code = f'''
def calculate_reimbursement_linear(days, miles, receipts):
    """Calculate reimbursement using extracted linear coefficients."""
    
    if days <= 0 or miles < 0 or receipts < 0:
        return 0.0
    
    # Engineer features exactly as in training
    features = engineer_features_exact(days, miles, receipts)
    
    # Linear calculation using extracted coefficients
    result = {intercept:.10f}  # Intercept
    
    # Add each feature contribution
'''
    
    # Add coefficient contributions
    for feature_name, coef in coefficients.items():
        if abs(coef) > 1e-10:  # Only include non-zero coefficients
            calculation_code += f'''    result += {coef:.10f} * features.get('{feature_name}', 0)\n'''
    
    calculation_code += '''
    return round(result, 2)
'''
    
    # Combine everything
    full_implementation = f'''#!/usr/bin/env python3
"""
Pure Python Linear Approximation of ML Model
MAE: ${config['mae']:.2f}
Generated from ML coefficients - no external dependencies
"""

import sys
import math

{feature_engineering_code}

{calculation_code}

def main():
    if len(sys.argv) != 4:
        print("Usage: script.py <days> <miles> <receipts>")
        sys.exit(1)
    
    try:
        days = int(sys.argv[1])
        miles = float(sys.argv[2])
        receipts = float(sys.argv[3])
        
        result = calculate_reimbursement_linear(days, miles, receipts)
        print(f"{{result:.2f}}")
        
    except ValueError:
        print("Error: Invalid input format")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    # Save the implementation
    with open('../calculate_reimbursement_ml_linear.py', 'w') as f:
        f.write(full_implementation)
    
    print(f"✅ Created calculate_reimbursement_ml_linear.py")
    print(f"   Expected MAE: ${config['mae']:.2f}")
    
    return full_implementation

def main():
    print("🚀 ML COEFFICIENT EXTRACTION")
    print("="*60)
    
    # Extract linear approximation
    config = extract_linear_approximation()
    
    # Create pure Python implementation
    implementation = create_pure_python_from_coefficients(config)
    
    print(f"\n🎯 SUMMARY:")
    print(f"  Linear approximation MAE: ${config['mae']:.2f}")
    print(f"  Pure Python file: calculate_reimbursement_ml_linear.py")
    print(f"  No external dependencies: ✅")
    
    return config

if __name__ == "__main__":
    main() 