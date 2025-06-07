#!/usr/bin/env python3
import sys

def main():
    if len(sys.argv) != 4:
        print("Usage: calculate_reimbursement.py <trip_duration_days> <miles_traveled> <total_receipts_amount>")
        sys.exit(1)
    
    days = int(sys.argv[1])
    miles = float(sys.argv[2])
    receipts = float(sys.argv[3])
    
    assert days > 0 and miles >= 0 and receipts >= 0

    # Base per diem - varies by trip length
    if days == 1:
        base = 120
    elif days <= 3:
        base = days * 105
    elif days <= 6:
        base = days * 95
    elif days <= 10:
        base = days * 85
    else:
        base = days * 75
    
    # Mileage - standard tiered approach
    if miles <= 100:
        mileage = miles * 0.58
    elif miles <= 500:
        mileage = 100 * 0.58 + (miles - 100) * 0.45
    else:
        mileage = 100 * 0.58 + 400 * 0.45 + (miles - 500) * 0.35
    
    # Sophisticated efficiency analysis
    miles_per_day = miles / days
    receipts_per_day = receipts / days
    
    if miles_per_day > 1000:  # Extreme cases - not real business
        # Heavy penalty for unrealistic travel
        receipt_component = receipts * 0.1
        
    elif miles_per_day >= 600 and miles_per_day <= 900:  # Super productivity zone
        # These 1-day intensive trips get major bonuses
        if receipts <= 800:
            receipt_component = receipts * 1.2  # BONUS for productive work
        elif receipts <= 1600:
            receipt_component = 800 * 1.2 + (receipts - 800) * 0.9
        else:
            receipt_component = 800 * 1.2 + 800 * 0.9 + (receipts - 1600) * 0.6
            
    elif miles_per_day > 400:  # High efficiency with moderate penalty
        # Some penalty but not extreme
        if receipts <= 500:
            receipt_component = receipts * 0.5
        elif receipts <= 1200:
            receipt_component = 500 * 0.5 + (receipts - 500) * 0.3
        else:
            receipt_component = 500 * 0.5 + 700 * 0.3 + (receipts - 1200) * 0.15
            
    elif miles_per_day >= 180:  # Kevin's sweet spot (180-220)
        # Good receipt treatment in the sweet spot
        if receipts <= 600:
            receipt_component = receipts * 0.75
        elif receipts <= 1200:
            receipt_component = 600 * 0.75 + (receipts - 600) * 0.6
        else:
            receipt_component = 600 * 0.75 + 600 * 0.6 + (receipts - 1200) * 0.45
            
    elif miles_per_day >= 100:  # Standard efficiency
        # Standard receipt processing
        if receipts <= 400:
            receipt_component = receipts * 0.65
        elif receipts <= 1000:
            receipt_component = 400 * 0.65 + (receipts - 400) * 0.45
        else:
            receipt_component = 400 * 0.65 + 600 * 0.45 + (receipts - 1000) * 0.25
            
    else:  # Low efficiency - heavy penalties
        # Poor receipt treatment for low efficiency
        if receipts <= 200:
            receipt_component = receipts * 0.5
        elif receipts <= 600:
            receipt_component = 200 * 0.5 + (receipts - 200) * 0.3
        else:
            receipt_component = 200 * 0.5 + 400 * 0.3 + (receipts - 600) * 0.1
    
    # Small adjustments
    # 5-day bonus (Lisa's observation)
    if days == 5:
        base += 50
    
    # Small receipt penalty
    if receipts < 30:
        receipt_component -= 20
    
    # Rounding bug bonus (Lisa's observation)
    cents = int(round((receipts - int(receipts)) * 100))
    if cents in [49, 99]:
        receipt_component += 8
    
    # Total
    total = base + mileage + receipt_component
    
    print(f"{total:.2f}")

if __name__ == "__main__":
    main() 