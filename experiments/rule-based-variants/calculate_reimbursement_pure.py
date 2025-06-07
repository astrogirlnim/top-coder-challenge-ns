#!/usr/bin/env python3
"""
Pure Python Reimbursement Calculator - No External Dependencies

This implementation captures the key insights from ML analysis but uses only
Python standard library to meet the no-external-dependencies requirement.

Based on ML feature importance analysis, the most critical factors are:
1. log_receipts (23% importance)
2. receipts_squared (21% importance) 
3. receipts (19% importance)
4. days_squared (9% importance)
5. days (7% importance)
"""

import sys
import math

def calculate_reimbursement(days, miles, receipts):
    """
    Calculate reimbursement using insights from ML analysis.
    
    This approximates the complex ML model using polynomial and logarithmic
    relationships discovered through feature importance analysis.
    """
    
    # Input validation
    if days <= 0 or miles < 0 or receipts < 0:
        return 0.0
    
    # Core derived features (from ML analysis)
    miles_per_day = miles / days
    receipts_per_day = receipts / days
    receipts_per_mile = receipts / (miles + 1)  # +1 to avoid division by zero
    
    # Mathematical transformations (top importance features)
    log_receipts = math.log1p(receipts)  # log(receipts + 1)
    receipts_squared = receipts ** 2
    days_squared = days ** 2
    miles_squared = miles ** 2
    log_miles = math.log1p(miles)
    
    # Feature interactions
    days_x_efficiency = days * miles_per_day
    
    # Business logic features (from interviews)
    has_rounding_bug = int((receipts * 100) % 100 in [49, 99])
    is_short_trip = int(days <= 3)
    is_long_trip = int(days >= 7)
    overspending_long = int(days >= 7 and receipts_per_day > 200)
    
    # Pseudo submission timing (deterministic based on inputs)
    submission_day = (days + int(miles) + int(receipts)) % 7
    
    # **Core Reimbursement Formula**
    # Based on ML feature weights and coefficients analysis
    
    # Base calculation using top features (polynomial regression approximation)
    base_amount = (
        # Primary receipts-based components (63% of importance)
        0.85 * log_receipts +           # 23% importance
        0.000012 * receipts_squared +   # 21% importance  
        0.42 * receipts +               # 19% importance
        
        # Days-based components (16% importance)
        8.5 * days_squared +            # 9% importance
        45.0 * days +                   # 7% importance
        
        # Miles-based components
        0.000031 * miles_squared +      # 3% importance
        0.15 * miles +                  # 3% importance
        0.08 * log_miles +              # 3% importance
        
        # Interaction terms
        0.095 * days_x_efficiency +     # 3% importance
        
        # Business logic adjustments
        12.0 * has_rounding_bug +       # Rounding quirk bonus
        -8.0 * is_short_trip +          # Short trip penalty
        15.0 * is_long_trip +           # Long trip bonus
        25.0 * overspending_long        # High spending long trip bonus
    )
    
    # **Efficiency Zone Adjustments** (from interview analysis)
    # These were key patterns identified by employees
    
    efficiency_multiplier = 1.0
    
    # Super productivity zone (Kevin's insight)
    if 600 <= miles_per_day <= 900:
        efficiency_multiplier *= 1.15
    
    # Sweet spot efficiency (Jennifer's insight)
    elif 180 <= miles_per_day <= 220:
        efficiency_multiplier *= 1.08
    
    # Penalty for very low efficiency
    elif miles_per_day < 50:
        efficiency_multiplier *= 0.92
    
    # **Receipt Pattern Adjustments** (from Lisa's insights)
    
    receipt_multiplier = 1.0
    
    # High receipt categories
    if receipts > 1200:
        receipt_multiplier *= 1.05
    elif 600 <= receipts <= 800:
        receipt_multiplier *= 1.03
    elif receipts < 50:
        receipt_multiplier *= 0.95
    
    # **Trip Length Adjustments**
    
    length_multiplier = 1.0
    
    # Optimal trip lengths (from interview patterns)
    if days == 5:
        length_multiplier *= 1.04  # 5-day trips get slight bonus
    elif days == 1:
        length_multiplier *= 0.98  # Single day trips get slight penalty
    
    # **Submission Timing Effects** (cyclical patterns)
    
    timing_adjustment = 0
    if submission_day in [1, 2]:  # Monday/Tuesday submissions
        timing_adjustment += 5
    elif submission_day in [5, 6]:  # Friday/Saturday submissions  
        timing_adjustment -= 3
    
    # **Final Calculation**
    
    final_amount = (
        base_amount * 
        efficiency_multiplier * 
        receipt_multiplier * 
        length_multiplier +
        timing_adjustment
    )
    
    # **Business Constraints** (from interview insights)
    
    # Minimum reimbursement (covers basic per diem)
    min_reimbursement = days * 75  # $75/day minimum
    
    # Maximum reimbursement cap (prevent abuse)
    max_reimbursement = days * 500 + receipts * 1.5
    
    # Apply constraints
    final_amount = max(final_amount, min_reimbursement)
    final_amount = min(final_amount, max_reimbursement)
    
    return round(final_amount, 2)

def main():
    """Main function for command line usage."""
    if len(sys.argv) != 4:
        print("Usage: calculate_reimbursement_pure.py <trip_duration_days> <miles_traveled> <total_receipts_amount>")
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
    
    # Calculate and output reimbursement
    reimbursement = calculate_reimbursement(days, miles, receipts)
    print(f"{reimbursement:.2f}")

if __name__ == "__main__":
    main() 