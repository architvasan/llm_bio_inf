"""
Uncertainty-guided peptide mutation generation.

Workflow:
1. Get logprobs for target_seq <eos> temp_pept_seq
2. Compute mutation likelihood = 1 - prob(s) for each position
3. Mask positions based on likelihood threshold or top-k
4. Generate mutations with masked positions

Supports multiple modalities (affibody, nanobody, affitin) with optional templates.
Includes CDR loop identification for nanobody redesign.
"""

from transformers import AutoModelForMaskedLM, AutoTokenizer
import torch
from dataclasses import dataclass
from typing import Tuple, List, Dict
from tqdm import tqdm

try:
    from abnumber import Chain
    HAS_ABNUMBER = True
except ImportError:
    HAS_ABNUMBER = False

# Template sequences for different modalities
MODALITY_TEMPLATES = {
    "affibody": "VDNKFNKELSVAGREIVTLPNLNDPQKKAFIFSLWDDPSQSANLLAEAKKLNDAQAPK",
    "nanobody": "AQVQLQESGGGLVQAGGSLRLSCAASERTFSTYAMGWFRQAPGREREFLAQINWSGTTTYYAESVKDRTTISRDNAKNTVYLEMNNLNADDTGIYFCAAHPQRGWGSTLGWTYWGQGTQVTVSSGGGGSGGGKPIPNPLLGLDSTRTGHHHHHH",
    "affitin": "MRGSHHHHHHGSVKVKFVSSGEEKEVDTSKIKKVWRNLTKYGTIVQFTYDDNGKTGRGYVRELDAPKELLDMLARAEGKLN",
}

# CDR loop definitions for nanobodies (IMGT numbering - fallback if abnumber not available)
# These are approximate positions and should be used only if abnumber is not available
NANOBODY_CDR_REGIONS_IMGT = {
    "CDR1": (26, 35),  # (start, end) inclusive, 0-indexed
    "CDR2": (49, 65),
    "CDR3": (94, 102),
}


@dataclass
class UncertaintyGuidedMutation:
    """
    Uncertainty-guided peptide mutation generation with modality support.

    Attributes:
        target_seq: Target protein sequence (e.g., antibody)
        temp_pept_seq: Temporary peptide sequence to mutate (optional if use_template=True)
        modality: Type of peptide scaffold ("affibody", "nanobody", "affitin", or "custom")
        model_id: HuggingFace model ID (default: Bo1015/proteinglm-1b-mlm)
        model_weights: Optional path to .safetensors file with custom weights
        device: Device to run model on (auto-detected)
        n_seq_out: Number of sequences to generate
        mask_strategy: How to select positions to mask ("top_k", "threshold", "entropy")
        mask_ratio: For top_k strategy, fraction of peptide positions to mask
        uncertainty_threshold: For threshold strategy, uncertainty cutoff
        use_template: Whether to use template sequence for the modality
        custom_template: Custom template sequence (overrides modality template)
        residues_to_mutate: Optional list of residue indices to mutate (0-indexed in peptide)
        nanobody_cdr_regions: For nanobody: which CDRs to mutate (list of "CDR1", "CDR2", "CDR3")
            Uses abnumber library with IMGT numbering for accurate identification
    """
    target_seq: str
    temp_pept_seq: str = ""  # Optional if use_template=True
    modality: str = "custom"  # "affibody", "nanobody", "affitin", or "custom"
    model_id: str = "Bo1015/proteinglm-1b-mlm"
    model_weights: str | None = None
    device: object = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    n_seq_out: int = 10
    mask_strategy: str = "top_k"  # "top_k", "threshold", or "entropy"
    mask_ratio: float = 0.3  # For top_k: fraction of positions to mask
    uncertainty_threshold: float = 0.5  # For threshold strategy
    use_template: bool = False  # Whether to use template for modality
    custom_template: str | None = None  # Custom template sequence
    residues_to_mutate: List[int] | None = None  # Specific residue indices to mutate
    nanobody_cdr_regions: List[str] | None = None  # For nanobody: ["CDR1", "CDR2", "CDR3"]
    
    def __post_init__(self):
        """Load model and tokenizer, validate inputs."""
        # Validate that either temp_pept_seq or use_template is provided
        if not self.temp_pept_seq and not self.use_template:
            raise ValueError(
                "Either provide temp_pept_seq or set use_template=True. "
                "Cannot proceed without a peptide sequence."
            )

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

    def get_template_sequence(self) -> str:
        """
        Get the template sequence for the specified modality.

        Returns:
            template_seq: Template sequence for the modality
        """
        if self.custom_template is not None:
            return self.custom_template

        if self.modality in MODALITY_TEMPLATES:
            return MODALITY_TEMPLATES[self.modality]

        raise ValueError(
            f"Unknown modality: {self.modality}. "
            f"Choose from {list(MODALITY_TEMPLATES.keys())} or set custom_template."
        )

    def get_peptide_sequence(self) -> str:
        """
        Get the peptide sequence to use (template or provided).

        If use_template=True, returns the template sequence.
        Otherwise, returns the provided temp_pept_seq.

        Returns:
            peptide_seq: Peptide sequence to mutate

        Raises:
            ValueError: If neither template nor custom sequence is available
        """
        if self.use_template:
            return self.get_template_sequence()

        if not self.temp_pept_seq:
            raise ValueError(
                "No peptide sequence available. Either provide temp_pept_seq or set use_template=True."
            )

        return self.temp_pept_seq

    def get_nanobody_cdr_residues(self) -> List[int]:
        """
        Get residue indices for specified CDR regions in nanobody.

        Uses abnumber library with IMGT numbering for accurate CDR identification.
        Falls back to hardcoded positions if abnumber is not available.

        Only works for nanobody modality. Returns residue indices (0-indexed)
        that correspond to the specified CDR regions.

        Returns:
            cdr_residues: List of residue indices (0-indexed) in the CDR regions

        Raises:
            ValueError: If modality is not nanobody or invalid CDR regions specified
        """
        if self.modality != "nanobody":
            raise ValueError(
                f"CDR identification only supported for nanobody modality, got {self.modality}"
            )

        if self.nanobody_cdr_regions is None:
            raise ValueError(
                "nanobody_cdr_regions must be specified for CDR-based mutation. "
                "Use: nanobody_cdr_regions=['CDR1', 'CDR2', 'CDR3']"
            )

        # Get the peptide sequence
        peptide_seq = self.get_peptide_sequence()

        # Use abnumber if available for accurate CDR identification
        if HAS_ABNUMBER:
            return self._get_cdr_residues_abnumber(peptide_seq)
        else:
            # Fallback to hardcoded positions
            return self._get_cdr_residues_fallback()

    def _get_cdr_residues_abnumber(self, nanobody_seq: str) -> List[int]:
        """
        Get CDR residues using abnumber library with IMGT numbering.

        Args:
            nanobody_seq: Nanobody sequence

        Returns:
            cdr_residues: List of residue indices (0-indexed)
        """
        try:
            chain = Chain(nanobody_seq, scheme='imgt')

            # Map CDR names to abnumber attributes
            cdr_map = {
                "CDR1": chain.cdr1_seq,
                "CDR2": chain.cdr2_seq,
                "CDR3": chain.cdr3_seq,
            }

            cdr_residues = []
            for cdr_name in self.nanobody_cdr_regions:
                if cdr_name not in cdr_map:
                    raise ValueError(
                        f"Unknown CDR region: {cdr_name}. "
                        f"Choose from {list(cdr_map.keys())}"
                    )

                cdr_seq = cdr_map[cdr_name]
                if cdr_seq:
                    # Find the CDR sequence in the full sequence
                    start_idx = nanobody_seq.find(cdr_seq)
                    if start_idx != -1:
                        end_idx = start_idx + len(cdr_seq) - 1
                        cdr_residues.extend(range(start_idx, end_idx + 1))

            return sorted(list(set(cdr_residues)))  # Remove duplicates and sort

        except Exception as e:
            print(f"Warning: abnumber CDR identification failed: {e}")
            print("Falling back to hardcoded CDR positions...")
            return self._get_cdr_residues_fallback()

    def _get_cdr_residues_fallback(self) -> List[int]:
        """
        Fallback CDR residue identification using hardcoded IMGT positions.

        Returns:
            cdr_residues: List of residue indices (0-indexed)
        """
        cdr_defs = NANOBODY_CDR_REGIONS_IMGT

        cdr_residues = []
        for cdr_name in self.nanobody_cdr_regions:
            if cdr_name not in cdr_defs:
                raise ValueError(
                    f"Unknown CDR region: {cdr_name}. "
                    f"Choose from {list(cdr_defs.keys())}"
                )
            start, end = cdr_defs[cdr_name]
            cdr_residues.extend(range(start, end + 1))

        return sorted(list(set(cdr_residues)))  # Remove duplicates and sort

    def identify_nanobody_cdrs(self, nanobody_seq: str) -> Dict[str, Tuple[int, int, str]]:
        """
        Identify CDR regions in a nanobody sequence.

        Uses abnumber library with IMGT numbering for accurate identification.
        Falls back to hardcoded positions if abnumber is not available.

        Args:
            nanobody_seq: Nanobody sequence

        Returns:
            cdr_dict: Dictionary with CDR info
                {
                    "CDR1": (start, end, sequence),
                    "CDR2": (start, end, sequence),
                    "CDR3": (start, end, sequence),
                }
        """
        if HAS_ABNUMBER:
            return self._identify_cdrs_abnumber(nanobody_seq)
        else:
            return self._identify_cdrs_fallback(nanobody_seq)

    def _identify_cdrs_abnumber(self, nanobody_seq: str) -> Dict[str, Tuple[int, int, str]]:
        """
        Identify CDR regions using abnumber library.

        Args:
            nanobody_seq: Nanobody sequence

        Returns:
            cdr_dict: Dictionary with CDR info
        """
        try:
            chain = Chain(nanobody_seq, scheme='imgt')

            cdr_dict = {}
            cdr_map = {
                "CDR1": chain.cdr1_seq,
                "CDR2": chain.cdr2_seq,
                "CDR3": chain.cdr3_seq,
            }

            for cdr_name, cdr_seq in cdr_map.items():
                if cdr_seq:
                    start_idx = nanobody_seq.find(cdr_seq)
                    if start_idx != -1:
                        end_idx = start_idx + len(cdr_seq) - 1
                        cdr_dict[cdr_name] = (start_idx, end_idx, cdr_seq)

            return cdr_dict

        except Exception as e:
            print(f"Warning: abnumber CDR identification failed: {e}")
            print("Falling back to hardcoded CDR positions...")
            return self._identify_cdrs_fallback(nanobody_seq)

    def _identify_cdrs_fallback(self, nanobody_seq: str) -> Dict[str, Tuple[int, int, str]]:
        """
        Identify CDR regions using hardcoded IMGT positions (fallback).

        Args:
            nanobody_seq: Nanobody sequence

        Returns:
            cdr_dict: Dictionary with CDR info
        """
        cdr_defs = NANOBODY_CDR_REGIONS_IMGT

        cdr_dict = {}
        for cdr_name, (start, end) in cdr_defs.items():
            if end < len(nanobody_seq):
                cdr_seq = nanobody_seq[start:end + 1]
                cdr_dict[cdr_name] = (start, end, cdr_seq)
            else:
                # Handle sequences shorter than expected
                actual_end = min(end, len(nanobody_seq) - 1)
                cdr_seq = nanobody_seq[start:actual_end + 1]
                cdr_dict[cdr_name] = (start, actual_end, cdr_seq)

        return cdr_dict

    def convert_residue_indices_to_token_indices(
        self,
        residue_indices: List[int],
        peptide_start_idx: int
    ) -> List[int]:
        """
        Convert residue indices (0-indexed in peptide) to token indices in full sequence.

        Args:
            residue_indices: List of residue indices (0-indexed in peptide)
            peptide_start_idx: Token index where peptide starts

        Returns:
            token_indices: List of token indices in full sequence
        """
        # Note: This is a simplified conversion assuming 1 token per residue
        # In reality, tokenization may vary
        token_indices = [peptide_start_idx + idx for idx in residue_indices]
        return token_indices
    
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
        Select positions to mask based on uncertainty, CDR regions, or custom residue indices.
        Only masks positions in the peptide sequence, not the target sequence.

        Args:
            uncertainty: Uncertainty scores for each position
            mask_indices: Indices of non-special tokens
            peptide_start_idx: Token index where peptide sequence starts (after <eos>)

        Returns:
            positions_to_mask: List of token positions to mask
        """
        # Priority 1: If CDR regions specified for nanobody, use those
        if self.nanobody_cdr_regions is not None and self.modality == "nanobody":
            if peptide_start_idx is None:
                raise ValueError("peptide_start_idx required when using nanobody_cdr_regions")
            cdr_residues = self.get_nanobody_cdr_residues()
            positions_to_mask = self.convert_residue_indices_to_token_indices(
                cdr_residues, peptide_start_idx
            )
            return positions_to_mask

        # Priority 2: If custom residues specified, use those
        if self.residues_to_mutate is not None:
            if peptide_start_idx is None:
                raise ValueError("peptide_start_idx required when using residues_to_mutate")
            positions_to_mask = self.convert_residue_indices_to_token_indices(
                self.residues_to_mutate, peptide_start_idx
            )
            return positions_to_mask

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
        # Step 0: Get peptide sequence (template or provided)
        peptide_seq = self.get_peptide_sequence()

        # Step 1: Create input sequence
        input_seq = f"{self.target_seq}<eos>{peptide_seq}"
        print(f"Modality: {self.modality}")
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

        if self.residues_to_mutate is not None:
            print(f"Custom residues to mutate: {self.residues_to_mutate}")

        # Step 5: Create masked sequence
        masked_seq = self.create_masked_sequence(input_seq, positions_to_mask)
        print(f"Masked sequence: {masked_seq}")

        # Step 6: Generate mutations
        generated_sequences = self.generate_mutations(masked_seq)

        return {
            "input_seq": input_seq,
            "peptide_seq": peptide_seq,
            "modality": self.modality,
            "uncertainty": uncertainty,
            "peptide_start_idx": peptide_start_idx,
            "positions_to_mask": positions_to_mask,
            "masked_seq": masked_seq,
            "generated_sequences": generated_sequences,
            "residues_to_mutate": self.residues_to_mutate,
        }


if __name__ == "__main__":
    # Example usage
    target_seq = "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV"
    temp_pept_seq = "HELVELLA"

    # Example 1: Using default model weights with custom peptide
    print("=" * 80)
    print("Example 1: Custom peptide with uncertainty-guided masking")
    print("=" * 80)
    mutator = UncertaintyGuidedMutation(
        target_seq=target_seq,
        temp_pept_seq=temp_pept_seq,
        modality="custom",
        mask_strategy="top_k",
        mask_ratio=0.3,
        n_seq_out=5,
    )

    results = mutator.run()
    print("\nGenerated mutations:")
    for seq in results["generated_sequences"]:
        print(seq)

    # Example 2: Using affibody template (no need to provide temp_pept_seq)
    print("\n" + "=" * 80)
    print("Example 2: Using affibody template")
    print("=" * 80)
    mutator_affibody = UncertaintyGuidedMutation(
        target_seq=target_seq,
        modality="affibody",
        use_template=True,
        mask_strategy="top_k",
        mask_ratio=0.2,
        n_seq_out=3,
    )
    results_affibody = mutator_affibody.run()
    print("\nGenerated affibody mutations:")
    for seq in results_affibody["generated_sequences"]:
        print(seq)

    # Example 3: Using specific residues to mutate
    print("\n" + "=" * 80)
    print("Example 3: Mutating specific residues")
    print("=" * 80)
    mutator_specific = UncertaintyGuidedMutation(
        target_seq=target_seq,
        temp_pept_seq=temp_pept_seq,
        modality="custom",
        residues_to_mutate=[0, 2, 4, 6],  # Mutate positions 0, 2, 4, 6 in peptide
        n_seq_out=3,
    )
    results_specific = mutator_specific.run()
    print("\nGenerated mutations at specific residues:")
    for seq in results_specific["generated_sequences"]:
        print(seq)

    # Example 4: Using nanobody template with custom weights
    print("\n" + "=" * 80)
    print("Example 4: Nanobody template (custom weights optional)")
    print("=" * 80)
    # Uncomment and provide path to your .safetensors file
    # mutator_nanobody = UncertaintyGuidedMutation(
    #     target_seq=target_seq,
    #     modality="nanobody",
    #     use_template=True,
    #     model_weights="/path/to/your/model.safetensors",
    #     mask_strategy="top_k",
    #     mask_ratio=0.25,
    #     n_seq_out=5,
    # )
    # results_nanobody = mutator_nanobody.run()
    # print("\nGenerated nanobody mutations:")
    # for seq in results_nanobody["generated_sequences"]:
    #     print(seq)

