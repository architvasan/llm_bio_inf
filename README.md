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

### With Modalities & Templates

```python
# Use affibody template
mutator = UncertaintyGuidedMutation(
    target_seq="...",
    temp_pept_seq="",
    modality="affibody",
    use_template=True,
    n_seq_out=10,
)

# Or specify residues to mutate
mutator = UncertaintyGuidedMutation(
    target_seq="...",
    temp_pept_seq="HELVELLA",
    residues_to_mutate=[0, 2, 4, 6],
    n_seq_out=10,
)
```

### Documentation

- **`MODALITY_QUICK_START.md`** - Quick start for new features
- **`MODALITY_AND_RESIDUES_GUIDE.md`** - Comprehensive modality guide
- **`QUICK_REFERENCE.md`** - Quick lookup for common tasks
- **`UNCERTAINTY_GUIDED_MUTATION_GUIDE.md`** - Comprehensive guide
- **`CUSTOM_WEIGHTS_USAGE.md`** - Loading custom weights
- **`NEW_FEATURES_SUMMARY.md`** - Summary of new features

### Key Features

✅ Uncertainty-driven masking
✅ Peptide-only mutations (target sequence fixed)
✅ **Multiple modalities** (affibody, nanobody, affitin)
✅ **Template sequences** for each modality
✅ **Residue-level control** for targeted mutations
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
