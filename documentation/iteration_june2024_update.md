# June 2024 Iteration: Black-Box Reimbursement System

## Current Algorithm Structure
- **Base Per Diem**: Varies by trip length (1-day: $120, 2-3 days: $105/day, 4-6 days: $95/day, 7-10 days: $85/day, 11+ days: $75/day)
- **Mileage Component**: Tiered (0-100mi: $0.58/mi, 100-500mi: $0.45/mi, 500+mi: $0.35/mi)
- **Efficiency-Based Receipt Processing**:
  - **Super Productivity Zone (600-900 mi/day)**: Major bonuses, but for 1-day trips, receipts above $1200 are reimbursed at only 0.2x (cap/diminishing return)
  - **Other Efficiency Zones**: Sweet spot (180-220 mi/day), standard, low efficiency, and extreme penalty for >1000 mi/day
- **Special Adjustments**: 5-day bonus, small receipt penalty, rounding bug bonus

## Rationale for High-Receipt Cap (1-Day Super Productivity)
- **Interview Claims**: Kevin and Lisa suggested the system rewards efficiency but is suspicious of extreme cases. However, interviews alone are not sufficient evidence.
- **Data Evidence**: High error cases were consistently 1-day, high-mileage, high-receipt trips. The previous algorithm overestimated these, with errors >$1200. After implementing a cap/diminishing return, maximum error dropped to ~$850, and average error improved.
- **Conclusion**: The cap is justified by observed data, not just interview claims.

## Evidence-Driven Analysis of Interview Claims
- **Supported**: Efficiency-based bonuses (miles/day) and penalties for extreme mileage are strongly supported by data.
- **Partially Supported**: 5-day bonus, small receipt penalty, and rounding bug bonus have some evidence in the data.
- **Not Fully Supported**: Some claims (e.g., calendar effects, department rules, user history) are not yet clearly visible in the error patterns or test results.
- **Contradicted**: No evidence for unlimited bonuses for high receipts; data shows diminishing returns/caps are necessary.

## Next Hypotheses to Test
- Investigate high-receipt, multi-day trips for similar cap/diminishing return patterns
- Explore possible calendar or department effects using modular and statistical analysis
- Test for user history or profile effects if data allows

## Principle: Interview Claims Must Be Backed by Data
Never assume any interviewee is correct without supporting evidence from the results. All changes must be justified by observed data and error analysis, not just anecdotal reports.

## Enhanced Small Receipt Penalty (June 2024)

### Rationale and Evidence
- **Interview Evidence:** Multiple employees (Lisa, Dave, Jennifer) reported that submitting very small receipts, especially for 1-day and 2-day trips, often resulted in lower reimbursements than submitting none at all. This was described as a "trap" for new employees and a source of frustration.
- **Data Evidence:** Analysis of 1-day and 2-day trips with receipts <$30, <$50, and <$100 confirmed that the penalty was real, but the previous penalty (-$20 for receipts <$30) was not always sufficient to match observed outputs. Some cases still produced higher-than-expected reimbursements for small receipts.

### Algorithm Change
- For 1-day trips:
  - If receipts < $30: penalty = -$40
  - If $30 ≤ receipts < $100: penalty = -$20
- For 2-day trips:
  - If receipts < $50: penalty = -$20
- For all other trips: penalty remains -$20 for receipts < $30

### Impact
- This change is designed to better match the observed penalty for small receipts, especially for short trips, and to align with both user experience and data-driven findings.
- The change had a small but measurable effect on average error and should reduce edge-case over-reimbursements for small receipts. 