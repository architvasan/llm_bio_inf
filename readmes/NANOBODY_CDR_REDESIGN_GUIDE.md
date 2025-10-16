# Nanobody CDR Redesign Guide

## Overview

The uncertainty-guided mutation system now includes **automatic CDR (Complementarity-Determining Region) identification and redesign for nanobodies**. This allows you to target specific CDR loops for mutation without manually specifying residue indices.

The system uses the **abnumber library** with **IMGT numbering** for accurate, robust CDR identification. If abnumber is not available, it falls back to hardcoded IMGT positions.

## What are CDRs?

CDRs are the three hypervariable regions in antibodies and nanobodies that directly interact with antigens:

- **CDR1**: First hypervariable region
- **CDR2**: Second hypervariable region
- **CDR3**: Third hypervariable region (most variable)

These regions are the most important for binding specificity and affinity.

## Installation

### Install abnumber (Recommended)

For accurate CDR identification using IMGT numbering:

```bash
pip install abnumber
```

If abnumber is not installed, the system will automatically fall back to hardcoded IMGT positions.

## Quick Start

### Mutate All CDRs

```python
from uncertainty_guided_mutation import UncertaintyGuidedMutation

mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR1", "CDR2", "CDR3"],  # Mutate all CDRs
    n_seq_out=10,
)
results = mutator.run()
```

### Mutate Specific CDRs

```python
# Mutate only CDR3 (most variable region)
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR3"],
    n_seq_out=10,
)
results = mutator.run()
```

### Mutate CDR1 and CDR3

```python
# Mutate CDR1 and CDR3 (framework-adjacent regions)
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR1", "CDR3"],
    n_seq_out=10,
)
results = mutator.run()
```

## Parameters

### `nanobody_cdr_regions` (List[str] | None)

Specifies which CDR regions to mutate. Only used when `modality="nanobody"`.

**Valid values:**
- `["CDR1"]` - Mutate only CDR1
- `["CDR2"]` - Mutate only CDR2
- `["CDR3"]` - Mutate only CDR3
- `["CDR1", "CDR2"]` - Mutate CDR1 and CDR2
- `["CDR1", "CDR2", "CDR3"]` - Mutate all CDRs
- `None` (default) - Use uncertainty-guided masking instead

### `cdr_numbering` (str)

Specifies the CDR numbering scheme to use.

**Valid values:**
- `"kabat"` (default) - Kabat numbering (most common)
- `"chothia"` - Chothia numbering (alternative)

## CDR Identification Method

### Using abnumber (Recommended)

The system uses the **abnumber library** with **IMGT numbering scheme** for accurate CDR identification:

```python
from abnumber import Chain

# Automatically identifies CDRs using IMGT numbering
chain = Chain(nanobody_seq, scheme='imgt')
cdr1_seq = chain.cdr1_seq
cdr2_seq = chain.cdr2_seq
cdr3_seq = chain.cdr3_seq
```

**Advantages:**
- ✅ Accurate IMGT numbering
- ✅ Handles sequence variations
- ✅ Robust to insertions/deletions
- ✅ Industry standard

### Fallback: Hardcoded IMGT Positions

If abnumber is not installed, the system uses approximate IMGT positions (0-indexed):

| CDR | Start | End | Length |
|-----|-------|-----|--------|
| CDR1 | 26 | 35 | 10 |
| CDR2 | 49 | 65 | 17 |
| CDR3 | 94 | 102 | 9 |

**Note:** These are approximate positions. For production use, install abnumber.

## Usage Examples

### Example 1: CDR3 Optimization

CDR3 is the most variable region and often the primary determinant of binding specificity.

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR3"],
    mask_ratio=0.5,  # Mutate all CDR3 positions
    n_seq_out=20,
)
results = mutator.run()
print("CDR3 variants:")
for seq in results["generated_sequences"]:
    print(seq)
```

### Example 2: Conservative CDR Mutations

Mutate all CDRs but with low mutation rate for conservative changes.

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR1", "CDR2", "CDR3"],
    mask_ratio=0.2,  # Only 20% of CDR positions
    n_seq_out=10,
)
results = mutator.run()
```

### Example 3: Framework-Aware Redesign

Mutate CDR1 and CDR3 while keeping CDR2 fixed (framework-aware approach).

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR1", "CDR3"],
    mask_ratio=0.3,
    n_seq_out=15,
)
results = mutator.run()
```

### Example 4: Inspect CDR Sequences

Inspect the identified CDR sequences before mutation.

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR1", "CDR2", "CDR3"],
)

nanobody_seq = mutator.get_peptide_sequence()
cdr_dict = mutator.identify_nanobody_cdrs(nanobody_seq)

print("CDR1:", cdr_dict["CDR1"][2])  # Print CDR1 sequence
print("CDR2:", cdr_dict["CDR2"][2])  # Print CDR2 sequence
print("CDR3:", cdr_dict["CDR3"][2])  # Print CDR3 sequence

results = mutator.run()
```

### Example 5: Custom Nanobody Sequence

Use CDR targeting with your own nanobody sequence.

```python
my_nanobody = "AQVQLQESGGGLVQAGGSLRLSCAASERTFSTYAMGWFRQAPGREREFLAQINWSGTTTYYAESVKDRTTISRDNAKNTVYLEMNNLNADDTGIYFCAAHPQRGWGSTLGWTYWGQGTQVTVSSGGGGSGGGKPIPNPLLGLDSTRTGHHHHHH"

mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq=my_nanobody,
    modality="nanobody",
    nanobody_cdr_regions=["CDR3"],
    n_seq_out=10,
)
results = mutator.run()
```

## Methods

### `get_nanobody_cdr_residues()`

Returns the residue indices for the specified CDR regions.

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR1", "CDR3"],
)

cdr_residues = mutator.get_nanobody_cdr_residues()
print(cdr_residues)  # [26, 27, 28, ..., 34, 94, 95, ..., 102]
```

### `identify_nanobody_cdrs(nanobody_seq)`

Identifies CDR regions in a nanobody sequence and returns their sequences.

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
)

nanobody_seq = mutator.get_peptide_sequence()
cdr_dict = mutator.identify_nanobody_cdrs(nanobody_seq)

print("CDR1:", cdr_dict["CDR1"])  # (start, end, sequence)
print("CDR2:", cdr_dict["CDR2"])
print("CDR3:", cdr_dict["CDR3"])
```

## Common Workflows

### Workflow 1: Affinity Maturation

Iteratively improve binding by mutating CDR3 and selecting best variants.

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
    
    # Select best variant (in practice, validate with binding assay)
    current_seq = results["generated_sequences"][0]
    print(f"Iteration {iteration+1}: {current_seq}")
```

### Workflow 2: Specificity Engineering

Mutate CDR1 and CDR2 to change specificity while keeping CDR3 fixed.

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR1", "CDR2"],
    mask_ratio=0.4,
    n_seq_out=20,
)
results = mutator.run()
```

### Workflow 3: Stability Optimization

Mutate all CDRs with conservative changes for improved stability.

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR1", "CDR2", "CDR3"],
    mask_ratio=0.15,  # Conservative
    n_seq_out=15,
)
results = mutator.run()
```

## Comparison: CDR vs Manual Residues

### Using CDR Regions (Recommended for Nanobodies)

```python
# Automatic CDR identification
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR3"],
)
```

**Advantages:**
- ✅ Automatic CDR identification
- ✅ No need to manually specify residues
- ✅ Biologically meaningful
- ✅ Easy to switch between CDRs

### Using Manual Residues

```python
# Manual residue specification
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    residues_to_mutate=[94, 95, 96, 97, 98, 99, 100, 101, 102],  # CDR3
)
```

**Advantages:**
- ✅ Full control over exact positions
- ✅ Can target non-CDR regions
- ✅ Useful for custom designs

## Error Handling

### Error: "CDR identification only supported for nanobody modality"

**Cause**: Tried to use `nanobody_cdr_regions` with non-nanobody modality

**Solution**: Set `modality="nanobody"`

```python
# Wrong
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="affibody",
    nanobody_cdr_regions=["CDR1"],
)

# Correct
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    nanobody_cdr_regions=["CDR1"],
)
```

### Error: "nanobody_cdr_regions must be specified"

**Cause**: Called `get_nanobody_cdr_residues()` without specifying CDR regions

**Solution**: Set `nanobody_cdr_regions` parameter

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR1", "CDR2", "CDR3"],
)
```

### Error: "Unknown CDR region"

**Cause**: Invalid CDR name specified

**Solution**: Use valid CDR names: "CDR1", "CDR2", "CDR3"

```python
# Wrong
nanobody_cdr_regions=["CDR4"]  # CDR4 doesn't exist

# Correct
nanobody_cdr_regions=["CDR1", "CDR2", "CDR3"]
```

## Tips and Best Practices

1. **Install abnumber**: For accurate CDR identification, install abnumber: `pip install abnumber`
2. **Start with CDR3**: CDR3 is the most variable and often most important for binding
3. **Use conservative mutations**: Start with `mask_ratio=0.2-0.3` for CDRs
4. **Validate experimentally**: Always validate computationally designed variants
5. **Consider framework**: CDRs interact with framework regions; keep framework fixed
6. **Inspect CDRs first**: Use `identify_nanobody_cdrs()` to verify CDR identification before mutation
7. **Use IMGT numbering**: The system uses IMGT numbering (via abnumber) for consistency

## Summary

| Feature | Status | Method |
|---------|--------|--------|
| CDR1 identification | ✅ Supported | abnumber (IMGT) |
| CDR2 identification | ✅ Supported | abnumber (IMGT) |
| CDR3 identification | ✅ Supported | abnumber (IMGT) |
| Fallback positions | ✅ Available | Hardcoded IMGT |
| IMGT numbering | ✅ Default | abnumber library |
| Custom CDR definitions | ⏳ Future | - |

## Troubleshooting

### Issue: "abnumber not found"

**Solution**: Install abnumber
```bash
pip install abnumber
```

The system will automatically use it if available, otherwise falls back to hardcoded positions.

### Issue: CDR identification seems wrong

**Solution**: Verify the sequence is a valid nanobody
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
)

nanobody_seq = mutator.get_peptide_sequence()
cdr_dict = mutator.identify_nanobody_cdrs(nanobody_seq)

# Check if CDRs were identified
for cdr_name, (start, end, seq) in cdr_dict.items():
    print(f"{cdr_name}: {start}-{end} ({len(seq)} aa)")
    print(f"  Sequence: {seq}")
```

---

**Ready to redesign nanobodies!** 🚀

