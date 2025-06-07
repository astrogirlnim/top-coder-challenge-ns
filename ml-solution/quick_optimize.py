#!/usr/bin/env python3
"""
Quick Model Optimization - Focus on proven approaches

Based on initial results:
1. Feature selection (30 features = best)
2. Model complexity (Medium = best balance)
3. Quick ensemble test
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

def main():
    print("⚡ QUICK MODEL OPTIMIZATION")
    print("="*40)
    
    # Load data
    print("\n📊 Loading data...")
    X_raw, y = load_data('../public_cases.json')
    X_engineered = engineer_features(X_raw)
    feature_names = list(X_engineered.columns)
    
    # Split data (same as original)
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X_engineered, y, test_size=0.2, random_state=42
    )
    
    print(f"Data loaded: {len(X_train)} train, {len(X_test)} test")
    
    # Get feature importance from original model
    print("\n🔍 Getting feature importance...")
    original_model = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42)
    original_model.fit(X_train, y_train)
    
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': original_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("Top 10 features:")
    for i, row in importance_df.head(10).iterrows():
        print(f"  {row['feature']:20} {row['importance']:.4f}")
    
    # Test top 30 features (best from partial run)
    top_30_features = importance_df.head(30)['feature'].tolist()
    X_train_opt = X_train[top_30_features]
    X_test_opt = X_test[top_30_features]
    
    # Test optimized model configurations
    configs = [
        {
            'name': 'Optimized-Speed',
            'params': {'n_estimators': 75, 'max_depth': 10, 'min_samples_split': 5, 'min_samples_leaf': 2},
            'features': top_30_features
        },
        {
            'name': 'Optimized-Accuracy', 
            'params': {'n_estimators': 125, 'max_depth': 12, 'min_samples_split': 3, 'min_samples_leaf': 1},
            'features': top_30_features
        },
        {
            'name': 'Original-Baseline',
            'params': {'n_estimators': 200, 'max_depth': 15, 'min_samples_split': 5, 'min_samples_leaf': 2},
            'features': feature_names
        }
    ]
    
    results = []
    
    for config in configs:
        print(f"\n🚀 Testing {config['name']}...")
        
        # Select features
        if len(config['features']) == 30:
            X_tr, X_te = X_train_opt, X_test_opt
        else:
            X_tr, X_te = X_train, X_test
            
        # Train model
        model = RandomForestRegressor(random_state=42, n_jobs=-1, **config['params'])
        
        # Time training
        start_time = time.time()
        model.fit(X_tr, y_train)
        train_time = time.time() - start_time
        
        # Time prediction
        start_time = time.time()
        predictions = model.predict(X_te)
        predict_time = time.time() - start_time
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        exact_matches = np.sum(np.abs(y_test - predictions) <= 0.01)
        close_matches = np.sum(np.abs(y_test - predictions) <= 1.0)
        
        result = {
            'name': config['name'],
            'mae': mae,
            'r2': r2,
            'exact_matches': exact_matches,
            'close_matches': close_matches,
            'train_time': train_time,
            'predict_time': predict_time,
            'n_features': len(config['features']),
            'model': model,
            'features': config['features'],
            'predictions': predictions
        }
        results.append(result)
        
        print(f"  MAE: ${mae:.2f}")
        print(f"  R²: {r2:.4f}")
        print(f"  Close matches: {close_matches} ({close_matches/len(y_test)*100:.1f}%)")
        print(f"  Training time: {train_time:.3f}s")
        print(f"  Prediction time: {predict_time*1000:.1f}ms")
        print(f"  Features: {len(config['features'])}")
    
    # Find best model
    best_result = min(results, key=lambda x: x['mae'])
    fastest_result = min(results, key=lambda x: x['train_time'])
    
    print(f"\n🏆 RESULTS SUMMARY")
    print("="*40)
    print(f"Best Accuracy: {best_result['name']} (MAE: ${best_result['mae']:.2f})")
    print(f"Fastest Training: {fastest_result['name']} ({fastest_result['train_time']:.3f}s)")
    
    # Compare with baseline
    baseline = next(r for r in results if r['name'] == 'Original-Baseline')
    optimized = best_result
    
    mae_improvement = (baseline['mae'] - optimized['mae']) / baseline['mae'] * 100
    speed_improvement = (baseline['train_time'] - optimized['train_time']) / baseline['train_time'] * 100
    feature_reduction = (len(feature_names) - optimized['n_features']) / len(feature_names) * 100
    
    print(f"\n📈 OPTIMIZATION GAINS:")
    print(f"  MAE improvement: {mae_improvement:+.1f}%")
    print(f"  Speed improvement: {speed_improvement:+.1f}%") 
    print(f"  Feature reduction: {feature_reduction:.1f}%")
    
    # Save optimized model
    print(f"\n💾 Saving optimized model...")
    joblib.dump(best_result['model'], 'best_model_optimized.pkl')
    
    optimization_config = {
        'model_name': best_result['name'],
        'test_mae': best_result['mae'],
        'test_r2': best_result['r2'],
        'close_matches': int(best_result['close_matches']),
        'train_time': best_result['train_time'],
        'predict_time': best_result['predict_time'],
        'n_features': best_result['n_features'],
        'top_features': best_result['features'],
        'improvements': {
            'mae_improvement_pct': mae_improvement,
            'speed_improvement_pct': speed_improvement,
            'feature_reduction_pct': feature_reduction
        }
    }
    
    with open('optimization_config.json', 'w') as f:
        json.dump(optimization_config, f, indent=2)
    
    print(f"✅ Optimization complete!")
    print(f"   Model: best_model_optimized.pkl")
    print(f"   Config: optimization_config.json")
    
    return results

if __name__ == "__main__":
    main() 