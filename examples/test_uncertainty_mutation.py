"""
Test script for uncertainty-guided mutation generation with modality support.
"""

import torch
from uncertainty_guided_mutation import UncertaintyGuidedMutation, MODALITY_TEMPLATES


def test_basic_workflow():
    """Test the basic workflow with a simple example."""
    print("=" * 80)
    print("TEST 1: Basic Workflow")
    print("=" * 80)
    
    target_seq = "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV"
    temp_pept_seq = "HELVELLA"
    
    mutator = UncertaintyGuidedMutation(
        target_seq=target_seq,
        temp_pept_seq=temp_pept_seq,
        mask_strategy="top_k",
        mask_ratio=0.3,
        n_seq_out=3,
    )
    
    results = mutator.run()
    
    print("\n✓ Generated sequences:")
    for i, seq in enumerate(results["generated_sequences"], 1):
        print(f"  {i}. {seq}")
    
    return results


def test_different_mask_strategies():
    """Test different masking strategies."""
    print("\n" + "=" * 80)
    print("TEST 2: Different Masking Strategies")
    print("=" * 80)
    
    target_seq = "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV"
    temp_pept_seq = "HELVELLA"
    
    strategies = [
        ("top_k", {"mask_ratio": 0.3}),
        ("top_k", {"mask_ratio": 0.5}),
        ("threshold", {"uncertainty_threshold": 0.4}),
    ]
    
    for strategy, kwargs in strategies:
        print(f"\n--- Strategy: {strategy} with {kwargs} ---")
        
        mutator = UncertaintyGuidedMutation(
            target_seq=target_seq,
            temp_pept_seq=temp_pept_seq,
            mask_strategy=strategy,
            n_seq_out=2,
            **kwargs
        )
        
        results = mutator.run()
        print(f"Positions masked: {len(results['positions_to_mask'])}")
        print(f"Generated: {results['generated_sequences'][0]}")


def test_uncertainty_analysis():
    """Analyze uncertainty distribution."""
    print("\n" + "=" * 80)
    print("TEST 3: Uncertainty Analysis (Peptide Only)")
    print("=" * 80)

    target_seq = "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV"
    temp_pept_seq = "HELVELLA"

    mutator = UncertaintyGuidedMutation(
        target_seq=target_seq,
        temp_pept_seq=temp_pept_seq,
    )

    input_seq = f"{target_seq}<eos>{temp_pept_seq}"
    _, probs, mask_indices = mutator.get_logprobs(input_seq)
    uncertainty = mutator.compute_uncertainty(probs)

    # Find peptide start index
    peptide_start_idx = mutator.find_peptide_start_idx(input_seq)
    peptide_mask_indices = [idx for idx in mask_indices if idx >= peptide_start_idx]

    print(f"\nPeptide token indices: {peptide_mask_indices}")
    print(f"\nUncertainty statistics (peptide only):")
    print(f"  Mean: {uncertainty[peptide_mask_indices].mean():.4f}")
    print(f"  Std:  {uncertainty[peptide_mask_indices].std():.4f}")
    print(f"  Min:  {uncertainty[peptide_mask_indices].min():.4f}")
    print(f"  Max:  {uncertainty[peptide_mask_indices].max():.4f}")

    # Show top-5 most uncertain positions in peptide
    if len(peptide_mask_indices) >= 5:
        top_uncertain_indices = torch.topk(uncertainty[peptide_mask_indices], k=5).indices
    else:
        top_uncertain_indices = torch.topk(uncertainty[peptide_mask_indices], k=len(peptide_mask_indices)).indices

    print(f"\nTop {len(top_uncertain_indices)} most uncertain positions (peptide):")
    for rank, idx in enumerate(top_uncertain_indices, 1):
        pos = peptide_mask_indices[idx]
        print(f"  {rank}. Position {pos}: uncertainty={uncertainty[pos]:.4f}")


def test_modality_templates():
    """Test different modality templates."""
    print("\n" + "=" * 80)
    print("TEST 4: Modality Templates")
    print("=" * 80)

    target_seq = "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV"

    for modality in ["affibody", "nanobody", "affitin"]:
        print(f"\n--- Modality: {modality} ---")

        mutator = UncertaintyGuidedMutation(
            target_seq=target_seq,
            temp_pept_seq="",
            modality=modality,
            use_template=True,
            mask_ratio=0.2,
            n_seq_out=2,
        )

        results = mutator.run()
        print(f"Template length: {len(results['peptide_seq'])}")
        print(f"Modality: {results['modality']}")
        print(f"Generated: {results['generated_sequences'][0][:50]}...")


def test_specific_residues():
    """Test mutation of specific residues."""
    print("\n" + "=" * 80)
    print("TEST 5: Specific Residue Mutation")
    print("=" * 80)

    target_seq = "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV"
    temp_pept_seq = "HELVELLA"

    residues_to_mutate = [0, 2, 4, 6]

    print(f"\nPeptide: {temp_pept_seq}")
    print(f"Residues to mutate (0-indexed): {residues_to_mutate}")
    print(f"Positions: {[temp_pept_seq[i] for i in residues_to_mutate]}")

    mutator = UncertaintyGuidedMutation(
        target_seq=target_seq,
        temp_pept_seq=temp_pept_seq,
        residues_to_mutate=residues_to_mutate,
        n_seq_out=3,
    )

    results = mutator.run()
    print(f"\nPositions to mask: {results['positions_to_mask']}")
    print("Generated sequences:")
    for i, seq in enumerate(results["generated_sequences"], 1):
        print(f"  {i}. {seq}")


def test_custom_template():
    """Test custom template override."""
    print("\n" + "=" * 80)
    print("TEST 6: Custom Template Override")
    print("=" * 80)

    target_seq = "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV"
    custom_template = "MYOWNSEQUENCE"

    print(f"\nCustom template: {custom_template}")

    mutator = UncertaintyGuidedMutation(
        target_seq=target_seq,
        temp_pept_seq="",
        modality="affibody",
        use_template=True,
        custom_template=custom_template,
        mask_ratio=0.3,
        n_seq_out=2,
    )

    results = mutator.run()
    print(f"Used template: {results['peptide_seq']}")
    print(f"Template matches custom: {results['peptide_seq'] == custom_template}")


if __name__ == "__main__":
    try:
        test_basic_workflow()
        test_different_mask_strategies()
        test_uncertainty_analysis()
        test_modality_templates()
        test_specific_residues()
        test_custom_template()
        print("\n" + "=" * 80)
        print("All tests completed!")
        print("=" * 80)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

