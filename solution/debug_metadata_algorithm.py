#!/usr/bin/env python3

import sys
from metadata_reconstructor import MetadataReconstructor

def debug_case(days, miles, receipts, expected=None):
    """Debug a specific case to understand the calculation breakdown"""
    
    print(f"\n=== DEBUGGING CASE: {days} days, {miles} miles, ${receipts} receipts ===")
    if expected:
        print(f"Expected: ${expected:.2f}")
    
    # Step 1: Reconstruct metadata
    reconstructor = MetadataReconstructor()
    metadata = reconstructor.reconstruct_metadata(days, miles, receipts)
    
    print(f"\nReconstructed Metadata:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")
    
    # Step 2: Get profile parameters
    user_profile = metadata['user_profile']
    profile_params = reconstructor.user_profiles[user_profile]
    department = metadata['department']
    dept_params = reconstructor.departments[department]
    
    print(f"\nProfile Parameters ({user_profile}):")
    for key, value in profile_params.items():
        print(f"  {key}: {value}")
    
    print(f"\nDepartment Parameters ({department}):")
    for key, value in dept_params.items():
        print(f"  {key}: {value}")
    
    # Step 3: Break down calculation
    print(f"\n=== CALCULATION BREAKDOWN ===")
    
    miles_per_day = miles / days
    receipts_per_day = receipts / days
    
    # Base calculation
    if user_profile == 'conference_attendee':
        base_component = 120 * days * profile_params['base_multiplier']
        print(f"Base: 120 * {days} * {profile_params['base_multiplier']} = ${base_component:.2f}")
        
        mileage_component = miles * profile_params['mileage_bonus']
        print(f"Mileage: {miles} * {profile_params['mileage_bonus']} = ${mileage_component:.2f}")
        
        # Conference receipt calculation
        if receipts <= 800:
            receipt_component = receipts * 0.8
            print(f"Receipts: {receipts} * 0.8 = ${receipt_component:.2f}")
        elif receipts <= 1500:
            receipt_component = 800 * 0.8 + (receipts - 800) * 0.7
            print(f"Receipts: 800*0.8 + ({receipts}-800)*0.7 = ${receipt_component:.2f}")
        else:
            receipt_component = 800 * 0.8 + 700 * 0.7 + (receipts - 1500) * 0.5
            print(f"Receipts: 800*0.8 + 700*0.7 + ({receipts}-1500)*0.5 = ${receipt_component:.2f}")
    
    elif user_profile == 'heavy_traveler':
        base_component = 100 * days * profile_params['base_multiplier']
        print(f"Base: 100 * {days} * {profile_params['base_multiplier']} = ${base_component:.2f}")
        
        # Standard mileage calculation
        if miles <= 100:
            mileage_component = miles * 0.58 * profile_params['mileage_bonus']
        elif miles <= 500:
            mileage_component = 100 * 0.58 * profile_params['mileage_bonus'] + (miles - 100) * 0.45 * profile_params['mileage_bonus']
        else:
            mileage_component = 100 * 0.58 * profile_params['mileage_bonus'] + 400 * 0.45 * profile_params['mileage_bonus'] + (miles - 500) * 0.35 * profile_params['mileage_bonus']
        print(f"Mileage (tiered): ${mileage_component:.2f}")
        
        # Standard receipt calculation
        efficiency = profile_params['receipt_efficiency']
        if receipts <= 400:
            receipt_component = receipts * efficiency
        elif receipts <= 1000:
            receipt_component = 400 * efficiency + (receipts - 400) * efficiency * 0.8
        elif receipts <= 1600:
            receipt_component = 400 * efficiency + 600 * efficiency * 0.8 + (receipts - 1000) * efficiency * 0.6
        else:
            receipt_component = 400 * efficiency + 600 * efficiency * 0.8 + 600 * efficiency * 0.6 + (receipts - 1600) * efficiency * 0.3
        print(f"Receipts (efficiency {efficiency}): ${receipt_component:.2f}")
    
    else:
        # Other profiles - simplified display
        if user_profile == 'efficiency_expert':
            base_component = 80 * days * profile_params['base_multiplier']
        elif user_profile == 'budget_conscious':
            base_component = 90 * days * profile_params['base_multiplier']
        else:
            base_component = 100 * days * profile_params['base_multiplier']
        print(f"Base: ${base_component:.2f}")
        
        # Approximate mileage and receipt calculations
        mileage_component = miles * 0.4 * profile_params['mileage_bonus']  # Rough estimate
        receipt_component = receipts * profile_params['receipt_efficiency'] * 0.7  # Rough estimate
        print(f"Mileage (approx): ${mileage_component:.2f}")
        print(f"Receipts (approx): ${receipt_component:.2f}")
    
    print(f"\nBefore adjustments: ${base_component + mileage_component + receipt_component:.2f}")
    
    # Apply department adjustments
    base_component *= dept_params['budget_flexibility']
    if miles_per_day > 150:
        mileage_component *= dept_params['efficiency_reward']
        print(f"High efficiency bonus applied ({dept_params['efficiency_reward']})")
    
    print(f"After department adjustments: ${base_component + mileage_component + receipt_component:.2f}")
    
    # Trip type adjustments
    trip_type = metadata['trip_type']
    print(f"Trip type: {trip_type}")
    
    # Apply all multipliers
    total = base_component + mileage_component + receipt_component
    
    # Phase and weekly multipliers
    phase_multipliers = [0.92, 1.02, 1.08, 1.12, 1.10, 1.05, 1.09, 1.07, 1.06, 1.03]
    weekly_multipliers = [1.01, 1.02, 1.00, 0.99, 1.05, 0.98, 1.01]
    
    phase_mult = phase_multipliers[metadata['submission_phase']]
    weekly_mult = weekly_multipliers[metadata['submission_day']]
    
    print(f"Phase multiplier: {phase_mult}")
    print(f"Weekly multiplier: {weekly_mult}")
    
    total *= phase_mult * weekly_mult
    
    print(f"After timing effects: ${total:.2f}")
    
    # Apply bounds
    if total > 2500:
        print(f"CAPPED at $2500 (was ${total:.2f})")
        total = 2500
    
    print(f"FINAL RESULT: ${total:.2f}")
    
    if expected:
        error = abs(total - expected)
        print(f"ERROR: ${error:.2f}")
        
        if error > 1000:
            print(f"*** HIGH ERROR CASE ***")
            if user_profile == 'conference_attendee':
                print("  - Conference attendee profile may be over-generous")
            if total >= 2500:
                print("  - Hit upper bound, calculation is too high")

def main():
    if len(sys.argv) < 4:
        # Debug the high-error cases from the evaluation
        high_error_cases = [
            (4, 69, 2321.49, 322.00),    # Case 152
            (11, 740, 1171.99, 902.09),  # Case 367
            (9, 13, 986.41, 1271.52),    # Case 722
            (9, 101, 950.23, 1281.64),   # Case 637
            (8, 221, 936.98, 1287.00),   # Case 706
        ]
        
        for days, miles, receipts, expected in high_error_cases:
            debug_case(days, miles, receipts, expected)
    else:
        days = int(sys.argv[1])
        miles = float(sys.argv[2])
        receipts = float(sys.argv[3])
        expected = float(sys.argv[4]) if len(sys.argv) > 4 else None
        debug_case(days, miles, receipts, expected)

if __name__ == "__main__":
    main() 