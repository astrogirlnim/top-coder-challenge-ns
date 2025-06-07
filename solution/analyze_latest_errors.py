#!/usr/bin/env python3
import subprocess

def main():
    cases = [
        (12, 1139, 124.65, 1314.30, 'Case 357'),
        (14, 94, 105.94, 1180.63, 'Case 626'),
        (5, 516, 1878.49, 669.85, 'Case 711'),
        (3, 1159, 2209.44, 1434.84, 'Case 253'),
        (3, 1162, 2152.66, 1434.71, 'Case 156')
    ]

    print('=== LATEST HIGH ERROR CASES ANALYSIS ===')
    for days, miles, receipts, expected, case_name in cases:
        result = subprocess.run(['python3', 'calculate_reimbursement.py', str(days), str(miles), str(receipts)], 
                              capture_output=True, text=True)
        calculated = float(result.stdout.strip())
        error = abs(expected - calculated)
        mpd = miles / days
        rpd = receipts / days
        
        print(f'{case_name}: {days}d, {miles:.0f}mi ({mpd:.0f}/day), ${receipts:.2f} (${rpd:.0f}/day)')
        print(f'  Expected: ${expected:.2f}, Got: ${calculated:.2f}, Error: ${error:.2f}')
        
        # Check efficiency zones
        if mpd >= 160:
            zone = 'sweet spot'
        elif mpd >= 100:
            zone = 'standard'
        else:
            zone = 'low efficiency'
        print(f'  Efficiency zone: {zone} ({mpd:.0f} mi/day)')
        
        # Check for specific patterns
        if receipts < 200 and miles > 1000:
            print(f'  *** LOW RECEIPT + HIGH MILEAGE pattern ***')
        if receipts > 1500:
            print(f'  *** HIGH RECEIPT pattern - may need diminishing returns ***')
        if days >= 12:
            print(f'  *** VERY LONG TRIP pattern ***')
        if days <= 3 and miles > 1000:
            print(f'  *** SHORT + HIGH MILEAGE pattern ***')
        
        # Estimate what the reimbursement should be roughly
        base_est = days * 85 if days > 10 else days * 95 if days > 6 else days * 105
        mileage_est = min(1000, miles) * 0.4  # Rough estimate
        print(f'  Rough estimate: ${base_est + mileage_est:.0f} (base + mileage only)')
        print()

if __name__ == "__main__":
    main() 