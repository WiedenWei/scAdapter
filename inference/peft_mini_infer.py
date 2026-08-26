import os
import sys
import torch
import importlib.util
from pathlib import Path

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

def load_local_kernel(repo_id, *args, **kwargs):
    kernel_dir = Path("./gpt-oss-triton-kernels/build/torch-cuda").absolute()
    if not kernel_dir.exists():
        raise FileNotFoundError(f"Missing kernel directory! Please run:\n git clone https://huggingface.co/{repo_id}")
    
    sys.path.insert(0, str(kernel_dir))
    
    try:
        return importlib.import_module("gpt_oss_triton_kernels")
    except ImportError:
        try:
            return importlib.import_module("src")
        except ImportError:
            init_file = kernel_dir / "__init__.py"
            spec = importlib.util.spec_from_file_location("local_triton_kernel", str(init_file))
            kernel_mod = importlib.util.module_from_spec(spec)
            sys.modules["local_triton_kernel"] = kernel_mod
            spec.loader.exec_module(kernel_mod)
            return kernel_mod

try:
    import transformers.integrations.hub_kernels
    transformers.integrations.hub_kernels.get_kernel = load_local_kernel
except ImportError:
    pass


from fastapi import FastAPI, HTTPException, Request
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import uvicorn

app = FastAPI(title="scAdapter Minimal PEFT Server")

BASE_MODEL_PATH = "scAdapter_model_files/gpt_oss_20b/"
JINJA_TEMPLATE_PATH = "scAdapter_model_files/cancer_major_top100/chat_template.jinja"
PORT = 30000

LORA_PATHS = {
    "healthy_major": "scAdapter_model_files/healthy_17_major_top100/",
    "cancer_major": "scAdapter_model_files/cancer_major_top100/",
    "healthy_t": "scAdapter_model_files/healthy_t_subtype_top300/",
    "cancer_t": "scAdapter_model_files/cancer_t_subtype_top300/",
    "healthy_b": "scAdapter_model_files/healthy_b_subtype_top300/",
    "cancer_b": "scAdapter_model_files/cancer_b_subtype_top300/",
    "healthy_dc": "scAdapter_model_files/healthy_dc_subtype_top300/",
    "cancer_dc": "scAdapter_model_files/cancer_dc_subtype_top300/",
    "healthy_mm": "scAdapter_model_files/healthy_mm_subtype_top300/",
    "cancer_mm": "scAdapter_model_files/cancer_mm_subtype_top300/"
}

first_adapter = list(LORA_PATHS.keys())[0]
first_adapter_path = LORA_PATHS[first_adapter]

print(f"Loading tokenizer from adapter directory: {first_adapter_path}...")
tokenizer = AutoTokenizer.from_pretrained(
    first_adapter_path, 
    trust_remote_code=True,
    local_files_only=True
)

if os.path.exists(JINJA_TEMPLATE_PATH):
    with open(JINJA_TEMPLATE_PATH, "r") as f:
        tokenizer.chat_template = f.read()
    print(f"✅ Loaded custom chat template.")

print("Loading base model (MXFP4 Native Acceleration via Local Source)...")
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_PATH,
    device_map="auto",
    torch_dtype="auto", 
    trust_remote_code=True,
    local_files_only=True
)

print(f"Initializing PEFT framework with: {first_adapter}")
model = PeftModel.from_pretrained(
    base_model, 
    first_adapter_path, 
    adapter_name=first_adapter,
    local_files_only=True
)

for adapter_name, path in LORA_PATHS.items():
    if adapter_name != first_adapter:
        print(f"Registering adapter: {adapter_name}")
        model.load_adapter(
            path, 
            adapter_name=adapter_name,
            local_files_only=True
        )

print("\n🚀 Minimal Multi-LoRA Server is ready (Offline Mode + MXFP4 Triton Acceleration).")

@app.post("/generate")
async def generate(request: Request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload.")

    adapter_name = data.get("model")
    message = data.get("message")
    max_tokens = int(data.get("max_tokens", 50))
    temperature = float(data.get("temperature", 0.0))

    if not adapter_name or not message:
        raise HTTPException(status_code=400, detail="Missing required 'model' or 'message' keys.")
    if adapter_name not in LORA_PATHS:
        raise HTTPException(status_code=400, detail=f"Invalid adapter. Options: {list(LORA_PATHS.keys())}")

    try:
        model.set_adapter(adapter_name)

        formatted_prompt = tokenizer.apply_chat_template(
            message, 
            tokenize=False, 
            add_generation_prompt=True
        )

        inputs = tokenizer(formatted_prompt, return_tensors="pt").to(model.device)
        input_len = inputs.input_ids.shape[1]

        with torch.no_grad():
            output_tokens = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True if temperature > 0.0 else False,
                pad_token_id=tokenizer.eos_token_id
            )

        generated_text = tokenizer.decode(output_tokens[0][input_len:], skip_special_tokens=True)
        
        return {"text": generated_text.strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
