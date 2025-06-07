#!/usr/bin/env python3
import json
import subprocess

def main():
    # Load public cases for pattern analysis
    with open('../public_cases.json', 'r') as f:
        data = json.load(f)

    print("=== MAGIC NUMBER & PATTERN ANALYSIS ===")
    
    # Analyze rounding patterns (Lisa's observation)
    print("\n1. ROUNDING BUG ANALYSIS:")
    rounding_patterns = {49: [], 99: [], 'other': []}
    
    for i, case in enumerate(data[:50]):
        inp = case['input']
        receipts = inp['total_receipts_amount']
        expected = case['expected_output']
        
        cents = int(round((receipts - int(receipts)) * 100))
        if cents == 49:
            rounding_patterns[49].append((i, receipts, expected))
        elif cents == 99:
            rounding_patterns[99].append((i, receipts, expected))
        else:
            rounding_patterns['other'].append((i, receipts, expected))
    
    print(f"Cases ending in .49 cents: {len(rounding_patterns[49])}")
    print(f"Cases ending in .99 cents: {len(rounding_patterns[99])}")
    print(f"Other cases: {len(rounding_patterns['other'])}")
    
    # Test a few specific cases
    if rounding_patterns[49]:
        case_idx, receipts, expected = rounding_patterns[49][0]
        print(f"  Example .49 case: {case_idx}, ${receipts:.2f} -> ${expected:.2f}")
    
    if rounding_patterns[99]:
        case_idx, receipts, expected = rounding_patterns[99][0]
        print(f"  Example .99 case: {case_idx}, ${receipts:.2f} -> ${expected:.2f}")

    # Analyze "magic numbers" mentioned by Marcus
    print("\n2. POTENTIAL MAGIC NUMBERS:")
    magic_candidates = [847, 623, 1200, 1500, 800]  # From interviews
    
    for magic in magic_candidates:
        close_cases = []
        for i, case in enumerate(data[:100]):
            expected = case['expected_output']
            if abs(expected - magic) < 50:  # Within $50 of magic number
                close_cases.append((i, expected))
        
        if close_cases:
            print(f"  Cases near ${magic}: {len(close_cases)} cases")
            if len(close_cases) <= 3:
                for case_idx, exp in close_cases:
                    print(f"    Case {case_idx}: ${exp:.2f}")

    # Analyze efficiency patterns (Marcus mentioned 300+ miles/day bonuses)
    print("\n3. HIGH EFFICIENCY PATTERNS:")
    high_efficiency_cases = []
    
    for i, case in enumerate(data[:50]):
        inp = case['input']
        days = inp['trip_duration_days']
        miles = inp['miles_traveled']
        expected = case['expected_output']
        
        miles_per_day = miles / days
        if miles_per_day > 250:  # Very high efficiency
            high_efficiency_cases.append((i, days, miles, miles_per_day, expected))
    
    print(f"Cases with >250 mi/day: {len(high_efficiency_cases)}")
    for case_idx, days, miles, mpd, expected in high_efficiency_cases[:3]:
        print(f"  Case {case_idx}: {days}d, {miles}mi ({mpd:.0f}/day) -> ${expected:.2f}")

    # Look for potential calendar effects (day of week, month, etc.)
    print("\n4. SUBTLE PATTERN CHECKS:")
    
    # Check for consistent under/over-reimbursement patterns
    errors = []
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
            error = calculated - expected  # Positive = over-reimburse, negative = under-reimburse
            errors.append((i, days, miles, receipts, expected, calculated, error))
        except:
            continue
    
    # Find systematic patterns
    over_reimburse = [e for e in errors if e[6] > 100]  # Over by $100+
    under_reimburse = [e for e in errors if e[6] < -100]  # Under by $100+
    
    print(f"  Systematic over-reimbursement: {len(over_reimburse)} cases")
    print(f"  Systematic under-reimbursement: {len(under_reimburse)} cases")
    
    if over_reimburse:
        print("  Over-reimbursement pattern examples:")
        for case_idx, days, miles, receipts, expected, calculated, error in over_reimburse[:3]:
            mpd = miles / days
            rpd = receipts / days
            print(f"    Case {case_idx}: {days}d, {mpd:.0f}mi/day, ${rpd:.0f}/day -> Over by ${error:.0f}")
    
    if under_reimburse:
        print("  Under-reimbursement pattern examples:")
        for case_idx, days, miles, receipts, expected, calculated, error in under_reimburse[:3]:
            mpd = miles / days
            rpd = receipts / days
            print(f"    Case {case_idx}: {days}d, {mpd:.0f}mi/day, ${rpd:.0f}/day -> Under by ${-error:.0f}")

if __name__ == "__main__":
    main() 