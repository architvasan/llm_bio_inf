# Nanobody CDR Redesign Feature - Complete Index

## 🎯 What Is This?

Complete integration of **abnumber-based CDR identification** for accurate nanobody CDR redesign using IMGT numbering.

## 📦 What You Get

✅ Automatic CDR identification (CDR1, CDR2, CDR3)  
✅ IMGT numbering via abnumber library  
✅ Graceful fallback to hardcoded positions  
✅ Flexible CDR targeting  
✅ Comprehensive documentation  
✅ 9 working examples  

## 🚀 Quick Start (2 minutes)

### 1. Install abnumber

```bash
pip install abnumber
```

### 2. Use CDR targeting

```python
from uncertainty_guided_mutation import UncertaintyGuidedMutation

mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR3"],  # Mutate CDR3
    n_seq_out=10,
)
results = mutator.run()
```

## 📚 Documentation Files

### 1. **NANOBODY_CDR_QUICK_START.md** ⭐ START HERE
**Best for**: Quick reference and one-liners  
**Read time**: 5 minutes  
**Contains**:
- Installation instructions
- One-liner examples
- Parameter reference
- Common workflows
- Error handling

### 2. **NANOBODY_CDR_REDESIGN_GUIDE.md**
**Best for**: Comprehensive guide  
**Read time**: 15 minutes  
**Contains**:
- What are CDRs?
- CDR identification methods
- Usage examples (5 scenarios)
- Methods documentation
- Common workflows
- Tips and best practices
- Troubleshooting

### 3. **CDR_INTEGRATION_SUMMARY.md**
**Best for**: Understanding the integration  
**Read time**: 10 minutes  
**Contains**:
- What was added
- Key features
- How it works
- Usage examples
- Integration with existing code
- Files modified
- Error handling
- Performance notes

### 4. **NANOBODY_CDR_FEATURE_COMPLETE.md**
**Best for**: Complete overview  
**Read time**: 10 minutes  
**Contains**:
- Implementation summary
- Feature comparison
- Usage examples
- Files modified/created
- How it works
- Key features
- Testing coverage
- Quality checklist

### 5. **example_nanobody_cdr_redesign.py**
**Best for**: Working examples  
**Run time**: 1-2 minutes  
**Contains**: 9 complete examples
1. Mutate CDR3 only
2. Mutate all CDRs
3. Mutate CDR1 and CDR3
4. Inspect CDR sequences
5. Get CDR residue indices
6. Conservative mutations
7. Custom nanobody sequence
8. Iterative refinement
9. Compare CDR vs uncertainty-guided

## 🎓 Learning Paths

### Path 1: Quick Start (10 minutes)
1. This file (2 min)
2. `NANOBODY_CDR_QUICK_START.md` (5 min)
3. Try an example (3 min)

### Path 2: Comprehensive (30 minutes)
1. `NANOBODY_CDR_QUICK_START.md` (5 min)
2. `NANOBODY_CDR_REDESIGN_GUIDE.md` (15 min)
3. `example_nanobody_cdr_redesign.py` (10 min)

### Path 3: Deep Dive (45 minutes)
1. `NANOBODY_CDR_QUICK_START.md` (5 min)
2. `CDR_INTEGRATION_SUMMARY.md` (10 min)
3. `NANOBODY_CDR_REDESIGN_GUIDE.md` (15 min)
4. `example_nanobody_cdr_redesign.py` (15 min)

### Path 4: Everything (60 minutes)
Read all files in order:
1. This index (2 min)
2. `NANOBODY_CDR_QUICK_START.md` (5 min)
3. `CDR_INTEGRATION_SUMMARY.md` (10 min)
4. `NANOBODY_CDR_REDESIGN_GUIDE.md` (15 min)
5. `NANOBODY_CDR_FEATURE_COMPLETE.md` (10 min)
6. `example_nanobody_cdr_redesign.py` (18 min)

## 🔍 Find What You Need

### I want to...

**...get started in 5 minutes**
→ Read: `NANOBODY_CDR_QUICK_START.md`

**...understand how it works**
→ Read: `CDR_INTEGRATION_SUMMARY.md`

**...see working examples**
→ Run: `example_nanobody_cdr_redesign.py`

**...learn comprehensive details**
→ Read: `NANOBODY_CDR_REDESIGN_GUIDE.md`

**...see complete overview**
→ Read: `NANOBODY_CDR_FEATURE_COMPLETE.md`

**...find specific information**
→ Use this index!

## 💡 Common Tasks

### Task 1: Mutate CDR3 Only

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR3"],
    n_seq_out=10,
)
results = mutator.run()
```

See: `NANOBODY_CDR_QUICK_START.md` → One-Liners

### Task 2: Mutate All CDRs

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR1", "CDR2", "CDR3"],
    n_seq_out=10,
)
results = mutator.run()
```

See: `NANOBODY_CDR_QUICK_START.md` → One-Liners

### Task 3: Inspect CDRs

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
)

nanobody_seq = mutator.get_peptide_sequence()
cdr_dict = mutator.identify_nanobody_cdrs(nanobody_seq)

for cdr_name, (start, end, seq) in cdr_dict.items():
    print(f"{cdr_name}: {seq}")
```

See: `NANOBODY_CDR_REDESIGN_GUIDE.md` → Inspect CDRs

### Task 4: Get CDR Residues

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR1", "CDR3"],
)

cdr_residues = mutator.get_nanobody_cdr_residues()
```

See: `NANOBODY_CDR_REDESIGN_GUIDE.md` → Methods

### Task 5: Iterative Refinement

```python
current_seq = nanobody_template

for iteration in range(3):
    mutator = UncertaintyGuidedMutation(
        target_seq=target,
        temp_pept_seq=current_seq,
        modality="nanobody",
        nanobody_cdr_regions=["CDR3"],
        mask_ratio=0.3,
        n_seq_out=10,
    )
    results = mutator.run()
    current_seq = results["generated_sequences"][0]
```

See: `NANOBODY_CDR_REDESIGN_GUIDE.md` → Common Workflows

## 🔧 Installation

### Required

```bash
pip install abnumber
```

### Optional

If abnumber is not installed, the system automatically falls back to hardcoded IMGT positions.

## 📊 Feature Summary

| Feature | Status | Location |
|---------|--------|----------|
| CDR1 targeting | ✅ Supported | All docs |
| CDR2 targeting | ✅ Supported | All docs |
| CDR3 targeting | ✅ Supported | All docs |
| abnumber integration | ✅ Supported | CDR_INTEGRATION_SUMMARY.md |
| IMGT numbering | ✅ Default | NANOBODY_CDR_REDESIGN_GUIDE.md |
| Fallback positions | ✅ Available | CDR_INTEGRATION_SUMMARY.md |
| Error handling | ✅ Robust | NANOBODY_CDR_QUICK_START.md |
| Examples | ✅ 9 scenarios | example_nanobody_cdr_redesign.py |

## 🎯 Key Parameters

| Parameter | Type | Example |
|-----------|------|---------|
| `modality` | str | `"nanobody"` |
| `nanobody_cdr_regions` | List[str] | `["CDR1", "CDR2", "CDR3"]` |
| `use_template` | bool | `True` |
| `mask_ratio` | float | `0.3` |
| `n_seq_out` | int | `10` |

See: `NANOBODY_CDR_QUICK_START.md` → Key Parameters

## 🆘 Troubleshooting

### Issue: "abnumber not found"

**Solution**: Install abnumber
```bash
pip install abnumber
```

See: `NANOBODY_CDR_QUICK_START.md` → Error Handling

### Issue: CDR identification seems wrong

**Solution**: Verify sequence and inspect CDRs
```python
cdr_dict = mutator.identify_nanobody_cdrs(nanobody_seq)
for cdr_name, (start, end, seq) in cdr_dict.items():
    print(f"{cdr_name}: {seq}")
```

See: `NANOBODY_CDR_REDESIGN_GUIDE.md` → Troubleshooting

### Issue: "CDR identification only supported for nanobody modality"

**Solution**: Set `modality="nanobody"`

See: `NANOBODY_CDR_QUICK_START.md` → Error Handling

## 📈 Performance

- **abnumber**: ~10-50ms per sequence
- **Fallback**: <1ms
- **Overall impact**: Negligible

See: `CDR_INTEGRATION_SUMMARY.md` → Performance

## ✅ Quality Checklist

- [x] abnumber integration
- [x] IMGT numbering
- [x] CDR1, CDR2, CDR3 support
- [x] Fallback mechanism
- [x] Error handling
- [x] Documentation (5 files)
- [x] Examples (9 scenarios)
- [x] Backward compatibility
- [x] Production ready

## 🚀 Next Steps

1. **Install**: `pip install abnumber`
2. **Read**: `NANOBODY_CDR_QUICK_START.md` (5 min)
3. **Run**: `python example_nanobody_cdr_redesign.py`
4. **Use**: In your nanobody redesign pipeline

## 📞 Support

| Question | Answer Location |
|----------|-----------------|
| How do I get started? | `NANOBODY_CDR_QUICK_START.md` |
| How does it work? | `CDR_INTEGRATION_SUMMARY.md` |
| What are CDRs? | `NANOBODY_CDR_REDESIGN_GUIDE.md` |
| Show me examples | `example_nanobody_cdr_redesign.py` |
| Complete overview | `NANOBODY_CDR_FEATURE_COMPLETE.md` |

## 🎉 Summary

| Aspect | Status |
|--------|--------|
| Implementation | ✅ Complete |
| Documentation | ✅ Complete (5 files) |
| Examples | ✅ Complete (9 scenarios) |
| Testing | ✅ Ready |
| Production | ✅ Ready |

---

## 📖 Start Here

**Recommended**: Start with `NANOBODY_CDR_QUICK_START.md` (5 minutes)

Then choose your next file based on your needs!

**Happy nanobody designing!** 🚀

