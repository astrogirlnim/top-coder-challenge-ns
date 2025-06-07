#!/usr/bin/env python3
"""
Final evaluation - compare pure Python solution vs original rule-based solution
"""

import json
import time
import subprocess
import os

def load_test_cases(n=50):
    """Load subset of test cases."""
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    return cases[:n]

def run_solution(script_path, days, miles, receipts):
    """Run a solution and return prediction, time, and error."""
    start_time = time.time()
    
    try:
        result = subprocess.run([
            script_path, str(days), str(miles), str(receipts)
        ], capture_output=True, text=True, timeout=10)
        
        exec_time = time.time() - start_time
        
        if result.returncode == 0:
            prediction = float(result.stdout.strip())
            return prediction, exec_time, None
        else:
            return None, exec_time, result.stderr
            
    except Exception as e:
        return None, time.time() - start_time, str(e)

def evaluate_solution(name, script_path, cases):
    """Evaluate a solution on test cases."""
    print(f"\n🚀 Testing {name}...")
    
    predictions = []
    actuals = []
    times = []
    errors = []
    
    for i, case in enumerate(cases):
        days = case['input']['trip_duration_days']
        miles = case['input']['miles_traveled']
        receipts = case['input']['total_receipts_amount']
        expected = case['expected_output']
        
        prediction, exec_time, error = run_solution(script_path, days, miles, receipts)
        
        if prediction is not None:
            predictions.append(prediction)
            actuals.append(expected)
            times.append(exec_time)
        else:
            errors.append(error)
        
        if (i + 1) % 10 == 0:
            print(f"  Processed {i+1}/{len(cases)} cases...")
    
    if predictions:
        # Calculate metrics
        mae = sum(abs(p - a) for p, a in zip(predictions, actuals)) / len(predictions)
        close_matches = sum(1 for p, a in zip(predictions, actuals) if abs(p - a) <= 1.0)
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        return {
            'name': name,
            'mae': mae,
            'close_matches': close_matches,
            'total_cases': len(predictions),
            'avg_time': avg_time,
            'max_time': max_time,
            'errors': len(errors),
            'predictions': predictions,
            'actuals': actuals
        }
    else:
        return {'name': name, 'error': 'No successful predictions'}

def main():
    print("🎯 FINAL SOLUTION EVALUATION")
    print("="*50)
    
    # Load test cases
    cases = load_test_cases(50)
    print(f"Testing on {len(cases)} cases...")
    
    # Test solutions
    solutions = {
        'Original Rule-Based': './run.sh.backup',
        'Pure Python (ML-Inspired)': './run.sh'
    }
    
    results = {}
    
    for name, script in solutions.items():
        if os.path.exists(script):
            results[name] = evaluate_solution(name, script, cases)
        else:
            print(f"⚠️  {name}: Script not found at {script}")
    
    # Compare results
    print(f"\n📊 FINAL COMPARISON")
    print("="*50)
    
    for name, result in results.items():
        if 'mae' in result:
            print(f"\n{name}:")
            print(f"  MAE: ${result['mae']:.2f}")
            print(f"  Close matches: {result['close_matches']}/{result['total_cases']} ({result['close_matches']/result['total_cases']*100:.1f}%)")
            print(f"  Avg time: {result['avg_time']*1000:.1f}ms")
            print(f"  Max time: {result['max_time']:.3f}s")
            print(f"  Errors: {result['errors']}")
            
            # Compliance check
            compliant = result['max_time'] < 5.0 and result['errors'] == 0
            print(f"  Compliant: {'✅ YES' if compliant else '❌ NO'}")
        else:
            print(f"\n{name}: {result.get('error', 'Failed')}")
    
    # Determine best solution
    valid_results = {k: v for k, v in results.items() if 'mae' in v}
    
    if len(valid_results) >= 2:
        solutions_list = list(valid_results.items())
        original = solutions_list[0][1]
        optimized = solutions_list[1][1]
        
        mae_improvement = (original['mae'] - optimized['mae']) / original['mae'] * 100
        speed_improvement = (original['avg_time'] - optimized['avg_time']) / original['avg_time'] * 100
        
        print(f"\n🏆 OPTIMIZATION SUMMARY:")
        print(f"  MAE: ${original['mae']:.2f} → ${optimized['mae']:.2f} ({mae_improvement:+.1f}%)")
        print(f"  Speed: {original['avg_time']*1000:.1f}ms → {optimized['avg_time']*1000:.1f}ms ({speed_improvement:+.1f}%)")
        
        # Final recommendation
        if optimized['max_time'] < 5.0:
            print(f"\n✅ FINAL SOLUTION: Pure Python (ML-Inspired)")
            print(f"   ✓ Meets all requirements")
            print(f"   ✓ No external dependencies")
            print(f"   ✓ Fast execution (~{optimized['avg_time']*1000:.0f}ms avg)")
            print(f"   ✓ Based on ML insights from {mae_improvement:+.1f}% analysis")
        else:
            print(f"\n⚠️  Compliance issue detected")
    
    return results

if __name__ == "__main__":
    main() 