#!/usr/bin/env python3
import json
import math
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

# Load the data
with open('../public_cases.json', 'r') as f:
    data = json.load(f)

# Extract features and targets
X = []
y = []

for case in data:
    input_data = case['input']
    output = case['expected_output']
    
    days = input_data['trip_duration_days']
    miles = input_data['miles_traveled']  
    receipts = input_data['total_receipts_amount']
    
    # Create feature vector with engineered features
    features = [
        days,                                    # 0: days
        miles,                                   # 1: miles
        receipts,                                # 2: receipts
        miles / days,                            # 3: miles per day
        receipts / days,                         # 4: receipts per day
        days * 100,                              # 5: base per diem component
        miles * 0.58,                           # 6: standard mileage rate
        min(receipts, 1000),                    # 7: capped receipts
        max(0, receipts - 1000),                # 8: excess receipts
        1 if days == 5 else 0,                 # 9: 5-day bonus flag
        1 if 180 <= miles/days <= 220 else 0,  # 10: efficiency sweet spot
        days * days,                            # 11: days squared
        miles * miles / 1000000,                # 12: miles squared (scaled)
        receipts * receipts / 1000000,          # 13: receipts squared (scaled)
        days * miles,                           # 14: days * miles interaction
        days * receipts,                        # 15: days * receipts interaction
        miles * receipts / 1000,                # 16: miles * receipts interaction (scaled)
        math.log(days),                         # 17: log days
        math.log(miles + 1),                    # 18: log miles
        math.log(receipts + 1),                 # 19: log receipts
    ]
    
    X.append(features)
    y.append(output)

X = np.array(X)
y = np.array(y)

print(f"Dataset: {len(X)} samples, {X.shape[1]} features")

# Split into train/test (use first 800 for training, last 200 for testing)
X_train, X_test = X[:800], X[800:]
y_train, y_test = y[:800], y[800:]

print(f"Training set: {len(X_train)} samples")
print(f"Test set: {len(X_test)} samples")

# Try different models
models = {
    'Linear Regression': LinearRegression(),
    'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
    'Polynomial Features (degree 2)': Pipeline([
        ('poly', PolynomialFeatures(degree=2, include_bias=False)),
        ('linear', LinearRegression())
    ])
}

results = {}
for name, model in models.items():
    print(f"\n=== {name} ===")
    
    # Train model
    model.fit(X_train, y_train)
    
    # Predictions
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    # Metrics
    train_mae = mean_absolute_error(y_train, y_pred_train)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    
    print(f"Train MAE: ${train_mae:.2f}, R²: {train_r2:.4f}")
    print(f"Test MAE: ${test_mae:.2f}, R²: {test_r2:.4f}")
    
    results[name] = {
        'model': model,
        'test_mae': test_mae,
        'test_r2': test_r2
    }
    
    # Show feature importance for Random Forest
    if name == 'Random Forest':
        feature_names = [
            'days', 'miles', 'receipts', 'miles_per_day', 'receipts_per_day',
            'base_perdiem', 'std_mileage', 'capped_receipts', 'excess_receipts',
            'day5_bonus', 'efficiency_sweet', 'days_sq', 'miles_sq', 'receipts_sq',
            'days_miles', 'days_receipts', 'miles_receipts', 'log_days', 'log_miles', 'log_receipts'
        ]
        
        importances = model.feature_importances_
        feature_importance = list(zip(feature_names, importances))
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        
        print("\nTop 10 Feature Importances:")
        for feature, importance in feature_importance[:10]:
            print(f"  {feature}: {importance:.4f}")

# Find the best model
best_model_name = min(results.keys(), key=lambda k: results[k]['test_mae'])
best_model = results[best_model_name]['model']

print(f"\n=== BEST MODEL: {best_model_name} ===")
print(f"Test MAE: ${results[best_model_name]['test_mae']:.2f}")

# Analyze some predictions to understand the pattern
print(f"\n=== PREDICTION ANALYSIS ===")
print("Comparing actual vs predicted for test set:")

# Show some examples
for i in range(min(10, len(X_test))):
    actual = y_test[i]
    pred = best_model.predict([X_test[i]])[0]
    
    # Get original inputs
    case_idx = 800 + i
    case = data[case_idx]
    days = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    
    print(f"  Days: {days}, Miles: {miles:.0f}, Receipts: ${receipts:.2f} | Actual: ${actual:.2f}, Pred: ${pred:.2f}, Diff: ${abs(actual-pred):.2f}")

# Try to reverse engineer a simple formula from the patterns
print(f"\n=== SIMPLE FORMULA ATTEMPT ===")

# Based on the analysis, try to build a simple rule-based system
def simple_formula(days, miles, receipts):
    # Base per diem
    base = days * 100
    
    # Mileage component - appears to be non-linear
    if miles <= 100:
        mileage = miles * 0.58
    elif miles <= 500:
        mileage = 100 * 0.58 + (miles - 100) * 0.45
    else:
        mileage = 100 * 0.58 + 400 * 0.45 + (miles - 500) * 0.35
    
    # Receipt component - appears to have diminishing returns
    if receipts <= 100:
        receipt_comp = receipts * 0.8
    elif receipts <= 1000:
        receipt_comp = 100 * 0.8 + (receipts - 100) * 0.7
    else:
        receipt_comp = 100 * 0.8 + 900 * 0.7 + (receipts - 1000) * 0.4
    
    # Efficiency bonus (from Kevin's observations)
    efficiency = miles / days
    if days >= 5 and 150 <= efficiency <= 250:
        efficiency_bonus = 50
    else:
        efficiency_bonus = 0
    
    return base + mileage + receipt_comp + efficiency_bonus

# Test simple formula
simple_predictions = []
for i in range(len(X_test)):
    case_idx = 800 + i
    case = data[case_idx]
    days = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    
    pred = simple_formula(days, miles, receipts)
    simple_predictions.append(pred)

simple_mae = mean_absolute_error(y_test, simple_predictions)
print(f"Simple formula MAE: ${simple_mae:.2f}")

print("\nSample predictions with simple formula:")
for i in range(min(10, len(X_test))):
    actual = y_test[i]
    pred = simple_predictions[i]
    
    case_idx = 800 + i
    case = data[case_idx]
    days = case['input']['trip_duration_days']
    miles = case['input']['miles_traveled']
    receipts = case['input']['total_receipts_amount']
    
    print(f"  Days: {days}, Miles: {miles:.0f}, Receipts: ${receipts:.2f} | Actual: ${actual:.2f}, Simple: ${pred:.2f}, Diff: ${abs(actual-pred):.2f}")

print('\nPolynomial Regression (degree=2):')
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)
reg_poly = LinearRegression()
reg_poly.fit(X_poly, y)
pred_poly = reg_poly.predict(X_poly)
print('MAE:', mean_absolute_error(y, pred_poly))
print('RMSE:', mean_squared_error(y, pred_poly, squared=False))

# Show top coefficients for polynomial regression
coefs = reg_poly.coef_
feature_names = poly.get_feature_names_out(['days','miles','receipts','miles_per_day','receipts_per_day','miles_per_receipt'])
coef_tuples = sorted(zip(np.abs(coefs), feature_names), reverse=True)
print('\nTop 10 polynomial features:')
for val, name in coef_tuples[:10]:
    print(f'{name}: {val:.2f}') 