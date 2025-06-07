#!/usr/bin/env python3
import json
import math
import statistics

# Load the data
with open('../public_cases.json', 'r') as f:
    data = json.load(f)

print(f"Total cases: {len(data)}")

# Extract features
cases = []
for case in data:
    input_data = case['input']
    output = case['expected_output']
    
    days = input_data['trip_duration_days']
    miles = input_data['miles_traveled']
    receipts = input_data['total_receipts_amount']
    
    # Calculate derived features
    miles_per_day = miles / days if days > 0 else 0
    receipts_per_day = receipts / days if days > 0 else 0
    
    cases.append({
        'days': days,
        'miles': miles,
        'receipts': receipts,
        'output': output,
        'miles_per_day': miles_per_day,
        'receipts_per_day': receipts_per_day
    })

# Analyze basic patterns
print("\n=== BASIC STATISTICS ===")
days_list = [c['days'] for c in cases]
miles_list = [c['miles'] for c in cases]
receipts_list = [c['receipts'] for c in cases]
output_list = [c['output'] for c in cases]

print(f"Days - Min: {min(days_list)}, Max: {max(days_list)}, Avg: {statistics.mean(days_list):.2f}")
print(f"Miles - Min: {min(miles_list)}, Max: {max(miles_list)}, Avg: {statistics.mean(miles_list):.2f}")
print(f"Receipts - Min: {min(receipts_list)}, Max: {max(receipts_list)}, Avg: ${statistics.mean(receipts_list):.2f}")
print(f"Output - Min: ${min(output_list)}, Max: ${max(output_list)}, Avg: ${statistics.mean(output_list):.2f}")

# Analyze by trip duration
print("\n=== BY TRIP DURATION ===")
by_days = {}
for case in cases:
    days = case['days']
    if days not in by_days:
        by_days[days] = []
    by_days[days].append(case)

for days in sorted(by_days.keys()):
    cases_for_days = by_days[days]
    avg_output = statistics.mean([c['output'] for c in cases_for_days])
    avg_per_day = avg_output / days
    print(f"{days} days: {len(cases_for_days)} cases, avg output: ${avg_output:.2f}, per day: ${avg_per_day:.2f}")

# Look for per diem base rate
print("\n=== PER DIEM ANALYSIS ===")
# Look at minimal cases (low miles, low receipts)
minimal_cases = [c for c in cases if c['miles'] < 50 and c['receipts'] < 50]
print(f"Minimal cases: {len(minimal_cases)}")
for case in minimal_cases[:10]:
    per_day = case['output'] / case['days']
    print(f"Days: {case['days']}, Miles: {case['miles']}, Receipts: ${case['receipts']:.2f}, Output: ${case['output']:.2f}, Per day: ${per_day:.2f}")

# Analyze mileage patterns
print("\n=== MILEAGE ANALYSIS ===")
# Group by days and look at mileage impact
for days in [1, 2, 3, 5]:
    if days in by_days:
        day_cases = by_days[days]
        # Sort by miles
        day_cases.sort(key=lambda x: x['miles'])
        print(f"\n{days}-day trips by mileage:")
        for i in range(0, min(10, len(day_cases))):
            case = day_cases[i]
            miles_component = case['output'] - (100 * case['days'])  # Assume base $100/day
            per_mile = miles_component / case['miles'] if case['miles'] > 0 else 0
            print(f"  Miles: {case['miles']:3.0f}, Receipts: ${case['receipts']:6.2f}, Output: ${case['output']:7.2f}, Miles comp: ${miles_component:6.2f}, $/mile: ${per_mile:.3f}")

print("\n=== RECEIPTS ANALYSIS ===")
# Look at receipt patterns
one_day_cases = [c for c in cases if c['days'] == 1]
one_day_cases.sort(key=lambda x: x['receipts'])
print("1-day trips by receipts:")
for i in range(0, min(15, len(one_day_cases))):
    case = one_day_cases[i]
    base_estimate = 100 + case['miles'] * 0.58  # Base per diem + standard mileage
    print(f"  Receipts: ${case['receipts']:6.2f}, Miles: {case['miles']:3.0f}, Output: ${case['output']:7.2f}, Est base: ${base_estimate:6.2f}, Diff: ${case['output'] - base_estimate:6.2f}") 