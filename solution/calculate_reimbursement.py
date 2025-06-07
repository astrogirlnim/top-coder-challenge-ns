#!/usr/bin/env python3
import sys

def diminishing_receipts(receipts, days):
    if days >= 8:
        first = min(receipts, 350)
        second = min(max(receipts - 350, 0), 650)
        rest = max(receipts - 1000, 0)
        return first + 0.2 * second + 0.05 * rest
    elif days >= 5:
        first = min(receipts, 700)
        rest = max(receipts - 700, 0)
        return first + 0.2 * rest
    else:
        first = min(receipts, 700)
        rest = max(receipts - 700, 0)
        return first + 0.2 * rest

def capped_mileage(miles, days):
    if days == 1:
        first = min(miles, 300)
        rest = max(miles - 300, 0)
        return first + 0.2 * rest
    else:
        return min(miles, 1000)

def main():
    if len(sys.argv) != 4:
        print("Usage: calculate_reimbursement.py <trip_duration_days> <miles_traveled> <total_receipts_amount>")
        sys.exit(1)
    days = int(sys.argv[1])
    miles = float(sys.argv[2])
    receipts = float(sys.argv[3])

    # Derived features
    miles_per_day = miles / days if days > 0 else 0
    receipts_per_day = receipts / days if days > 0 else 0
    miles_per_receipt = miles / (receipts + 1e-6)
    capped_miles = capped_mileage(miles, days)

    # Diminishing returns for receipts
    effective_receipts = diminishing_receipts(receipts, days)

    # Formula (based on regression analysis and new diminishing returns)
    base = 90 * days
    mileage_component = 0.45 * capped_miles + 0.08 * (capped_miles ** 0.9)
    receipts_component = 0.55 * effective_receipts + 0.04 * (effective_receipts ** 0.95)
    interaction = 0.012 * days * effective_receipts + 0.011 * days * capped_miles
    receipts_sq = 0.00002 * (effective_receipts ** 2)
    miles_sq = 0.00001 * (capped_miles ** 2)
    efficiency_bonus = 0
    if 180 <= miles_per_day <= 220 and receipts_per_day < 100:
        efficiency_bonus = 50 * days
    # Small receipts penalty
    penalty = 0
    if receipts < 20:
        penalty -= 0.1 * (20 - receipts)
    # Rounding bug/bonus for .49 or .99
    rounding_bonus = 0
    if str(receipts)[-2:] in ('49', '99'):
        rounding_bonus = 7.5

    reimbursement = (base + mileage_component + receipts_component +
                     interaction + receipts_sq + miles_sq + efficiency_bonus + penalty + rounding_bonus)

    # Hard cap for long trips
    if days == 14:
        reimbursement = min(reimbursement, 1350)
    elif days >= 12:
        reimbursement = min(reimbursement, 1400)

    print(f"{reimbursement:.2f}")

if __name__ == "__main__":
    main() 