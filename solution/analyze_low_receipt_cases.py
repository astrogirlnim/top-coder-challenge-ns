#!/usr/bin/env python3
import subprocess

def main():
    cases = [
        (11, 1179, 31.36, 1550.55, 'Case 153'),
        (12, 1077, 32.55, 1387.43, 'Case 567'),
        (13, 1204, 24.47, 1344.17, 'Case 917'),
        (7, 803, 12.75, 1146.78, 'Case 708'),
        (10, 1192, 23.47, 1157.87, 'Case 522')
    ]

    print('=== VERY LOW RECEIPT HIGH MILEAGE ANALYSIS ===')
    for days, miles, receipts, expected, case_name in cases:
        result = subprocess.run(['python3', 'calculate_reimbursement.py', str(days), str(miles), str(receipts)], 
                              capture_output=True, text=True)
        calculated = float(result.stdout.strip())
        error = abs(expected - calculated)
        mpd = miles / days
        rpd = receipts / days
        
        print(f'{case_name}: {days}d, {miles:.0f}mi ({mpd:.0f}/day), ${receipts:.2f} (${rpd:.1f}/day)')
        print(f'  Expected: ${expected:.2f}, Got: ${calculated:.2f}, Error: ${error:.2f}')
        print(f'  Pattern: HIGH MILEAGE + VERY LOW RECEIPTS')
        
        # These should get mostly mileage reimbursement, minimal receipt penalty
        base_estimate = days * 85  # Rough base per diem
        mileage_estimate = miles * 0.35  # Rough mileage estimate
        print(f'  Base estimate: ${base_estimate}, Mileage estimate: ${mileage_estimate:.0f}')
        print(f'  Total without receipts: ${base_estimate + mileage_estimate:.0f}')
        print(f'  But getting severe penalty for low receipts!')
        print()

if __name__ == "__main__":
    main() 