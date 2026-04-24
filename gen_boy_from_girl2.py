# -*- coding: utf-8 -*-
"""img2img: 以女孩素底为参考，只改发型/性别生成男孩版本"""
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
                "chibi cute anime BOY character, same pose same stance same proportions as reference image, "
                "short messy boy hair brown or black, white simple cotton t-shirt and white shorts, "
                "barefoot feet, no shoes, no hat, no accessories, no weapon, no armor, no cape, no wings, "
                "no pet, completely plain simple white outfit, maple story style character, "
                "pure white background, EXACT same pose and position as reference image, "
                "arms and legs visible skin, basic t-shirt and shorts only, ultra simple base character, "
                "clean flat illustration anime style high quality"
            ),
            "clip": ["1", 1]
        },
        "class_type": "CLIPTextEncode"
    },
    "3": {
        "inputs": {
            "text": "realistic 3d render photograph dark nsfw ugly bad anatomy deformed low quality blurry complex background watermark text colorful bright flashy crowded cluttered detailed accessories armor cape wings pet jewelry hat weapon flashy colorful nsfw long hair girl feminine face feminine body",
            "clip": ["1", 1]
        },
        "class_type": "CLIPTextEncode"
    },
    "4": {
        "inputs": {"image": "girl_base_simple.png", "choose tokenizer to use": "CLIP"},
        "class_type": "LoadImage"
    },
    "5": {
        "inputs": {"pixels": ["4", 0], "vae": ["1", 2]},
        "class_type": "VAEEncode"
    },
    "6": {
        "inputs": {
            "seed": 2026002,
            "steps": 30,
            "cfg": 7.5,
            "sampler_name": "euler",
            "scheduler": "normal",
            "positive": ["2", 0],
            "negative": ["3", 0],
            "latent_image": ["5", 0],
            "model": ["1", 0],
            "denoise": 0.35
        },
        "class_type": "KSampler"
    },
    "7": {
        "inputs": {"samples": ["6", 0], "vae": ["1", 2]},
        "class_type": "VAEDecode"
    },
    "8": {
        "inputs": {"filename_prefix": "boy_base_from_girl", "images": ["7", 0]},
        "class_type": "SaveImage"
    }
}

print("提交 img2img（男孩）...")
result = send_prompt(prompt)
if result:
    print(f"✅ 成功！prompt_id: {result.get('prompt_id', 'N/A')}")
else:
    print("❌ 提交失败")
