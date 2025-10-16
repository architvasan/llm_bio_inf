# Getting Started: Uncertainty-Guided Peptide Mutation

## ✅ Pre-Flight Checklist

Before you start, make sure you have:

- [ ] Python 3.8+
- [ ] PyTorch installed
- [ ] transformers library installed
- [ ] safetensors library installed

### Install Dependencies

```bash
pip install torch transformers safetensors
```

## 🚀 Step-by-Step Guide

### Step 1: Verify Installation

```python
# Test imports
from uncertainty_guided_mutation import UncertaintyGuidedMutation
import torch

print("✓ All imports successful")
print(f"✓ CUDA available: {torch.cuda.is_available()}")
```

### Step 2: Run Tests

```bash
python test_uncertainty_mutation.py
```

Expected output:
```
================================================================================
TEST 1: Basic Workflow
================================================================================
Input sequence: MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV<eos>HELVELLA
Peptide starts at token index: XX
Positions to mask (peptide only): [XX, XX, XX]
Masked sequence: ...
✓ Generated sequences:
  1. HELVXLLA
  2. HXLVELLA
  ...
```

### Step 3: Try Basic Example

```python
from uncertainty_guided_mutation import UncertaintyGuidedMutation

# Your sequences
target = "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV"
peptide = "HELVELLA"

# Create mutator
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq=peptide,
    n_seq_out=5,
)

# Generate mutations
results = mutator.run()

# Print results
print("Generated mutations:")
for i, seq in enumerate(results["generated_sequences"], 1):
    print(f"  {i}. {seq}")
```

### Step 4: Try with Custom Weights (Optional)

If you have custom weights:

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq=peptide,
    model_weights="./path/to/your/model.safetensors",
    n_seq_out=5,
)

results = mutator.run()
```

### Step 5: Experiment with Parameters

```python
# Try different masking ratios
for ratio in [0.1, 0.3, 0.5]:
    mutator = UncertaintyGuidedMutation(
        target_seq=target,
        temp_pept_seq=peptide,
        mask_ratio=ratio,
        n_seq_out=3,
    )
    results = mutator.run()
    print(f"\nMask ratio {ratio}:")
    for seq in results["generated_sequences"]:
        print(f"  {seq}")
```

## 📚 Documentation Roadmap

### For Quick Start
1. Read this file (GETTING_STARTED.md)
2. Check `QUICK_REFERENCE.md` for common tasks

### For Understanding
1. Read `UNCERTAINTY_GUIDED_MUTATION_GUIDE.md`
2. Review design decisions section
3. Check validation recommendations

### For Custom Weights
1. Read `CUSTOM_WEIGHTS_USAGE.md`
2. Check usage patterns
3. Review error handling

### For Complete Overview
1. Read `IMPLEMENTATION_COMPLETE.md`
2. Check `FEATURE_CHECKLIST.md`
3. Review `FINAL_SUMMARY.md`

## 🎯 Common Tasks

### Task 1: Generate Mutations with Default Model

```python
from uncertainty_guided_mutation import UncertaintyGuidedMutation

mutator = UncertaintyGuidedMutation(
    target_seq="MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV",
    temp_pept_seq="HELVELLA",
    n_seq_out=10,
)

results = mutator.run()
sequences = results["generated_sequences"]
```

### Task 2: Load Custom Weights

```python
mutator = UncertaintyGuidedMutation(
    target_seq="...",
    temp_pept_seq="...",
    model_weights="./my_model.safetensors",
)

results = mutator.run()
```

### Task 3: Analyze Uncertainty

```python
mutator = UncertaintyGuidedMutation(target, peptide)
results = mutator.run()

uncertainty = results["uncertainty"]
print(f"Mean uncertainty: {uncertainty.mean():.4f}")
print(f"Max uncertainty: {uncertainty.max():.4f}")
print(f"Positions masked: {results['positions_to_mask']}")
```

### Task 4: Try Different Strategies

```python
# Top-K strategy
mutator_topk = UncertaintyGuidedMutation(
    target, peptide,
    mask_strategy="top_k",
    mask_ratio=0.3,
)

# Threshold strategy
mutator_threshold = UncertaintyGuidedMutation(
    target, peptide,
    mask_strategy="threshold",
    uncertainty_threshold=0.5,
)
```

## 🔧 Troubleshooting

### Issue: "CUDA out of memory"
**Solution**: Use CPU
```python
import torch
mutator = UncertaintyGuidedMutation(
    target, peptide,
    device=torch.device("cpu")
)
```

### Issue: "Model not found"
**Solution**: Check model_id
```python
# Verify model exists on HuggingFace
# Default: Bo1015/proteinglm-1b-mlm
```

### Issue: "Weights file not found"
**Solution**: Check file path
```python
import os
weights_path = "./my_model.safetensors"
assert os.path.exists(weights_path), f"File not found: {weights_path}"
```

### Issue: "No sequences generated"
**Solution**: Check n_seq_out
```python
mutator = UncertaintyGuidedMutation(
    target, peptide,
    n_seq_out=10,  # Must be > 0
)
```

## 📊 Expected Output

### Basic Run
```
Input sequence: MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV<eos>HELVELLA
Peptide starts at token index: 75
Uncertainty scores: tensor([0.1234, 0.2345, ...])
Positions to mask (peptide only): [76, 78, 80]
Masked sequence: MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV<eos>HEL[MASK]EL[MASK]A
Generated mutations:
  1. HELVXLLA
  2. HXLVELLA
  3. HELVXLXA
  ...
```

## 🎓 Learning Path

### Beginner
1. Run tests: `python test_uncertainty_mutation.py`
2. Try basic example (Task 1 above)
3. Read `QUICK_REFERENCE.md`

### Intermediate
1. Try different parameters (Task 4 above)
2. Analyze uncertainty (Task 3 above)
3. Read `UNCERTAINTY_GUIDED_MUTATION_GUIDE.md`

### Advanced
1. Load custom weights (Task 2 above)
2. Read `CUSTOM_WEIGHTS_USAGE.md`
3. Integrate with your pipeline
4. Optimize for your use case

## 💡 Tips & Tricks

### Tip 1: Start Small
```python
# Test with small n_seq_out first
mutator = UncertaintyGuidedMutation(
    target, peptide,
    n_seq_out=2,  # Small number for testing
)
```

### Tip 2: Analyze Before Generating
```python
# Check uncertainty distribution first
results = mutator.run()
uncertainty = results["uncertainty"]
print(f"Uncertainty range: {uncertainty.min():.3f} - {uncertainty.max():.3f}")
```

### Tip 3: Use GPU for Speed
```python
import torch
# GPU is auto-detected, but you can force it
mutator = UncertaintyGuidedMutation(
    target, peptide,
    device=torch.device("cuda:0")
)
```

### Tip 4: Batch Multiple Runs
```python
# Reuse mutator for multiple runs
mutator = UncertaintyGuidedMutation(target, peptide)

for i in range(3):
    results = mutator.run()
    print(f"Run {i+1}: {len(results['generated_sequences'])} sequences")
```

## 📞 Need Help?

| Question | Resource |
|----------|----------|
| How do I get started? | This file (GETTING_STARTED.md) |
| What's the quick way? | `QUICK_REFERENCE.md` |
| How does it work? | `UNCERTAINTY_GUIDED_MUTATION_GUIDE.md` |
| How do I load weights? | `CUSTOM_WEIGHTS_USAGE.md` |
| What features exist? | `FEATURE_CHECKLIST.md` |
| What changed? | `CHANGES_SUMMARY.md` |

## ✅ Success Checklist

- [ ] Dependencies installed
- [ ] Tests pass: `python test_uncertainty_mutation.py`
- [ ] Basic example works
- [ ] Can generate mutations
- [ ] Can load custom weights (if needed)
- [ ] Understand uncertainty scores
- [ ] Ready to integrate with your pipeline

## 🎉 You're Ready!

Once you've completed the checklist above, you're ready to:
- Generate uncertainty-guided peptide mutations
- Use custom model weights
- Integrate with your downstream tasks
- Optimize for your specific use case

**Happy mutating!** 🚀

---

## Quick Command Reference

```bash
# Run tests
python test_uncertainty_mutation.py

# Python quick start
python -c "
from uncertainty_guided_mutation import UncertaintyGuidedMutation
m = UncertaintyGuidedMutation('MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV', 'HELVELLA')
r = m.run()
print(r['generated_sequences'])
"
```

---

**Next Step**: Read `QUICK_REFERENCE.md` for common tasks!

