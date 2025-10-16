# 🚀 START HERE: New Features Guide

## What's New?

Three major features have been added to your uncertainty-guided mutation system:

### 1. 🧬 Modality Support
Choose from multiple protein scaffolds:
- **Affibody** - Small, compact (58 residues)
- **Nanobody** - Antibody-like (110 residues)
- **Affitin** - Fibronectin-based (94 residues)
- **Custom** - Your own sequence

### 2. 📋 Template Sequences
Use pre-defined sequences for each modality:
- Built-in templates for all modalities
- Option to override with custom templates
- Automatic template selection

### 3. 🎯 Residue-Level Control
Specify exactly which residues to mutate:
- 0-indexed positions in peptide
- Bypass uncertainty-guided selection
- Combine with other strategies

## Quick Examples

### Example 1: Use Affibody Template
```python
from uncertainty_guided_mutation import UncertaintyGuidedMutation

mutator = UncertaintyGuidedMutation(
    target_seq="MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV",
    temp_pept_seq="",
    modality="affibody",
    use_template=True,
    n_seq_out=10,
)

results = mutator.run()
for seq in results["generated_sequences"]:
    print(seq)
```

### Example 2: Mutate Specific Residues
```python
mutator = UncertaintyGuidedMutation(
    target_seq="MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV",
    temp_pept_seq="HELVELLA",
    residues_to_mutate=[0, 2, 4, 6],  # Mutate positions 0, 2, 4, 6
    n_seq_out=8,
)

results = mutator.run()
```

### Example 3: Nanobody with Specific Residues
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="",
    modality="nanobody",
    use_template=True,
    residues_to_mutate=[10, 15, 20, 25, 30],
    n_seq_out=5,
)

results = mutator.run()
```

## New Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `modality` | str | "custom" | Scaffold type |
| `use_template` | bool | False | Use template sequence |
| `custom_template` | str | None | Override template |
| `residues_to_mutate` | List[int] | None | Specific residues |

## Testing

Run the tests to see all features in action:

```bash
python test_uncertainty_mutation.py
```

You'll see:
- TEST 1: Basic Workflow ✓
- TEST 2: Different Masking Strategies ✓
- TEST 3: Uncertainty Analysis ✓
- **TEST 4: Modality Templates ✓** (NEW!)
- **TEST 5: Specific Residue Mutation ✓** (NEW!)
- **TEST 6: Custom Template Override ✓** (NEW!)

## Documentation

### Quick Start (5 minutes)
→ Read: **`MODALITY_QUICK_START.md`**
- One-liner examples
- Common patterns
- Quick reference

### Comprehensive Guide (30 minutes)
→ Read: **`MODALITY_AND_RESIDUES_GUIDE.md`**
- Detailed explanations
- All modalities
- Best practices
- Troubleshooting

### Feature Overview (15 minutes)
→ Read: **`NEW_FEATURES_SUMMARY.md`**
- What's new
- Implementation details
- Usage examples

### Complete Reference
→ Read: **`COMPLETE_FEATURE_OVERVIEW.md`**
- All features
- Parameter reference
- Integration points
- Workflows

## Backward Compatibility

✅ **100% Backward Compatible!**

Your existing code still works:
```python
# Old code still works exactly the same
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq=peptide,
    mask_strategy="top_k",
    mask_ratio=0.3,
    n_seq_out=10,
)
results = mutator.run()
```

## Common Workflows

### Workflow 1: Explore Affibody Space
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="",
    modality="affibody",
    use_template=True,
    mask_ratio=0.25,
    n_seq_out=20,
)
results = mutator.run()
```

### Workflow 2: Optimize CDR Regions
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="",
    modality="nanobody",
    use_template=True,
    residues_to_mutate=[27, 28, 29, 30, 31, 32, 33, 34, 35],
    n_seq_out=10,
)
results = mutator.run()
```

### Workflow 3: Conservative Mutations
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq=peptide,
    mask_ratio=0.1,  # Only 10%
    n_seq_out=5,
)
results = mutator.run()
```

## Modality Comparison

| Modality | Size | Use Case | Best For |
|----------|------|----------|----------|
| Affibody | 58 | Display tech | Compact binders |
| Nanobody | 110 | Therapeutics | Antibody-like |
| Affitin | 94 | Binding proteins | Natural scaffold |
| Custom | Variable | Any sequence | Flexibility |

## Residue Indexing

Residues are 0-indexed in the peptide:

```
Peptide:  H E L V E L L A
Index:    0 1 2 3 4 5 6 7

residues_to_mutate=[0, 3, 7]  # Mutate H, V, A
```

## Output Changes

Results now include:

```python
results = mutator.run()

# New fields:
results["modality"]           # "affibody", "nanobody", etc.
results["peptide_seq"]        # Actual peptide used
results["residues_to_mutate"] # Specified residues (if any)

# Existing fields still there:
results["generated_sequences"]
results["uncertainty"]
results["positions_to_mask"]
# ... etc
```

## Next Steps

### Step 1: Test It (2 minutes)
```bash
python test_uncertainty_mutation.py
```

### Step 2: Read Quick Start (5 minutes)
→ Open: **`MODALITY_QUICK_START.md`**

### Step 3: Try Examples (10 minutes)
- Copy examples from this file
- Modify for your use case
- Run and see results

### Step 4: Read Detailed Guide (30 minutes)
→ Open: **`MODALITY_AND_RESIDUES_GUIDE.md`**

### Step 5: Integrate (varies)
- Use with structure prediction
- Validate with experiments
- Optimize for your target

## Key Features

✅ **Modality Support** - Choose your scaffold  
✅ **Template Sequences** - Pre-defined or custom  
✅ **Residue Control** - Specify exact positions  
✅ **Backward Compatible** - Old code still works  
✅ **Well Documented** - Comprehensive guides  
✅ **Fully Tested** - All features verified  

## Documentation Files

### For Quick Start
- `MODALITY_QUICK_START.md` ← Start here!
- `QUICK_REFERENCE.md`

### For Learning
- `MODALITY_AND_RESIDUES_GUIDE.md`
- `UNCERTAINTY_GUIDED_MUTATION_GUIDE.md`

### For Reference
- `COMPLETE_FEATURE_OVERVIEW.md`
- `NEW_FEATURES_SUMMARY.md`
- `IMPLEMENTATION_SUMMARY.md`

### For Navigation
- `INDEX.md` - Documentation index
- `README.md` - Project overview

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Unknown modality" | Use: affibody, nanobody, affitin, or custom |
| Template not used | Set `use_template=True` |
| Residues not mutated | Check indices are 0 to len(peptide)-1 |
| No sequences | Check `n_seq_out > 0` |

## Support

- **Quick questions?** → `MODALITY_QUICK_START.md`
- **How does it work?** → `MODALITY_AND_RESIDUES_GUIDE.md`
- **All features?** → `COMPLETE_FEATURE_OVERVIEW.md`
- **Run tests?** → `python test_uncertainty_mutation.py`

## Summary

You now have:
- ✅ 3 modalities (affibody, nanobody, affitin)
- ✅ Template sequences for each
- ✅ Residue-level control
- ✅ Custom template override
- ✅ Full backward compatibility
- ✅ Comprehensive documentation
- ✅ Complete test coverage

**Everything is ready to use!** 🚀

---

## 🎯 Your Next Action

**Read**: `MODALITY_QUICK_START.md` (5 minutes)

Then try the examples and run the tests!

Happy mutating! 🧬

