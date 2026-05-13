# -*- coding: utf-8 -*-
"""生成素底 Q 版女孩角色 - 最简单的白衣短裤，便于叠加装备"""
import urllib.request
import urllib.error
import json

COMFYUI_URL = "http://localhost:8188"

def send_prompt(prompt):
    data = json.dumps({"prompt": prompt}).encode("utf-8")
    req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP错误: {e.code} {e.reason}")
        print(e.read().decode("utf-8"))
        return None

# 简单素底女孩提示词 - 白衣短裤/短裙，无任何装备
prompt = {
    "1": {
        "inputs": {"ckpt_name": "AnythingXL_xl.safetensors"},
        "class_type": "CheckpointLoaderSimple"
    },
    "2": {
        "inputs": {
            "text": "chibi cute anime girl character, plain white simple cotton t-shirt and white shorts, barefoot feet, no shoes, no hat, no accessories, no weapon, no armor, no cape, no wings, no pet, no jewelry, completely plain simple white outfit, maple story style character, pure white background, front view standing pose, clean minimal clothing, arms and legs visible skin, basic t-shirt and shorts only, ultra simple base character for layering equipment on top later, clean flat illustration anime style high quality",
            "clip": ["1", 1]
        },
        "class_type": "CLIPTextEncode"
    },
    "3": {
        "inputs": {
            "text": "realistic 3d render photograph dark nsfw ugly bad anatomy deformed low quality blurry complex background watermark text colorful bright flashy crowded cluttered detailed accessories armor cape wings pet jewelry hat weapon flashy colorful nsfw underwear",
            "clip": ["1", 1]
        },
        "class_type": "CLIPTextEncode"
    },
    "4": {
        "inputs": {"width": 768, "height": 768, "batch_size": 1},
        "class_type": "EmptyLatentImage"
    },
    "5": {
        "inputs": {
            "seed": 2026001,
            "steps": 30,
            "cfg": 7.5,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 1.0,
            "model": ["1", 0],
            "positive": ["2", 0],
            "negative": ["3", 0],
            "latent_image": ["4", 0]
        },
        "class_type": "KSampler"
    },
    "6": {
        "inputs": {"samples": ["5", 0], "vae": ["1", 2]},
        "class_type": "VAEDecode"
    },
    "7": {
        "inputs": {"filename_prefix": "girl_base_simple", "images": ["6", 0]},
        "class_type": "SaveImage"
    }
}

print("正在生成素底女孩角色...")
result = send_prompt(prompt)
if result:
    print(f"提交成功！prompt_id: {result.get('prompt_id', 'N/A')}")
else:
    print("提交失败")
