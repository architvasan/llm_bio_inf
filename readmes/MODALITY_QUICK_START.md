# Modality & Residue Selection - Quick Start

## One-Liner Examples

### Affibody Template
```python
mutator = UncertaintyGuidedMutation(target, "", modality="affibody", use_template=True)
```

### Nanobody Template
```python
mutator = UncertaintyGuidedMutation(target, "", modality="nanobody", use_template=True)
```

### Affitin Template
```python
mutator = UncertaintyGuidedMutation(target, "", modality="affitin", use_template=True)
```

### Custom Peptide
```python
mutator = UncertaintyGuidedMutation(target, "HELVELLA", modality="custom")
```

### Specific Residues
```python
mutator = UncertaintyGuidedMutation(target, peptide, residues_to_mutate=[0, 2, 4, 6])
```

## Template Sequences

| Modality | Sequence | Length |
|----------|----------|--------|
| **Affibody** | `VDNKFNKELSVAGREIVTLPNLNDPQKKAFIFSLWDDPSQSANLLAEAKKLNDAQAPK` | 58 |
| **Nanobody** | `AQVQLQESGGGLVQAGGSLRLSCAASERTFSTYAMGWFRQAPGREREFLAQINWSGTTTYYAESVKDRTTISRDNAKNTVYLEMNNLNADDTGIYFCAAHPQRGWGSTLGWTYWGQGTQVTVSSGGGGSGGGKPIPNPLLGLDSTRTGHHHHHH` | 110 |
| **Affitin** | `MRGSHHHHHHGSVKVKFVSSGEEKEVDTSKIKKVWRNLTKYGTIVQFTYDDNGKTGRGYVRELDAPKELLDMLARAEGKLN` | 94 |

## Common Patterns

### Pattern 1: Affibody with Uncertainty
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

### Pattern 2: Nanobody with Specific Residues
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

### Pattern 3: Custom Peptide with Specific Residues
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

### Pattern 4: Custom Template
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

## Parameter Reference

### New Parameters

| Parameter | Type | Default | Options |
|-----------|------|---------|---------|
| `modality` | str | "custom" | "affibody", "nanobody", "affitin", "custom" |
| `use_template` | bool | False | True/False |
| `custom_template` | str | None | Any sequence |
| `residues_to_mutate` | List[int] | None | [0, 2, 4, ...] |

### When to Use Each

**`modality`**: Choose your scaffold type
- "affibody" → Small, compact
- "nanobody" → Antibody-like
- "affitin" → Fibronectin-based
- "custom" → Your own sequence

**`use_template`**: Use pre-defined sequence?
- True → Use template for modality
- False → Use temp_pept_seq

**`custom_template`**: Override template?
- None → Use default template
- "SEQUENCE" → Use your sequence

**`residues_to_mutate`**: Specify positions?
- None → Auto-select (uncertainty-guided)
- [0, 2, 4] → Mutate these positions

## Output Changes

Results now include:

```python
results = mutator.run()

results["modality"]           # "affibody", "nanobody", etc.
results["peptide_seq"]        # Actual peptide used
results["residues_to_mutate"] # Specified residues (if any)
```

## Residue Indexing

Residues are 0-indexed in the peptide:

```
Peptide:  H E L V E L L A
Index:    0 1 2 3 4 5 6 7

residues_to_mutate=[0, 3, 7]  # Mutate H, V, A
```

## Decision Tree

```
Do you want to use a template?
├─ Yes
│  ├─ Affibody? → modality="affibody", use_template=True
│  ├─ Nanobody? → modality="nanobody", use_template=True
│  ├─ Affitin? → modality="affitin", use_template=True
│  └─ Custom template? → custom_template="SEQUENCE"
└─ No
   └─ Use temp_pept_seq

Do you want to specify residues?
├─ Yes → residues_to_mutate=[0, 2, 4, ...]
└─ No → Use mask_strategy and mask_ratio
```

## Examples by Use Case

### Use Case 1: Optimize Affibody
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

### Use Case 2: Mutate CDR Regions
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

### Use Case 3: Conservative Mutations
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq=peptide,
    modality="custom",
    mask_ratio=0.1,
    n_seq_out=5,
)
```

### Use Case 4: Aggressive Exploration
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target,
    temp_pept_seq=peptide,
    modality="custom",
    mask_ratio=0.5,
    n_seq_out=30,
)
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Unknown modality" | Use: "affibody", "nanobody", "affitin", or "custom" |
| Template not used | Set `use_template=True` |
| Residues not mutated | Check indices are valid (0 to len(peptide)-1) |
| No mutations | Check `n_seq_out > 0` |

## Tips

1. **Affibody**: Best for compact, stable binders
2. **Nanobody**: Best for antibody-like properties
3. **Affitin**: Best for natural scaffold
4. **Custom**: Best for novel sequences

5. **Uncertainty-guided**: Good for exploration
6. **Specific residues**: Good for targeted optimization

7. **Low mask_ratio** (0.1): Conservative
8. **High mask_ratio** (0.5): Aggressive

## Full Example

```python
from uncertainty_guided_mutation import UncertaintyGuidedMutation

# Your target
target = "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV"

# Generate affibody mutations
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

print(f"Modality: {results['modality']}")
print(f"Peptide length: {len(results['peptide_seq'])}")
print("Generated sequences:")
for seq in results["generated_sequences"]:
    print(f"  {seq}")
```

---

**Quick reference complete!** For more details, see `MODALITY_AND_RESIDUES_GUIDE.md`

