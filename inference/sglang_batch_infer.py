import sys
import json
import sglang as sgl
from transformers import AutoTokenizer
from tqdm import tqdm

def main():
    model_path = "/path/to/gpt-20b_merge_lora_cancer_t"
    input_file = "/path/to/t.jsonl"
    chat_template_file = "/path/to/chat_template.jinja"
    output_file = "outputs.txt"
    
    print("1. Initializing sglang Engine (this may take a moment)...", flush=True)
    llm = sgl.Engine(
        model_path=model_path,
        mem_fraction_static=0.80,
        chunked_prefill_size=16384 
    )
    print("Engine initialized successfully!", flush=True)

    print("2. Loading tokenizer...", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    with open(chat_template_file, "r", encoding="utf-8") as f:
        tokenizer.chat_template = f.read()
    
    print("3. Reading data and formatting text...", flush=True)
    original_data = []
    prompt_texts = []
    
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): 
                continue
            
            data = json.loads(line)
            original_data.append(data)
            
            text = tokenizer.apply_chat_template(
                data.get("messages", []),
                tokenize=False, 
                add_generation_prompt=True
            )
            prompt_texts.append(text)
                
    print(f"Loaded {len(original_data)} items. Batch tokenizing via Rust backend...", flush=True)

    batch_encoding = tokenizer(prompt_texts, add_special_tokens=False)
    tokenized_prompts = batch_encoding["input_ids"]
            
    print(f"Successfully tokenized {len(tokenized_prompts)} prompts.", flush=True)

    sampling_params = {
        "temperature": 0.1, 
        "top_p": 0.95,
        "max_new_tokens": 50
    }
    
    print(f"4. Starting batch inference and writing to {output_file}...", flush=True)
    
    chunk_size = 250
    
    with open(output_file, "w", encoding="utf-8") as out_f:
        for i in tqdm(range(0, len(tokenized_prompts), chunk_size), desc="Processing Chunks"):
            
            chunk_inputs = tokenized_prompts[i : i + chunk_size]
            chunk_originals = original_data[i : i + chunk_size]
            
            chunk_outputs = llm.generate(input_ids=chunk_inputs, sampling_params=sampling_params)
            
            for j, out in enumerate(chunk_outputs):
                generated_text = out['text'].strip().replace("analysisassistantfinal", "").replace("analysisassistantcommentaryassistantfinal", "")
                out_f.write(generated_text + "\n")
                
            out_f.flush()
            
    llm.shutdown()
    print(f"Inference complete! All results successfully saved to {output_file}", flush=True)
    sys.exit(0)

if __name__ == "__main__":
    main()
