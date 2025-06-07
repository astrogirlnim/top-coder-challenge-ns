#!/usr/bin/env python3
import json
import statistics
from collections import defaultdict

with open('../public_cases.json', 'r') as f:
    data = json.load(f)

print("=== CALENDAR-BASED ANALYSIS FOR SHORT TRIPS ===")
print("Investigating Marcus's theory about monthly variations\n")

# Focus on shorter trips (1-3 days) as mentioned
short_trips = []
for i, case in enumerate(data):
    inp = case['input']
    days = inp['trip_duration_days']
    if days <= 3:  # Short trips
        miles = inp['miles_traveled']
        receipts = inp['total_receipts_amount']
        output = case['expected_output']
        short_trips.append({
            'case_id': i,
            'days': days,
            'miles': miles,
            'receipts': receipts,
            'output': output
        })

print(f"Short trips (1-3 days): {len(short_trips)} cases")

# Test Marcus's "early vs late month" theory using modular arithmetic
# Since we don't have dates, let's see if there are patterns based on:
# 1. Case ID modulo various numbers (simulating day of month)
# 2. Receipt amount modulo various numbers
# 3. Miles modulo various numbers

def test_modular_patterns(trips, field_name, modulo_base):
    print(f"\n--- Testing {field_name} % {modulo_base} patterns ---")
    
    groups = defaultdict(list)
    for trip in trips:
        if field_name == 'case_id':
            key = trip['case_id'] % modulo_base
        elif field_name == 'receipts_int':
            key = int(trip['receipts']) % modulo_base
        elif field_name == 'miles':
            key = trip['miles'] % modulo_base
        
        groups[key].append(trip)
    
    # Calculate average outputs for each group
    for key in sorted(groups.keys()):
        group_trips = groups[key]
        if len(group_trips) >= 3:  # Only show groups with enough data
            avg_output = statistics.mean([t['output'] for t in group_trips])
            avg_receipts = statistics.mean([t['receipts'] for t in group_trips])
            avg_miles = statistics.mean([t['miles'] for t in group_trips])
            print(f"  {field_name} % {modulo_base} = {key}: {len(group_trips)} cases, avg output: ${avg_output:.2f}, avg receipts: ${avg_receipts:.2f}, avg miles: {avg_miles:.0f}")

# Test different modular patterns that might simulate calendar effects
test_modular_patterns(short_trips, 'case_id', 7)   # Weekly cycle
test_modular_patterns(short_trips, 'case_id', 30)  # Monthly cycle
test_modular_patterns(short_trips, 'case_id', 31)  # Days in month

# Test receipt-based patterns (maybe receipts encode date info)
test_modular_patterns(short_trips, 'receipts_int', 7)
test_modular_patterns(short_trips, 'receipts_int', 30)
test_modular_patterns(short_trips, 'receipts_int', 31)

# Test mile-based patterns
test_modular_patterns(short_trips, 'miles', 7)
test_modular_patterns(short_trips, 'miles', 30)

print("\n=== RECEIPT DECIMAL PATTERNS ===")
print("Looking for patterns in receipt cents (might encode dates)")

# Group by last two digits of receipts (cents)
cents_groups = defaultdict(list)
for trip in short_trips:
    cents = int(round((trip['receipts'] - int(trip['receipts'])) * 100))
    cents_groups[cents].append(trip)

# Look for significant patterns in cents
significant_cents = []
for cents, trips in cents_groups.items():
    if len(trips) >= 3:
        avg_output = statistics.mean([t['output'] for t in trips])
        significant_cents.append((cents, len(trips), avg_output))

# Sort by count and show top patterns
significant_cents.sort(key=lambda x: x[1], reverse=True)
print("Top cents patterns (might be date encodings):")
for cents, count, avg_output in significant_cents[:15]:
    print(f"  Receipts ending in .{cents:02d}: {count} cases, avg output: ${avg_output:.2f}")

print("\n=== LOOKING FOR EARLY/LATE MONTH PATTERNS ===")
print("Testing if first half vs second half of something affects reimbursement")

# Test various "early vs late" splits
def test_early_late_split(trips, field_name, threshold_func):
    early_trips = []
    late_trips = []
    
    for trip in trips:
        if field_name == 'case_id':
            value = trip['case_id']
        elif field_name == 'receipts_int':
            value = int(trip['receipts'])
        elif field_name == 'miles':
            value = trip['miles']
        
        if threshold_func(value):
            early_trips.append(trip)
        else:
            late_trips.append(trip)
    
    if len(early_trips) >= 5 and len(late_trips) >= 5:
        early_avg = statistics.mean([t['output'] for t in early_trips])
        late_avg = statistics.mean([t['output'] for t in late_trips])
        early_receipts = statistics.mean([t['receipts'] for t in early_trips])
        late_receipts = statistics.mean([t['receipts'] for t in late_trips])
        
        print(f"\n{field_name} split:")
        print(f"  Early: {len(early_trips)} cases, avg output: ${early_avg:.2f}, avg receipts: ${early_receipts:.2f}")
        print(f"  Late:  {len(late_trips)} cases, avg output: ${late_avg:.2f}, avg receipts: ${late_receipts:.2f}")
        print(f"  Difference: ${late_avg - early_avg:.2f}")

# Test case ID early/late (first half vs second half of dataset)
test_early_late_split(short_trips, 'case_id', lambda x: x < 500)

# Test receipt amount early/late  
test_early_late_split(short_trips, 'receipts_int', lambda x: (x % 100) < 50)

# Test miles early/late
test_early_late_split(short_trips, 'miles', lambda x: (x % 100) < 50)

print("\n=== SPECIFIC RECEIPT AMOUNT ANALYSIS ===")
print("Looking for 'lucky numbers' Marcus mentioned")

# Group by exact receipt amounts (for small amounts)
exact_amounts = defaultdict(list)
for trip in short_trips:
    if trip['receipts'] < 100:  # Focus on smaller amounts
        rounded_receipts = round(trip['receipts'], 2)
        exact_amounts[rounded_receipts].append(trip)

# Find amounts that appear multiple times
repeated_amounts = []
for amount, trips in exact_amounts.items():
    if len(trips) >= 2:
        avg_output = statistics.mean([t['output'] for t in trips])
        repeated_amounts.append((amount, len(trips), avg_output))

repeated_amounts.sort(key=lambda x: x[1], reverse=True)
print("Repeated small receipt amounts (might show calendar effects):")
for amount, count, avg_output in repeated_amounts[:10]:
    print(f"  ${amount:.2f}: {count} cases, avg output: ${avg_output:.2f}") 