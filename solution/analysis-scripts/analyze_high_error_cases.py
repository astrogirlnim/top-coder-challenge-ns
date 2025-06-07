#!/usr/bin/env python3
import json

with open('../public_cases.json', 'r') as f:
    data = json.load(f)

# Find cases with days >= 8 and receipts > 900
high_receipt_long_trips = [
    (i, c) for i, c in enumerate(data)
    if c['input']['trip_duration_days'] >= 8 and c['input']['total_receipts_amount'] > 900
]

print(f"Cases with days >= 8 and receipts > $900: {len(high_receipt_long_trips)}")
for idx, case in high_receipt_long_trips[:10]:
    inp = case['input']
    out = case['expected_output']
    print(f"Case {idx}: {inp['trip_duration_days']} days, {inp['miles_traveled']} miles, ${inp['total_receipts_amount']:.2f} receipts | Output: ${out:.2f}")

# Compare to similar cases with lower receipts
for idx, case in high_receipt_long_trips[:10]:
    inp = case['input']
    days = inp['trip_duration_days']
    miles = inp['miles_traveled']
    similar = [c for c in data if c['input']['trip_duration_days'] == days and abs(c['input']['miles_traveled'] - miles) < 50 and c['input']['total_receipts_amount'] < 500]
    if similar:
        print(f"  Similar lower-receipt cases for {days}d/{miles}mi:")
        for s in similar[:2]:
            sinp = s['input']
            sout = s['expected_output']
            print(f"    {sinp['trip_duration_days']}d, {sinp['miles_traveled']}mi, ${sinp['total_receipts_amount']:.2f} receipts | Output: ${sout:.2f}")

# Analyze 14-day moderate receipt/mileage cases
print("\n14-day trips with moderate receipts and mileage:")
for i, c in enumerate(data):
    inp = c['input']
    if inp['trip_duration_days'] == 14 and 200 < inp['miles_traveled'] < 700 and 500 < inp['total_receipts_amount'] < 1200:
        print(f"Case {i}: {inp['trip_duration_days']}d, {inp['miles_traveled']}mi, ${inp['total_receipts_amount']:.2f} receipts | Output: ${c['expected_output']:.2f}") 