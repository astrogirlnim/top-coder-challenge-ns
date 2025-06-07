#!/usr/bin/env python3
"""
Machine Learning approach to reverse engineer the black-box reimbursement system.

This script trains multiple models on the public cases to predict reimbursement amounts
from trip_duration_days, miles_traveled, and total_receipts_amount.

Based on extensive interview analysis, we engineer features that capture the complex
business logic patterns observed by employees.
"""

import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(filepath):
    """Load and parse the JSON test cases."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Extract features and targets
    features = []
    targets = []
    
    for case in data:
        inp = case['input']
        features.append([
            inp['trip_duration_days'],
            inp['miles_traveled'],
            inp['total_receipts_amount']
        ])
        targets.append(case['expected_output'])
    
    return np.array(features), np.array(targets)

def engineer_features(X):
    """
    Engineer features based on employee interview insights.
    
    Key patterns identified:
    - Miles per day (efficiency) is crucial
    - Receipts per day matters for spending patterns  
    - Sweet spots around 5-day trips, 180-220 miles/day
    - Super productivity zone 600-900 miles/day
    - Various interaction effects between variables
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

def train_models(X_train, y_train, X_test, y_test):
    """Train multiple models and return the best performer."""
    
    models = {
        'RandomForest': RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        ),
        'GradientBoosting': GradientBoostingRegressor(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.1,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        ),
        'Ridge': Ridge(alpha=1.0),
        'LinearRegression': LinearRegression()
    }
    
    results = {}
    trained_models = {}
    
    print("Training models...")
    print("=" * 50)
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        # Train model
        model.fit(X_train, y_train)
        trained_models[name] = model
        
        # Make predictions
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)
        
        # Calculate metrics
        train_mae = mean_absolute_error(y_train, train_pred)
        test_mae = mean_absolute_error(y_test, test_pred)
        train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
        test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
        train_r2 = r2_score(y_train, train_pred)
        test_r2 = r2_score(y_test, test_pred)
        
        # Cross-validation score
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='neg_mean_absolute_error')
        cv_mae = -cv_scores.mean()
        cv_std = cv_scores.std()
        
        results[name] = {
            'train_mae': train_mae,
            'test_mae': test_mae,
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'cv_mae': cv_mae,
            'cv_std': cv_std,
            'predictions': test_pred
        }
        
        print(f"  Train MAE: ${train_mae:.2f}")
        print(f"  Test MAE:  ${test_mae:.2f}")
        print(f"  Test R²:   {test_r2:.4f}")
        print(f"  CV MAE:    ${cv_mae:.2f} (±${cv_std:.2f})")
    
    return trained_models, results

def analyze_feature_importance(model, feature_names):
    """Analyze feature importance for tree-based models."""
    if hasattr(model, 'feature_importances_'):
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nTop 20 Most Important Features:")
        print("=" * 40)
        for _, row in importance_df.head(20).iterrows():
            print(f"{row['feature']:25} {row['importance']:.4f}")
        
        return importance_df
    return None

def calculate_exact_matches(y_true, y_pred, tolerance=0.01):
    """Calculate number of exact matches within tolerance."""
    return np.sum(np.abs(y_true - y_pred) <= tolerance)

def main():
    print("🤖 Machine Learning Approach to Black-Box Reimbursement System")
    print("=" * 65)
    
    # Load data
    print("\n📊 Loading training data from public_cases.json...")
    X_raw, y = load_data('../public_cases.json')
    print(f"Loaded {len(X_raw)} training examples")
    
    # Engineer features
    print("\n🔧 Engineering features based on interview insights...")
    X_engineered = engineer_features(X_raw)
    print(f"Created {X_engineered.shape[1]} features from {X_raw.shape[1]} original inputs")
    
    # Display feature summary
    print("\nEngineered features:")
    for col in X_engineered.columns:
        if col not in ['days', 'miles', 'receipts']:
            unique_vals = X_engineered[col].nunique()
            print(f"  {col:25} (unique values: {unique_vals})")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_engineered, y, test_size=0.2, random_state=42, stratify=None
    )
    
    print(f"\nTrain set: {len(X_train)} examples")
    print(f"Test set:  {len(X_test)} examples")
    
    # Scale features for linear models (but keep tree models unscaled)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train models with scaled features for linear models
    models, results = train_models(X_train, y_train, X_test, y_test)
    
    # Find best model
    best_model_name = min(results.keys(), key=lambda k: results[k]['test_mae'])
    best_model = models[best_model_name]
    best_results = results[best_model_name]
    
    print(f"\n🏆 Best Model: {best_model_name}")
    print(f"   Test MAE: ${best_results['test_mae']:.2f}")
    print(f"   Test R²:  {best_results['test_r2']:.4f}")
    
    # Calculate exact matches
    exact_matches = calculate_exact_matches(y_test, best_results['predictions'])
    close_matches = calculate_exact_matches(y_test, best_results['predictions'], tolerance=1.0)
    
    print(f"   Exact matches (±$0.01): {exact_matches} ({exact_matches/len(y_test)*100:.1f}%)")
    print(f"   Close matches (±$1.00): {close_matches} ({close_matches/len(y_test)*100:.1f}%)")
    
    # Feature importance analysis
    importance_df = analyze_feature_importance(best_model, X_engineered.columns)
    
    # Save the best model and scaler
    print(f"\n💾 Saving best model ({best_model_name}) and feature engineering pipeline...")
    joblib.dump(best_model, 'best_model.pkl')
    joblib.dump(scaler, 'scaler.pkl')
    
    # Save feature names for later use
    feature_names = list(X_engineered.columns)
    with open('feature_names.json', 'w') as f:
        json.dump(feature_names, f)
    
    # Save model metadata
    metadata = {
        'best_model_name': best_model_name,
        'test_mae': best_results['test_mae'],
        'test_r2': best_results['test_r2'],
        'exact_matches': int(exact_matches),
        'close_matches': int(close_matches),
        'total_test_cases': len(y_test),
        'feature_count': len(feature_names),
        'top_features': importance_df.head(10).to_dict('records') if importance_df is not None else None
    }
    
    with open('model_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("✅ Model training complete!")
    print(f"   Files saved to ml-solution/")
    print(f"   - best_model.pkl ({best_model_name})")
    print(f"   - feature_names.json")
    print(f"   - model_metadata.json")
    
    # Error analysis on worst cases
    print("\n🔍 Analyzing highest error cases...")
    test_errors = np.abs(y_test - best_results['predictions'])
    worst_indices = np.argsort(test_errors)[-10:]
    
    print("Top 10 worst predictions:")
    for i, idx in enumerate(reversed(worst_indices)):
        days = X_test.iloc[idx]['days']
        miles = X_test.iloc[idx]['miles']
        receipts = X_test.iloc[idx]['receipts']
        actual = y_test[idx]
        predicted = best_results['predictions'][idx]
        error = abs(actual - predicted)
        
        print(f"  {i+1:2d}. {days:2.0f} days, {miles:4.0f} miles, ${receipts:6.2f} receipts")
        print(f"      Expected: ${actual:7.2f}, Predicted: ${predicted:7.2f}, Error: ${error:6.2f}")

if __name__ == "__main__":
    main() 