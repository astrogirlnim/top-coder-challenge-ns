#!/usr/bin/env python3
import json
import math
import statistics
from collections import defaultdict

# Load the data
with open('../public_cases.json', 'r') as f:
    data = json.load(f)

cases = []
for case in data:
    input_data = case['input']
    output = case['expected_output']
    
    days = input_data['trip_duration_days']
    miles = input_data['miles_traveled']
    receipts = input_data['total_receipts_amount']
    
    cases.append({
        'days': days,
        'miles': miles,
        'receipts': receipts,
        'output': output,
        'miles_per_day': miles / days,
        'receipts_per_day': receipts / days
    })

print(f"Total cases: {len(cases)}")

# Try different hypotheses about the formula structure
print("\n=== HYPOTHESIS TESTING ===")

# Hypothesis 1: Base per diem + mileage + receipt percentage
def test_hypothesis_1():
    print("\n--- Hypothesis 1: Base + Mileage Rate + Receipt % ---")
    # Try to find cases where we can isolate variables
    
    # Look for simple pattern: Base per day + miles * rate + receipts * percentage
    # Test with low-receipt cases to isolate base + mileage
    low_receipt_cases = [c for c in cases if c['receipts'] < 30]
    print(f"Low receipt cases: {len(low_receipt_cases)}")
    
    # Calculate implied base + mileage rates
    for case in low_receipt_cases[:10]:
        # Assume receipts contribute minimally
        base_plus_mileage = case['output']
        per_day_component = base_plus_mileage - (case['receipts'] * 0.5)  # assume 50% receipt rate
        base_rate = per_day_component / case['days'] - (case['miles'] / case['days']) * 0.58
        print(f"Days: {case['days']}, Miles: {case['miles']:3.0f}, Receipts: ${case['receipts']:5.2f}, Output: ${case['output']:6.2f}, Implied base/day: ${base_rate:.2f}")

test_hypothesis_1()

# Hypothesis 2: Different calculation for 1-day vs multi-day trips
def test_hypothesis_2():
    print("\n--- Hypothesis 2: Different formulas by trip length ---")
    
    # Separate 1-day trips
    one_day = [c for c in cases if c['days'] == 1]
    multi_day = [c for c in cases if c['days'] > 1]
    
    print(f"1-day trips: {len(one_day)}")
    print(f"Multi-day trips: {len(multi_day)}")
    
    # Look at 1-day trips with similar mileage
    one_day.sort(key=lambda x: x['miles'])
    print("\n1-day trips - trying to find mileage pattern:")
    for i in range(0, min(20, len(one_day))):
        case = one_day[i]
        # Try different formulas
        simple_calc = case['miles'] * 0.58 + case['receipts']
        better_calc = case['miles'] * 0.58 + case['receipts'] * 0.7 + 100
        print(f"Miles: {case['miles']:3.0f}, Receipts: ${case['receipts']:6.2f}, Output: ${case['output']:6.2f}, Simple: ${simple_calc:6.2f}, Better: ${better_calc:6.2f}")

test_hypothesis_2()

# Hypothesis 3: Receipt tiers/bonuses
def test_hypothesis_3():
    print("\n--- Hypothesis 3: Receipt processing tiers ---")
    
    # Group by receipt ranges
    ranges = [(0, 100), (100, 500), (500, 1000), (1000, 1500), (1500, 2000), (2000, 3000)]
    
    for min_r, max_r in ranges:
        range_cases = [c for c in cases if min_r <= c['receipts'] < max_r]
        if range_cases:
            avg_output = statistics.mean([c['output'] for c in range_cases])
            avg_receipts = statistics.mean([c['receipts'] for c in range_cases])
            avg_days = statistics.mean([c['days'] for c in range_cases])
            avg_miles = statistics.mean([c['miles'] for c in range_cases])
            print(f"Receipts ${min_r}-${max_r}: {len(range_cases)} cases, avg output: ${avg_output:.2f}, avg receipts: ${avg_receipts:.2f}, avg days: {avg_days:.1f}, avg miles: {avg_miles:.0f}")

test_hypothesis_3()

# Hypothesis 4: Miles per day efficiency bonuses
def test_hypothesis_4():
    print("\n--- Hypothesis 4: Miles per day efficiency bonuses ---")
    
    # Kevin mentioned 180-220 miles per day sweet spot
    efficiency_ranges = [(0, 50), (50, 100), (100, 150), (150, 200), (200, 250), (250, 300), (300, 999)]
    
    for min_e, max_e in efficiency_ranges:
        range_cases = [c for c in cases if min_e <= c['miles_per_day'] < max_e and c['days'] > 1]  # Multi-day only
        if range_cases:
            avg_output = statistics.mean([c['output'] for c in range_cases])
            avg_per_day = avg_output / statistics.mean([c['days'] for c in range_cases])
            print(f"Miles/day {min_e}-{max_e}: {len(range_cases)} cases, avg output: ${avg_output:.2f}, avg per day: ${avg_per_day:.2f}")

test_hypothesis_4()

# Hypothesis 5: Try to reverse engineer exact formula
def test_hypothesis_5():
    print("\n--- Hypothesis 5: Reverse engineering attempt ---")
    
    # Focus on specific cases that might reveal the pattern
    # Look at 5-day trips as Kevin mentioned they get bonuses
    five_day_cases = [c for c in cases if c['days'] == 5]
    five_day_cases.sort(key=lambda x: (x['miles'], x['receipts']))
    
    print("5-day trips (Kevin's sweet spot):")
    for case in five_day_cases[:15]:
        # Try Kevin's theory: base + mileage + receipts + efficiency bonus
        base_perdiem = 100 * case['days']  # Base $100/day
        mileage_comp = case['miles'] * 0.58  # Standard mileage rate
        receipt_comp = case['receipts'] * 0.7  # Assume 70% of receipts
        
        # Efficiency bonus calculation attempt
        efficiency = case['miles_per_day']
        if 180 <= efficiency <= 220:
            efficiency_bonus = 50 * case['days']  # Bonus for sweet spot
        else:
            efficiency_bonus = 0
            
        estimated = base_perdiem + mileage_comp + receipt_comp + efficiency_bonus
        diff = case['output'] - estimated
        
        print(f"Miles: {case['miles']:3.0f} ({efficiency:5.1f}/day), Receipts: ${case['receipts']:6.2f}, Output: ${case['output']:7.2f}, Est: ${estimated:7.2f}, Diff: ${diff:6.2f}")

test_hypothesis_5()

# Let's look at the specific patterns Kevin mentioned
def analyze_kevin_patterns():
    print("\n--- Kevin's Specific Claims Analysis ---")
    
    # "5-day trips with 180+ miles per day and under $100 per day in spending—that's a guaranteed bonus"
    kevin_sweet_spot = [c for c in cases if c['days'] == 5 and c['miles_per_day'] >= 180 and c['receipts_per_day'] < 100]
    print(f"\nKevin's sweet spot (5 days, 180+ miles/day, <$100/day receipts): {len(kevin_sweet_spot)} cases")
    if kevin_sweet_spot:
        avg_output = statistics.mean([c['output'] for c in kevin_sweet_spot])
        print(f"Average output: ${avg_output:.2f}")
        for case in kevin_sweet_spot[:5]:
            print(f"  Days: {case['days']}, Miles/day: {case['miles_per_day']:.1f}, Receipts/day: ${case['receipts_per_day']:.2f}, Output: ${case['output']:.2f}")
    
    # Compare with similar 5-day trips that don't meet criteria
    other_five_day = [c for c in cases if c['days'] == 5 and not (c['miles_per_day'] >= 180 and c['receipts_per_day'] < 100)]
    if other_five_day:
        other_avg = statistics.mean([c['output'] for c in other_five_day])
        print(f"Other 5-day trips average: ${other_avg:.2f}")
        if kevin_sweet_spot:
            print(f"Sweet spot advantage: ${avg_output - other_avg:.2f}")

analyze_kevin_patterns() 