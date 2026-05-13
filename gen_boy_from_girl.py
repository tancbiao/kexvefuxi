# -*- coding: utf-8 -*-
"""img2img: 以女孩素底为参考，只改发型/性别生成男孩版本
   denoise=0.35 极低，最大程度保持姿势/大小/动作不变"""
import urllib.request
import urllib.error
import urllib.parse
import json
import base64
import os

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

def upload_image(image_path):
    """上传图片到 ComfyUI"""
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    # 构造 multipart/form-data
    boundary = "----WebKitFormBoundary"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="girl_base_simple.png"\r\n'
        f"Content-Type: image/png\r\n\r\n"
        f"{img_b64}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="type"\r\n\r\n'
        f"input\r\n"
        f"--{boundary}--\r\n"
    ).encode("utf-8")

    req = urllib.request.Request(
        f"{COMFYUI_URL}/upload/image",
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            print(f"上传成功: {result}")
            return result.get("name", "girl_base_simple.png")
    except urllib.error.HTTPError as e:
        print(f"上传失败: {e.code} {e.reason}")
        print(e.read().decode("utf-8")[:300])
        # 尝试直接用 input 目录文件名
        return "girl_base_simple_00001_.png"

img_path = r"D:\ComfyUI\input\girl_base_simple_00001_.png"
print("上传女孩底稿...")
img_name = upload_image(img_path)
print(f"图片名: {img_name}")

# ========== img2img 工作流 ==========
# 节点连接：
# 1(Checkpoint) → model给KSampler, vae给VAEEncode/VAEDecode, clip给CLIPTextEncode
# 2(CLIPTextEncode+正面) → positive给KSampler
# 3(CLIPTextEncode-负面) → negative给KSampler  (注意：不是LoadImage)
# 4(LoadImage) → pixels给VAEEncode
# 5(VAEEncode) → latent给KSampler
# 6(KSampler denoise=0.35) → latent给VAEDecode
# 7(VAEDecode) → image给SaveImage
# 8(SaveImage)

prompt = {
    "1": {
        "inputs": {"ckpt_name": "AnythingXL_xl.safetensors"},
        "class_type": "CheckpointLoaderSimple"
    },
    "2": {
        "inputs": {
            "text": (
                "chibi cute anime BOY character, same pose same stance same proportions as reference image, "
                "short messy boy hair brown color, white simple cotton t-shirt and white shorts, "
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
            "text": "realistic 3d render photograph dark nsfw ugly bad anatomy deformed low quality blurry complex background watermark text colorful bright flashy crowded cluttered detailed accessories armor cape wings pet jewelry hat weapon flashy colorful nsfw underwear long hair girl feminine face",
            "clip": ["1", 1]
        },
        "class_type": "CLIPTextEncode"
    },
    "4": {
        "inputs": {"image": img_name, "choose tokenizer to use": "CLIP"},
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
