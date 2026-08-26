source code for model inference.

llama_factory_serving.sh - cmd using llama-factory-api for scAdapter model serving (moderate comsumption of GPU memory and inferencing speed)

llama_factory_infer.py - using OpenAI compatible api to use scAdapter model served by llama-factory framework.

peft_mini_infer.py - using peft python library for serving scAdapter model (MPX4 qutanization, miniment GPU memory comsumption. typically ~5GB, lowest inferencing speed).

sgalng_bath_infer.py - using sglang framework for inferencing (highest level of inferencing speed and GPU memory comsumption).
