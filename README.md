# llm_bio_inf

General repository for LLM-based biological inference tasks.

## 🆕 Uncertainty-Guided Peptide Mutation Generation

A production-ready implementation for generating peptide mutations using uncertainty-guided masking with the pglm-mlm model.

### Quick Start

```python
from uncertainty_guided_mutation import UncertaintyGuidedMutation

# Create mutator
mutator = UncertaintyGuidedMutation(
    target_seq="MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV",
    temp_pept_seq="HELVELLA",
    n_seq_out=10,
)

# Generate mutations
results = mutator.run()
for seq in results["generated_sequences"]:
    print(seq)
```

### With Custom Weights

```python
mutator = UncertaintyGuidedMutation(
    target_seq="...",
    temp_pept_seq="...",
    model_weights="./fine_tuned_model.safetensors",
    n_seq_out=10,
)
results = mutator.run()
```

### Documentation

- **`QUICK_REFERENCE.md`** - Quick lookup for common tasks
- **`UNCERTAINTY_GUIDED_MUTATION_GUIDE.md`** - Comprehensive guide
- **`CUSTOM_WEIGHTS_USAGE.md`** - Loading custom weights
- **`FEATURE_CHECKLIST.md`** - Complete feature list

### Key Features

✅ Uncertainty-driven masking
✅ Peptide-only mutations (target sequence fixed)
✅ Custom model weights support
✅ Multiple masking strategies
✅ Production-ready code

### Testing

```bash
python test_uncertainty_mutation.py
```

### Files

- `uncertainty_guided_mutation.py` - Main implementation
- `test_uncertainty_mutation.py` - Test suite
- Documentation files (see above)
