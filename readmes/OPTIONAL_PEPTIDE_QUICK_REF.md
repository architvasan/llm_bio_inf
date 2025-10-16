# Optional Peptide Sequence - Quick Reference

## TL;DR

**Before**: Had to provide empty string for templates
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="",  # ← Unnecessary
    modality="affibody",
    use_template=True,
)
```

**After**: No need to provide peptide for templates
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="affibody",
    use_template=True,
)
```

## One-Liners

### Custom Peptide
```python
UncertaintyGuidedMutation(target_seq=target, temp_pept_seq="SEQUENCE")
```

### Affibody Template
```python
UncertaintyGuidedMutation(target_seq=target, modality="affibody", use_template=True)
```

### Nanobody Template
```python
UncertaintyGuidedMutation(target_seq=target, modality="nanobody", use_template=True)
```

### Affitin Template
```python
UncertaintyGuidedMutation(target_seq=target, modality="affitin", use_template=True)
```

### Custom Template
```python
UncertaintyGuidedMutation(target_seq=target, use_template=True, custom_template="SEQUENCE")
```

### Template + Specific Residues
```python
UncertaintyGuidedMutation(target_seq=target, modality="nanobody", use_template=True, residues_to_mutate=[0, 5, 10])
```

## Parameter Reference

| Parameter | Type | Default | Required? |
|-----------|------|---------|-----------|
| `target_seq` | str | - | ✅ Yes |
| `temp_pept_seq` | str | `""` | ❌ No* |
| `modality` | str | `"custom"` | ❌ No |
| `use_template` | bool | `False` | ❌ No |
| `custom_template` | str | `None` | ❌ No |
| `residues_to_mutate` | List[int] | `None` | ❌ No |

*Either `temp_pept_seq` or `use_template=True` required

## Valid Combinations

| Scenario | Code |
|----------|------|
| Custom peptide | `temp_pept_seq="SEQUENCE"` |
| Affibody | `modality="affibody", use_template=True` |
| Nanobody | `modality="nanobody", use_template=True` |
| Affitin | `modality="affitin", use_template=True` |
| Custom template | `use_template=True, custom_template="SEQUENCE"` |
| With residues | `residues_to_mutate=[0, 5, 10]` |

## Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| "Either provide temp_pept_seq or set use_template=True" | No peptide | Provide one or the other |
| "Unknown modality" | Invalid modality | Use: affibody, nanobody, affitin |
| "No peptide sequence available" | Template not available | Set use_template=True |

## Decision Tree

```
Have custom peptide?
├─ YES → temp_pept_seq="SEQUENCE"
└─ NO → use_template=True + modality
```

## Examples

### Example 1: Explore Affibody
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="affibody",
    use_template=True,
    n_seq_out=20,
)
```

### Example 2: Optimize Peptide
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="MYPEPTIDE",
    n_seq_out=10,
)
```

### Example 3: Mutate CDR
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    residues_to_mutate=[27, 28, 29, 30, 31, 32, 33, 34, 35],
    n_seq_out=10,
)
```

### Example 4: Custom Template
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    use_template=True,
    custom_template="MYSEQUENCE",
    n_seq_out=5,
)
```

## Modalities

| Modality | Size | Use Case |
|----------|------|----------|
| affibody | 58 | Display tech |
| nanobody | 110 | Therapeutics |
| affitin | 94 | Binding proteins |
| custom | Variable | Any sequence |

## What Changed?

✅ `temp_pept_seq` now optional (default: `""`)  
✅ Validation added for peptide/template  
✅ Better error messages  
✅ Examples updated  
✅ 100% backward compatible  

## Files

- **uncertainty_guided_mutation.py** - Updated implementation
- **OPTIONAL_PEPTIDE_GUIDE.md** - Comprehensive guide
- **OPTIONAL_PEPTIDE_CHANGES.md** - Detailed changes
- **OPTIONAL_PEPTIDE_SUMMARY.md** - Complete summary
- **OPTIONAL_PEPTIDE_QUICK_REF.md** - This file

## Key Points

1. **Optional Parameter**: `temp_pept_seq` is now optional
2. **Validation**: Either provide peptide OR use template
3. **Cleaner API**: No empty strings needed
4. **Backward Compatible**: Old code still works
5. **Better Errors**: Clear error messages

## Quick Checklist

- [ ] Have custom peptide? → Use `temp_pept_seq="SEQUENCE"`
- [ ] Want template? → Use `modality="X", use_template=True`
- [ ] Want specific residues? → Add `residues_to_mutate=[...]`
- [ ] Want custom template? → Add `custom_template="SEQUENCE"`
- [ ] Want custom weights? → Add `model_weights="path"`

## Common Patterns

### Pattern 1: Template Only
```python
UncertaintyGuidedMutation(
    target_seq=target,
    modality="affibody",
    use_template=True,
)
```

### Pattern 2: Custom Peptide
```python
UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="PEPTIDE",
)
```

### Pattern 3: Template + Residues
```python
UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    residues_to_mutate=[0, 5, 10],
)
```

### Pattern 4: Everything
```python
UncertaintyGuidedMutation(
    target_seq=target,
    modality="affibody",
    use_template=True,
    residues_to_mutate=[0, 5, 10],
    mask_ratio=0.2,
    n_seq_out=20,
    model_weights="path/to/weights.safetensors",
)
```

## Migration

### Old Code
```python
UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="",
    modality="affibody",
    use_template=True,
)
```

### New Code
```python
UncertaintyGuidedMutation(
    target_seq=target,
    modality="affibody",
    use_template=True,
)
```

## Status

✅ Implemented  
✅ Tested  
✅ Documented  
✅ Backward Compatible  
✅ Ready to Use  

---

**For more details, see:**
- `OPTIONAL_PEPTIDE_GUIDE.md` - Full guide
- `OPTIONAL_PEPTIDE_CHANGES.md` - Change details
- `OPTIONAL_PEPTIDE_SUMMARY.md` - Complete summary

