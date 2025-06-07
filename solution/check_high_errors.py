#!/usr/bin/env python3
import json

with open('../public_cases.json', 'r') as f:
    data = json.load(f)

# Look at the high error cases mentioned in eval
cases_to_check = [148, 863, 633, 289, 569]  # 0-indexed
for i in cases_to_check:
    case = data[i]
    inp = case['input']
    out = case['expected_output']
    days = inp['trip_duration_days']
    miles = inp['miles_traveled']
    receipts = inp['total_receipts_amount']
    print(f'Case {i+1}: {days}d, {miles}mi, ${receipts:.2f} -> ${out:.2f}')
    print(f'  Miles/day: {miles/days:.1f}, Receipts/day: ${receipts/days:.2f}') 