#!/bin/bash

CUDA_VISIBLE_DEVICES=0,1 accelerate launch \
    --config_file fsdp_config.yaml \
    src/train.py gpt_lora_sft.yaml
