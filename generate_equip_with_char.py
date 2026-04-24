# -*- coding: utf-8 -*-
"""
给角色穿戴装备 - img2img 版本
用法：python generate_equip_with_char.py
会弹出选择文件窗口，选中角色底稿图片后开始生成
"""
import subprocess
import sys
import json
import os
import tkinter as tk
from tkinter import filedialog

# ========== 工具函数 ==========
def send_prompt(prompt):
    """发送 prompt 到 ComfyUI"""
    payload = {"prompt": prompt}
    result = subprocess.run(
        ["curl.exe", "-s", "-X", "POST",
         "http://localhost:8188/prompt",
         "-H", "Content-Type: application/json",
         "-d", json.dumps(payload)],
        capture_output=True, text=True
    )
    return result.stdout

def check_comfyui():
    """检查 ComfyUI 是否运行"""
    r = subprocess.run(
        ["curl.exe", "-s", "http://localhost:8188/system_stats"],
        capture_output=True
    )
    return r.returncode == 0 and "memory" in r.stdout

# ========== 装备定义 ==========
# 格式：(文件名, 英文提示词, 中文名)
EQUIPMENTS = [
    # --- 武器 ---
    ("weapon_firesword",  
     "chibi cute boy character wearing golden flame sword at waist, maple story style pixel RPG, transparent background, sharp sword with fire effect, golden handle, warm orange flames, white t-shirt base character intact, detailed flame sword equipment icon",
     "火焰长剑"),
    ("weapon_icewand",
     "chibi cute girl character holding magical ice wand with crystal tip, maple story style anime, transparent background, blue crystalline wand, frost and snowflake effects on wand, purple robe base character intact, magical staff equipment icon",
     "冰晶魔杖"),
    ("weapon_thunderorb",
     "chibi cute boy character with glowing electric orb floating near hand, maple story style anime, transparent background, yellow electric orb with lightning sparks, blue outfit base character intact, energy sphere equipment icon",
     "雷电宝珠"),

    # --- 头部 ---
    ("hat_wizard",
     "chibi cute girl character wearing pointed wizard hat with star decorations, maple story style anime, transparent background, purple cone hat, golden stars and moon symbols, white blouse base character intact, wizard hat equipment icon",
     "魔法师帽"),
    ("hat_viking",
     "chibi cute boy character wearing viking horned helmet, maple story style RPG, transparent background, brown leather helmet with upward curved horns, grey metal rim, white t-shirt base character intact, viking helmet equipment icon",
     "维京头盔"),
    ("hat_cat",
     "chibi cute girl character wearing cute cat ear headband, maple story style anime, transparent background, pink cat ear headband with ribbon bow, white blouse base character intact, kawaii cat ears equipment icon",
     "猫咪发箍"),

    # --- 身体/披风 ---
    ("cape_dragon",
     "chibi cute boy character wearing long red dragon scale cape flowing behind, maple story style anime, transparent background, red flowing cape with scale texture, gold dragon embroidery on cape, white t-shirt base character intact, dragon cape equipment icon",
     "龙鳞披风"),
    ("cape_angel",
     "chibi cute girl character wearing white angel feather wings and halo, maple story style anime, transparent background, white feathered wings spread out, golden glowing halo above head, purple dress base character intact, angel wing equipment icon",
     "天使之翼"),
    ("armor_knight",
     "chibi cute boy character wearing silver knight chestplate armor with blue gem in center, maple story style RPG, transparent background, silver shiny chest armor, shoulder pauldrons, blue jewel emblem, white t-shirt base character intact, knight armor equipment icon",
     "骑士胸甲"),
    ("dress_fairy",
     "chibi cute girl character wearing pastel pink fairy dress with flower petal skirt, maple story style anime, transparent background, layered pink tulle skirt, small flower decorations, leaf shoulder straps, white base character intact, fairy dress equipment icon",
     "精灵仙裙"),

    # --- 特殊 ---
    ("pet_slime",
     "chibi cute girl character with small cute transparent slime pet floating beside shoulder, maple story style anime, transparent background, bouncy translucent slime creature, blue-green color, cute smiley face on slime, white dress base character intact, slime pet companion icon",
     "史莱姆宠物"),
    ("pet_panda",
     "chibi cute boy character with small round panda bear companion sitting on shoulder, maple story style anime, transparent background, black and white round panda cub, cute expression, bamboo leaf in paw, white t-shirt base character intact, panda pet companion icon",
     "熊猫伙伴"),
    ("accessory_necklace",
     "chibi cute girl character wearing golden heart-shaped pendant necklace, maple story style anime, transparent background, shiny golden chain necklace, glowing red heart gem pendant, white blouse base character intact, heart necklace accessory icon",
     "心形项链"),
    ("accessory_scarf",
     "chibi cute boy character wearing flowing red scarf wrapped around neck, maple story style anime RPG, transparent background, long red scarf with white stripe pattern, scarf ends flowing in wind, white t-shirt base character intact, red scarf accessory icon",
     "红色围巾"),
    ("glove_fire",
     "chibi cute girl character wearing red fingerless gloves with flame patterns, maple story style anime, transparent background, red open-finger gloves, flame designs on back of gloves, white skin visible on fingers, purple dress base character intact, flame glove equipment icon",
     "火焰手套"),
]

# ========== 主程序 ==========

# 1. 选择角色图片
root = tk.Tk()
root.withdraw()
char_file = filedialog.askopenfilename(
    title="选择角色底稿（白衣白裤/白裙背景）",
    filetypes=[("PNG图片", "*.png"), ("所有图片", "*.jpg *.jpeg *.bmp")]
)
if not char_file:
    print("未选择文件，退出。")
    sys.exit(0)

char_file_abs = os.path.abspath(char_file)
char_file_name = os.path.splitext(os.path.basename(char_file))[0]
print(f"已选择角色图：{char_file_name}")

# 2. 检查 ComfyUI
print("检查 ComfyUI 连接...")
if not check_comfyui():
    print("⚠️ ComfyUI 未运行，正在启动...")
    subprocess.Popen(
        ["C:\\Users\\tanc\\miniconda3\\envs\\comfyui\\python.exe",
         "main.py", "--force-fp16", "--listen", "0.0.0.0"],
        cwd="D:\\ComfyUI",
        creationsubprocessflags=0x08000000  # DETACHED_PROCESS
    )
    import time
    for i in range(30):
        time.sleep(2)
        if check_comfyui():
            print("✅ ComfyUI 已就绪")
            break
        print(f"  等待中... ({i+1}/30)")
    else:
        print("❌ ComfyUI 启动超时，请手动启动后重试")
        sys.exit(1)

print("✅ ComfyUI 运行正常，开始生成装备...")

# 3. 逐个生成装备
generated = []
failed = []

for filename, eng_prompt, cn_name in EQUIPMENTS:
    prompt = {
        # 加载角色底图
        "3": {
            "inputs": {"image": char_file_name + ".png", "choose input to add": "image"},
            "class_type": "LoadImage"
        },
        "4": {
            "inputs": {"channel": "alpha"},
            "class_type": "ChannelAjustOutput"
        },
        "5": {
            "inputs": {"image": "white"},  # 白色背景
            "class_type": "LoadImage"
        },

        # Checkpoint
        "1": {
            "inputs": {"ckpt_name": "AnythingXL_xl.safetensors"},
            "class_type": "CheckpointLoaderSimple"
        },

        # Positive Prompt
        "2": {
            "inputs": {
                "text": eng_prompt,
                "clip": ["1", 1]
            },
            "class_type": "CLIPTextEncode"
        },

        # Negative Prompt
        "6": {
            "inputs": {
                "text": "realistic 3d render photograph dark nsfw ugly bad anatomy deformed low quality blurry complex background watermark text extra limbs",
                "clip": ["1", 1]
            },
            "class_type": "CLIPTextEncode"
        },

        # VAE 编码（用于 img2img）
        "7": {
            "inputs": {"pixels": ["3", 0], "vae": ["1", 2]},
            "class_type": "VAEEncodeForInpaint"
        },

        # 潜空间图像（与原图尺寸相同）
        "8": {
            "inputs": {"width": 512, "height": 512, "batch_size": 1},
            "class_type": "EmptyLatentImage"
        },

        # KSampler - denoise 0.5 平衡保真度和创作自由度
        "9": {
            "inputs": {
                "seed": 88888,
                "steps": 30,
                "cfg": 7.5,
                "sampler_name": "euler",
                "scheduler": "normal",
                "positive": ["2", 0],
                "negative": ["6", 0],
                "latent_image": ["7", 0],
                "denoise": 0.55
            },
            "class_type": "KSampler"
        },

        # 解码
        "10": {
            "inputs": {"samples": ["9", 0], "vae": ["1", 2]},
            "class_type": "VAEDecode"
        },

        # 保存
        "11": {
            "inputs": {
                "filename_prefix": filename,
                "images": ["10", 0]
            },
            "class_type": "SaveImage"
        }
    }

    resp = send_prompt(prompt)
    try:
        data = json.loads(resp)
        if data.get("prompt_id"):
            generated.append(f"{cn_name} ({filename})")
            print(f"  ✅ {cn_name} - 已提交")
        else:
            failed.append(cn_name)
            print(f"  ❌ {cn_name} - 提交失败")
    except:
        failed.append(cn_name)
        print(f"  ❌ {cn_name} - 响应解析失败: {resp[:100]}")

print(f"\n🎉 提交完成！")
print(f"  ✅ 成功: {len(generated)} 件")
print(f"  ❌ 失败: {len(failed)} 件")
if failed:
    print(f"  失败列表: {', '.join(failed)}")
print(f"\n生成的图片请到 D:\\ComfyUI\\output 查看")
