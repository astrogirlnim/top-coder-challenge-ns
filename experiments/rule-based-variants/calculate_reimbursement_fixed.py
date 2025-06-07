#!/usr/bin/env python3
"""
Fixed Pure Python Reimbursement Calculator

Going back to basics with coefficients that actually make sense,
based on the original rule-based solution but improved.
"""

import sys
import math

def calculate_reimbursement(days, miles, receipts):
    """
    Calculate reimbursement using a much simpler approach.
    
    The original rule-based solution was getting ~$125 MAE.
    The ML solution was getting ~$43 MAE.
    My complex version got ~$437 MAE (disaster!).
    
    Let's use a simple linear approach with light feature engineering.
    """
    
    # Input validation
    if days <= 0 or miles < 0 or receipts < 0:
        return 0.0
    
    # Basic derived metrics
    miles_per_day = miles / days
    receipts_per_day = receipts / days
    
    # **Simple Linear Model** (based on original rule-based performance)
    # Start with the original logic but improve coefficients
    
    # Base day rate (from original solution analysis)
    base_daily_rate = 100  # Roughly $100/day base
    
    # Miles component (moderate influence)
    miles_component = miles * 0.25  # Much smaller coefficient
    
    # Receipts component (major influence, but capped)
    receipts_component = receipts * 0.45  # Moderate coefficient
    
    # Base calculation
    base_amount = (days * base_daily_rate) + miles_component + receipts_component
    
    # **Simple Adjustments** (much more conservative)
    
    # Efficiency adjustments (small effects)
    efficiency_bonus = 0
    if 200 <= miles_per_day <= 400:  # Sweet spot
        efficiency_bonus = days * 10
    elif miles_per_day > 600:  # High efficiency
        efficiency_bonus = days * 15
    elif miles_per_day < 30:  # Low efficiency penalty
        efficiency_bonus = days * -5
    
    # Receipt level adjustments (small effects)
    receipt_bonus = 0
    if receipts > 1000:  # High receipts
        receipt_bonus = 20
    elif receipts < 20:  # Low receipts penalty
        receipt_bonus = -10
    
    # Trip length adjustments (small effects)
    length_bonus = 0
    if days >= 7:  # Long trip bonus
        length_bonus = 25
    elif days == 1:  # Single day penalty
        length_bonus = -15
    
    # Final calculation
    final_amount = base_amount + efficiency_bonus + receipt_bonus + length_bonus
    
    # **Conservative Constraints** (prevent the massive overestimation)
    
    # Much tighter bounds
    min_amount = days * 60   # $60/day minimum
    max_amount = days * 200 + receipts * 0.8  # Much more conservative max
    
    # Apply constraints
    final_amount = max(final_amount, min_amount)
    final_amount = min(final_amount, max_amount)
    
    return round(final_amount, 2)

def main():
    """Main function for command line usage."""
    if len(sys.argv) != 4:
        print("Usage: calculate_reimbursement_fixed.py <trip_duration_days> <miles_traveled> <total_receipts_amount>")
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