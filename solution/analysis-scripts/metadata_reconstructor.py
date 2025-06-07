#!/usr/bin/env python3

import json
import hashlib
from collections import defaultdict

class MetadataReconstructor:
    """
    Reconstructs likely business metadata from trip patterns.
    
    Based on our pattern analysis, we know there are:
    - User profile clusters (5 main types)
    - Phase-based variations (10 phases with different reimbursement levels)
    - Weekly submission timing effects
    - Department/role-based differences
    - Trip type classifications
    """
    
    def __init__(self):
        # User profiles based on travel patterns
        self.user_profiles = {
            'heavy_traveler': {
                'description': 'High miles, high spending sales reps',
                'base_multiplier': 1.0,
                'receipt_efficiency': 0.4,
                'mileage_bonus': 1.0
            },
            'conference_attendee': {
                'description': 'Low miles, high spending conference/stationary trips',
                'base_multiplier': 1.4,
                'receipt_efficiency': 0.8,
                'mileage_bonus': 5.0  # Moderate per-mile rate for minimal travel
            },
            'budget_conscious': {
                'description': 'Low spending, various mileage',
                'base_multiplier': 0.9,
                'receipt_efficiency': 0.25,
                'mileage_bonus': 2.0
            },
            'efficiency_expert': {
                'description': 'High miles, moderate spending - gets penalized',
                'base_multiplier': 0.6,
                'receipt_efficiency': 0.15,
                'mileage_bonus': 0.1
            },
            'standard_employee': {
                'description': 'Average patterns',
                'base_multiplier': 1.0,
                'receipt_efficiency': 0.4,
                'mileage_bonus': 1.2
            }
        }
        
        # Department profiles (inferred from spending patterns)
        self.departments = {
            'sales': {'budget_flexibility': 1.2, 'efficiency_reward': 1.1},
            'engineering': {'budget_flexibility': 0.8, 'efficiency_reward': 0.9},
            'executive': {'budget_flexibility': 1.5, 'efficiency_reward': 1.0},
            'support': {'budget_flexibility': 0.7, 'efficiency_reward': 1.0},
            'marketing': {'budget_flexibility': 1.1, 'efficiency_reward': 1.05}
        }
    
    def reconstruct_metadata(self, days, miles, receipts):
        """
        Reconstruct likely metadata for a trip based on the input patterns.
        Returns a dictionary with reconstructed business context.
        """
        metadata = {}
        
        # Calculate derived metrics
        miles_per_day = miles / days
        receipts_per_day = receipts / days
        receipts_per_mile = receipts / (miles + 1)
        
        # === USER PROFILE RECONSTRUCTION ===
        metadata['user_profile'] = self._classify_user_profile(miles_per_day, receipts_per_day, days)
        
        # === SUBMISSION TIMING RECONSTRUCTION ===
        # Use deterministic hash of inputs to simulate submission patterns
        submission_hash = self._generate_submission_hash(days, miles, receipts)
        
        # Submission phase (0-9, affects reimbursement level)
        metadata['submission_phase'] = submission_hash % 10
        
        # Day of week submitted (affects weekly correlation)
        metadata['submission_day'] = submission_hash % 7
        
        # Quarter effect (Q4 more generous according to interviews)
        metadata['quarter'] = (submission_hash % 4) + 1
        
        # === DEPARTMENT RECONSTRUCTION ===
        metadata['department'] = self._infer_department(miles_per_day, receipts_per_day, days)
        
        # === TRIP TYPE RECONSTRUCTION ===
        metadata['trip_type'] = self._classify_trip_type(days, miles, receipts_per_day)
        
        # === BUDGET PERIOD EFFECTS ===
        # Month within quarter (month 3 of quarter might be more restrictive)
        metadata['month_in_quarter'] = (submission_hash % 3) + 1
        
        # === APPROVAL WORKFLOW RECONSTRUCTION ===
        # Different approval paths based on spending and profile
        metadata['approval_level'] = self._determine_approval_level(receipts, days, metadata['user_profile'])
        
        # === SEASONAL/CALENDAR EFFECTS ===
        # Business seasonality (some "months" are busier/more generous)
        metadata['business_season'] = self._determine_business_season(submission_hash)
        
        return metadata
    
    def _classify_user_profile(self, miles_per_day, receipts_per_day, days):
        """Classify user based on travel patterns from our cluster analysis"""
        
        if miles_per_day > 300 and receipts_per_day > 500:
            return 'heavy_traveler'
        elif miles_per_day < 30 and receipts_per_day > 100:
            return 'conference_attendee'
        elif miles_per_day < 80 and receipts_per_day < 50:
            return 'budget_conscious'
        elif miles_per_day > 400 and 200 < receipts_per_day < 800:
            return 'efficiency_expert'
        else:
            return 'standard_employee'
    
    def _generate_submission_hash(self, days, miles, receipts):
        """Generate deterministic hash for submission timing simulation"""
        # Use input characteristics to create consistent "submission timing"
        hash_input = f"{days}:{miles:.2f}:{receipts:.2f}"
        return int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
    
    def _infer_department(self, miles_per_day, receipts_per_day, days):
        """Infer department based on travel patterns"""
        
        # High travel, high spending -> Sales
        if miles_per_day > 200 and receipts_per_day > 200:
            return 'sales'
        
        # Low travel, high spending, long trips -> Executive
        elif miles_per_day < 50 and receipts_per_day > 150 and days >= 7:
            return 'executive'
        
        # Moderate travel, moderate spending -> Marketing
        elif 50 <= miles_per_day <= 200 and 50 <= receipts_per_day <= 200:
            return 'marketing'
        
        # Low spending regardless of travel -> Engineering/Support
        elif receipts_per_day < 50:
            return 'engineering' if miles_per_day > 100 else 'support'
        
        else:
            return 'support'  # Default
    
    def _classify_trip_type(self, days, receipts_per_day, miles):
        """Classify the type of business trip"""
        
        if days == 1 and miles > 400:
            return 'day_trip_intensive'
        elif days >= 7 and receipts_per_day < 50:
            return 'extended_project'
        elif receipts_per_day > 200 and days <= 3:
            return 'client_meeting'
        elif days >= 5 and receipts_per_day > 150:
            return 'conference'
        elif miles > 800 and days <= 5:
            return 'territory_coverage'
        else:
            return 'standard_business'
    
    def _determine_approval_level(self, receipts, days, user_profile):
        """Determine approval workflow level based on spending and profile"""
        
        total_estimated_cost = receipts + (days * 150)  # Rough total cost estimate
        
        if total_estimated_cost > 2000 or user_profile == 'executive':
            return 'executive_approval'
        elif total_estimated_cost > 1000 or days >= 7:
            return 'manager_approval'
        elif user_profile in ['heavy_traveler', 'conference_attendee']:
            return 'auto_approval'
        else:
            return 'standard_approval'
    
    def _determine_business_season(self, hash_value):
        """Determine business seasonality effects"""
        season_code = hash_value % 12  # 12 "months"
        
        if season_code in [8, 9, 10]:  # "Q4" - more generous
            return 'high_budget'
        elif season_code in [0, 1]:   # "Q1" - restrictive after holidays
            return 'low_budget'
        elif season_code in [5, 6]:   # "Mid-year" - moderate
            return 'moderate_budget'
        else:
            return 'standard_budget'

def test_metadata_reconstruction():
    """Test the metadata reconstruction on some sample cases"""
    
    reconstructor = MetadataReconstructor()
    
    test_cases = [
        (7, 1006, 1181.33),  # High-error case 149
        (14, 481, 939.99),   # High-error case 520
        (7, 901, 136.8),     # High-error case 455
        (1, 822, 2170.53),   # High-error case 157
        (5, 126, 696.14),    # Test case
    ]
    
    print("=== METADATA RECONSTRUCTION TEST ===")
    for days, miles, receipts in test_cases:
        metadata = reconstructor.reconstruct_metadata(days, miles, receipts)
        print(f"\nTrip: {days} days, {miles} miles, ${receipts} receipts")
        print(f"  User Profile: {metadata['user_profile']}")
        print(f"  Department: {metadata['department']}")
        print(f"  Trip Type: {metadata['trip_type']}")
        print(f"  Submission Phase: {metadata['submission_phase']}")
        print(f"  Submission Day: {metadata['submission_day']}")
        print(f"  Quarter: Q{metadata['quarter']}")
        print(f"  Business Season: {metadata['business_season']}")
        print(f"  Approval Level: {metadata['approval_level']}")

if __name__ == "__main__":
    test_metadata_reconstruction() 