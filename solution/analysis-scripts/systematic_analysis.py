#!/usr/bin/env python3
import json
import statistics

with open('../public_cases.json', 'r') as f:
    data = json.load(f)

print("=== SYSTEMATIC REVERSE ENGINEERING ===")

# Let's start by looking at simple cases to understand the base formula
print("\n=== ANALYZING SIMPLE CASES ===")

# Find cases with low receipts and low miles to isolate the base rate
simple_cases = []
for i, case in enumerate(data):
    inp = case['input']
    days = inp['trip_duration_days']
    miles = inp['miles_traveled']
    receipts = inp['total_receipts_amount']
    output = case['expected_output']
    
    if receipts < 30 and miles < 100:
        simple_cases.append({
            'case_id': i,
            'days': days,
            'miles': miles,
            'receipts': receipts,
            'output': output,
            'per_day': output / days
        })

simple_cases.sort(key=lambda x: (x['days'], x['miles']))
print("Simple cases (low receipts, low miles):")
for case in simple_cases[:15]:
    print(f"Days: {case['days']}, Miles: {case['miles']:3.0f}, Receipts: ${case['receipts']:5.2f}, Output: ${case['output']:6.2f}, Per day: ${case['per_day']:6.2f}")

# Look for the base per diem rate
if simple_cases:
    per_day_values = [c['per_day'] for c in simple_cases]
    avg_per_day = statistics.mean(per_day_values)
    print(f"\nAverage per day for simple cases: ${avg_per_day:.2f}")

# Analyze 1-day trips separately
print("\n=== 1-DAY TRIP ANALYSIS ===")
one_day_cases = []
for i, case in enumerate(data):
    inp = case['input']
    if inp['trip_duration_days'] == 1:
        miles = inp['miles_traveled']
        receipts = inp['total_receipts_amount']
        output = case['expected_output']
        
        # Try to reverse engineer: output = base + miles_component + receipt_component
        # Assume base = 100 for 1 day
        # Standard mileage rate would be miles * 0.58
        
        remaining_after_base = output - 100
        if miles <= 100:
            standard_mileage = miles * 0.58
        else:
            standard_mileage = 100 * 0.58 + (miles - 100) * 0.45
        
        remaining_after_mileage = remaining_after_base - standard_mileage
        receipt_rate = remaining_after_mileage / receipts if receipts > 0 else 0
        
        one_day_cases.append({
            'case_id': i,
            'miles': miles,
            'receipts': receipts,
            'output': output,
            'receipt_component': remaining_after_mileage,
            'receipt_rate': receipt_rate
        })

# Sort by receipts to see the pattern
one_day_cases.sort(key=lambda x: x['receipts'])
print("1-day cases showing receipt rate calculation:")
for case in one_day_cases[:20]:
    print(f"Miles: {case['miles']:3.0f}, Receipts: ${case['receipts']:6.2f}, Output: ${case['output']:6.2f}, Receipt comp: ${case['receipt_component']:6.2f}, Rate: {case['receipt_rate']:.3f}")

# Look for patterns in receipt rates
if one_day_cases:
    receipt_rates = [c['receipt_rate'] for c in one_day_cases if c['receipts'] > 10 and c['receipt_rate'] > 0]
    if receipt_rates:
        print(f"\nReceipt rate statistics:")
        print(f"Min: {min(receipt_rates):.3f}, Max: {max(receipt_rates):.3f}, Avg: {statistics.mean(receipt_rates):.3f}")

# Check if there are tiers or thresholds
print("\n=== LOOKING FOR RECEIPT TIERS ===")
receipt_ranges = [(0, 50), (50, 200), (200, 500), (500, 1000), (1000, 1500), (1500, 2000), (2000, 10000)]

for min_r, max_r in receipt_ranges:
    range_cases = [c for c in one_day_cases if min_r <= c['receipts'] < max_r and c['receipts'] > 0]
    if len(range_cases) >= 3:
        avg_rate = statistics.mean([c['receipt_rate'] for c in range_cases])
        print(f"Receipts ${min_r}-${max_r}: {len(range_cases)} cases, avg rate: {avg_rate:.3f}")

# Check if the .49 penalty is real
print("\n=== CHECKING .49 PENALTY ===")
penalty_cases = []
normal_cases = []

for case in one_day_cases:
    cents = int(round((case['receipts'] - int(case['receipts'])) * 100))
    if cents == 49:
        penalty_cases.append(case['receipt_rate'])
    elif 40 <= cents <= 60 and cents != 49:
        normal_cases.append(case['receipt_rate'])

if penalty_cases and normal_cases:
    print(f"Receipts ending in .49: {len(penalty_cases)} cases, avg rate: {statistics.mean(penalty_cases):.3f}")
    print(f"Receipts ending in .40-.60 (not .49): {len(normal_cases)} cases, avg rate: {statistics.mean(normal_cases):.3f}")

# Look for day-length effects
print("\n=== DAY LENGTH EFFECTS ===")
by_days = {}
for i, case in enumerate(data):
    inp = case['input']
    days = inp['trip_duration_days']
    output = case['expected_output']
    
    if days not in by_days:
        by_days[days] = []
    by_days[days].append(output / days)

for days in sorted(by_days.keys())[:10]:
    if len(by_days[days]) >= 5:
        avg_per_day = statistics.mean(by_days[days])
        print(f"{days} days: {len(by_days[days])} cases, avg per day: ${avg_per_day:.2f}")

# Try to find a better base formula
print("\n=== TESTING BASE FORMULA HYPOTHESIS ===")

def test_formula(days, miles, receipts):
    # Base per diem
    base = days * 100
    
    # Mileage (standard federal rate with tiers)
    if miles <= 100:
        mileage = miles * 0.58
    else:
        mileage = 100 * 0.58 + (miles - 100) * 0.45
    
    # Receipts - try different rates for different ranges
    if receipts <= 100:
        receipt_comp = receipts * 0.6
    elif receipts <= 500:
        receipt_comp = 100 * 0.6 + (receipts - 100) * 0.8
    elif receipts <= 1000:
        receipt_comp = 100 * 0.6 + 400 * 0.8 + (receipts - 500) * 0.9
    else:
        receipt_comp = 100 * 0.6 + 400 * 0.8 + 500 * 0.9 + (receipts - 1000) * 0.7
    
    return base + mileage + receipt_comp

# Test on a sample
print("Testing base formula on sample cases:")
errors = []
for i in range(0, 100, 10):
    case = data[i]
    inp = case['input']
    expected = case['expected_output']
    predicted = test_formula(inp['trip_duration_days'], inp['miles_traveled'], inp['total_receipts_amount'])
    error = abs(expected - predicted)
    errors.append(error)
    print(f"Case {i}: Expected ${expected:.2f}, Predicted ${predicted:.2f}, Error ${error:.2f}")

if errors:
    print(f"Average error on sample: ${statistics.mean(errors):.2f}") 