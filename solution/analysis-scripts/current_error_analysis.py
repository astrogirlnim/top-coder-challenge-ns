#!/usr/bin/env python3
import json
import subprocess
import sys

def main():
    # Load private cases - this file doesn't have expected outputs, so let's check public cases
    try:
        with open('../public_cases.json', 'r') as f:
            data = json.load(f)
    except:
        print("Error loading public cases, trying different format")
        return

    print("Analyzing current algorithm performance...")
    errors = []
    
    # Test first 100 cases for performance
    for i, case in enumerate(data[:100]):
        inp = case['input']
        days = inp['trip_duration_days']
        miles = inp['miles_traveled'] 
        receipts = inp['total_receipts_amount']
        expected = case['expected_output']
        
        # Run our algorithm
        try:
            result = subprocess.run(['python3', 'calculate_reimbursement.py', str(days), str(miles), str(receipts)], 
                                  capture_output=True, text=True, timeout=5)
            calculated = float(result.stdout.strip())
            error = abs(expected - calculated)
            errors.append((i, days, miles, receipts, expected, calculated, error))
        except:
            print(f"Error processing case {i}")
            continue

    # Sort by error (highest first)
    errors.sort(key=lambda x: x[6], reverse=True)
    
    print('\n=== TOP 10 HIGH ERROR CASES ===')
    for rank, (case_idx, days, miles, receipts, expected, calculated, error) in enumerate(errors[:10]):
        mpd = miles / days
        rpd = receipts / days
        print(f'{rank+1}. Case {case_idx}: {days}d, {miles:.0f}mi ({mpd:.0f}/day), ${receipts:.2f} (${rpd:.0f}/day)')
        print(f'   Expected: ${expected:.2f}, Got: ${calculated:.2f}, Error: ${error:.2f}')
        print()

    # Pattern analysis
    print('=== PATTERN ANALYSIS ===')
    top_errors = errors[:20]
    
    print('Trip Length Distribution in Top 20 Errors:')
    length_counts = {}
    for _, days, _, _, _, _, _ in top_errors:
        length_counts[days] = length_counts.get(days, 0) + 1
    for days in sorted(length_counts.keys()):
        print(f'  {days} days: {length_counts[days]} cases')

    print('\nEfficiency Distribution in Top 20 Errors:')
    efficiency_ranges = {'<100': 0, '100-200': 0, '200-400': 0, '400+': 0}
    for _, days, miles, _, _, _, _ in top_errors:
        mpd = miles / days
        if mpd < 100:
            efficiency_ranges['<100'] += 1
        elif mpd < 200:
            efficiency_ranges['100-200'] += 1
        elif mpd < 400:
            efficiency_ranges['200-400'] += 1
        else:
            efficiency_ranges['400+'] += 1

    for range_name, count in efficiency_ranges.items():
        print(f'  {range_name} mi/day: {count} cases')

    print('\nSpending Distribution in Top 20 Errors:')
    spending_ranges = {'<$100': 0, '$100-150': 0, '$150-200': 0, '$200+': 0}
    for _, days, _, receipts, _, _, _ in top_errors:
        rpd = receipts / days
        if rpd < 100:
            spending_ranges['<$100'] += 1
        elif rpd < 150:
            spending_ranges['$100-150'] += 1
        elif rpd < 200:
            spending_ranges['$150-200'] += 1
        else:
            spending_ranges['$200+'] += 1

    for range_name, count in spending_ranges.items():
        print(f'  {range_name}/day: {count} cases')

    # Analyze specific patterns mentioned in documentation
    print('\n=== 7+ DAY HIGH RECEIPTS ANALYSIS ===')
    long_trip_high_receipts = [e for e in top_errors if e[1] >= 7 and e[3] > 1000]
    print(f'7+ day trips with >$1000 receipts in top errors: {len(long_trip_high_receipts)}')
    
    for case_idx, days, miles, receipts, expected, calculated, error in long_trip_high_receipts:
        mpd = miles / days
        rpd = receipts / days
        print(f'  Case {case_idx}: {days}d, {miles:.0f}mi ({mpd:.0f}/day), ${receipts:.2f} (${rpd:.0f}/day)')
        print(f'    Expected: ${expected:.2f}, Got: ${calculated:.2f}, Error: ${error:.2f}')
        
        # Check if this case would be affected by our current penalty logic
        if days >= 7 and rpd > 90 and miles < 800:
            print(f'    *** CURRENTLY PENALIZED: >$90/day spending, <800mi total ***')
        print()

if __name__ == "__main__":
    main() 