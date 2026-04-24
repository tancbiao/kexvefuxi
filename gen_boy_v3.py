# -*- coding: utf-8 -*-
"""txt2img 生成男孩，素底白衣短裤
   描述与女孩素底相同的构图和姿势"""
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
        print(f"HTTP错误: {e.code}")
        print(e.read().decode("utf-8")[:500])
        return None

prompt = {
    "1": {
        "inputs": {"ckpt_name": "AnythingXL_xl.safetensors"},
        "class_type": "CheckpointLoaderSimple"
    },
    "2": {
        "inputs": {
            "text": (
                "chibi cute anime BOY character, same style and quality as reference image, "
                "SHORT MESSY BOY HAIR dark brown color short cut neat hair, "
                "white simple cotton t-shirt plain no graphics, white shorts, "
                "barefoot feet no shoes, no hat, no accessories, no weapon, no armor, no cape, no wings, "
                "no pet, completely plain simple white outfit, standing pose both arms slightly away from body, "
                "legs shoulder width apart feet flat on ground, "
                "maple story style anime character art, "
                "pure white background no scenery no pattern, "
                "arms and legs visible, face front view looking at viewer, "
                "basic white t-shirt white shorts barefoot boy character only, "
                "ultra simple plain base character for layering equipment on top later, "
                "clean flat illustration anime style high quality"
            ),
            "clip": ["1", 1]
        },
        "class_type": "CLIPTextEncode"
    },
    "3": {
        "inputs": {
            "text": "realistic 3d render photograph dark nsfw ugly bad anatomy deformed low quality blurry complex background watermark text colorful bright flashy crowded cluttered detailed accessories armor cape wings pet jewelry hat weapon flashy colorful nsfw girl feminine long hair skirt dress high heels",
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
            "seed": 2026003,
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
        "inputs": {"filename_prefix": "boy_base_v3", "images": ["6", 0]},
        "class_type": "SaveImage"
    }
}

print("提交 txt2img（男孩 v3）...")
result = send_prompt(prompt)
if result:
    print(f"✅ 成功！prompt_id: {result.get('prompt_id', 'N/A')}")
else:
    print("❌ 提交失败")
