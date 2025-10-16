"""
Uncertainty-guided peptide mutation generation.

Workflow:
1. Get logprobs for target_seq <eos> temp_pept_seq
2. Compute mutation likelihood = 1 - prob(s) for each position
3. Mask positions based on likelihood threshold or top-k
4. Generate mutations with masked positions
"""

from transformers import AutoModelForMaskedLM, AutoTokenizer
import torch
import numpy as np
from dataclasses import dataclass
from typing import Tuple, List, Dict
from tqdm import tqdm


@dataclass
class UncertaintyGuidedMutation:
    """
    Uncertainty-guided peptide mutation generation.

    Attributes:
        target_seq: Target protein sequence (e.g., antibody)
        temp_pept_seq: Temporary peptide sequence to mutate
        model_id: HuggingFace model ID (default: Bo1015/proteinglm-1b-mlm)
        model_weights: Optional path to .safetensors file with custom weights
        device: Device to run model on (auto-detected)
        n_seq_out: Number of sequences to generate
        mask_strategy: How to select positions to mask ("top_k", "threshold", "entropy")
        mask_ratio: For top_k strategy, fraction of peptide positions to mask
        uncertainty_threshold: For threshold strategy, uncertainty cutoff
    """
    target_seq: str
    temp_pept_seq: str
    model_id: str = "Bo1015/proteinglm-1b-mlm"
    model_weights: str | None = None
    device: object = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    n_seq_out: int = 10
    mask_strategy: str = "top_k"  # "top_k", "threshold", or "entropy"
    mask_ratio: float = 0.3  # For top_k: fraction of positions to mask
    uncertainty_threshold: float = 0.5  # For threshold strategy
    
    def __post_init__(self):
        """Load model and tokenizer."""
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_id, trust_remote_code=True, use_fast=True
        )
        self.model = AutoModelForMaskedLM.from_pretrained(
            self.model_id, trust_remote_code=True, torch_dtype=torch.bfloat16
        ).to(self.device)

        # Load custom weights if provided
        if self.model_weights is not None:
            self.model = self._load_weights_safetensors(self.model, self.model_weights)

        self.model.eval()

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
    
    def get_logprobs(self, seq: str) -> Tuple[torch.Tensor, torch.Tensor, List[int]]:
        """
        Get log probabilities for each position in sequence.
        
        Args:
            seq: Input sequence (no masks)
            
        Returns:
            logprobs: Log probabilities for each position (seq_len,)
            probs: Probabilities for each position (seq_len,)
            mask_indices: Indices of non-special tokens
        """
        inputs = self.tokenizer(seq, return_tensors='pt')
        input_ids = inputs['input_ids'].to(self.device)
        attention_mask = inputs['attention_mask'].to(self.device)
        
        with torch.inference_mode():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits[0]  # (seq_len, vocab_size)
        
        # Get probabilities
        probs = torch.softmax(logits, dim=-1)  # (seq_len, vocab_size)
        
        # Get max probability for each position (greedy prediction)
        max_probs, _ = torch.max(probs, dim=-1)  # (seq_len,)
        logprobs = torch.log(max_probs + 1e-10)  # Add small epsilon to avoid log(0)
        
        # Get non-special token indices
        mask_token_id = self.tokenizer.mask_token_id
        non_special_mask = input_ids[0] != mask_token_id
        mask_indices = torch.where(non_special_mask)[0].tolist()
        
        return logprobs, max_probs, mask_indices
    
    def compute_uncertainty(self, probs: torch.Tensor) -> torch.Tensor:
        """
        Compute uncertainty for each position.
        
        Args:
            probs: Probabilities for each position (seq_len,)
            
        Returns:
            uncertainty: Uncertainty scores (seq_len,)
        """
        # Option 1: 1 - prob(s)
        uncertainty = 1.0 - probs
        return uncertainty
    
    def select_positions_to_mask(
        self,
        uncertainty: torch.Tensor,
        mask_indices: List[int],
        peptide_start_idx: int | None = None
    ) -> List[int]:
        """
        Select positions to mask based on uncertainty.
        Only masks positions in the peptide sequence, not the target sequence.

        Args:
            uncertainty: Uncertainty scores for each position
            mask_indices: Indices of non-special tokens
            peptide_start_idx: Token index where peptide sequence starts (after <eos>)

        Returns:
            positions_to_mask: List of token positions to mask
        """
        # Filter mask_indices to only include peptide positions
        if peptide_start_idx is not None:
            peptide_mask_indices = [idx for idx in mask_indices if idx >= peptide_start_idx]
        else:
            peptide_mask_indices = mask_indices

        if not peptide_mask_indices:
            return []

        if self.mask_strategy == "top_k":
            # Mask top-k most uncertain positions in peptide
            n_mask = max(1, int(len(peptide_mask_indices) * self.mask_ratio))
            _, top_uncertain_indices = torch.topk(
                uncertainty[peptide_mask_indices], k=min(n_mask, len(peptide_mask_indices))
            )
            positions_to_mask = [peptide_mask_indices[i] for i in top_uncertain_indices.tolist()]

        elif self.mask_strategy == "threshold":
            # Mask positions above uncertainty threshold in peptide
            positions_to_mask = [
                idx for idx in peptide_mask_indices
                if uncertainty[idx] > self.uncertainty_threshold
            ]

        elif self.mask_strategy == "entropy":
            # Use entropy-based uncertainty (requires full probability distribution)
            positions_to_mask = [peptide_mask_indices[0]]  # Placeholder

        else:
            raise ValueError(f"Unknown mask_strategy: {self.mask_strategy}")

        return positions_to_mask
    
    def create_masked_sequence(
        self, 
        seq: str, 
        positions_to_mask: List[int]
    ) -> str:
        """
        Create masked sequence by replacing positions with [MASK].
        
        Args:
            seq: Original sequence
            positions_to_mask: Token positions to mask
            
        Returns:
            masked_seq: Sequence with [MASK] tokens
        """
        inputs = self.tokenizer(seq, return_tensors='pt')
        input_ids = inputs['input_ids'][0].tolist()
        
        # Replace positions with mask token
        mask_token_id = self.tokenizer.mask_token_id
        for pos in positions_to_mask:
            input_ids[pos] = mask_token_id
        
        # Decode back to sequence
        masked_seq = self.tokenizer.decode(input_ids, skip_special_tokens=False)
        return masked_seq
    
    def generate_mutations(self, masked_seq: str) -> List[str]:
        """
        Generate mutated sequences from masked sequence.
        
        Args:
            masked_seq: Sequence with [MASK] tokens
            
        Returns:
            generated_sequences: List of generated sequences
        """
        inputs = self.tokenizer(masked_seq, return_tensors='pt')
        input_ids = inputs['input_ids'].to(self.device)
        attention_mask = inputs['attention_mask'].to(self.device)
        
        # Identify mask token positions
        mask_token_id = self.tokenizer.mask_token_id
        mask_indices = (input_ids == mask_token_id).nonzero(as_tuple=False)
        
        generated_sequences = []
        
        with torch.inference_mode():
            for _ in tqdm(range(self.n_seq_out), desc="Generating mutations"):
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                logits = outputs.logits[0]
                
                sampled_ids = input_ids.clone()
                
                for idx in mask_indices:
                    pos = idx[1]
                    probs = torch.softmax(logits[pos], dim=-1)
                    sampled_token_id = torch.multinomial(probs, num_samples=1)
                    sampled_ids[0, pos] = sampled_token_id
                
                decoded_seq = self.tokenizer.decode(sampled_ids[0], skip_special_tokens=True)
                seq_out = "".join(decoded_seq.split())
                generated_sequences.append(seq_out)
        
        return generated_sequences
    
    def find_peptide_start_idx(self, input_seq: str) -> int:
        """
        Find the token index where the peptide sequence starts (after <eos>).

        Args:
            input_seq: Full input sequence with target<eos>peptide

        Returns:
            peptide_start_idx: Token index where peptide starts
        """
        # Tokenize to find where <eos> token is
        inputs = self.tokenizer(input_seq, return_tensors='pt')
        input_ids = inputs['input_ids'][0].tolist()

        # Find <eos> token ID
        eos_token_id = self.tokenizer.eos_token_id

        # Find the position of <eos> token
        try:
            eos_idx = input_ids.index(eos_token_id)
            peptide_start_idx = eos_idx + 1  # Position right after <eos>
        except ValueError:
            # If <eos> not found, assume peptide starts at middle
            peptide_start_idx = len(input_ids) // 2
            print(f"Warning: <eos> token not found. Assuming peptide starts at index {peptide_start_idx}")

        return peptide_start_idx

    def run(self) -> Dict[str, any]:
        """
        Run the full uncertainty-guided mutation pipeline.
        Only masks positions in the peptide sequence.

        Returns:
            results: Dictionary with uncertainty scores and generated sequences
        """
        # Step 1: Create input sequence
        input_seq = f"{self.target_seq}<eos>{self.temp_pept_seq}"
        print(f"Input sequence: {input_seq}")

        # Step 2: Get logprobs and uncertainty
        _, probs, mask_indices = self.get_logprobs(input_seq)
        uncertainty = self.compute_uncertainty(probs)

        print(f"Uncertainty scores: {uncertainty[mask_indices]}")

        # Step 3: Find where peptide starts
        peptide_start_idx = self.find_peptide_start_idx(input_seq)
        print(f"Peptide starts at token index: {peptide_start_idx}")

        # Step 4: Select positions to mask (only in peptide)
        positions_to_mask = self.select_positions_to_mask(
            uncertainty, mask_indices, peptide_start_idx
        )
        print(f"Positions to mask (peptide only): {positions_to_mask}")

        # Step 5: Create masked sequence
        masked_seq = self.create_masked_sequence(input_seq, positions_to_mask)
        print(f"Masked sequence: {masked_seq}")

        # Step 6: Generate mutations
        generated_sequences = self.generate_mutations(masked_seq)

        return {
            "input_seq": input_seq,
            "uncertainty": uncertainty,
            "peptide_start_idx": peptide_start_idx,
            "positions_to_mask": positions_to_mask,
            "masked_seq": masked_seq,
            "generated_sequences": generated_sequences,
        }


if __name__ == "__main__":
    # Example usage
    target_seq = "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV"
    temp_pept_seq = "HELVELLA"

    # Example 1: Using default model weights
    print("=" * 80)
    print("Example 1: Using default model weights")
    print("=" * 80)
    mutator = UncertaintyGuidedMutation(
        target_seq=target_seq,
        temp_pept_seq=temp_pept_seq,
        mask_strategy="top_k",
        mask_ratio=0.3,
        n_seq_out=5,
    )

    results = mutator.run()
    print("\nGenerated mutations:")
    for seq in results["generated_sequences"]:
        print(seq)

    # Example 2: Using custom model weights
    print("\n" + "=" * 80)
    print("Example 2: Using custom model weights (if available)")
    print("=" * 80)
    # Uncomment and provide path to your .safetensors file
    # mutator_custom = UncertaintyGuidedMutation(
    #     target_seq=target_seq,
    #     temp_pept_seq=temp_pept_seq,
    #     model_weights="/path/to/your/model.safetensors",
    #     mask_strategy="top_k",
    #     mask_ratio=0.3,
    #     n_seq_out=5,
    # )
    # results_custom = mutator_custom.run()
    # print("\nGenerated mutations with custom weights:")
    # for seq in results_custom["generated_sequences"]:
    #     print(seq)

