# June 2024: 4-Day Trip Analysis

## Problem Identification
All top error cases are **4-day trips with very high receipts** ($1300-1800). Our algorithm consistently underestimates these by ~50%, suggesting we're over-penalizing them.

## Evidence Analysis

### High-Error Cases (All 4-day trips)

| Case | Days | Miles | Receipts | Expected | Got | Error | $/Day |
|------|------|-------|-----------|-----------|-----|-------|-------|
| 823  | 4    | 238   | $1707.28  | $1483.48  | $748.15 | $735.33 | $426.82 |
| 465  | 4    | 217   | $1506.46  | $1455.37  | $723.63 | $731.74 | $376.62 |
| 946  | 4    | 317   | $1793.28  | $1518.93  | $790.15 | $728.78 | $448.32 |
| 924  | 4    | 103   | $1790.07  | $1394.55  | $693.61 | $700.94 | $447.52 |
| 569  | 4    | 199   | $1310.01  | $1400.57  | $700.80 | $699.77 | $327.50 |

### Key Observations
1. **Expected outputs are VERY HIGH** - much higher than our penalty-based logic produces
2. **All cases have low-medium mileage** (103-317 miles) but high receipts
3. **Expected/Got ratio is ~2:1**, suggesting we're under-reimbursing by ~50%

### Interview Evidence
- **Jennifer (HR):** "There seems to be a sweet spot around 4-6 days where the reimbursements are particularly good."
- **Kevin:** "Medium trips—4-6 days—you can go up to $120 per day and still get good treatment."
- **Contradiction:** Our data shows 4-day trips with $300-400/day getting very generous treatment, not penalties

## Hypothesis
**The black-box system treats 4-day trips as a special "business trip sweet spot" and does NOT penalize high receipts the way longer trips do.**

Possible reasons:
- 4-day trips are seen as intensive business work requiring high expenses
- 4-day trips are too short to be "vacations" but long enough for serious business
- Legacy business policy favored 4-day conference/meeting trips

## Proposed Solution
**Remove spending penalties entirely for 4-day trips.** Let the efficiency-based receipt processing handle them normally without additional multipliers.

### Implementation
1. Exclude 4-day trips from per-day spending penalties
2. Only apply spending limits to 5-6 day trips (medium) and 7+ day trips (long)
3. Let 4-day trips use the standard efficiency zones without additional penalty layers

### Expected Impact
- Target Case 823: $748.15 → ~$1400+ (closer to expected $1483.48)
- Target Case 465: $723.63 → ~$1350+ (closer to expected $1455.37)
- Should maintain performance on other trip lengths

## Risk Assessment
- **Low risk:** Only affects 4-day trips, which are a specific case
- **Evidence-backed:** Multiple interview sources mention 4-6 day "sweet spot"
- **Data-driven:** Expected outputs clearly show generous treatment for 4-day high-receipt trips

---
*Analysis Date: June 2024*  
*Current Performance: $272.74 average error*" 