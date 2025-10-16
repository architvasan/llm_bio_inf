# Optional Peptide Sequence - Changes Summary

## What Changed?

The `temp_pept_seq` parameter is now **optional** when using templates!

## Key Changes

### 1. Parameter Made Optional
**Before:**
```python
temp_pept_seq: str  # Required
```

**After:**
```python
temp_pept_seq: str = ""  # Optional (default: empty string)
```

### 2. Input Validation Added
New validation in `__post_init__()` ensures you provide **either**:
- A custom `temp_pept_seq`, **OR**
- `use_template=True` with a valid modality

```python
if not self.temp_pept_seq and not self.use_template:
    raise ValueError(
        "Either provide temp_pept_seq or set use_template=True. "
        "Cannot proceed without a peptide sequence."
    )
```

### 3. Enhanced `get_peptide_sequence()` Method
Now includes better error handling:
```python
def get_peptide_sequence(self) -> str:
    if self.use_template:
        return self.get_template_sequence()
    
    if not self.temp_pept_seq:
        raise ValueError(
            "No peptide sequence available. Either provide temp_pept_seq or set use_template=True."
        )
    
    return self.temp_pept_seq
```

### 4. Updated Examples
Removed unnecessary empty string parameters:

**Before:**
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target_seq,
    temp_pept_seq="",  # Empty string
    modality="affibody",
    use_template=True,
)
```

**After:**
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target_seq,
    modality="affibody",
    use_template=True,
)
```

## Usage Examples

### Example 1: Custom Peptide (Still Works)
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="HELVELLA",  # Provide custom peptide
    mask_ratio=0.3,
    n_seq_out=10,
)
```

### Example 2: Template Only (New - Cleaner)
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="affibody",  # No temp_pept_seq needed!
    use_template=True,
    mask_ratio=0.2,
    n_seq_out=10,
)
```

### Example 3: Template with Specific Residues
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    residues_to_mutate=[10, 15, 20, 25, 30],
    n_seq_out=5,
)
```

### Example 4: Custom Template Override
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="affibody",
    use_template=True,
    custom_template="MYOWNSEQUENCE",
    n_seq_out=5,
)
```

## Backward Compatibility

✅ **100% Backward Compatible!**

Old code still works exactly the same:
```python
# This still works
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="HELVELLA",
    mask_ratio=0.3,
    n_seq_out=10,
)
```

## Valid Combinations

### ✅ Valid

```python
# Custom peptide
UncertaintyGuidedMutation(target_seq=target, temp_pept_seq="SEQUENCE")

# Template
UncertaintyGuidedMutation(target_seq=target, modality="affibody", use_template=True)

# Custom template
UncertaintyGuidedMutation(
    target_seq=target,
    modality="affibody",
    use_template=True,
    custom_template="SEQUENCE"
)
```

### ❌ Invalid

```python
# No peptide sequence
UncertaintyGuidedMutation(target_seq=target)
# Error: Either provide temp_pept_seq or set use_template=True

# Empty peptide and no template
UncertaintyGuidedMutation(target_seq=target, temp_pept_seq="", use_template=False)
# Error: Either provide temp_pept_seq or set use_template=True
```

## Error Messages

### Error 1: No Peptide Sequence
```
ValueError: Either provide temp_pept_seq or set use_template=True. 
Cannot proceed without a peptide sequence.
```

**Solution**: Provide either `temp_pept_seq` or set `use_template=True`

### Error 2: No Peptide Available
```
ValueError: No peptide sequence available. Either provide temp_pept_seq or set use_template=True.
```

**Solution**: Same as above

### Error 3: Unknown Modality
```
ValueError: Unknown modality: xyz. Choose from ['affibody', 'nanobody', 'affitin'] or set custom_template.
```

**Solution**: Use valid modality or provide `custom_template`

## Benefits

✅ **Cleaner API** - No empty strings needed  
✅ **Better Validation** - Clear error messages  
✅ **More Intuitive** - Only provide what you need  
✅ **Backward Compatible** - Old code still works  
✅ **Flexible** - Works with templates or custom sequences  

## Migration Guide

If you have existing code with empty strings:

### Old Code
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="",
    modality="affibody",
    use_template=True,
)
```

### New Code (Optional)
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="affibody",
    use_template=True,
)
```

**Note**: Old code still works! This is just cleaner.

## Files Modified

1. **uncertainty_guided_mutation.py**
   - Made `temp_pept_seq` optional (default: `""`)
   - Added validation in `__post_init__()`
   - Enhanced `get_peptide_sequence()` method
   - Updated examples (removed empty strings)

2. **OPTIONAL_PEPTIDE_GUIDE.md** (NEW)
   - Comprehensive guide to optional peptide usage
   - Usage patterns and examples
   - Decision tree
   - Common scenarios
   - Error messages and solutions

## Testing

The changes maintain all existing functionality:
- ✅ Custom peptide sequences still work
- ✅ Template sequences work
- ✅ Specific residue selection works
- ✅ Custom templates work
- ✅ All masking strategies work
- ✅ Custom weights still work

## Summary

| Aspect | Status |
|--------|--------|
| Backward Compatible | ✅ Yes |
| Breaking Changes | ✅ None |
| New Features | ✅ Optional peptide |
| Validation | ✅ Added |
| Error Messages | ✅ Improved |
| Documentation | ✅ Updated |

---

## Quick Reference

| Use Case | Code |
|----------|------|
| Custom peptide | `temp_pept_seq="SEQUENCE"` |
| Affibody template | `modality="affibody", use_template=True` |
| Nanobody template | `modality="nanobody", use_template=True` |
| Affitin template | `modality="affitin", use_template=True` |
| Custom template | `use_template=True, custom_template="SEQUENCE"` |

---

**Ready to use the cleaner API!** 🚀

For detailed usage guide, see: `OPTIONAL_PEPTIDE_GUIDE.md`

