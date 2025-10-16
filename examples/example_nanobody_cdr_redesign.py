"""
Example: Nanobody CDR Redesign using Uncertainty-Guided Mutation

This example demonstrates how to use the CDR identification and targeting
features for nanobody redesign.

Requirements:
    - abnumber: pip install abnumber
    - uncertainty_guided_mutation.py
"""

from uncertainty_guided_mutation import UncertaintyGuidedMutation

# Example target sequence (antibody or protein)
target_seq = "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVV"

# Example 1: Mutate CDR3 Only (Most Variable Region)
print("=" * 80)
print("Example 1: Mutate CDR3 Only")
print("=" * 80)

mutator_cdr3 = UncertaintyGuidedMutation(
    target_seq=target_seq,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR3"],  # Only mutate CDR3
    mask_ratio=0.5,  # Mutate all CDR3 positions
    n_seq_out=5,
)

results_cdr3 = mutator_cdr3.run()
print("\nGenerated CDR3 variants:")
for i, seq in enumerate(results_cdr3["generated_sequences"], 1):
    print(f"{i}. {seq}")

# Example 2: Mutate All CDRs
print("\n" + "=" * 80)
print("Example 2: Mutate All CDRs (CDR1, CDR2, CDR3)")
print("=" * 80)

mutator_all_cdrs = UncertaintyGuidedMutation(
    target_seq=target_seq,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR1", "CDR2", "CDR3"],
    mask_ratio=0.3,  # Mutate 30% of CDR positions
    n_seq_out=5,
)

results_all_cdrs = mutator_all_cdrs.run()
print("\nGenerated variants with all CDRs mutated:")
for i, seq in enumerate(results_all_cdrs["generated_sequences"], 1):
    print(f"{i}. {seq}")

# Example 3: Mutate CDR1 and CDR3 (Framework-Aware)
print("\n" + "=" * 80)
print("Example 3: Mutate CDR1 and CDR3 (Keep CDR2 Fixed)")
print("=" * 80)

mutator_cdr1_3 = UncertaintyGuidedMutation(
    target_seq=target_seq,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR1", "CDR3"],
    mask_ratio=0.3,
    n_seq_out=5,
)

results_cdr1_3 = mutator_cdr1_3.run()
print("\nGenerated variants with CDR1 and CDR3 mutated:")
for i, seq in enumerate(results_cdr1_3["generated_sequences"], 1):
    print(f"{i}. {seq}")

# Example 4: Inspect CDR Sequences
print("\n" + "=" * 80)
print("Example 4: Inspect CDR Sequences")
print("=" * 80)

mutator_inspect = UncertaintyGuidedMutation(
    target_seq=target_seq,
    modality="nanobody",
    use_template=True,
)

nanobody_seq = mutator_inspect.get_peptide_sequence()
print(f"\nNanobody sequence ({len(nanobody_seq)} aa):")
print(nanobody_seq)

# Identify CDRs
cdr_dict = mutator_inspect.identify_nanobody_cdrs(nanobody_seq)

print("\nIdentified CDRs:")
for cdr_name, (start, end, seq) in cdr_dict.items():
    print(f"\n{cdr_name}:")
    print(f"  Position: {start}-{end} (0-indexed)")
    print(f"  Length: {len(seq)} aa")
    print(f"  Sequence: {seq}")

# Example 5: Get CDR Residue Indices
print("\n" + "=" * 80)
print("Example 5: Get CDR Residue Indices")
print("=" * 80)

mutator_indices = UncertaintyGuidedMutation(
    target_seq=target_seq,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR1", "CDR3"],
)

cdr_residues = mutator_indices.get_nanobody_cdr_residues()
print(f"\nCDR1 and CDR3 residue indices (0-indexed):")
print(cdr_residues)

# Example 6: Conservative Mutations
print("\n" + "=" * 80)
print("Example 6: Conservative Mutations (Low Mutation Rate)")
print("=" * 80)

mutator_conservative = UncertaintyGuidedMutation(
    target_seq=target_seq,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR1", "CDR2", "CDR3"],
    mask_ratio=0.15,  # Only 15% of CDR positions
    n_seq_out=5,
)

results_conservative = mutator_conservative.run()
print("\nConservatively mutated variants:")
for i, seq in enumerate(results_conservative["generated_sequences"], 1):
    print(f"{i}. {seq}")

# Example 7: Custom Nanobody Sequence
print("\n" + "=" * 80)
print("Example 7: Custom Nanobody Sequence with CDR Targeting")
print("=" * 80)

custom_nanobody = "AQVQLQESGGGLVQAGGSLRLSCAASERTFSTYAMGWFRQAPGREREFLAQINWSGTTTYYAESVKDRTTISRDNAKNTVYLEMNNLNADDTGIYFCAAHPQRGWGSTLGWTYWGQGTQVTVSSGGGGSGGGKPIPNPLLGLDSTRTGHHHHHH"

mutator_custom = UncertaintyGuidedMutation(
    target_seq=target_seq,
    temp_pept_seq=custom_nanobody,
    modality="nanobody",
    nanobody_cdr_regions=["CDR3"],
    mask_ratio=0.4,
    n_seq_out=5,
)

results_custom = mutator_custom.run()
print("\nCustom nanobody CDR3 variants:")
for i, seq in enumerate(results_custom["generated_sequences"], 1):
    print(f"{i}. {seq}")

# Example 8: Iterative Refinement
print("\n" + "=" * 80)
print("Example 8: Iterative Refinement (Multi-Round Optimization)")
print("=" * 80)

current_seq = mutator_inspect.get_peptide_sequence()
print(f"\nStarting sequence: {current_seq}")

for iteration in range(2):
    print(f"\n--- Iteration {iteration + 1} ---")
    
    mutator_iter = UncertaintyGuidedMutation(
        target_seq=target_seq,
        temp_pept_seq=current_seq,
        modality="nanobody",
        nanobody_cdr_regions=["CDR3"],
        mask_ratio=0.3,
        n_seq_out=3,
    )
    
    results_iter = mutator_iter.run()
    
    # Select best variant (in practice, validate with binding assay)
    current_seq = results_iter["generated_sequences"][0]
    print(f"Selected variant: {current_seq}")

# Example 9: Compare CDR vs Non-CDR Targeting
print("\n" + "=" * 80)
print("Example 9: Compare CDR-Targeted vs Uncertainty-Guided")
print("=" * 80)

# CDR-targeted
mutator_cdr = UncertaintyGuidedMutation(
    target_seq=target_seq,
    modality="nanobody",
    use_template=True,
    nanobody_cdr_regions=["CDR3"],
    n_seq_out=3,
)
results_cdr = mutator_cdr.run()

# Uncertainty-guided (no CDR targeting)
mutator_unc = UncertaintyGuidedMutation(
    target_seq=target_seq,
    modality="nanobody",
    use_template=True,
    mask_ratio=0.3,
    n_seq_out=3,
)
results_unc = mutator_unc.run()

print("\nCDR3-targeted variants:")
for seq in results_cdr["generated_sequences"]:
    print(f"  {seq}")

print("\nUncertainty-guided variants:")
for seq in results_unc["generated_sequences"]:
    print(f"  {seq}")

print("\n" + "=" * 80)
print("All examples completed!")
print("=" * 80)

