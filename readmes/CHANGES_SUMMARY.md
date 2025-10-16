# Changes Summary: Peptide-Only Uncertainty Sampling

## Overview
Modified the uncertainty-guided mutation pipeline to **only mask positions in the peptide sequence**, while keeping the target sequence fixed.

## Key Changes

### 1. New Method: `find_peptide_start_idx()`
```python
def find_peptide_start_idx(self, input_seq: str) -> int:
    """Find the token index where the peptide sequence starts (after <eos>)."""
```

- Tokenizes the full input sequence
- Finds the `<eos>` token position
- Returns the index of the first peptide token (right after `<eos>`)
- Handles edge cases where `<eos>` might not be found

### 2. Updated Method: `select_positions_to_mask()`
```python
def select_positions_to_mask(
    self, 
    uncertainty: torch.Tensor, 
    mask_indices: List[int],
    peptide_start_idx: int | None = None
) -> List[int]:
```

**Changes:**
- Added `peptide_start_idx` parameter
- Filters `mask_indices` to only include positions >= `peptide_start_idx`
- Only considers peptide positions when selecting top-k or threshold-based masks
- Prevents any masking in the target sequence

### 3. Updated Method: `run()`
```python
def run(self) -> Dict[str, any]:
```

**Changes:**
- Calls `find_peptide_start_idx()` to locate peptide start
- Passes `peptide_start_idx` to `select_positions_to_mask()`
- Prints peptide start index for debugging
- Returns `peptide_start_idx` in results dictionary

### 4. Updated Tests
- `test_uncertainty_analysis()` now:
  - Filters mask indices to peptide-only positions
  - Shows uncertainty statistics for peptide only
  - Displays top uncertain positions in peptide

## Workflow Diagram

```
Input: target_seq <eos> temp_pept_seq
  ↓
[Tokenize] Find <eos> token position
  ↓
[Get logprobs] For entire sequence
  ↓
[Compute uncertainty] For entire sequence
  ↓
[Filter to peptide] Only consider positions after <eos>
  ↓
[Select positions] Top-k or threshold in peptide only
  ↓
[Create masked sequence] Mask only peptide positions
  ↓
[Generate mutations] Sample from masked peptide positions
  ↓
Output: mutated peptides (target sequence unchanged)
```

## Example Usage

```python
from uncertainty_guided_mutation import UncertaintyGuidedMutation

mutator = UncertaintyGuidedMutation(
    target_seq="MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV",
    temp_pept_seq="HELVELLA",
    mask_strategy="top_k",
    mask_ratio=0.3,
    n_seq_out=10,
)

results = mutator.run()

# Results will show:
# - peptide_start_idx: Token index where peptide starts
# - positions_to_mask: Only indices >= peptide_start_idx
# - generated_sequences: Mutations of HELVELLA only
```

## Benefits

✅ **Target sequence remains fixed** - provides stable context
✅ **Focused mutation** - only explores peptide sequence space
✅ **Cleaner interpretation** - uncertainty scores are for peptide only
✅ **Biologically sensible** - target provides binding context

## Testing

Run the updated tests:
```bash
python test_uncertainty_mutation.py
```

Key test outputs:
- Peptide token indices are correctly identified
- Uncertainty statistics are computed for peptide only
- Top uncertain positions are within peptide range
- Generated sequences show mutations only in peptide

## Files Modified

1. `uncertainty_guided_mutation.py`
   - Added `find_peptide_start_idx()` method
   - Updated `select_positions_to_mask()` signature and logic
   - Updated `run()` method

2. `test_uncertainty_mutation.py`
   - Updated `test_uncertainty_analysis()` to filter for peptide positions

3. `UNCERTAINTY_GUIDED_MUTATION_GUIDE.md`
   - Updated implementation details section
   - Updated questions to consider section

