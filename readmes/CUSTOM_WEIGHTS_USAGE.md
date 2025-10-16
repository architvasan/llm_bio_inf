# Loading Custom Model Weights

## Quick Start

```python
from uncertainty_guided_mutation import UncertaintyGuidedMutation

# With custom weights
mutator = UncertaintyGuidedMutation(
    target_seq="MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV",
    temp_pept_seq="HELVELLA",
    model_weights="/path/to/your/model.safetensors",
    n_seq_out=10,
)

results = mutator.run()
```

## Implementation Details

### Method: `_load_weights_safetensors()`

```python
@staticmethod
def _load_weights_safetensors(model, safetensors_path):
    """
    Load weights from a .safetensors file into a PyTorch model.
    
    Args:
        model: The model to load weights into
        safetensors_path: Path to the .safetensors file
        
    Returns:
        model: Model with loaded weights
    """
    from safetensors.torch import load_file
    
    loaded_state_dict = load_file(safetensors_path)
    model.load_state_dict(loaded_state_dict)
    return model
```

### Loading Process in `__post_init__()`

1. **Load base model** from HuggingFace
   ```python
   self.model = AutoModelForMaskedLM.from_pretrained(
       self.model_id, trust_remote_code=True, torch_dtype=torch.bfloat16
   ).to(self.device)
   ```

2. **Load custom weights** (if provided)
   ```python
   if self.model_weights is not None:
       self.model = self._load_weights_safetensors(self.model, self.model_weights)
   ```

3. **Set to eval mode**
   ```python
   self.model.eval()
   ```

## Usage Patterns

### Pattern 1: Default Weights Only
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target_seq,
    temp_pept_seq=temp_pept_seq,
)
# Uses Bo1015/proteinglm-1b-mlm from HuggingFace
```

### Pattern 2: Custom Weights
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target_seq,
    temp_pept_seq=temp_pept_seq,
    model_weights="./fine_tuned_model.safetensors",
)
# Loads base model, then applies custom weights
```

### Pattern 3: Different Model + Custom Weights
```python
mutator = UncertaintyGuidedMutation(
    target_seq=target_seq,
    temp_pept_seq=temp_pept_seq,
    model_id="different/model-id",
    model_weights="./custom_weights.safetensors",
)
# Loads different base model with custom weights
```

## File Format Requirements

### .safetensors Format
- Binary format optimized for safe tensor loading
- Contains complete state dict of the model
- Must be compatible with the model architecture

### Compatibility Checklist
- ✅ Model architecture matches (e.g., both are proteinglm-1b-mlm)
- ✅ State dict keys match the model's expected keys
- ✅ Tensor shapes are compatible
- ✅ File is not corrupted

## Error Handling

### Common Issues

**Issue**: `RuntimeError: Error(s) in loading state_dict`
- **Cause**: Weights don't match model architecture
- **Solution**: Verify model_id matches the weights file

**Issue**: `FileNotFoundError: [Errno 2] No such file or directory`
- **Cause**: Path to .safetensors file is incorrect
- **Solution**: Check file path and ensure file exists

**Issue**: `RuntimeError: CUDA out of memory`
- **Cause**: Model + weights too large for GPU
- **Solution**: Use CPU or reduce batch size

## Comparison with generate.py

The implementation is based on the pattern from `generate.py`:

### generate.py approach:
```python
@staticmethod
def load_weights_safetensors(model, safetensors_path, device="cpu"):
    """Loads weights from a .safetensors file into a PyTorch model."""
    loaded_state_dict = {}
    with safe_open(safetensors_path, framework="pt", device=device) as f:
        for key in f.keys():
            loaded_state_dict[key] = f.get_tensor(key)
    
    model.load_state_dict(loaded_state_dict)
    return model
```

### uncertainty_guided_mutation.py approach:
```python
@staticmethod
def _load_weights_safetensors(model, safetensors_path):
    """Load weights from a .safetensors file into a PyTorch model."""
    from safetensors.torch import load_file
    
    loaded_state_dict = load_file(safetensors_path)
    model.load_state_dict(loaded_state_dict)
    return model
```

**Differences**:
- Uses `load_file()` instead of `safe_open()` context manager
- Simpler and more direct approach
- Device handling is done in `__post_init__()` before loading weights

## Testing Custom Weights

```python
from uncertainty_guided_mutation import UncertaintyGuidedMutation

# Test with custom weights
try:
    mutator = UncertaintyGuidedMutation(
        target_seq="MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV",
        temp_pept_seq="HELVELLA",
        model_weights="./my_model.safetensors",
        n_seq_out=2,
    )
    results = mutator.run()
    print("✓ Custom weights loaded successfully")
    print(f"Generated {len(results['generated_sequences'])} sequences")
except Exception as e:
    print(f"✗ Error loading custom weights: {e}")
```

## Next Steps

1. Prepare your `.safetensors` file
2. Verify file path is correct
3. Test with a small example first
4. Run full pipeline with custom weights

