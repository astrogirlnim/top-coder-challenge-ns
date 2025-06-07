#!/usr/bin/env python3
"""
Machine Learning-based reimbursement calculator.

This script loads a pre-trained ML model and uses it to predict reimbursement amounts
based on trip_duration_days, miles_traveled, and total_receipts_amount.

The model has been trained on interview insights and patterns from the legacy system.
"""

import sys
import numpy as np
import pandas as pd
import joblib
import json
import os

def engineer_features(X):
    """
    Engineer features based on employee interview insights.
    This must match the feature engineering used during training.
    """
    df = pd.DataFrame(X, columns=['days', 'miles', 'receipts'])
    
    # Basic derived features
    df['miles_per_day'] = df['miles'] / df['days']
    df['receipts_per_day'] = df['receipts'] / df['days']
    
    # Interview-driven feature engineering
    
    # Kevin's efficiency zones (key insight from interviews)
    df['is_super_productivity'] = ((df['miles_per_day'] >= 600) & (df['miles_per_day'] <= 900)).astype(int)
    df['is_sweet_spot_efficiency'] = ((df['miles_per_day'] >= 180) & (df['miles_per_day'] <= 220)).astype(int)
    df['is_high_efficiency'] = (df['miles_per_day'] > 400).astype(int)
    df['is_extreme_miles'] = (df['miles_per_day'] > 1000).astype(int)
    df['is_low_efficiency'] = (df['miles_per_day'] < 100).astype(int)
    
    # Trip length patterns (Jennifer's observations)
    df['is_5_day_trip'] = (df['days'] == 5).astype(int)
    df['is_sweet_spot_length'] = ((df['days'] >= 4) & (df['days'] <= 6)).astype(int)
    df['is_short_trip'] = (df['days'] <= 3).astype(int)
    df['is_long_trip'] = (df['days'] >= 7).astype(int)
    
    # Receipt amount patterns (Lisa's observations)
    df['is_small_receipts'] = (df['receipts'] < 50).astype(int)
    df['is_very_small_receipts'] = (df['receipts'] < 30).astype(int)
    df['is_medium_receipts'] = ((df['receipts'] >= 600) & (df['receipts'] <= 800)).astype(int)
    df['is_high_receipts'] = (df['receipts'] > 1200).astype(int)
    df['is_very_high_receipts'] = (df['receipts'] > 2000).astype(int)
    
    # Spending patterns by trip length (Kevin's thresholds)
    df['overspending_short'] = ((df['days'] <= 3) & (df['receipts_per_day'] > 75)).astype(int)
    df['overspending_medium'] = ((df['days'] >= 4) & (df['days'] <= 6) & (df['receipts_per_day'] > 120)).astype(int)
    df['overspending_long'] = ((df['days'] >= 7) & (df['receipts_per_day'] > 90)).astype(int)
    
    # Rounding bug feature (Lisa's observation)
    df['has_rounding_bug'] = ((df['receipts'] * 100) % 100).isin([49, 99]).astype(int)
    
    # Calendar effect proxy (Kevin's timing theory)
    # Use receipt amount as pseudo-random seed for "submission day"
    df['pseudo_submission_day'] = (df['receipts'] * 100).astype(int) % 7
    df['is_tuesday_submission'] = (df['pseudo_submission_day'] == 1).astype(int)
    df['is_friday_submission'] = (df['pseudo_submission_day'] == 4).astype(int)
    
    # Interaction features (Kevin emphasized these)
    df['efficiency_x_receipts'] = df['miles_per_day'] * df['receipts_per_day']
    df['days_x_efficiency'] = df['days'] * df['miles_per_day']
    df['total_productivity'] = df['miles'] * df['receipts'] / (df['days'] ** 2)
    
    # Polynomial features for potential non-linear relationships
    df['miles_squared'] = df['miles'] ** 2
    df['receipts_squared'] = df['receipts'] ** 2
    df['days_squared'] = df['days'] ** 2
    df['miles_per_day_squared'] = df['miles_per_day'] ** 2
    
    # Log features for potentially exponential relationships
    df['log_miles'] = np.log1p(df['miles'])
    df['log_receipts'] = np.log1p(df['receipts'])
    df['log_miles_per_day'] = np.log1p(df['miles_per_day'])
    
    # Business logic zones (combinations that trigger bonuses/penalties)
    df['ideal_combo'] = ((df['days'] == 5) & (df['miles_per_day'] >= 180) & (df['receipts_per_day'] <= 100)).astype(int)
    df['vacation_penalty'] = ((df['days'] >= 8) & (df['receipts_per_day'] > 150)).astype(int)
    df['efficiency_bonus'] = ((df['miles_per_day'] > 200) & (df['receipts_per_day'] < 100)).astype(int)
    
    return df

def load_model():
    """Load the trained model and associated components."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        # Load model
        model_path = os.path.join(script_dir, 'best_model.pkl')
        model = joblib.load(model_path)
        
        # Load feature names
        feature_names_path = os.path.join(script_dir, 'feature_names.json')
        with open(feature_names_path, 'r') as f:
            feature_names = json.load(f)
            
        # Load model metadata
        metadata_path = os.path.join(script_dir, 'model_metadata.json')
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
            
        return model, feature_names, metadata
        
    except FileNotFoundError as e:
        print(f"Error: Model files not found. Please run train_model.py first.", file=sys.stderr)
        print(f"Missing file: {e.filename}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading model: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) != 4:
        print("Usage: calculate_reimbursement.py <trip_duration_days> <miles_traveled> <total_receipts_amount>")
        sys.exit(1)
    
    try:
        days = int(sys.argv[1])
        miles = float(sys.argv[2])
        receipts = float(sys.argv[3])
        
        # Validate inputs
        if days <= 0 or miles < 0 or receipts < 0:
            print("Error: Invalid input values. Days must be positive, miles and receipts must be non-negative.")
            sys.exit(1)
            
    except ValueError:
        print("Error: Invalid input format. Please provide numeric values.")
        sys.exit(1)
    
    # Load model
    model, feature_names, metadata = load_model()
    
    # Prepare input data
    X_raw = np.array([[days, miles, receipts]])
    
    # Engineer features
    X_engineered = engineer_features(X_raw)
    
    # Ensure features are in the same order as training
    X_engineered = X_engineered[feature_names]
    
    # Make prediction
    prediction = model.predict(X_engineered)[0]
    
    # Output prediction (matching the format expected by eval.sh)
    print(f"{prediction:.2f}")

if __name__ == "__main__":
    main() 