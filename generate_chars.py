import json
import urllib.request
import urllib.error
import sys

sys.stdout.reconfigure(encoding='utf-8')

COMFYUI_URL = "http://localhost:8188/prompt"

def submit_prompt(prompt_dict, label=""):
    data = json.dumps({"prompt": prompt_dict}).encode('utf-8')
    req = urllib.request.Request(
        COMFYUI_URL,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            print(f"✓ {label} 提交成功: {result.get('prompt_id', '')}")
            return result
    except urllib.error.HTTPError as e:
        print(f"✗ {label} HTTP错误 {e.code}: {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"✗ {label} 错误: {e}")
        return None

# 通用生图工作流
def make_workflow(positive_prompt, negative_prompt, seed, filename_prefix, width=1024, height=1536):
    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "AnythingXL_xl.safetensors"}
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": positive_prompt, "clip": ["1", 1]}
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative_prompt, "clip": ["1", 1]}
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": width, "height": height, "batch_size": 1}
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": 30,
                "cfg": 7.5,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0]
            }
        },
        "6": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["5", 0], "vae": ["1", 2]}
        },
        "7": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": filename_prefix, "images": ["6", 0]}
        }
    }

POSITIVE_GIRL = (
    "1girl, chibi, Q version, front-facing standing pose, arms slightly open at sides, "
    "simple white tank top and white shorts, barefoot, clean minimalist style, "
    "big head small body proportions, pure white background, maple story inspired anime art, "
    "clean lineart, soft pastel colors, long pink hair with bangs, big bright eyes, "
    "cute round face, flat 2D style, single character, masterpiece, best quality"
)

POSITIVE_BOY = (
    "1boy, chibi, Q version, front-facing standing pose, arms slightly open at sides, "
    "simple white tank top and white shorts, barefoot, clean minimalist style, "
    "big head small body proportions, pure white background, maple story inspired anime art, "
    "clean lineart, soft pastel colors, short black messy hair with bangs, big bright eyes, "
    "cute round face, flat 2D style, single character, masterpiece, best quality"
)

NEGATIVE = "realistic, 3d render, photograph, nsfw, ugly, bad anatomy, deformed, low quality, blurry, complex background, multiple characters, text, watermark"

print("=" * 50)
print("开始生成冒险岛风格Q版角色底稿")
print("=" * 50)

# 女孩
girl_workflow = make_workflow(POSITIVE_GIRL, NEGATIVE, seed=20240101, filename_prefix="ms_girl_base")
r1 = submit_prompt(girl_workflow, "Q版女孩")

# 男孩
boy_workflow = make_workflow(POSITIVE_BOY, NEGATIVE, seed=20240102, filename_prefix="ms_boy_base")
r2 = submit_prompt(boy_workflow, "Q版男孩")

print("\n等待生成完成（约60秒）...")
import time
time.sleep(70)

print("\n生成完成！查看 D:\\ComfyUI\\output\\ 目录")
