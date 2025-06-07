# Repository Structure

## Overview
This repository contains a black-box reverse engineering project for a receipt reimbursement algorithm. The files have been organized into logical groups for better maintainability.

## 🎯 **Main Solution**
- **`run.sh`** - Main entry point (calls solution/calculate_reimbursement.py)
- **`solution/calculate_reimbursement.py`** - **Current best implementation** (MAE: $125.04)

## 📁 **Directory Structure**

### `solution/` - Current Working Solution
- **`calculate_reimbursement.py`** - Main implementation (rule-based approach)
- `analysis-scripts/` - Data analysis and pattern discovery tools
- `debugging-tools/` - Debugging utilities for troubleshooting

### `experiments/` - Alternative Approaches Tested
- `ml-approaches/` - Machine learning based solutions
  - `calculate_reimbursement_ml_linear.py` - Linear regression approximation
  - `calculate_reimbursement_tree.py` - Decision tree approach  
  - `calculate_reimbursement_hybrid.py` - ML lookup table hybrid
  - `create_ml_lookup.py` - Lookup table generator
  - `extract_model_info.py` - ML model analysis tools

- `rule-based-variants/` - Rule-based algorithm variations
  - `calculate_reimbursement_optimized.py` - ML-optimized coefficients
  - `calculate_reimbursement_fixed.py` - Improved version
  - `calculate_reimbursement_pure.py` - Pure Python attempt
  - `optimize_rule_based.py` - Coefficient optimization scripts

- `evaluation-tools/` - Testing and evaluation utilities
  - `final_eval.py` - Comprehensive performance evaluation
  - `test_compliance.py` - Compliance requirement testing
  - `quick_eval.py` - Quick performance checks

- `documentation-and-analysis/` - Project documentation
  - `FINAL_SOLUTION.md` - Final solution documentation
  - `README_ML_SOLUTION.md` - ML approach documentation

### `ml-solution/` - Full ML Pipeline
- Complete machine learning solution with dependencies
- Training scripts, models, and optimization tools
- **Note**: Not used in production due to dependency requirements

### `archive/` - Historical Files
- `backup-scripts/` - Backup versions of run scripts
- `unused-files/` - Deprecated or unused experimental files

### Other Directories
- `documentation/` - Additional project documentation
- `black-box-reverse-engineering-diagrams/` - Analysis diagrams
- `.git/` - Git version control
- `.cursor/` - IDE configuration

## 🚀 **Usage**

```bash
# Run the main solution
./run.sh <days> <miles> <receipts>

# Example
./run.sh 5 250 150.75
```

## 📊 **Performance Results**

| Approach | MAE | Dependencies | Status |
|----------|-----|--------------|---------|
| **Rule-Based (Current)** | **$125.04** | ✅ None | ✅ **Active** |
| Decision Tree | $136.63 | ✅ None | 🧪 Experimental |
| ML Linear | $286.93 | ✅ None | 🧪 Experimental |
| Random Forest | $43.00 | ❌ scikit-learn | 🚫 Cannot deploy |

## 🔧 **Development Guidelines**

1. **Main solution**: Keep `solution/calculate_reimbursement.py` as the production implementation
2. **Experiments**: Use `experiments/` for trying new approaches
3. **Testing**: Use tools in `experiments/evaluation-tools/` for validation
4. **Documentation**: Update this file when adding new approaches

## 📝 **Key Files to Know**

- **`run.sh`** - Entry point for the solution
- **`solution/calculate_reimbursement.py`** - Core algorithm
- **`experiments/evaluation-tools/final_eval.py`** - Performance testing
- **`public_cases.json`** - Test data
- **`INTERVIEWS.md`** - Business domain knowledge

## 🎯 **Next Steps**

If you want to improve the solution:
1. Use `experiments/evaluation-tools/final_eval.py` to test new approaches
2. Put new experiments in appropriate `experiments/` subdirectories  
3. Update this README when you find improvements
4. Only update `solution/calculate_reimbursement.py` when you have a better solution

---
*Repository organized on June 7, 2024 for better maintainability* 