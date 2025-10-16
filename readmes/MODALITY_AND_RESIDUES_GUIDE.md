# Modality and Residue Selection Guide

## Overview

The uncertainty-guided mutation system now supports:
1. **Multiple modalities** - Different protein scaffolds (affibody, nanobody, affitin)
2. **Template sequences** - Pre-defined sequences for each modality
3. **Custom residue selection** - Specify exactly which residues to mutate

## Modalities

### Available Modalities

#### 1. Affibody
- **Description**: Small engineered protein scaffold (~58 residues)
- **Template**: `VDNKFNKELSVAGREIVTLPNLNDPQKKAFIFSLWDDPSQSANLLAEAKKLNDAQAPK`
- **Use case**: Compact binding proteins, good for display technologies
- **Advantages**: Small size, stable, good expression

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="",
    modality="affibody",
    use_template=True,
)
```

#### 2. Nanobody
- **Description**: Single-domain antibody (~110 residues)
- **Template**: `AQVQLQESGGGLVQAGGSLRLSCAASERTFSTYAMGWFRQAPGREREFLAQINWSGTTTYYAESVKDRTTISRDNAKNTVYLEMNNLNADDTGIYFCAAHPQRGWGSTLGWTYWGQGTQVTVSSGGGGSGGGKPIPNPLLGLDSTRTGHHHHHH`
- **Use case**: Antibody-like binding, good for therapeutic applications
- **Advantages**: Antibody-like properties, good stability, can be humanized

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="",
    modality="nanobody",
    use_template=True,
)
```

#### 3. Affitin
- **Description**: Engineered fibronectin domain (~94 residues)
- **Template**: `MRGSHHHHHHGSVKVKFVSSGEEKEVDTSKIKKVWRNLTKYGTIVQFTYDDNGKTGRGYVRELDAPKELLDMLARAEGKLN`
- **Use case**: Binding proteins with fibronectin scaffold
- **Advantages**: Natural protein scaffold, good for display

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="",
    modality="affitin",
    use_template=True,
)
```

#### 4. Custom
- **Description**: User-provided peptide sequence
- **Use case**: Any custom peptide or protein sequence
- **Default**: When no template is used

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="HELVELLA",
    modality="custom",
)
```

## Using Templates

### Enable Template Usage

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="",  # Ignored when use_template=True
    modality="affibody",
    use_template=True,  # Use template sequence
)
```

### Custom Template

Override the default template for a modality:

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="",
    modality="affibody",
    use_template=True,
    custom_template="MYOWNSEQUENCE",  # Override template
)
```

### Without Template

Use the provided peptide sequence:

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="HELVELLA",
    modality="custom",
    use_template=False,  # Use provided sequence
)
```

## Residue Selection

### Automatic Selection (Uncertainty-Guided)

Let the model select positions based on uncertainty:

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq=peptide,
    mask_strategy="top_k",
    mask_ratio=0.3,  # Mutate 30% most uncertain
    residues_to_mutate=None,  # Auto-select
)
```

### Manual Selection (Specific Residues)

Specify exactly which residues to mutate (0-indexed in peptide):

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="HELVELLA",
    residues_to_mutate=[0, 2, 4, 6],  # Mutate positions 0, 2, 4, 6
)
```

### Residue Indexing

Residues are 0-indexed within the peptide sequence:

```
Peptide: H E L V E L L A
Index:   0 1 2 3 4 5 6 7

residues_to_mutate=[0, 3, 7]  # Mutate H, V, A
```

## Usage Examples

### Example 1: Affibody with Uncertainty-Guided Masking

```python
from uncertainty_guided_mutation import UncertaintyGuidedMutation

mutator = UncertaintyGuidedMutation(
    target_seq="MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV",
    temp_pept_seq="",
    modality="affibody",
    use_template=True,
    mask_strategy="top_k",
    mask_ratio=0.2,
    n_seq_out=10,
)

results = mutator.run()
print(f"Modality: {results['modality']}")
print(f"Peptide length: {len(results['peptide_seq'])}")
for seq in results["generated_sequences"]:
    print(seq)
```

### Example 2: Nanobody with Specific Residues

```python
mutator = UncertaintyGuidedMutation(
    target_seq="MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV",
    temp_pept_seq="",
    modality="nanobody",
    use_template=True,
    residues_to_mutate=[10, 15, 20, 25, 30],  # CDR-like regions
    n_seq_out=5,
)

results = mutator.run()
print(f"Mutating residues: {results['residues_to_mutate']}")
for seq in results["generated_sequences"]:
    print(seq)
```

### Example 3: Custom Peptide with Specific Residues

```python
mutator = UncertaintyGuidedMutation(
    target_seq="MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV",
    temp_pept_seq="HELVELLA",
    modality="custom",
    residues_to_mutate=[0, 2, 4, 6],  # Mutate H, L, E, L
    n_seq_out=8,
)

results = mutator.run()
for seq in results["generated_sequences"]:
    print(seq)
```

### Example 4: Affitin with Custom Template

```python
custom_affitin = "MRGSHHHHHHGSVKVKFVSSGEEKEVDTSKIKKVWRNLTKYGTIVQFTYDDNGKTGRGYVRELDAPKELLDMLARAEGKLN"

mutator = UncertaintyGuidedMutation(
    target_seq="MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV",
    temp_pept_seq="",
    modality="affitin",
    use_template=True,
    custom_template=custom_affitin,
    mask_strategy="threshold",
    uncertainty_threshold=0.4,
    n_seq_out=5,
)

results = mutator.run()
```

## Output Format

The results dictionary now includes:

```python
results = mutator.run()

{
    "input_seq": str,                    # Full input sequence
    "peptide_seq": str,                  # Peptide sequence used
    "modality": str,                     # Modality used
    "uncertainty": torch.Tensor,         # Uncertainty scores
    "peptide_start_idx": int,            # Where peptide starts
    "positions_to_mask": List[int],      # Token positions masked
    "masked_seq": str,                   # Sequence with [MASK]
    "generated_sequences": List[str],    # Generated mutations
    "residues_to_mutate": List[int],     # Residues mutated (if specified)
}
```

## Configuration Reference

### Modality Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `modality` | str | "custom" | Scaffold type: "affibody", "nanobody", "affitin", "custom" |
| `use_template` | bool | False | Use template sequence for modality |
| `custom_template` | str | None | Override template with custom sequence |
| `residues_to_mutate` | List[int] | None | Specific residues to mutate (0-indexed) |

### Masking Parameters (when residues_to_mutate is None)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mask_strategy` | str | "top_k" | "top_k", "threshold", or "entropy" |
| `mask_ratio` | float | 0.3 | For top_k: fraction to mask |
| `uncertainty_threshold` | float | 0.5 | For threshold: cutoff |

## Common Workflows

### Workflow 1: Optimize Affibody Binding

```python
# Use affibody template with uncertainty-guided masking
mutator = UncertaintyGuidedMutation(
    target_seq=antibody_seq,
    temp_pept_seq="",
    modality="affibody",
    use_template=True,
    mask_strategy="top_k",
    mask_ratio=0.25,
    n_seq_out=20,
)
results = mutator.run()
```

### Workflow 2: Mutate CDR-Like Regions

```python
# Mutate specific positions in nanobody
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq="",
    modality="nanobody",
    use_template=True,
    residues_to_mutate=[27, 28, 29, 30, 31, 32, 33, 34, 35],  # CDR3-like
    n_seq_out=10,
)
results = mutator.run()
```

### Workflow 3: Conservative Mutations

```python
# Only mutate most uncertain positions
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq=peptide,
    modality="custom",
    mask_strategy="top_k",
    mask_ratio=0.1,  # Only 10%
    n_seq_out=5,
)
results = mutator.run()
```

### Workflow 4: Aggressive Exploration

```python
# Mutate many positions
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq=peptide,
    modality="custom",
    mask_strategy="top_k",
    mask_ratio=0.5,  # 50%
    n_seq_out=30,
)
results = mutator.run()
```

## Tips & Best Practices

### Tip 1: Choose Right Modality
- **Affibody**: Compact, good for display
- **Nanobody**: Antibody-like, therapeutic
- **Affitin**: Natural scaffold, good stability
- **Custom**: Any sequence you want

### Tip 2: Template vs Custom
- Use template for well-characterized scaffolds
- Use custom for novel sequences
- Can override template with custom_template

### Tip 3: Residue Selection
- Use uncertainty-guided for exploration
- Use specific residues for targeted optimization
- Combine with mask_ratio for fine control

### Tip 4: Validation
- Always validate generated sequences
- Check for structural integrity
- Test binding affinity experimentally

## Troubleshooting

### Issue: "Unknown modality"
**Solution**: Use one of: "affibody", "nanobody", "affitin", "custom"

### Issue: Template not used
**Solution**: Set `use_template=True`

### Issue: Residues not mutated
**Solution**: Ensure `residues_to_mutate` is a list of valid indices

### Issue: No mutations generated
**Solution**: Check `n_seq_out > 0` and positions_to_mask is not empty

## Advanced Usage

### Combining Multiple Strategies

```python
# First pass: uncertainty-guided
mutator1 = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq=peptide,
    mask_strategy="top_k",
    mask_ratio=0.3,
    n_seq_out=10,
)
results1 = mutator1.run()

# Second pass: specific residues on best sequence
best_seq = results1["generated_sequences"][0]
mutator2 = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq=best_seq,
    residues_to_mutate=[0, 2, 4],
    n_seq_out=5,
)
results2 = mutator2.run()
```

### Iterative Refinement

```python
current_seq = initial_peptide
for iteration in range(3):
    mutator = UncertaintyGuidedMutation(
        target_seq=target,
        temp_pept_seq=current_seq,
        mask_strategy="top_k",
        mask_ratio=0.2,
        n_seq_out=5,
    )
    results = mutator.run()
    current_seq = results["generated_sequences"][0]
    print(f"Iteration {iteration+1}: {current_seq}")
```

---

**Ready to optimize your peptides!** 🚀

