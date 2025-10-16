# New Features Summary: Modality & Residue Selection

## 🎯 What's New

Three major new features have been added to the uncertainty-guided mutation system:

### 1. **Modality Support**
Specify the type of protein scaffold you're optimizing:
- **Affibody** - Small, compact binding proteins (~58 residues)
- **Nanobody** - Single-domain antibodies (~110 residues)
- **Affitin** - Fibronectin-based scaffolds (~94 residues)
- **Custom** - Your own peptide sequences

### 2. **Template Sequences**
Use pre-defined, well-characterized sequences for each modality:
- Built-in templates for affibody, nanobody, and affitin
- Option to override with custom templates
- Automatic template selection based on modality

### 3. **Residue-Level Control**
Specify exactly which residues to mutate:
- Provide a list of residue indices (0-indexed)
- Bypass uncertainty-guided selection
- Combine with specific masking strategies

## 📝 New Parameters

### `modality` (str, default: "custom")
The type of protein scaffold:
```python
modality="affibody"   # Use affibody scaffold
modality="nanobody"   # Use nanobody scaffold
modality="affitin"    # Use affitin scaffold
modality="custom"     # Use custom peptide
```

### `use_template` (bool, default: False)
Whether to use the template sequence for the modality:
```python
use_template=True   # Use template sequence
use_template=False  # Use temp_pept_seq
```

### `custom_template` (str, default: None)
Override the default template with your own sequence:
```python
custom_template="MYOWNSEQUENCE"  # Use this instead of default
custom_template=None             # Use default template
```

### `residues_to_mutate` (List[int], default: None)
Specify which residues to mutate (0-indexed in peptide):
```python
residues_to_mutate=[0, 2, 4, 6]  # Mutate positions 0, 2, 4, 6
residues_to_mutate=None          # Auto-select (uncertainty-guided)
```

## 🔧 Implementation Details

### New Methods

#### `get_template_sequence()`
Returns the template sequence for the specified modality.

#### `get_peptide_sequence()`
Returns the peptide sequence to use (template or provided).

#### `convert_residue_indices_to_token_indices()`
Converts residue indices (0-indexed in peptide) to token indices in the full sequence.

### Updated Methods

#### `select_positions_to_mask()`
Now checks for `residues_to_mutate` first:
- If specified, uses those positions
- Otherwise, uses uncertainty-guided selection

#### `run()`
Now includes:
- Modality information in output
- Peptide sequence used
- Residues mutated (if specified)

### New Constants

```python
MODALITY_TEMPLATES = {
    "affibody": "VDNKFNKELSVAGREIVTLPNLNDPQKKAFIFSLWDDPSQSANLLAEAKKLNDAQAPK",
    "nanobody": "AQVQLQESGGGLVQAGGSLRLSCAASERTFSTYAMGWFRQAPGREREFLAQINWSGTTTYYAESVKDRTTISRDNAKNTVYLEMNNLNADDTGIYFCAAHPQRGWGSTLGWTYWGQGTQVTVSSGGGGSGGGKPIPNPLLGLDSTRTGHHHHHH",
    "affitin": "MRGSHHHHHHGSVKVKFVSSGEEKEVDTSKIKKVWRNLTKYGTIVQFTYDDNGKTGRGYVRELDAPKELLDMLARAEGKLN",
}
```

## 📊 Output Changes

Results dictionary now includes:

```python
results = mutator.run()

{
    "input_seq": str,                    # Full input sequence
    "peptide_seq": str,                  # Peptide sequence used (NEW!)
    "modality": str,                     # Modality used (NEW!)
    "uncertainty": torch.Tensor,         # Uncertainty scores
    "peptide_start_idx": int,            # Where peptide starts
    "positions_to_mask": List[int],      # Token positions masked
    "masked_seq": str,                   # Sequence with [MASK]
    "generated_sequences": List[str],    # Generated mutations
    "residues_to_mutate": List[int],     # Residues mutated (NEW!)
}
```

## 💡 Usage Examples

### Example 1: Affibody with Uncertainty
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="",
    modality="affibody",
    use_template=True,
    mask_strategy="top_k",
    mask_ratio=0.2,
    n_seq_out=10,
)
results = mutator.run()
```

### Example 2: Nanobody with Specific Residues
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

### Example 3: Custom Peptide with Specific Residues
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="HELVELLA",
    modality="custom",
    residues_to_mutate=[0, 2, 4, 6],
    n_seq_out=8,
)
results = mutator.run()
```

### Example 4: Custom Template
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="",
    modality="affibody",
    use_template=True,
    custom_template="MYOWNSEQUENCE",
    n_seq_out=5,
)
results = mutator.run()
```

## 🧪 Testing

New tests have been added to `test_uncertainty_mutation.py`:

- **TEST 4**: Modality Templates - Tests all three modalities
- **TEST 5**: Specific Residue Mutation - Tests residue selection
- **TEST 6**: Custom Template Override - Tests custom templates

Run tests:
```bash
python test_uncertainty_mutation.py
```

## 📚 Documentation

### New Documentation Files

1. **`MODALITY_AND_RESIDUES_GUIDE.md`**
   - Comprehensive guide to all features
   - Detailed examples for each modality
   - Best practices and tips

2. **`MODALITY_QUICK_START.md`**
   - Quick reference for common patterns
   - One-liner examples
   - Decision tree for choosing options

3. **`NEW_FEATURES_SUMMARY.md`** (this file)
   - Overview of new features
   - Implementation details
   - Quick reference

## 🔄 Backward Compatibility

✅ **Fully backward compatible!**

Existing code continues to work without changes:

```python
# Old code still works
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq=peptide,
    mask_strategy="top_k",
    mask_ratio=0.3,
    n_seq_out=10,
)
results = mutator.run()
```

Default values ensure no breaking changes:
- `modality="custom"` - Uses custom peptide
- `use_template=False` - Uses provided sequence
- `residues_to_mutate=None` - Uses uncertainty-guided selection

## 🎓 Quick Decision Guide

### Choose Modality
- **Affibody**: Compact, good for display technologies
- **Nanobody**: Antibody-like, good for therapeutics
- **Affitin**: Natural scaffold, good stability
- **Custom**: Any sequence you want

### Choose Template
- **Use template**: For well-characterized scaffolds
- **Don't use template**: For novel sequences

### Choose Residue Selection
- **Uncertainty-guided**: For exploration
- **Specific residues**: For targeted optimization

## 🚀 Common Workflows

### Workflow 1: Optimize Affibody
```python
mutator = UncertaintyGuidedMutation(
    target_seq=antibody,
    temp_pept_seq="",
    modality="affibody",
    use_template=True,
    mask_ratio=0.25,
    n_seq_out=20,
)
```

### Workflow 2: Mutate CDR Regions
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="",
    modality="nanobody",
    use_template=True,
    residues_to_mutate=[27, 28, 29, 30, 31, 32, 33, 34, 35],
    n_seq_out=10,
)
```

### Workflow 3: Conservative Mutations
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq=peptide,
    modality="custom",
    mask_ratio=0.1,
    n_seq_out=5,
)
```

### Workflow 4: Aggressive Exploration
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq=peptide,
    modality="custom",
    mask_ratio=0.5,
    n_seq_out=30,
)
```

## 📋 Residue Indexing

Residues are 0-indexed within the peptide sequence:

```
Peptide:  H E L V E L L A
Index:    0 1 2 3 4 5 6 7

residues_to_mutate=[0, 3, 7]  # Mutate H, V, A
```

## ✨ Key Benefits

1. **Modality Support**
   - Work with standard scaffolds
   - Use well-characterized templates
   - Easy to switch between modalities

2. **Template Sequences**
   - Pre-defined, validated sequences
   - Easy to override with custom
   - Consistent across projects

3. **Residue-Level Control**
   - Precise targeting
   - Combine with uncertainty
   - Flexible optimization strategies

## 🔗 Integration

These features integrate seamlessly with existing functionality:

- ✅ Works with custom model weights
- ✅ Works with all masking strategies
- ✅ Works with GPU/CPU
- ✅ Works with all existing parameters

## 📞 Support

For more information:
- **Quick start**: See `MODALITY_QUICK_START.md`
- **Detailed guide**: See `MODALITY_AND_RESIDUES_GUIDE.md`
- **Examples**: See `uncertainty_guided_mutation.py` main section
- **Tests**: Run `python test_uncertainty_mutation.py`

## ✅ Checklist

- [x] Modality support implemented
- [x] Template sequences added
- [x] Residue selection implemented
- [x] Backward compatibility maintained
- [x] Tests added
- [x] Documentation created
- [x] Examples provided
- [x] Quick reference created

---

**Ready to use the new features!** 🚀

Start with `MODALITY_QUICK_START.md` for quick examples, or `MODALITY_AND_RESIDUES_GUIDE.md` for comprehensive documentation.

