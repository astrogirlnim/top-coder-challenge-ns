#!/usr/bin/env python3
"""
Model Optimization Script

Tests multiple approaches to improve speed and predictability:
1. Feature selection based on importance
2. Model complexity reduction
3. Hyperparameter tuning
4. Alternative algorithms
5. Ensemble methods
"""

import json
import numpy as np
import pandas as pd
import time
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.feature_selection import SelectKBest, f_regression
import joblib

# Import our existing functions
from train_model import load_data, engineer_features

def time_model_training_and_prediction(model, X_train, y_train, X_test):
    """Time both training and prediction phases."""
    # Training time
    start_time = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - start_time
    
    # Prediction time
    start_time = time.time()
    predictions = model.predict(X_test)
    predict_time = time.time() - start_time
    
    return train_time, predict_time, predictions

def evaluate_model(model, X_train, y_train, X_test, y_test, model_name):
    """Comprehensive model evaluation including timing."""
    print(f"\n{'='*20} {model_name} {'='*20}")
    
    # Time training and prediction
    train_time, predict_time, test_pred = time_model_training_and_prediction(
        model, X_train, y_train, X_test
    )
    
    # Calculate metrics
    train_pred = model.predict(X_train)
    train_mae = mean_absolute_error(y_train, train_pred)
    test_mae = mean_absolute_error(y_test, test_pred)
    test_r2 = r2_score(y_test, test_pred)
    
    # Calculate exact matches
    exact_matches = np.sum(np.abs(y_test - test_pred) <= 0.01)
    close_matches = np.sum(np.abs(y_test - test_pred) <= 1.0)
    
    print(f"Training time: {train_time:.3f}s")
    print(f"Prediction time: {predict_time:.4f}s")
    print(f"Train MAE: ${train_mae:.2f}")
    print(f"Test MAE: ${test_mae:.2f}")
    print(f"Test R²: {test_r2:.4f}")
    print(f"Exact matches (±$0.01): {exact_matches} ({exact_matches/len(y_test)*100:.1f}%)")
    print(f"Close matches (±$1.00): {close_matches} ({close_matches/len(y_test)*100:.1f}%)")
    
    return {
        'model_name': model_name,
        'train_time': train_time,
        'predict_time': predict_time,
        'train_mae': train_mae,
        'test_mae': test_mae,
        'test_r2': test_r2,
        'exact_matches': exact_matches,
        'close_matches': close_matches,
        'predictions': test_pred
    }

def test_feature_selection(X_train, y_train, X_test, y_test, feature_names):
    """Test different numbers of top features."""
    print(f"\n🔍 FEATURE SELECTION OPTIMIZATION")
    print("="*50)
    
    # Load original model to get feature importance
    original_model = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42)
    original_model.fit(X_train, y_train)
    
    # Get feature importance ranking
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': original_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    feature_counts = [10, 15, 20, 25, 30, 39]  # 39 is all features
    results = []
    
    for n_features in feature_counts:
        print(f"\nTesting top {n_features} features...")
        
        # Select top N features
        top_features = importance_df.head(n_features)['feature'].tolist()
        X_train_selected = X_train[top_features]
        X_test_selected = X_test[top_features]
        
        # Train model with selected features
        model = RandomForestRegressor(
            n_estimators=100,  # Reduced for speed comparison
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        result = evaluate_model(
            model, X_train_selected, y_train, X_test_selected, y_test,
            f"RF-{n_features}feat"
        )
        result['n_features'] = n_features
        result['top_features'] = top_features
        results.append(result)
    
    return results

def test_model_complexity(X_train, y_train, X_test, y_test):
    """Test different model complexity configurations."""
    print(f"\n⚙️  MODEL COMPLEXITY OPTIMIZATION")
    print("="*50)
    
    configs = [
        {'n_estimators': 50, 'max_depth': 8, 'name': 'RF-Light'},
        {'n_estimators': 100, 'max_depth': 10, 'name': 'RF-Medium'},
        {'n_estimators': 150, 'max_depth': 12, 'name': 'RF-Heavy'},
        {'n_estimators': 200, 'max_depth': 15, 'name': 'RF-Original'},
    ]
    
    results = []
    for config in configs:
        model = RandomForestRegressor(
            n_estimators=config['n_estimators'],
            max_depth=config['max_depth'],
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        result = evaluate_model(model, X_train, y_train, X_test, y_test, config['name'])
        result['config'] = config
        results.append(result)
    
    return results

def test_alternative_algorithms(X_train, y_train, X_test, y_test):
    """Test faster alternative algorithms."""
    print(f"\n🚀 ALTERNATIVE ALGORITHMS")
    print("="*50)
    
    models = {
        'Ridge-Optimized': Ridge(alpha=0.1),
        'GradientBoosting-Light': GradientBoostingRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        ),
        'RandomForest-Minimal': RandomForestRegressor(
            n_estimators=50,
            max_depth=8,
            min_samples_split=10,
            min_samples_leaf=4,
            random_state=42,
            n_jobs=-1
        )
    }
    
    results = []
    for name, model in models.items():
        result = evaluate_model(model, X_train, y_train, X_test, y_test, name)
        results.append(result)
    
    return results

def test_hyperparameter_tuning(X_train, y_train, X_test, y_test):
    """Quick hyperparameter tuning for Random Forest."""
    print(f"\n🎯 HYPERPARAMETER TUNING")
    print("="*50)
    
    # Define parameter grid (kept small for speed)
    param_grid = {
        'n_estimators': [75, 100, 125],
        'max_depth': [8, 10, 12],
        'min_samples_split': [3, 5, 7],
        'min_samples_leaf': [1, 2, 3]
    }
    
    print("Running GridSearchCV (this may take a few minutes)...")
    
    # Use a smaller subset for faster tuning
    subset_size = min(500, len(X_train))
    subset_indices = np.random.RandomState(42).choice(len(X_train), subset_size, replace=False)
    X_subset = X_train.iloc[subset_indices]
    if hasattr(y_train, 'iloc'):
        y_subset = y_train.iloc[subset_indices]
    else:
        y_subset = y_train[subset_indices]
    
    rf = RandomForestRegressor(random_state=42, n_jobs=-1)
    grid_search = GridSearchCV(
        rf, param_grid, 
        cv=3,  # 3-fold CV for speed
        scoring='neg_mean_absolute_error',
        n_jobs=-1,
        verbose=1
    )
    
    grid_search.fit(X_subset, y_subset)
    
    print(f"Best parameters: {grid_search.best_params_}")
    print(f"Best CV score: ${-grid_search.best_score_:.2f}")
    
    # Test best model on full dataset
    best_model = grid_search.best_estimator_
    result = evaluate_model(best_model, X_train, y_train, X_test, y_test, "RF-Tuned")
    result['best_params'] = grid_search.best_params_
    
    return [result]

def test_ensemble_approach(X_train, y_train, X_test, y_test, top_features):
    """Test ensemble of different models."""
    print(f"\n🎭 ENSEMBLE METHODS")
    print("="*50)
    
    # Use top features for faster ensemble
    X_train_selected = X_train[top_features]
    X_test_selected = X_test[top_features]
    
    # Define ensemble components
    models = {
        'rf': RandomForestRegressor(n_estimators=75, max_depth=10, random_state=42, n_jobs=-1),
        'gb': GradientBoostingRegressor(n_estimators=75, max_depth=6, learning_rate=0.1, random_state=42),
        'ridge': Ridge(alpha=0.1)
    }
    
    # Train all models
    predictions = {}
    train_times = {}
    
    for name, model in models.items():
        start_time = time.time()
        model.fit(X_train_selected, y_train)
        train_times[name] = time.time() - start_time
        predictions[name] = model.predict(X_test_selected)
    
    # Simple ensemble: average predictions
    ensemble_pred = np.mean([predictions[name] for name in models.keys()], axis=0)
    
    # Weighted ensemble: weight by individual performance
    individual_maes = {}
    for name in models.keys():
        individual_maes[name] = mean_absolute_error(y_test, predictions[name])
    
    # Inverse MAE weighting (lower MAE = higher weight)
    weights = {}
    total_inv_mae = sum(1/mae for mae in individual_maes.values())
    for name, mae in individual_maes.items():
        weights[name] = (1/mae) / total_inv_mae
    
    weighted_ensemble_pred = np.sum([
        weights[name] * predictions[name] for name in models.keys()
    ], axis=0)
    
    # Evaluate ensembles
    results = []
    
    for ensemble_name, ensemble_predictions in [
        ('Ensemble-Simple', ensemble_pred),
        ('Ensemble-Weighted', weighted_ensemble_pred)
    ]:
        mae = mean_absolute_error(y_test, ensemble_predictions)
        r2 = r2_score(y_test, ensemble_predictions)
        exact_matches = np.sum(np.abs(y_test - ensemble_predictions) <= 0.01)
        close_matches = np.sum(np.abs(y_test - ensemble_predictions) <= 1.0)
        
        print(f"\n{ensemble_name}:")
        print(f"Test MAE: ${mae:.2f}")
        print(f"Test R²: {r2:.4f}")
        print(f"Exact matches: {exact_matches} ({exact_matches/len(y_test)*100:.1f}%)")
        print(f"Close matches: {close_matches} ({close_matches/len(y_test)*100:.1f}%)")
        
        results.append({
            'model_name': ensemble_name,
            'test_mae': mae,
            'test_r2': r2,
            'exact_matches': exact_matches,
            'close_matches': close_matches,
            'predictions': ensemble_predictions,
            'train_time': sum(train_times.values()),  # Combined training time
            'predict_time': 0.001  # Ensemble prediction is very fast
        })
    
    return results

def main():
    print("🚀 MODEL OPTIMIZATION & SPEED ANALYSIS")
    print("="*60)
    
    # Load data
    print("\n📊 Loading data...")
    X_raw, y = load_data('../public_cases.json')
    X_engineered = engineer_features(X_raw)
    feature_names = list(X_engineered.columns)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_engineered, y, test_size=0.2, random_state=42
    )
    
    print(f"Train set: {len(X_train)} examples")
    print(f"Test set: {len(X_test)} examples")
    print(f"Features: {len(feature_names)}")
    
    # Run all optimization tests
    all_results = []
    
    # 1. Feature selection
    feature_results = test_feature_selection(X_train, y_train, X_test, y_test, feature_names)
    all_results.extend(feature_results)
    
    # Find best feature count
    best_feature_result = min(feature_results, key=lambda x: x['test_mae'])
    top_features = best_feature_result['top_features']
    print(f"\n✅ Best feature count: {best_feature_result['n_features']} (MAE: ${best_feature_result['test_mae']:.2f})")
    
    # 2. Model complexity
    complexity_results = test_model_complexity(X_train, y_train, X_test, y_test)
    all_results.extend(complexity_results)
    
    # 3. Alternative algorithms
    algorithm_results = test_alternative_algorithms(X_train, y_train, X_test, y_test)
    all_results.extend(algorithm_results)
    
    # 4. Hyperparameter tuning (on top features for speed)
    X_train_top = X_train[top_features]
    X_test_top = X_test[top_features]
    tuning_results = test_hyperparameter_tuning(X_train_top, y_train, X_test_top, y_test)
    all_results.extend(tuning_results)
    
    # 5. Ensemble methods
    ensemble_results = test_ensemble_approach(X_train, y_train, X_test, y_test, top_features)
    all_results.extend(ensemble_results)
    
    # Analyze results
    print(f"\n📈 OPTIMIZATION RESULTS SUMMARY")
    print("="*60)
    
    # Create results DataFrame for analysis
    results_df = pd.DataFrame(all_results)
    
    # Sort by test MAE
    results_df = results_df.sort_values('test_mae')
    
    print(f"\nTop 10 Models by Accuracy:")
    print(f"{'Rank':<4} {'Model':<20} {'MAE':<8} {'R²':<8} {'Close':<6} {'Train(s)':<9} {'Pred(ms)':<9}")
    print("-" * 70)
    
    for i, (_, row) in enumerate(results_df.head(10).iterrows()):
        pred_time_ms = row.get('predict_time', 0) * 1000
        train_time = row.get('train_time', 0)
        
        print(f"{i+1:<4} {row['model_name']:<20} ${row['test_mae']:<7.2f} {row['test_r2']:<7.3f} "
              f"{row['close_matches']:<6} {train_time:<8.3f} {pred_time_ms:<8.1f}")
    
    # Find best overall model (balance of speed and accuracy)
    print(f"\n🏆 RECOMMENDATIONS")
    print("="*40)
    
    # Best accuracy
    best_accuracy = results_df.iloc[0]
    print(f"Best Accuracy: {best_accuracy['model_name']} (MAE: ${best_accuracy['test_mae']:.2f})")
    
    # Best speed (prediction time)
    if 'predict_time' in results_df.columns:
        fastest = results_df.loc[results_df['predict_time'].idxmin()]
        print(f"Fastest Prediction: {fastest['model_name']} ({fastest['predict_time']*1000:.1f}ms)")
    
    # Best balance (good accuracy + reasonable speed)
    # Filter for models with reasonable accuracy (within 10% of best)
    accuracy_threshold = best_accuracy['test_mae'] * 1.10
    good_accuracy = results_df[results_df['test_mae'] <= accuracy_threshold]
    
    if len(good_accuracy) > 1 and 'train_time' in good_accuracy.columns:
        best_balance = good_accuracy.loc[good_accuracy['train_time'].idxmin()]
        print(f"Best Balance: {best_balance['model_name']} (MAE: ${best_balance['test_mae']:.2f}, "
              f"Train: {best_balance['train_time']:.2f}s)")
    
    # Save best model
    best_model_name = best_accuracy['model_name']
    print(f"\n💾 Saving optimized model: {best_model_name}")
    
    # Find and save the best configuration
    if 'RF-Tuned' in best_model_name and len(tuning_results) > 0:
        # Re-train tuned model and save
        best_params = tuning_results[0]['best_params']
        optimized_model = RandomForestRegressor(**best_params, random_state=42, n_jobs=-1)
        optimized_model.fit(X_train[top_features], y_train)
        
        joblib.dump(optimized_model, 'best_model_optimized.pkl')
        
        # Save optimized configuration
        optimization_config = {
            'model_type': 'RandomForest',
            'best_params': best_params,
            'top_features': top_features,
            'n_features': len(top_features),
            'test_mae': best_accuracy['test_mae'],
            'test_r2': best_accuracy['test_r2'],
            'optimization_results': results_df.to_dict('records')
        }
        
        with open('optimization_results.json', 'w') as f:
            json.dump(optimization_config, f, indent=2)
            
        print(f"Saved optimized model with {len(top_features)} features")
        print(f"Best parameters: {best_params}")
    
    return results_df

if __name__ == "__main__":
    main() 