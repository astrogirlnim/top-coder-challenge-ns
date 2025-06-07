#!/usr/bin/env python3
"""
Optimized ML-based reimbursement calculator.
Uses only top 15 features for faster prediction while maintaining accuracy.
"""

import sys
import numpy as np
import pandas as pd
import joblib
import json
import os

def engineer_features(X):
    """Optimized feature engineering - only creates the most important features."""
    df = pd.DataFrame(X, columns=['days', 'miles', 'receipts'])
    
    # Basic derived features
    df['miles_per_day'] = df['miles'] / df['days']
    df['receipts_per_day'] = df['receipts'] / df['days']
    
    # Top importance features (matches exactly what training used)
    df['log_receipts'] = np.log1p(df['receipts'])
    df['receipts_squared'] = df['receipts'] ** 2
    df['days_squared'] = df['days'] ** 2
    df['miles_squared'] = df['miles'] ** 2
    df['days_x_efficiency'] = df['days'] * df['miles_per_day']
    df['log_miles'] = np.log1p(df['miles'])
    df['has_rounding_bug'] = ((df['receipts'] * 100) % 100).isin([49, 99]).astype(int)
    
    # Simple categorical features
    df['is_short_trip'] = (df['days'] <= 3).astype(int)
    df['is_long_trip'] = (df['days'] >= 7).astype(int)
    
    # Additional features to match training set
    df['receipts_per_mile'] = df['receipts'] / (df['miles'] + 1)
    df['overspending_long'] = ((df['days'] >= 7) & (df['receipts_per_day'] > 200)).astype(int)
    df['pseudo_submission_day'] = ((df['days'] + df['miles'].astype(int) + df['receipts'].astype(int)) % 7)
    
    return df

def load_model():
    """Load the optimized model."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        model_path = os.path.join(script_dir, 'best_model_optimized.pkl')
        model = joblib.load(model_path)
        
        config_path = os.path.join(script_dir, 'optimization_config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        return model, config['top_features'], config
        
    except FileNotFoundError as e:
        print(f"Error: Optimized model files not found. Please run create_optimized_model.py first.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading optimized model: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) != 4:
        print("Usage: calculate_reimbursement_optimized.py <trip_duration_days> <miles_traveled> <total_receipts_amount>")
        sys.exit(1)
    
    try:
        days = int(sys.argv[1])
        miles = float(sys.argv[2])
        receipts = float(sys.argv[3])
        
        if days <= 0 or miles < 0 or receipts < 0:
            print("Error: Invalid input values. Days must be positive, miles and receipts must be non-negative.")
            sys.exit(1)
            
    except ValueError:
        print("Error: Invalid input format. Please provide numeric values.")
        sys.exit(1)
    
    # Load optimized model
    model, feature_names, config = load_model()
    
    # Prepare input data
    X_raw = np.array([[days, miles, receipts]])
    
    # Engineer features (only the important ones)
    X_engineered = engineer_features(X_raw)
    
    # Select only the top features used by the optimized model
    X_selected = X_engineered[feature_names]
    
    # Make prediction
    prediction = model.predict(X_selected)[0]
    
    # Output prediction
    print(f"{prediction:.2f}")

if __name__ == "__main__":
    main()
