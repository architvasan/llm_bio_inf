# Optional Peptide Sequence - Complete Summary

## 🎯 What You Asked For

> "I want to be able to either use the custom input sequence or the template. If the template is being used then we do not need to feed in our custom input sequence"

## ✅ What Was Implemented

The `temp_pept_seq` parameter is now **optional** when using templates!

## 📊 Changes Made

### 1. Parameter Definition
```python
# Before
temp_pept_seq: str  # Required

# After
temp_pept_seq: str = ""  # Optional (default: empty string)
```

### 2. Input Validation
Added validation in `__post_init__()`:
```python
if not self.temp_pept_seq and not self.use_template:
    raise ValueError(
        "Either provide temp_pept_seq or set use_template=True. "
        "Cannot proceed without a peptide sequence."
    )
```

### 3. Enhanced Error Handling
Updated `get_peptide_sequence()` with better error messages:
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
Removed unnecessary empty string parameters from examples.

## 🚀 Usage Examples

### Example 1: Custom Peptide (Original Way - Still Works)
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="HELVELLA",  # Provide custom peptide
    mask_ratio=0.3,
    n_seq_out=10,
)
results = mutator.run()
```

### Example 2: Template Only (New - Cleaner!)
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="affibody",  # No temp_pept_seq needed!
    use_template=True,
    mask_ratio=0.2,
    n_seq_out=10,
)
results = mutator.run()
```

### Example 3: Nanobody Template
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    n_seq_out=10,
)
results = mutator.run()
```

### Example 4: Affitin Template
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="affitin",
    use_template=True,
    n_seq_out=10,
)
results = mutator.run()
```

### Example 5: Template with Specific Residues
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

### Example 6: Custom Template Override
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="affibody",
    use_template=True,
    custom_template="MYOWNSEQUENCE",
    n_seq_out=5,
)
results = mutator.run()
```

## ✨ Key Benefits

✅ **Cleaner API** - No empty strings needed  
✅ **More Intuitive** - Only provide what you need  
✅ **Better Validation** - Clear error messages  
✅ **Backward Compatible** - Old code still works  
✅ **Flexible** - Works with templates or custom sequences  

## 📋 Valid Combinations

### ✅ Valid

```python
# Custom peptide
UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="HELVELLA"
)

# Template (no peptide needed!)
UncertaintyGuidedMutation(
    target_seq=target,
    modality="affibody",
    use_template=True
)

# Custom template
UncertaintyGuidedMutation(
    target_seq=target,
    modality="affibody",
    use_template=True,
    custom_template="MYSEQUENCE"
)

# Template with residues
UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    residues_to_mutate=[0, 5, 10]
)
```

### ❌ Invalid

```python
# No peptide sequence provided
UncertaintyGuidedMutation(target_seq=target)
# Error: Either provide temp_pept_seq or set use_template=True

# Empty peptide and no template
UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="",
    use_template=False
)
# Error: Either provide temp_pept_seq or set use_template=True
```

## 🔄 Migration Guide

### Old Code (Still Works!)
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="",  # Empty string
    modality="affibody",
    use_template=True,
)
```

### New Code (Cleaner)
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="affibody",
    use_template=True,
)
```

**Note**: Both work! The new way is just cleaner.

## 📚 Documentation

### New Files Created
1. **OPTIONAL_PEPTIDE_GUIDE.md** - Comprehensive usage guide
2. **OPTIONAL_PEPTIDE_CHANGES.md** - Detailed change summary
3. **OPTIONAL_PEPTIDE_SUMMARY.md** - This file

### Updated Files
1. **uncertainty_guided_mutation.py** - Implementation updated
2. **README.md** - Can be updated with new examples

## 🧪 Testing

All existing functionality is preserved:
- ✅ Custom peptide sequences work
- ✅ Template sequences work
- ✅ Specific residue selection works
- ✅ Custom templates work
- ✅ All masking strategies work
- ✅ Custom weights work
- ✅ Backward compatibility maintained

## 💡 Decision Tree

```
Do you have a custom peptide?
├─ YES
│  └─ Use: temp_pept_seq="YOURSEQUENCE"
│
└─ NO
   └─ Use template?
      ├─ Affibody
      │  └─ modality="affibody", use_template=True
      │
      ├─ Nanobody
      │  └─ modality="nanobody", use_template=True
      │
      ├─ Affitin
      │  └─ modality="affitin", use_template=True
      │
      └─ Custom
         └─ use_template=True, custom_template="SEQUENCE"
```

## 🎯 Common Scenarios

### Scenario 1: Explore Affibody Space
```python
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
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="MYPEPTIDE",
    mask_ratio=0.3,
    n_seq_out=10,
)
```

### Scenario 3: Mutate CDR Regions
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    residues_to_mutate=[27, 28, 29, 30, 31, 32, 33, 34, 35],
    n_seq_out=10,
)
```

## 📊 Comparison

| Feature | Before | After |
|---------|--------|-------|
| temp_pept_seq required | ✅ Yes | ❌ No |
| Empty string needed | ✅ Yes | ❌ No |
| Template support | ✅ Yes | ✅ Yes |
| Validation | ❌ No | ✅ Yes |
| Error messages | ❌ Generic | ✅ Clear |
| Backward compatible | N/A | ✅ Yes |

## ✅ Quality Checklist

- [x] Parameter made optional
- [x] Validation added
- [x] Error handling improved
- [x] Examples updated
- [x] Documentation created
- [x] Backward compatible
- [x] No breaking changes
- [x] Clear error messages

## 🚀 Ready to Use!

The implementation is complete and ready for use.

### Quick Start
```python
# Use template (no peptide needed!)
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="affibody",
    use_template=True,
)
results = mutator.run()
```

### For More Details
- **Usage Guide**: See `OPTIONAL_PEPTIDE_GUIDE.md`
- **Change Details**: See `OPTIONAL_PEPTIDE_CHANGES.md`
- **Code**: See `uncertainty_guided_mutation.py`

---

## Summary

✅ **Feature Implemented**: Optional peptide sequence  
✅ **Cleaner API**: No empty strings needed  
✅ **Better Validation**: Clear error messages  
✅ **Backward Compatible**: Old code still works  
✅ **Well Documented**: Comprehensive guides provided  

**Ready to use!** 🎉

