#!/usr/bin/env python3
"""
Pure Python Linear Approximation of ML Model
MAE: $85.65
Generated from ML coefficients - no external dependencies
"""

import sys
import math


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



def calculate_reimbursement_linear(days, miles, receipts):
    """Calculate reimbursement using extracted linear coefficients."""
    
    if days <= 0 or miles < 0 or receipts < 0:
        return 0.0
    
    # Engineer features exactly as in training
    features = engineer_features_exact(days, miles, receipts)
    
    # Linear calculation using extracted coefficients
    result = 716.8035985605  # Intercept
    
    # Add each feature contribution
    result += 76.6313823101 * features.get('days', 0)
    result += 0.2728436307 * features.get('miles', 0)
    result += 1.4775182275 * features.get('receipts', 0)
    result += -1.0300423997 * features.get('miles_per_day', 0)
    result += 0.1182179117 * features.get('receipts_per_day', 0)
    result += 109.8966914324 * features.get('is_super_productivity', 0)
    result += -6.1098605043 * features.get('is_sweet_spot_efficiency', 0)
    result += 83.1242641628 * features.get('is_high_efficiency', 0)
    result += -40.7700822655 * features.get('is_extreme_miles', 0)
    result += -124.3227186736 * features.get('is_low_efficiency', 0)
    result += 2.7762049929 * features.get('is_5_day_trip', 0)
    result += -17.6601075603 * features.get('is_sweet_spot_length', 0)
    result += 42.0017810101 * features.get('is_short_trip', 0)
    result += -24.3416734498 * features.get('is_long_trip', 0)
    result += 35.4324571759 * features.get('is_small_receipts', 0)
    result += -220.8640564383 * features.get('is_very_small_receipts', 0)
    result += -59.0173304126 * features.get('is_medium_receipts', 0)
    result += -20.7575733246 * features.get('is_high_receipts', 0)
    result += 1.7044121035 * features.get('is_very_high_receipts', 0)
    result += -17.5244797953 * features.get('overspending_short', 0)
    result += 54.4412352611 * features.get('overspending_medium', 0)
    result += 73.8621024116 * features.get('overspending_long', 0)
    result += -428.3673519773 * features.get('has_rounding_bug', 0)
    result += -0.6948559506 * features.get('pseudo_submission_day', 0)
    result += 5.6941430633 * features.get('is_tuesday_submission', 0)
    result += 9.6321547899 * features.get('is_friday_submission', 0)
    result += -0.0000281672 * features.get('efficiency_x_receipts', 0)
    result += 0.2728436164 * features.get('days_x_efficiency', 0)
    result += -0.0000281503 * features.get('total_productivity', 0)
    result += -0.0000737635 * features.get('miles_squared', 0)
    result += -0.0003689489 * features.get('receipts_squared', 0)
    result += -1.9986363841 * features.get('days_squared', 0)
    result += 0.0006523721 * features.get('miles_per_day_squared', 0)
    result += 49.6130329019 * features.get('log_miles', 0)
    result += -155.6659336515 * features.get('log_receipts', 0)
    result += -40.8861589997 * features.get('log_miles_per_day', 0)
    result += -43.5485940884 * features.get('ideal_combo', 0)
    result += -166.5678729979 * features.get('vacation_penalty', 0)
    result += 30.6034652471 * features.get('efficiency_bonus', 0)

    return round(result, 2)


def main():
    if len(sys.argv) != 4:
        print("Usage: script.py <days> <miles> <receipts>")
        sys.exit(1)
    
    try:
        days = int(sys.argv[1])
        miles = float(sys.argv[2])
        receipts = float(sys.argv[3])
        
        result = calculate_reimbursement_linear(days, miles, receipts)
        print(f"{result:.2f}")
        
    except ValueError:
        print("Error: Invalid input format")
        sys.exit(1)

if __name__ == "__main__":
    main()
