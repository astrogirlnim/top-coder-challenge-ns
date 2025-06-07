# June 2024 High-Error Case Targeting Iteration

## Summary
- Targeted the largest remaining error classes: (1) 5–8 day trips with very high receipts, and (2) 1-day trips with extreme mileage and receipts.
- Used both interview evidence (especially Kevin and Lisa) and error case data to guide new logic.

## Interview Tie-Ins
- Kevin: "Optimal" per-day spending for 4–6 day trips is <$120/day, for longer trips <$90/day. High spending triggers penalties ("vacation penalty").
- Lisa: Diminishing returns and penalties for high receipts, especially on long trips.
- Kevin: For 1-day, very high mileage/receipts, bonuses drop off but penalty may be too severe; a "soft landing" is likely.

## Algorithm Changes
- **Per-Day Spending Penalty:**
  - For trips of 4–6 days, if receipts per day > $120, subtract a penalty from the receipt component.
  - For trips of 7+ days, if receipts per day > $90, subtract a larger penalty.
- **Softened 1-Day Extreme Penalty:**
  - For 1-day trips with >1000 miles and receipts > $1000, apply a softer penalty: 0.1x for first $1000, 0.4x for the rest.

## Expected Impact
- Should reduce overestimation for high-receipt, medium/long trips and underestimation for 1-day, high-receipt, high-mileage trips.
- Designed to increase close matches and lower average error.

## Evidence-Driven, Trackable Iteration
- This file documents the rationale, changes, and expected impact for this specific iteration, enabling backtracking and comparison. 