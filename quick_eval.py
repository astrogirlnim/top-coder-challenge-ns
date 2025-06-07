#!/usr/bin/env python3
"""
Quick evaluation script - tests on subset of cases for speed (no external dependencies)
"""

import json
import time
import subprocess
import os

def load_subset_cases(n=50):
    """Load first n test cases for quick evaluation."""
    with open('public_cases.json', 'r') as f:
        cases = json.load(f)
    return cases[:n]

def run_model(script_path, days, miles, receipts):
    """Run a model script and return prediction and timing."""
    start_time = time.time()
    
    try:
        result = subprocess.run([
            script_path, str(days), str(miles), str(receipts)
        ], capture_output=True, text=True, timeout=10)
        
        run_time = time.time() - start_time
        
        if result.returncode == 0:
            prediction = float(result.stdout.strip())
            return prediction, run_time, None
        else:
            return None, run_time, result.stderr
            
    except subprocess.TimeoutExpired:
        return None, 10.0, "Timeout"
    except Exception as e:
        return None, time.time() - start_time, str(e)

def calculate_mae(predictions, actuals):
    """Calculate mean absolute error."""
    errors = [abs(p - a) for p, a in zip(predictions, actuals)]
    return sum(errors) / len(errors)

def count_close_matches(predictions, actuals, threshold=1.0):
    """Count predictions within threshold of actual values."""
    return sum(1 for p, a in zip(predictions, actuals) if abs(p - a) <= threshold)

def evaluate_models():
    """Compare original ML model vs optimized model."""
    
    print("⚡ QUICK MODEL EVALUATION")
    print("="*50)
    
    # Load subset of test cases
    cases = load_subset_cases(30)  # Test on 30 cases for speed
    print(f"Testing on {len(cases)} cases...")
    
    # Model configurations
    models = {
        'Original ML': './run_original_ml.sh',
        'Optimized ML': './run.sh'  # Currently pointing to optimized
    }
    
    results = {}
    
    for model_name, script_path in models.items():
        print(f"\n🚀 Testing {model_name}...")
        
        predictions = []
        actual_values = []
        run_times = []
        errors = []
        
        for i, case in enumerate(cases):
            days = case['input']['trip_duration_days']
            miles = case['input']['miles_traveled']
            receipts = case['input']['total_receipts_amount']
            expected = case['expected_output']
            
            prediction, run_time, error = run_model(script_path, days, miles, receipts)
            
            if prediction is not None:
                predictions.append(prediction)
                actual_values.append(expected)
                run_times.append(run_time)
            else:
                errors.append(f"Case {i}: {error}")
            
            if (i + 1) % 10 == 0:
                print(f"  Processed {i+1}/{len(cases)} cases...")
        
        # Calculate metrics
        if predictions:
            # Accuracy metrics
            mae = calculate_mae(predictions, actual_values)
            exact_matches = count_close_matches(predictions, actual_values, 0.01)
            close_matches = count_close_matches(predictions, actual_values, 1.0)
            
            # Speed metrics
            avg_runtime = sum(run_times) / len(run_times)
            total_runtime = sum(run_times)
            
            results[model_name] = {
                'mae': mae,
                'exact_matches': exact_matches,
                'close_matches': close_matches,
                'total_cases': len(predictions),
                'avg_runtime': avg_runtime,
                'total_runtime': total_runtime,
                'errors': len(errors)
            }
            
            print(f"  ✅ MAE: ${mae:.2f}")
            print(f"  ✅ Close matches: {close_matches}/{len(predictions)} ({close_matches/len(predictions)*100:.1f}%)")
            print(f"  ✅ Avg runtime: {avg_runtime*1000:.1f}ms")
            print(f"  ✅ Total time: {total_runtime:.2f}s")
            if errors:
                print(f"  ⚠️  Errors: {len(errors)}")
        else:
            print(f"  ❌ No successful predictions")
            results[model_name] = {'error': 'No successful predictions', 'errors': errors}
    
    # Compare results
    print(f"\n📊 COMPARISON RESULTS")
    print("="*50)
    
    if len(results) == 2:
        models_list = list(results.keys())
        orig = results[models_list[0]]
        opt = results[models_list[1]]
        
        if 'mae' in orig and 'mae' in opt:
            # Accuracy comparison
            mae_improvement = (orig['mae'] - opt['mae']) / orig['mae'] * 100
            orig_close_rate = orig['close_matches'] / orig['total_cases'] * 100
            opt_close_rate = opt['close_matches'] / opt['total_cases'] * 100
            close_improvement = opt_close_rate - orig_close_rate
            
            # Speed comparison  
            speed_improvement = (orig['avg_runtime'] - opt['avg_runtime']) / orig['avg_runtime'] * 100
            
            print(f"Accuracy Changes:")
            print(f"  MAE: ${orig['mae']:.2f} → ${opt['mae']:.2f} ({mae_improvement:+.1f}%)")
            print(f"  Close matches: {orig['close_matches']}/{orig['total_cases']} → {opt['close_matches']}/{opt['total_cases']}")
            print(f"  Close rate: {orig_close_rate:.1f}% → {opt_close_rate:.1f}% ({close_improvement:+.1f}%)")
            
            print(f"\nSpeed Changes:")
            print(f"  Avg runtime: {orig['avg_runtime']*1000:.1f}ms → {opt['avg_runtime']*1000:.1f}ms ({speed_improvement:+.1f}%)")
            print(f"  Total time: {orig['total_runtime']:.2f}s → {opt['total_runtime']:.2f}s")
            
            if speed_improvement > 0 and mae_improvement > -5:  # Speed up with minimal accuracy loss
                print(f"\n🏆 OPTIMIZATION SUCCESS!")
                print(f"   Speed improved by {speed_improvement:.1f}% with minimal accuracy impact")
            elif mae_improvement > 0:
                print(f"\n🎯 ACCURACY IMPROVEMENT!")
                print(f"   Accuracy improved by {mae_improvement:.1f}%")
            else:
                print(f"\n📝 MIXED RESULTS")
                print(f"   Trade-offs detected between speed and accuracy")
    
    return results

if __name__ == "__main__":
    evaluate_models() 