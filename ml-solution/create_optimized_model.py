#!/usr/bin/env python3
"""
Create Optimized Model

Based on analysis:
- Top 15 features give nearly same accuracy as 39 features
- Reduced complexity maintains performance while being faster
- Focus on the most impactful optimizations
"""

import json
import numpy as np
import pandas as pd
import time
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# Import our existing functions
from train_model import load_data, engineer_features

def create_optimized_calculate_reimbursement():
    """Create an optimized version of the calculation script."""
    
    # Load optimization config
    with open('optimization_config.json', 'r') as f:
        config = json.load(f)
    
    optimized_script = '''#!/usr/bin/env python3
"""
Optimized ML-based reimbursement calculator.
Uses only top {n_features} features for faster prediction while maintaining accuracy.
"""

import sys
import numpy as np
import pandas as pd
import joblib
import json
import os

def engineer_features(X):
    """Optimized feature engineering - only creates top features."""
    df = pd.DataFrame(X, columns=['days', 'miles', 'receipts'])
    
    # Basic derived features
    df['miles_per_day'] = df['miles'] / df['days']
    df['receipts_per_day'] = df['receipts'] / df['days']
    
    # Only create the most important features
    
    # Top importance features from analysis
    df['log_receipts'] = np.log1p(df['receipts'])
    df['receipts_squared'] = df['receipts'] ** 2
    df['days_squared'] = df['days'] ** 2
    df['miles_squared'] = df['miles'] ** 2
    df['days_x_efficiency'] = df['days'] * df['miles_per_day']
    df['log_miles'] = np.log1p(df['miles'])
    df['has_rounding_bug'] = ((df['receipts'] * 100) % 100).isin([49, 99]).astype(int)
    
    # Interview-driven features (most important ones)
    df['is_super_productivity'] = ((df['miles_per_day'] >= 600) & (df['miles_per_day'] <= 900)).astype(int)
    df['is_sweet_spot_efficiency'] = ((df['miles_per_day'] >= 180) & (df['miles_per_day'] <= 220)).astype(int)
    df['is_5_day_trip'] = (df['days'] == 5).astype(int)
    df['is_small_receipts'] = (df['receipts'] < 50).astype(int)
    df['is_medium_receipts'] = ((df['receipts'] >= 600) & (df['receipts'] <= 800)).astype(int)
    df['is_high_receipts'] = (df['receipts'] > 1200).astype(int)
    df['is_short_trip'] = (df['days'] <= 3).astype(int)
    df['is_long_trip'] = (df['days'] >= 7).astype(int)
    
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
        print(f"Error loading optimized model: {{e}}", file=sys.stderr)
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
    print(f"{{prediction:.2f}}")

if __name__ == "__main__":
    main()
'''.format(n_features=config['n_features'])
    
    return optimized_script

def main():
    print("🔧 CREATING OPTIMIZED MODEL")
    print("="*40)
    
    # Load data and train optimized model
    print("\n📊 Loading data...")
    X_raw, y = load_data('../public_cases.json')
    X_engineered = engineer_features(X_raw)
    
    # Split data 
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X_engineered, y, test_size=0.2, random_state=42
    )
    
    # Get feature importance and select top features
    original_model = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42)
    original_model.fit(X_train, y_train)
    
    importance_df = pd.DataFrame({
        'feature': X_engineered.columns,
        'importance': original_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    # Test different feature counts for optimal balance
    feature_counts = [10, 15, 20, 25]
    results = []
    
    for n_features in feature_counts:
        top_features = importance_df.head(n_features)['feature'].tolist()
        X_train_selected = X_train[top_features]
        X_test_selected = X_test[top_features]
        
        # Optimized Random Forest (faster but still accurate)
        model = RandomForestRegressor(
            n_estimators=100,   # Reduced from 200
            max_depth=12,       # Reduced from 15  
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        # Time training
        start_time = time.time()
        model.fit(X_train_selected, y_train)
        train_time = time.time() - start_time
        
        # Time prediction
        start_time = time.time()
        predictions = model.predict(X_test_selected)
        predict_time = time.time() - start_time
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        close_matches = np.sum(np.abs(y_test - predictions) <= 1.0)
        
        results.append({
            'n_features': n_features,
            'mae': mae,
            'r2': r2,
            'close_matches': close_matches,
            'train_time': train_time,
            'predict_time': predict_time,
            'top_features': top_features,
            'model': model
        })
        
        print(f"\n✅ {n_features} features: MAE=${mae:.2f}, R²={r2:.4f}, Train={train_time:.3f}s")
    
    # Find best balance (accuracy within 2% of best, prioritize speed)
    best_mae = min(r['mae'] for r in results)
    acceptable_threshold = best_mae * 1.02  # Within 2% of best
    
    acceptable_results = [r for r in results if r['mae'] <= acceptable_threshold]
    optimal_result = min(acceptable_results, key=lambda x: x['train_time'])
    
    print(f"\n🏆 OPTIMAL CONFIGURATION")
    print("="*40)
    print(f"Features: {optimal_result['n_features']}")
    print(f"MAE: ${optimal_result['mae']:.2f}")
    print(f"R²: {optimal_result['r2']:.4f}")
    print(f"Close matches: {optimal_result['close_matches']} ({optimal_result['close_matches']/len(y_test)*100:.1f}%)")
    print(f"Training time: {optimal_result['train_time']:.3f}s")
    print(f"Prediction time: {optimal_result['predict_time']*1000:.1f}ms")
    
    # Calculate improvements vs original
    original_result = results[-1]  # Assume worst timing with most features
    speed_improvement = (original_result['train_time'] - optimal_result['train_time']) / original_result['train_time'] * 100
    feature_reduction = (39 - optimal_result['n_features']) / 39 * 100
    mae_change = (optimal_result['mae'] - best_mae) / best_mae * 100
    
    print(f"\n📈 OPTIMIZATIONS:")
    print(f"  Speed improvement: +{speed_improvement:.1f}%")
    print(f"  Feature reduction: {feature_reduction:.1f}%")
    print(f"  Accuracy loss: {mae_change:+.1f}%")
    
    # Save optimized model and configuration
    print(f"\n💾 Saving optimized model...")
    joblib.dump(optimal_result['model'], 'best_model_optimized.pkl')
    
    config = {
        'model_name': 'RandomForest-Optimized',
        'n_features': optimal_result['n_features'],
        'top_features': optimal_result['top_features'],
        'test_mae': optimal_result['mae'],
        'test_r2': optimal_result['r2'],
        'close_matches': int(optimal_result['close_matches']),
        'train_time': optimal_result['train_time'],
        'predict_time': optimal_result['predict_time'],
        'improvements': {
            'speed_improvement_pct': speed_improvement,
            'feature_reduction_pct': feature_reduction,
            'accuracy_loss_pct': mae_change
        }
    }
    
    with open('optimization_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    # Create optimized calculation script
    optimized_script = create_optimized_calculate_reimbursement()
    with open('calculate_reimbursement_optimized.py', 'w') as f:
        f.write(optimized_script)
    
    print(f"✅ Created optimized files:")
    print(f"   - best_model_optimized.pkl")
    print(f"   - optimization_config.json") 
    print(f"   - calculate_reimbursement_optimized.py")
    
    return optimal_result

if __name__ == "__main__":
    main() 