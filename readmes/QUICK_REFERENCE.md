# Quick Reference: Uncertainty-Guided Peptide Mutation

## One-Liner Examples

### Default Model
```python
from uncertainty_guided_mutation import UncertaintyGuidedMutation
mutator = UncertaintyGuidedMutation("MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV", "HELVELLA")
results = mutator.run()
```

### With Custom Weights
```python
mutator = UncertaintyGuidedMutation("MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV", "HELVELLA", model_weights="./model.safetensors")
results = mutator.run()
```

## Common Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target_seq` | str | Required | Target protein sequence |
| `temp_pept_seq` | str | Required | Peptide to mutate |
| `model_weights` | str | None | Path to .safetensors file |
| `n_seq_out` | int | 10 | Number of sequences to generate |
| `mask_strategy` | str | "top_k" | "top_k", "threshold", or "entropy" |
| `mask_ratio` | float | 0.3 | For top_k: fraction to mask |
| `uncertainty_threshold` | float | 0.5 | For threshold: cutoff value |

## Masking Strategies

### Top-K (Recommended)
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq=peptide,
    mask_strategy="top_k",
    mask_ratio=0.3,  # Mask 30% most uncertain
)
```

### Threshold
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq=peptide,
    mask_strategy="threshold",
    uncertainty_threshold=0.5,  # Mask if uncertainty > 0.5
)
```

## Results Dictionary

```python
results = mutator.run()

# Access results
sequences = results["generated_sequences"]  # List of mutated peptides
uncertainty = results["uncertainty"]        # Uncertainty scores
positions = results["positions_to_mask"]    # Masked token positions
masked_seq = results["masked_seq"]          # Sequence with [MASK]
peptide_idx = results["peptide_start_idx"]  # Where peptide starts
```

## Running Tests

```bash
# Run all tests
python test_uncertainty_mutation.py

# Or in Python
from test_uncertainty_mutation import test_basic_workflow
test_basic_workflow()
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| CUDA out of memory | Use CPU: `device=torch.device("cpu")` |
| Model not found | Check `model_id` is correct |
| Weights file not found | Verify path to `.safetensors` file |
| No sequences generated | Check `n_seq_out` > 0 |
| All positions masked | Reduce `mask_ratio` or `uncertainty_threshold` |

## File Locations

```
uncertainty_guided_mutation.py          # Main implementation
test_uncertainty_mutation.py            # Tests
UNCERTAINTY_GUIDED_MUTATION_GUIDE.md    # Full guide
CUSTOM_WEIGHTS_USAGE.md                 # Weights guide
QUICK_REFERENCE.md                      # This file
```

## Workflow at a Glance

```
1. Create mutator
   ↓
2. Call mutator.run()
   ↓
3. Get results["generated_sequences"]
   ↓
4. Use mutated peptides
```

## Key Methods

```python
mutator = UncertaintyGuidedMutation(...)

# Main method
results = mutator.run()

# Individual steps (if needed)
logprobs, probs, mask_indices = mutator.get_logprobs(seq)
uncertainty = mutator.compute_uncertainty(probs)
peptide_idx = mutator.find_peptide_start_idx(seq)
positions = mutator.select_positions_to_mask(uncertainty, mask_indices, peptide_idx)
masked_seq = mutator.create_masked_sequence(seq, positions)
sequences = mutator.generate_mutations(masked_seq)
```

## Configuration Presets

### Conservative (Few Mutations)
```python
UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq=peptide,
    mask_strategy="top_k",
    mask_ratio=0.1,  # Only 10%
    n_seq_out=5,
)
```

### Moderate (Balanced)
```python
UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq=peptide,
    mask_strategy="top_k",
    mask_ratio=0.3,  # 30%
    n_seq_out=10,
)
```

### Aggressive (Many Mutations)
```python
UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq=peptide,
    mask_strategy="top_k",
    mask_ratio=0.5,  # 50%
    n_seq_out=20,
)
```

## Device Selection

```python
import torch

# Auto-detect (default)
mutator = UncertaintyGuidedMutation(target, peptide)

# Force GPU
mutator = UncertaintyGuidedMutation(
    target, peptide,
    device=torch.device("cuda:0")
)

# Force CPU
mutator = UncertaintyGuidedMutation(
    target, peptide,
    device=torch.device("cpu")
)
```

## Output Examples

```python
results = mutator.run()

# Generated sequences
for seq in results["generated_sequences"]:
    print(seq)
# Output:
# HELVXLLA
# HXLVELLA
# HELVXLXA
# ...

# Uncertainty scores
print(results["uncertainty"])
# tensor([0.1, 0.2, 0.15, 0.3, 0.25, 0.18, 0.22, 0.19])

# Positions masked
print(results["positions_to_mask"])
# [3, 5, 7]  (token indices)
```

## Integration Example

```python
from uncertainty_guided_mutation import UncertaintyGuidedMutation

# Your target and peptide
target = "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV"
peptide = "HELVELLA"

# Generate mutations
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq=peptide,
    model_weights="./my_weights.safetensors",
    n_seq_out=10,
)

results = mutator.run()

# Use generated sequences
for mutated_peptide in results["generated_sequences"]:
    # Do something with mutated_peptide
    print(f"Target: {target}")
    print(f"Mutated: {mutated_peptide}")
    # Could pass to structure prediction, binding affinity, etc.
```

## Performance Tips

1. **Batch processing**: Generate multiple sequences at once with `n_seq_out`
2. **GPU usage**: Use GPU for faster inference
3. **Caching**: Reuse mutator instance for multiple runs
4. **Masking**: Adjust `mask_ratio` to balance exploration vs. stability

## Common Patterns

### Pattern 1: Explore Uncertainty
```python
mutator = UncertaintyGuidedMutation(target, peptide)
results = mutator.run()
print(f"Uncertainty range: {results['uncertainty'].min():.3f} - {results['uncertainty'].max():.3f}")
```

### Pattern 2: Conservative Mutations
```python
mutator = UncertaintyGuidedMutation(target, peptide, mask_ratio=0.1)
results = mutator.run()
```

### Pattern 3: Diverse Mutations
```python
mutator = UncertaintyGuidedMutation(target, peptide, mask_ratio=0.5, n_seq_out=20)
results = mutator.run()
```

## Need Help?

1. Check `UNCERTAINTY_GUIDED_MUTATION_GUIDE.md` for detailed info
2. Check `CUSTOM_WEIGHTS_USAGE.md` for weights loading
3. Run `test_uncertainty_mutation.py` for examples
4. Review docstrings: `help(UncertaintyGuidedMutation)`

