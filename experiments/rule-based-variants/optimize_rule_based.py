#!/usr/bin/env python3
"""
ML-Optimized Rule-Based Approach

Strategy: Keep the original rule-based structure but optimize its coefficients
using insights from the ML model's feature importance and performance.
"""

import json
import sys
import os

# Add the solution directory to path to import the original
sys.path.append('solution')
from metadata_reconstructor import MetadataReconstructor

def load_test_cases(n=100):
    """Load test cases for optimization."""
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    return cases[:n]

def evaluate_rule_based_with_params(days_coef, miles_coef, receipts_coef, cases):
    """Evaluate rule-based approach with different coefficients."""
    
    errors = []
    
    for case in cases:
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        # Simple rule-based calculation with adjustable coefficients
        prediction = (days * days_coef) + (miles * miles_coef) + (receipts * receipts_coef)
        
        # Apply basic constraints
        prediction = max(prediction, days * 50)  # Minimum per day
        prediction = min(prediction, days * 300 + receipts)  # Maximum cap
        
        error = abs(prediction - expected)
        errors.append(error)
    
    mae = sum(errors) / len(errors)
    return mae, errors

def grid_search_coefficients():
    """Find optimal coefficients using grid search."""
    
    print("🔍 OPTIMIZING RULE-BASED COEFFICIENTS")
    print("="*50)
    
    # Load test cases
    cases = load_test_cases(200)  # Use more cases for better optimization
    print(f"Optimizing on {len(cases)} test cases...")
    
    # Grid search ranges (based on ML feature importance)
    days_range = [80, 90, 100, 110, 120]     # Base per-day rate
    miles_range = [0.1, 0.2, 0.3, 0.4, 0.5]  # Per-mile rate
    receipts_range = [0.3, 0.4, 0.5, 0.6, 0.7]  # Receipt multiplier
    
    best_mae = float('inf')
    best_params = None
    
    total_combinations = len(days_range) * len(miles_range) * len(receipts_range)
    print(f"Testing {total_combinations} coefficient combinations...")
    
    tested = 0
    for days_coef in days_range:
        for miles_coef in miles_range:
            for receipts_coef in receipts_range:
                tested += 1
                
                mae, _ = evaluate_rule_based_with_params(days_coef, miles_coef, receipts_coef, cases)
                
                if mae < best_mae:
                    best_mae = mae
                    best_params = (days_coef, miles_coef, receipts_coef)
                    print(f"  New best: Days={days_coef}, Miles={miles_coef:.1f}, Receipts={receipts_coef:.1f} → MAE=${mae:.2f}")
                
                if tested % 20 == 0:
                    print(f"  Progress: {tested}/{total_combinations} combinations tested...")
    
    print(f"\n🏆 OPTIMAL COEFFICIENTS FOUND:")
    print(f"  Days coefficient: {best_params[0]}")
    print(f"  Miles coefficient: {best_params[1]}")
    print(f"  Receipts coefficient: {best_params[2]}")
    print(f"  Best MAE: ${best_mae:.2f}")
    
    return best_params, best_mae

def create_optimized_implementation(best_params):
    """Create optimized rule-based implementation."""
    
    days_coef, miles_coef, receipts_coef = best_params
    
    implementation = f'''#!/usr/bin/env python3
"""
ML-Optimized Rule-Based Reimbursement Calculator

Coefficients optimized using ML insights:
- Days coefficient: {days_coef}
- Miles coefficient: {miles_coef}
- Receipts coefficient: {receipts_coef}

No external dependencies, fast execution.
"""

import sys

def calculate_reimbursement(days, miles, receipts):
    """Calculate reimbursement using ML-optimized coefficients."""
    
    if days <= 0 or miles < 0 or receipts < 0:
        return 0.0
    
    # Base calculation with optimized coefficients
    base_amount = (days * {days_coef}) + (miles * {miles_coef}) + (receipts * {receipts_coef})
    
    # Apply constraints (based on original business logic)
    min_amount = days * 50    # Minimum $50/day
    max_amount = days * 300 + receipts  # Maximum cap
    
    final_amount = max(base_amount, min_amount)
    final_amount = min(final_amount, max_amount)
    
    return round(final_amount, 2)

def main():
    if len(sys.argv) != 4:
        print("Usage: calculate_reimbursement_optimized.py <days> <miles> <receipts>")
        sys.exit(1)
    
    try:
        days = int(sys.argv[1])
        miles = float(sys.argv[2])
        receipts = float(sys.argv[3])
        
        result = calculate_reimbursement(days, miles, receipts)
        print(f"{{result:.2f}}")
        
    except ValueError:
        print("Error: Invalid input format")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    with open('calculate_reimbursement_optimized.py', 'w') as f:
        f.write(implementation)
    
    print(f"\n✅ Created calculate_reimbursement_optimized.py")

def main():
    print("🚀 ML-GUIDED RULE-BASED OPTIMIZATION")
    print("="*60)
    
    # Find optimal coefficients
    best_params, best_mae = grid_search_coefficients()
    
    # Create optimized implementation
    create_optimized_implementation(best_params)
    
    # Test on problematic case
    days_coef, miles_coef, receipts_coef = best_params
    prediction = (14 * days_coef) + (1056 * miles_coef) + (2489.69 * receipts_coef)
    prediction = max(prediction, 14 * 50)
    prediction = min(prediction, 14 * 300 + 2489.69)
    
    print(f"\n🧪 TESTING ON PROBLEMATIC CASE:")
    print(f"  Input: 14 days, 1056 miles, $2489.69 receipts")
    print(f"  Optimized prediction: ${prediction:.2f}")
    print(f"  Expected: $1894.16")
    print(f"  Error: ${abs(prediction - 1894.16):.2f}")
    
    print(f"\n🎯 SUMMARY:")
    print(f"  Optimized MAE: ${best_mae:.2f}")
    print(f"  Improvement over original: {((125 - best_mae) / 125 * 100):+.1f}%")
    print(f"  No external dependencies: ✅")
    print(f"  Fast execution: ✅")

if __name__ == "__main__":
    main() 