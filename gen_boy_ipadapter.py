# -*- coding: utf-8 -*-
"""IPAdapter 版：以女孩素底为参考生成男孩
   IPAdapter 保持角色结构/姿势，只改变发型和性别"""
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
    # 1: Checkpoint
    "1": {
        "inputs": {"ckpt_name": "AnythingXL_xl.safetensors"},
        "class_type": "CheckpointLoaderSimple"
    },
    # 2: 正面提示词（男孩短头发）
    "2": {
        "inputs": {
            "text": (
                "chibi anime BOY character, short boy haircut brown short cut, "
                "white cotton t-shirt white shorts barefoot feet, "
                "no hat no accessories no weapon, maple story style, "
                "pure white background, front view standing pose, "
                "clean flat illustration high quality anime"
            ),
            "clip": ["1", 1]
        },
        "class_type": "CLIPTextEncode"
    },
    # 3: 负面提示词
    "3": {
        "inputs": {
            "text": "realistic 3d render photograph nsfw ugly bad anatomy deformed low quality blurry watermark colorful bright cluttered accessories armor cape wings pet jewelry hat weapon long hair girl feminine face",
            "clip": ["1", 1]
        },
        "class_type": "CLIPTextEncode"
    },
    # 4: 女孩底稿（角色参考）
    "4": {
        "inputs": {"image": "girl_base_simple.png", "choose tokenizer to use": "CLIP"},
        "class_type": "LoadImage"
    },
    # 5: IPAdapter（女孩做参考，保持角色结构）
    "5": {
        "inputs": {
            "model": ["1", 0],
            "ipadapter": "ip-adapter-plus_sd15.bin",
            "image": ["4", 0],
            "weight": 0.6,
            "start_at": 0.0,
            "end_at": 1.0,
            "weight_type": "standard"
        },
        "class_type": "IPAdapter"
    },
    # 6: 空潜空间
    "6": {
        "inputs": {"width": 768, "height": 768, "batch_size": 1},
        "class_type": "EmptyLatentImage"
    },
    # 7: KSampler（IPAdapter后的模型 + 提示词）
    "7": {
        "inputs": {
            "seed": 2026004,
            "steps": 30,
            "cfg": 7.5,
            "sampler_name": "euler",
            "scheduler": "normal",
            "positive": ["2", 0],
            "negative": ["3", 0],
            "latent_image": ["6", 0],
            "model": ["5", 0],
            "denoise": 1.0
        },
        "class_type": "KSampler"
    },
    # 8: VAE解码
    "8": {
        "inputs": {"samples": ["7", 0], "vae": ["1", 2]},
        "class_type": "VAEDecode"
    },
    # 9: 保存
    "9": {
        "inputs": {"filename_prefix": "boy_ipadapter", "images": ["8", 0]},
        "class_type": "SaveImage"
    }
}

print("提交 IPAdapter 男孩生成...")
result = send_prompt(prompt)
if result:
    print(f"✅ 成功！prompt_id: {result.get('prompt_id', 'N/A')}")
else:
    print("❌ 提交失败")
