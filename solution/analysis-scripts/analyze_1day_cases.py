#!/usr/bin/env python3
import json
import subprocess

with open('public_cases.json', 'r') as f:
    data = json.load(f)

print(f"{'Miles':>6} {'Receipts':>9} | {'Expected':>8} | {'Actual':>8} | {'Diff':>7}")
print('-'*50)
for case in data:
    inp = case['input']
    if inp['trip_duration_days'] == 1:
        miles = inp['miles_traveled']
        receipts = inp['total_receipts_amount']
        expected = case['expected_output']
        # Call the current solution
        result = subprocess.run([
            'python3', 'solution/calculate_reimbursement.py',
            '1', str(miles), str(receipts)
        ], capture_output=True, text=True)
        try:
            actual = float(result.stdout.strip())
        except Exception:
            actual = None
        diff = abs(expected - actual) if actual is not None else None
        if actual is not None:
            print(f"{miles:6.2f} {receipts:9.2f} | {expected:8.2f} | {actual:8.2f} | {diff:7.2f}")
        else:
            print(f"{miles:6.2f} {receipts:9.2f} | {expected:8.2f} | {'ERR':>8} | {'ERR':>7}") 