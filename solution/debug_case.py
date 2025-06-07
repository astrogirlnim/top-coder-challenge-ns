#!/usr/bin/env python3

# Debug Case 153: 11d, 1179mi, 31.36 receipts -> expected 1550.55, getting 78.40
days, miles, receipts = 11, 1179, 31.36

print(f"Debugging Case 153: {days}d, {miles}mi, ${receipts}")

# Base per diem calculation
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

print(f"Base per diem: ${base}")

# Mileage calculation
if miles <= 100:
    mileage = miles * 0.58
elif miles <= 500:
    mileage = 100 * 0.58 + (miles - 100) * 0.45
else:
    mileage = 100 * 0.58 + 400 * 0.45 + (miles - 500) * 0.35

print(f"Mileage component: ${mileage:.2f}")

# Receipt component - should be 0 for receipts < 50
if receipts < 50:
    receipt_component = 0
    print(f"Receipt component: ${receipt_component} (ignored due to < $50)")
else:
    print("Receipt component: calculated normally")

# Small receipt penalty check
miles_per_day = miles / days
print(f"Miles per day: {miles_per_day:.1f}")

if miles_per_day < 80:
    print("Would apply small receipt penalty")
else:
    print("No small receipt penalty (high mileage exemption)")

# Expected total
expected_total = base + mileage + receipt_component
print(f"Expected total: ${expected_total:.2f}")
print(f"But algorithm returns: $78.40")
print(f"Difference suggests there's still a penalty being applied somewhere") 