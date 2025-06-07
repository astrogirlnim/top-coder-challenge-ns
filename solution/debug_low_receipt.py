#!/usr/bin/env python3

# Debug Case 357: 12d, 1139mi, 124.65 receipts
days, miles, receipts = 12, 1139, 124.65

print(f"Debugging Case 357: {days}d, {miles}mi, ${receipts}")

receipts_per_day = receipts / days
print(f"Receipts per day: ${receipts_per_day:.2f}")

# Check low receipt condition
if receipts < 50:
    print(f"Condition 1: receipts < 50? {receipts} < 50 = {receipts < 50}")
else:
    print(f"Condition 1: receipts < 50? {receipts} < 50 = False")

if days >= 10 and receipts_per_day < 15:
    print(f"Condition 2: days >= 10 AND receipts_per_day < 15? {days} >= 10 AND {receipts_per_day:.2f} < 15 = True")
    print("*** SHOULD GET ZERO RECEIPT COMPONENT ***")
else:
    print(f"Condition 2: days >= 10 AND receipts_per_day < 15? {days} >= 10 AND {receipts_per_day:.2f} < 15 = False")

# Check what the base + mileage should be
if days <= 10:
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

print(f"Mileage: ${mileage:.2f}")
print(f"Expected base + mileage: ${base + mileage:.2f}")
print(f"But getting: $498.60")
print(f"Difference suggests receipt component is not zero") 