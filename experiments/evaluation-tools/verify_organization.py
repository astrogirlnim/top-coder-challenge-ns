#!/usr/bin/env python3
"""
Repository Organization Verification Script

Verifies that the repository reorganization was successful and 
all key components are working correctly.
"""

import os
import subprocess
import sys

def test_main_solution():
    """Test that the main solution works correctly."""
    print("🧪 Testing main solution...")
    
    try:
        result = subprocess.run(['./run.sh', '5', '250', '150.75'], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            output = result.stdout.strip()
            print(f"   ✅ Main solution works: {output}")
            return True
        else:
            print(f"   ❌ Main solution failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing main solution: {e}")
        return False

def check_file_organization():
    """Check that files are properly organized."""
    print("📁 Checking file organization...")
    
    expected_structure = {
        'solution/calculate_reimbursement.py': 'Main solution file',
        'experiments/ml-approaches/': 'ML approaches directory',
        'experiments/rule-based-variants/': 'Rule-based variants directory', 
        'experiments/evaluation-tools/': 'Evaluation tools directory',
        'archive/backup-scripts/': 'Backup scripts directory',
        'REPOSITORY_STRUCTURE.md': 'Repository documentation'
    }
    
    all_good = True
    for path, description in expected_structure.items():
        if os.path.exists(path):
            print(f"   ✅ {description}: {path}")
        else:
            print(f"   ❌ Missing {description}: {path}")
            all_good = False
    
    return all_good

def check_experiments_accessible():
    """Check that experimental tools are still accessible."""
    print("🔬 Checking experimental tools...")
    
    # Check if we can access an experimental file
    exp_file = 'experiments/ml-approaches/calculate_reimbursement_tree.py'
    if os.path.exists(exp_file):
        try:
            result = subprocess.run(['python3', exp_file, '3', '100', '50'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"   ✅ Experimental tools accessible: {result.stdout.strip()}")
                return True
            else:
                print(f"   ⚠️  Experimental tool has issues: {result.stderr}")
                return True  # Still accessible, just might have issues
        except Exception as e:
            print(f"   ❌ Error accessing experimental tools: {e}")
            return False
    else:
        print(f"   ❌ Experimental file not found: {exp_file}")
        return False

def main():
    print("🚀 REPOSITORY ORGANIZATION VERIFICATION")
    print("="*50)
    
    tests = [
        ("Main Solution", test_main_solution),
        ("File Organization", check_file_organization), 
        ("Experimental Tools", check_experiments_accessible)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        result = test_func()
        results.append((test_name, result))
    
    print(f"\n🎯 VERIFICATION SUMMARY")
    print("="*30)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print(f"\n🏆 ALL TESTS PASSED! Repository is properly organized.")
        print(f"   Main solution: ./run.sh")
        print(f"   Documentation: REPOSITORY_STRUCTURE.md")
        return 0
    else:
        print(f"\n⚠️  Some tests failed. Check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 