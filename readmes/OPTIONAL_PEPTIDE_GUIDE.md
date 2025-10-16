# Optional Peptide Sequence Guide

## What Changed?

The `temp_pept_seq` parameter is now **optional** when using templates!

### Before (Old Way)
```python
# Had to provide empty string even when using template
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="",  # Required, even if ignored
    modality="affibody",
    use_template=True,
)
```

### After (New Way)
```python
# No need to provide temp_pept_seq when using template
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="affibody",
    use_template=True,
)
```

## Usage Patterns

### Pattern 1: Use Custom Peptide (Uncertainty-Guided)
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="HELVELLA",  # Required
    mask_ratio=0.3,
    n_seq_out=10,
)
results = mutator.run()
```

### Pattern 2: Use Template (No Custom Peptide)
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="affibody",  # or "nanobody", "affitin"
    use_template=True,
    mask_ratio=0.2,
    n_seq_out=10,
)
results = mutator.run()
```

### Pattern 3: Use Custom Peptide with Specific Residues
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="HELVELLA",  # Required
    residues_to_mutate=[0, 2, 4, 6],
    n_seq_out=5,
)
results = mutator.run()
```

### Pattern 4: Use Template with Specific Residues
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    residues_to_mutate=[10, 15, 20, 25, 30],
    n_seq_out=5,
)
results = mutator.run()
```

### Pattern 5: Override Template with Custom Template
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="affibody",
    use_template=True,
    custom_template="MYOWNSEQUENCE",  # Override default template
    n_seq_out=5,
)
results = mutator.run()
```

## Validation Rules

The system now validates that you provide **either**:
1. A custom `temp_pept_seq`, **OR**
2. `use_template=True` with a valid modality

### Valid Combinations ✅

```python
# Valid: Custom peptide
UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="HELVELLA",
)

# Valid: Template
UncertaintyGuidedMutation(
    target_seq=target,
    modality="affibody",
    use_template=True,
)

# Valid: Custom template
UncertaintyGuidedMutation(
    target_seq=target,
    modality="affibody",
    use_template=True,
    custom_template="MYSEQUENCE",
)
```

### Invalid Combinations ❌

```python
# Invalid: No peptide sequence provided
UncertaintyGuidedMutation(
    target_seq=target,
)
# Error: Either provide temp_pept_seq or set use_template=True

# Invalid: Empty peptide and no template
UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="",
    use_template=False,
)
# Error: Either provide temp_pept_seq or set use_template=True

# Invalid: Template requested but modality not recognized
UncertaintyGuidedMutation(
    target_seq=target,
    modality="unknown",
    use_template=True,
)
# Error: Unknown modality
```

## Decision Tree

```
Do you have a custom peptide sequence?
├─ YES
│  └─ Use: temp_pept_seq="YOURSEQUENCE"
│     (use_template will be ignored)
│
└─ NO
   └─ Do you want to use a template?
      ├─ YES (Affibody)
      │  └─ Use: modality="affibody", use_template=True
      │
      ├─ YES (Nanobody)
      │  └─ Use: modality="nanobody", use_template=True
      │
      ├─ YES (Affitin)
      │  └─ Use: modality="affitin", use_template=True
      │
      └─ YES (Custom Template)
         └─ Use: modality="affibody", use_template=True,
                 custom_template="YOURSEQUENCE"
```

## Common Scenarios

### Scenario 1: Explore Affibody Space
```python
# No need to provide a peptide sequence
mutator = UncertaintyGuidedMutation(
    target_seq=antibody,
    modality="affibody",
    use_template=True,
    mask_ratio=0.25,
    n_seq_out=20,
)
```

### Scenario 2: Optimize Your Peptide
```python
# Provide your custom peptide
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="MYPEPTIDE",
    mask_ratio=0.3,
    n_seq_out=10,
)
```

### Scenario 3: Mutate Specific Positions in Template
```python
# Use template but only mutate specific residues
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    residues_to_mutate=[27, 28, 29, 30, 31, 32, 33, 34, 35],
    n_seq_out=10,
)
```

### Scenario 4: Conservative Mutations on Custom Peptide
```python
# Use your peptide with low mutation rate
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="MYPEPTIDE",
    mask_ratio=0.1,  # Only 10%
    n_seq_out=5,
)
```

## Error Messages

### Error: "Either provide temp_pept_seq or set use_template=True"
**Cause**: You didn't provide a peptide sequence or template

**Solution**: Either:
- Provide `temp_pept_seq="YOURSEQUENCE"`, OR
- Set `use_template=True` with a valid modality

### Error: "Unknown modality"
**Cause**: Invalid modality name

**Solution**: Use one of:
- `modality="affibody"`
- `modality="nanobody"`
- `modality="affitin"`
- `modality="custom"`

### Error: "No peptide sequence available"
**Cause**: Tried to use template but it's not available

**Solution**: Set `use_template=True` or provide `temp_pept_seq`

## Migration Guide

If you have existing code, here's how to update it:

### Old Code
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="",  # Empty string
    modality="affibody",
    use_template=True,
)
```

### New Code
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="affibody",
    use_template=True,
)
```

**Note**: Old code still works! The default value for `temp_pept_seq` is now `""` instead of being required.

## Summary

✅ **Cleaner API** - No need for empty strings  
✅ **Better Validation** - Clear error messages  
✅ **Backward Compatible** - Old code still works  
✅ **Flexible** - Use templates or custom sequences  

## Quick Reference

| Scenario | Code |
|----------|------|
| Custom peptide | `temp_pept_seq="SEQUENCE"` |
| Affibody template | `modality="affibody", use_template=True` |
| Nanobody template | `modality="nanobody", use_template=True` |
| Affitin template | `modality="affitin", use_template=True` |
| Custom template | `use_template=True, custom_template="SEQUENCE"` |
| Specific residues | `residues_to_mutate=[0, 2, 4, 6]` |

---

**Ready to use the cleaner API!** 🚀

