from transformers import AutoModelForMaskedLM, AutoTokenizer
import torch
from tqdm import tqdm
import inspect
from dataclasses import dataclass
import antibody_design.utils.id_cdrloop as id_cdrloop
import pandas as pd
from safetensors import safe_open
from safetensors.torch import load_file, save_file


@dataclass
class Generate:
    target_seq: str
    original_petide: str
    mut_index: list[int] | None = None
    n_seq_out: int = 10
    model_id: str = "Bo1015/proteinglm-1b-mlm"
    model_weights: str | None = None
    device: object = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    @staticmethod
    # Example: Load weights from a .safetensors file
    def load_weights_safetensors(model, safetensors_path, device="cpu"):
        """Loads weights from a .safetensors file into a PyTorch model."""
        loaded_state_dict = {}
        with safe_open(safetensors_path, framework="pt", device=device) as f:
            for key in f.keys():
                loaded_state_dict[key] = f.get_tensor(key)
        
        model.load_state_dict(loaded_state_dict)
        return model

    def __post_init__(self):
        
        # Load model and tokenizer
        self.tokenizer  = AutoTokenizer.from_pretrained(self.model_id, trust_remote_code=True, use_fast=True)
        self.model = AutoModelForMaskedLM.from_pretrained(self.model_id, trust_remote_code=True, torch_dtype=torch.bfloat16).cuda()

        if self.model_weights == None:
            initial_state_dict = self.model.state_dict()
            for it_k, key in enumerate(initial_state_dict):
                if it_k %1 == 0: 
                    print(initial_state_dict[key])

        elif self.model_weights !=None:
            # 1. Save the initial state
            initial_state_dict = self.model.state_dict()
            self.model = self.load_weights_safetensors(self.model, self.model_weights)#.load_state_dict(self.model_weights)#state_dict)
            if torch.cuda.is_available():
                self.model = self.model.cuda()
            self.model.eval()
            # 3. Compare the states
            updated_state_dict = self.model.state_dict()

            modified_weights = {}
            
            for it_k, key in enumerate(initial_state_dict):
                if it_k %1 == 0: 
                    print(initial_state_dict[key])
                    print(updated_state_dict[key])
                if not torch.equal(initial_state_dict[key], updated_state_dict[key]):
                    modified_weights[key] = "Modified"
                else:
                     modified_weights[key] = "Not Modified"
            # 4. Print or process the modified weights
            for key, status in modified_weights.items():
                if status == 'Modified':
                    print(f"Layer: {key}, Status: {status}")

    def mask_inp_ab(self):
        for cdrid in self.cdrs_mut:
            cdrseq = self.cdrdict[cdrid] 
            if cdrid in self.cdrs_heavy:
                cdrseq_st = self.H_seq.find(cdrseq)
                cdrseq_end = cdrseq_st + len(cdrseq) - 1
                self.H_seq = self.H_seq[:cdrseq_st] +\
                                     '<mask>' * (len(cdrseq)) +\
                                          self.H_seq[cdrseq_end:] 
            elif cdrid in self.cdrs_light:
                cdrseq_st = self.L_seq.find(cdrseq)
                cdrseq_end = cdrseq_st + len(cdrseq)# - 1
                self.L_seq = self.L_seq[:cdrseq_st] +\
                                     '<mask>' * (len(cdrseq)) +\
                                          self.L_seq[cdrseq_end:]

    def tokenize_seq(self,
                     seq): 
        inputs = self.tokenizer(seq, return_tensors='pt')
        input_ids = inputs['input_ids'].to(self.device)
        attention_mask = inputs['attention_mask'].to(self.device)

        # Identify mask token positions
        mask_token_id = self.tokenizer.mask_token_id
        mask_indices = (input_ids == mask_token_id).nonzero(as_tuple=False)  # shape: (num_masks, 2)

        return input_ids, attention_mask, mask_indices

    def generate(self,
                 input_ids, 
                 attention_mask, 
                 mask_indices
                 ):
        generated_sequences = []

        # Generate n_seq_out sequences
        with torch.inference_mode():
            for _ in tqdm(range(self.n_seq_out)):
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                logits = outputs.logits[0]  # shape: (seq_len, vocab_size)

                sampled_ids = input_ids.clone()

                for idx in mask_indices:
                    pos = idx[1]
                    # Sample from distribution at masked position
                    probs = torch.softmax(logits[pos], dim=-1)
                    sampled_token_id = torch.multinomial(probs, num_samples=1)
                    sampled_ids[0, pos] = sampled_token_id

                # Decode the sampled sequence
                decoded_seq = self.tokenizer.decode(sampled_ids[0], skip_special_tokens=True)
                seq_out = "".join(decoded_seq.split())
                generated_sequences.append(seq_out)
        return generated_sequences

    def run_generate(self):
        generated_dict = {'heavy': None, 'light': None}
        self.mask_inp_ab()
        
        for (seqid,seq) in zip(['heavy', 'light'], [self.H_seq, self.L_seq]):
            input_ids, attention_mask, mask_indices = self.tokenize_seq(seq)
            generated_dict[seqid] = list(set(self.generate(
                                        input_ids, 
                                        attention_mask, 
                                        mask_indices
                                        )))
        return generated_dict

if __name__ == "__main__":
    import argparse

    # Create an argument parser object
    parser = argparse.ArgumentParser(description="A simple example of argparse")
    
    # Add arguments
    parser.add_argument("-i", "--inp_ab_scaff", help="input csv with ab heavy/light chains")
    parser.add_argument("-m", "--mut_cdr", type=str, nargs='+', help="cdr ids to mutate (CDRH1... CDRL1...)")
    parser.add_argument("-n", "--n_seq_out", type=int, help = "number of seqs per chain")
    
    # Parse the arguments
    args = parser.parse_args()
    
    df_ab_scaff = pd.read_csv(args.inp_ab_scaff)
    H_seq = list(df_ab_scaff['heavy_chain'])[0]
    L_seq = list(df_ab_scaff['light_chain'])[0]

    print(H_seq)
    print(L_seq)
    generator = Generate(H_seq,
                         L_seq,
                        args.mut_cdr,
                        args.n_seq_out)

    generated_dict = generator.run_generate()
    #print(generated_dict)

    for seq_h, seq_l in zip(generated_dict['heavy'], generated_dict['light']):
        cdr_it_dict = id_cdrloop.id_cdr(seq_h, seq_l)
        print(cdr_it_dict['CDRL3'])

if False:
    # Original sequence
    seq = 'MILMCQHFSGQFSKYFLAVSSDFCHFVFPIILVSHVNFKQMKRKGFALWNDRAVPFTQGIFTTVMILLQYLHGTG'

    # Replace residues 5-10 (0-indexed) with [MASK]
    start = 5
    end = 6
    masked_seq = seq[:start] + '<mask>' * (end - start + 1) + seq[end+1:]

    # Tokenize sequence
    inputs = tokenizer(masked_seq, return_tensors='pt')
    input_ids = inputs['input_ids']

    # Move to GPU if available
    if torch.cuda.is_available():
        input_ids = input_ids.cuda()
        attention_mask = inputs['attention_mask'].cuda()
    else:
        attention_mask = inputs['attention_mask']

    # Run MLM
    with torch.inference_mode():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)#, max_sequence_length = 5)
        predictions = torch.argmax(outputs.logits, dim=-1)

    # Decode original and predicted sequences
    original_decoded = tokenizer.decode(input_ids[0], skip_special_tokens=True)
    predicted_decoded = tokenizer.decode(predictions[0], skip_special_tokens=True)

    # Print
    print("Original (masked):", masked_seq)
    print("Model input sequence:", original_decoded)
    print("Model prediction:", predicted_decoded)