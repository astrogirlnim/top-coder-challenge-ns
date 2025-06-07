#!/usr/bin/env python3
import subprocess

def main():
    # Test the new high error cases specifically
    cases = [
        (5, 516, 1878.49, 669.85, "Case 711"),
        (14, 481, 939.99, 877.17, "Case 520"),  
        (4, 69, 2321.49, 322.00, "Case 152"),
        (8, 795, 1645.99, 644.69, "Case 684"),
        (7, 1006, 1181.33, 2279.82, "Case 149")
    ]

    print("=== NEW HIGH ERROR CASES ANALYSIS ===")
    for days, miles, receipts, expected, case_name in cases:
        result = subprocess.run(['python3', 'calculate_reimbursement.py', str(days), str(miles), str(receipts)], 
                              capture_output=True, text=True)
        calculated = float(result.stdout.strip())
        error = abs(expected - calculated)
        mpd = miles / days
        rpd = receipts / days
        
        status = 'OVER-REIMBURSE' if calculated > expected else 'UNDER-REIMBURSE'
        print(f'{case_name}: {days}d, {miles:.0f}mi ({mpd:.0f}/day), ${receipts:.2f} (${rpd:.0f}/day)')
        print(f'  Expected: ${expected:.2f}, Got: ${calculated:.2f}, Error: ${error:.2f} [{status}]')
        
        # Analyze why this might be happening
        if calculated > expected:
            print(f'  *** OVER-REIMBURSING ***')
            if days == 5:
                print(f'    - 5-day trip getting enhanced bonus (base+100, 15% receipt bonus)')
            if rpd > 200:
                print(f'    - Very high spending: ${rpd:.0f}/day')
            if mpd < 100:
                print(f'    - Low efficiency: {mpd:.0f} mi/day')
        else:
            print(f'  *** UNDER-REIMBURSING ***')
            if mpd > 100:
                print(f'    - High efficiency: {mpd:.0f} mi/day - should get better treatment')
                
        print()

if __name__ == "__main__":
    main() 