#!/usr/bin/env python3
"""
ML-Optimized Rule-Based Reimbursement Calculator

Coefficients optimized using ML insights:
- Days coefficient: 80
- Miles coefficient: 0.5
- Receipts coefficient: 0.5

No external dependencies, fast execution.
"""

import sys

def calculate_reimbursement(days, miles, receipts):
    """Calculate reimbursement using ML-optimized coefficients."""
    
    if days <= 0 or miles < 0 or receipts < 0:
        return 0.0
    
    # Base calculation with optimized coefficients
    base_amount = (days * 80) + (miles * 0.5) + (receipts * 0.5)
    
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
        print(f"{result:.2f}")
        
    except ValueError:
        print("Error: Invalid input format")
        sys.exit(1)

if __name__ == "__main__":
    main()
