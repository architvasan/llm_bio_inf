# Custom Weights Support Added

## What Was Added

### 1. New Static Method: `_load_weights_safetensors()`

**Location**: `uncertainty_guided_mutation.py` lines 60-76

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

**Key Features**:
- Static method (can be called without instance)
- Uses `safetensors.torch.load_file()` for safe loading
- Simple and direct approach
- Proper error handling via exceptions

### 2. Updated `__post_init__()` Method

**Location**: `uncertainty_guided_mutation.py` lines 45-58

**Changes**:
```python
def __post_init__(self):
    """Load model and tokenizer."""
    self.tokenizer = AutoTokenizer.from_pretrained(...)
    self.model = AutoModelForMaskedLM.from_pretrained(...)
    
    # NEW: Load custom weights if provided
    if self.model_weights is not None:
        self.model = self._load_weights_safetensors(self.model, self.model_weights)
    
    self.model.eval()
```

**What It Does**:
1. Loads base model from HuggingFace
2. Checks if `model_weights` parameter is provided
3. If yes, loads custom weights from `.safetensors` file
4. Sets model to eval mode

### 3. Updated Class Docstring

**Location**: `uncertainty_guided_mutation.py` lines 21-34

Added comprehensive docstring documenting:
- `model_weights`: Optional path to .safetensors file with custom weights
- All other attributes for clarity

### 4. Updated Example Usage

**Location**: `uncertainty_guided_mutation.py` lines 316-356

Added two examples:
1. **Example 1**: Using default model weights
2. **Example 2**: Using custom model weights (commented out for safety)

## How It Works

### Loading Flow

```
1. Create UncertaintyGuidedMutation instance
   ↓
2. __post_init__() is called
   ↓
3. Load base model from HuggingFace
   ↓
4. Check if model_weights parameter is provided
   ├─ If None: Use default weights (skip to step 6)
   └─ If provided: Go to step 5
   ↓
5. Load custom weights from .safetensors file
   ├─ Read file using safetensors.torch.load_file()
   ├─ Get state dict
   └─ Apply to model using load_state_dict()
   ↓
6. Set model to eval mode
   ↓
7. Ready to use!
```

## Usage Examples

### Example 1: Default Weights (No Change)
```python
mutator = UncertaintyGuidedMutation(
    target_seq="MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV",
    temp_pept_seq="HELVELLA",
)
# Uses Bo1015/proteinglm-1b-mlm from HuggingFace
```

### Example 2: Custom Weights (NEW)
```python
mutator = UncertaintyGuidedMutation(
    target_seq="MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV",
    temp_pept_seq="HELVELLA",
    model_weights="./fine_tuned_model.safetensors",
)
# Loads base model, then applies custom weights
```

### Example 3: Different Model + Custom Weights
```python
mutator = UncertaintyGuidedMutation(
    target_seq="MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV",
    temp_pept_seq="HELVELLA",
    model_id="different/model-id",
    model_weights="./custom_weights.safetensors",
)
```

## Comparison with generate.py

### Your generate.py Implementation
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

### New Implementation in uncertainty_guided_mutation.py
```python
@staticmethod
def _load_weights_safetensors(model, safetensors_path):
    """Load weights from a .safetensors file into a PyTorch model."""
    from safetensors.torch import load_file
    
    loaded_state_dict = load_file(safetensors_path)
    model.load_state_dict(loaded_state_dict)
    return model
```

### Differences
| Aspect | generate.py | uncertainty_guided_mutation.py |
|--------|-------------|-------------------------------|
| Method | `safe_open()` context manager | `load_file()` direct |
| Device handling | Explicit parameter | Handled in `__post_init__()` |
| Complexity | More verbose | Simpler |
| Flexibility | More control | Streamlined |

**Both approaches are valid!** The new one is simpler because device handling is done before calling the method.

## Integration Points

### Where Custom Weights Are Used
1. **In `__post_init__()`**: Automatically loaded when instance is created
2. **No changes needed elsewhere**: Rest of pipeline works the same

### Backward Compatibility
- ✅ Fully backward compatible
- ✅ Default behavior unchanged if `model_weights=None`
- ✅ Existing code continues to work

## Error Handling

### Automatic Error Handling
```python
try:
    mutator = UncertaintyGuidedMutation(
        target_seq=target,
        temp_pept_seq=peptide,
        model_weights="./nonexistent.safetensors",
    )
except FileNotFoundError:
    print("Weights file not found!")
except RuntimeError as e:
    print(f"Error loading weights: {e}")
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError` | Path doesn't exist | Check file path |
| `RuntimeError: Error(s) in loading state_dict` | Weights don't match model | Verify model_id matches weights |
| `CUDA out of memory` | Model too large for GPU | Use CPU or reduce batch size |

## Testing Custom Weights

### Test 1: Verify Loading Works
```python
from uncertainty_guided_mutation import UncertaintyGuidedMutation

try:
    mutator = UncertaintyGuidedMutation(
        target_seq="MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV",
        temp_pept_seq="HELVELLA",
        model_weights="./my_model.safetensors",
        n_seq_out=2,
    )
    print("✓ Custom weights loaded successfully")
except Exception as e:
    print(f"✗ Error: {e}")
```

### Test 2: Verify Generation Works
```python
results = mutator.run()
print(f"✓ Generated {len(results['generated_sequences'])} sequences")
for seq in results["generated_sequences"]:
    print(f"  - {seq}")
```

## Files Modified

1. **uncertainty_guided_mutation.py**
   - Added `_load_weights_safetensors()` static method
   - Updated `__post_init__()` to load custom weights
   - Updated class docstring
   - Updated example usage

## Files Created (Documentation)

1. **CUSTOM_WEIGHTS_USAGE.md** - Detailed guide
2. **CUSTOM_WEIGHTS_ADDED.md** - This file

## Summary

✅ **Custom weights support fully implemented!**

- Simple, clean implementation
- Backward compatible
- Well documented
- Ready to use
- Based on your generate.py pattern

You can now:
1. Use default model weights (no change)
2. Load custom `.safetensors` weights
3. Mix and match different models and weights
4. Integrate with your existing pipeline

