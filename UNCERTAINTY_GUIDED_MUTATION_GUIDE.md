# Uncertainty-Guided Peptide Mutation Generation

## Overview

Your proposed approach is **sound and well-motivated**. It uses model uncertainty to guide which positions should be mutated, which is a principled way to explore the sequence space.

## Proposed Workflow

```
Input: target_seq <eos> temp_pept_seq
  ↓
[Step 1] Get logprobs for each position
  ↓
[Step 2] Compute uncertainty = 1 - prob(s)
  ↓
[Step 3] Select positions to mask based on uncertainty
  ↓
[Step 4] Create masked sequence
  ↓
[Step 5] Generate mutations with pglm model
  ↓
Output: mutated peptides
```

## Key Design Decisions

### 1. Uncertainty Metric
- **Current**: `uncertainty = 1 - prob(s)` (simple and interpretable)
- **Alternative**: Entropy-based uncertainty (more robust)
  ```python
  entropy = -sum(p * log(p)) for all tokens
  ```
- **Recommendation**: Start with `1 - prob(s)`, validate with entropy later

### 2. Masking Strategy
Three options implemented:

#### a) Top-K Strategy (Recommended for start)
- Mask top-k% most uncertain positions
- Pros: Predictable, easy to control
- Cons: May miss important positions
- Usage: `mask_strategy="top_k", mask_ratio=0.3`

#### b) Threshold Strategy
- Mask all positions above uncertainty threshold
- Pros: Adaptive to sequence
- Cons: May mask too many/few positions
- Usage: `mask_strategy="threshold", uncertainty_threshold=0.5`

#### c) Entropy Strategy
- Use full probability distribution entropy
- Pros: More theoretically grounded
- Cons: More computationally expensive
- Usage: `mask_strategy="entropy"`

### 3. Probability Calibration
**Important**: Neural network probabilities are often miscalibrated.

Consider:
```python
# Temperature scaling
calibrated_probs = softmax(logits / temperature)

# Or use model confidence scores if available
```

## Implementation Details

### File: `uncertainty_guided_mutation.py`

Main class: `UncertaintyGuidedMutation`

Key methods:
- `get_logprobs()`: Extract probabilities for each position
- `compute_uncertainty()`: Convert probs to uncertainty scores
- `find_peptide_start_idx()`: Locate where peptide sequence starts (after `<eos>`)
- `select_positions_to_mask()`: Choose which positions to mask **in peptide only**
- `create_masked_sequence()`: Build masked input
- `generate_mutations()`: Sample from masked positions
- `run()`: Execute full pipeline

**Important**: Only the peptide sequence is masked for uncertainty sampling. The target sequence remains fixed.

### File: `test_uncertainty_mutation.py`

Test suite with:
1. Basic workflow test
2. Different masking strategies comparison
3. Uncertainty distribution analysis

## Usage Examples

### Basic Usage (Default Model Weights)

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
print(results["generated_sequences"])
```

### Using Custom Model Weights

```python
from uncertainty_guided_mutation import UncertaintyGuidedMutation

mutator = UncertaintyGuidedMutation(
    target_seq="MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV",
    temp_pept_seq="HELVELLA",
    model_weights="/path/to/your/model.safetensors",  # Load custom weights
    mask_strategy="top_k",
    mask_ratio=0.3,
    n_seq_out=10,
)

results = mutator.run()
print(results["generated_sequences"])
```

### Different Masking Strategies

```python
# Top-k strategy (mask 30% most uncertain positions)
mutator_topk = UncertaintyGuidedMutation(
    target_seq=target_seq,
    temp_pept_seq=temp_pept_seq,
    mask_strategy="top_k",
    mask_ratio=0.3,
)

# Threshold strategy (mask positions with uncertainty > 0.5)
mutator_threshold = UncertaintyGuidedMutation(
    target_seq=target_seq,
    temp_pept_seq=temp_pept_seq,
    mask_strategy="threshold",
    uncertainty_threshold=0.5,
)
```

## Recommendations for Validation

### 1. Sanity Checks
- [ ] Verify uncertainty scores are in [0, 1]
- [ ] Check that masked positions are actually uncertain
- [ ] Confirm generated sequences are different from input

### 2. Biological Validation
- [ ] Do generated mutations preserve secondary structure?
- [ ] Are mutations at conserved positions less frequent?
- [ ] Compare with random mutation baseline

### 3. Hyperparameter Tuning
- [ ] Try different `mask_ratio` values (0.1, 0.3, 0.5)
- [ ] Compare masking strategies
- [ ] Analyze uncertainty distribution

### 4. Ablation Studies
- [ ] Single-pass vs. two-pass generation
- [ ] Different uncertainty metrics
- [ ] Impact of target_seq context

## Potential Improvements

### Short-term
1. Add entropy-based uncertainty metric
2. Implement temperature scaling for calibration
3. Add visualization of uncertainty scores
4. Compare with random masking baseline

### Medium-term
1. Learn optimal mask_ratio from data
2. Use reinforcement learning to optimize mutations
3. Add biological constraints (e.g., hydrophobicity)
4. Multi-round iterative refinement

### Long-term
1. Combine with structure prediction (xT-Fold)
2. Optimize for specific properties (binding, stability)
3. Ensemble multiple models
4. Active learning for efficient exploration

## Running Tests

```bash
# Run all tests
python test_uncertainty_mutation.py

# Or import and use directly
from uncertainty_guided_mutation import UncertaintyGuidedMutation
```

## Loading Custom Model Weights

The `UncertaintyGuidedMutation` class supports loading custom model weights from `.safetensors` files:

```python
mutator = UncertaintyGuidedMutation(
    target_seq=target_seq,
    temp_pept_seq=temp_pept_seq,
    model_weights="/path/to/model.safetensors",
)
```

### How It Works

1. Model is first loaded from HuggingFace with default weights
2. If `model_weights` is provided, the `.safetensors` file is loaded
3. Weights are applied to the model using `load_state_dict()`
4. Model is moved to the specified device (GPU/CPU)
5. Model is set to eval mode

### Requirements

- `.safetensors` file must be compatible with the model architecture
- File should contain the complete state dict for the model
- Ensure the model_id matches the weights file

### Example with Custom Weights

```python
from uncertainty_guided_mutation import UncertaintyGuidedMutation

# Load model with custom fine-tuned weights
mutator = UncertaintyGuidedMutation(
    target_seq="MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV",
    temp_pept_seq="HELVELLA",
    model_id="Bo1015/proteinglm-1b-mlm",  # Base model
    model_weights="./fine_tuned_weights.safetensors",  # Custom weights
    n_seq_out=10,
)

results = mutator.run()
```

## Notes

- The `<eos>` token is correctly used as separator between target and peptide
- Model is set to eval mode to avoid dropout randomness
- Uses `torch.inference_mode()` for efficiency
- Supports both CPU and GPU (auto-detected)
- Custom weights are optional; default HuggingFace weights are used if not provided

## Questions to Consider

1. **How many rounds of refinement?**
   - Current: 1 round (2-pass total)
   - Alternative: Iterative refinement (3+ passes)
   - Could re-run uncertainty sampling on generated sequences

2. **How to handle context effects?**
   - Current: Full sequence context (target + peptide)
   - Alternative: Local context windows around peptide
   - Note: Target sequence provides important context for peptide mutations

3. **Validation metric?**
   - Binding affinity?
   - Structural stability?
   - Sequence diversity?
   - Comparison to wild-type?

4. **Should you iterate on generated sequences?**
   - Current: Single pass generation
   - Alternative: Use generated sequences as new temp_pept_seq for refinement

