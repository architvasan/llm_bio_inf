# Nanobody CDR Redesign - Quick Start

## Installation

```bash
pip install abnumber
```

## One-Liners

### Mutate CDR3 Only

```python
from uncertainty_guided_mutation import UncertaintyGuidedMutation

mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR3"],
    n_seq_out=10,
)
results = mutator.run()
```

### Mutate All CDRs

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

### Mutate CDR1 and CDR3

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR1", "CDR3"],
    n_seq_out=10,
)
results = mutator.run()
```

## Key Parameters

| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
| `modality` | str | `"nanobody"` | Must be "nanobody" for CDR targeting |
| `nanobody_cdr_regions` | List[str] | `["CDR1", "CDR2", "CDR3"]` | Which CDRs to mutate |
| `use_template` | bool | `True` | Use nanobody template |
| `mask_ratio` | float | `0.3` | Fraction of CDR positions to mutate |
| `n_seq_out` | int | `10` | Number of variants to generate |

## Common Workflows

### Workflow 1: Explore CDR3 Space

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
```

### Workflow 2: Conservative Optimization

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

### Workflow 3: Iterative Refinement

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
    print(f"Iteration {iteration+1}: {current_seq}")
```

## Inspect CDRs

### View CDR Sequences

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

### Get CDR Residue Indices

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR1", "CDR3"],
)

cdr_residues = mutator.get_nanobody_cdr_residues()
print(cdr_residues)  # [26, 27, ..., 35, 94, 95, ..., 102]
```

## CDR Regions

### CDR1
- **Role**: Framework-adjacent, moderate variability
- **Typical length**: ~10 residues
- **Best for**: Specificity tuning

### CDR2
- **Role**: Central binding region
- **Typical length**: ~17 residues
- **Best for**: Affinity optimization

### CDR3
- **Role**: Most variable, primary binding determinant
- **Typical length**: ~9 residues
- **Best for**: Binding specificity

## Examples

### Example 1: CDR3 Optimization

```python
mutator = UncertaintyGuidedMutation(
    target_seq=antibody_seq,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR3"],
    mask_ratio=0.5,
    n_seq_out=20,
)
results = mutator.run()

print("Generated CDR3 variants:")
for i, seq in enumerate(results["generated_sequences"], 1):
    print(f"{i}. {seq}")
```

### Example 2: Custom Nanobody

```python
my_nanobody = "AQVQLQESGGGLVQAGGSLRLSCAASERTFSTYAMGWFRQAPGREREFLAQINWSGTTTYYAESVKDRTTISRDNAKNTVYLEMNNLNADDTGIYFCAAHPQRGWGSTLGWTYWGQGTQVTVSSGGGGSGGGKPIPNPLLGLDSTRTGHHHHHH"

mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq=my_nanobody,
    modality="nanobody",
    nanobody_cdr_regions=["CDR1", "CDR2", "CDR3"],
    n_seq_out=10,
)
results = mutator.run()
```

### Example 3: Multi-CDR Targeting

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR1", "CDR3"],  # Skip CDR2
    mask_ratio=0.3,
    n_seq_out=15,
)
results = mutator.run()
```

## Error Handling

### Error: "CDR identification only supported for nanobody modality"

**Fix**: Set `modality="nanobody"`

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

**Fix**: Provide CDR regions to mutate

```python
# Wrong
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
)
cdr_residues = mutator.get_nanobody_cdr_residues()  # Error!

# Correct
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR1", "CDR2", "CDR3"],
)
cdr_residues = mutator.get_nanobody_cdr_residues()  # OK
```

### Error: "Unknown CDR region"

**Fix**: Use valid CDR names: "CDR1", "CDR2", "CDR3"

```python
# Wrong
nanobody_cdr_regions=["CDR4"]  # CDR4 doesn't exist

# Correct
nanobody_cdr_regions=["CDR1", "CDR2", "CDR3"]
```

## Tips

1. **Install abnumber**: `pip install abnumber` for accurate IMGT numbering
2. **Start with CDR3**: Most variable region, often most important
3. **Use conservative mask_ratio**: Start with 0.2-0.3 for CDRs
4. **Inspect before mutating**: Use `identify_nanobody_cdrs()` to verify
5. **Validate experimentally**: Always test computationally designed variants

## Methods

### `get_nanobody_cdr_residues()`

Returns residue indices for specified CDR regions.

```python
cdr_residues = mutator.get_nanobody_cdr_residues()
# Returns: [26, 27, ..., 35, 49, 50, ..., 65, 94, 95, ..., 102]
```

### `identify_nanobody_cdrs(nanobody_seq)`

Identifies CDR sequences in a nanobody.

```python
cdr_dict = mutator.identify_nanobody_cdrs(nanobody_seq)
# Returns: {
#     "CDR1": (start, end, sequence),
#     "CDR2": (start, end, sequence),
#     "CDR3": (start, end, sequence),
# }
```

## Summary

| Feature | Status |
|---------|--------|
| CDR1 targeting | ✅ Supported |
| CDR2 targeting | ✅ Supported |
| CDR3 targeting | ✅ Supported |
| abnumber integration | ✅ Supported |
| IMGT numbering | ✅ Default |
| Fallback positions | ✅ Available |

---

**Ready to design nanobodies!** 🚀

