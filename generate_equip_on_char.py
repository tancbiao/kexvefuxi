# -*- coding: utf-8 -*-
"""
给角色穿戴装备 - img2img 版本
直接用 ms_boy_base 和 ms_girl_base 作为底稿，无需手动选择
"""
import subprocess
import json
import os
import time
import sys

def send_prompt(prompt):
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
    r = subprocess.run(
        ["curl.exe", "-s", "http://localhost:8188/system_stats"],
        capture_output=True
    )
    return r.returncode == 0

# ========== 装备列表 ==========
# (文件名, 底稿名, 提示词)
EQUIPMENTS = [
    # --- 武器 ---
    ("eq_boy_firesword",
     "ms_boy_base_00001_",
     "chibi cute boy character wearing golden flame sword at waist, maple story style RPG game, transparent white background, sharp sword with fire effect on blade, golden handle, orange flames, boy character unchanged, detailed flame sword equipment icon clean flat style",
     "火焰长剑-男"),
    ("eq_girl_icewand",
     "ms_girl_base_00001_",
     "chibi cute girl character holding magical ice wand with crystal tip, maple story style anime game, transparent white background, blue crystalline wand with frost and snowflake effects, girl character unchanged, purple magical staff icon clean flat style",
     "冰晶魔杖-女"),
    ("eq_boy_thunderorb",
     "ms_boy_base_00001_",
     "chibi cute boy character with glowing electric orb floating near hand, maple story style anime game, transparent white background, yellow electric orb with lightning sparks and blue bolts, boy character unchanged, energy sphere equipment icon clean flat style",
     "雷电宝珠-男"),

    # --- 头部 ---
    ("eq_girl_wizardhat",
     "ms_girl_base_00001_",
     "chibi cute girl character wearing pointed purple wizard hat with golden stars and crescent moon decorations, maple story style anime game, transparent white background, cone shaped hat with star symbols, girl character unchanged, wizard hat equipment icon clean flat style",
     "魔法师帽-女"),
    ("eq_boy_vikinghelm",
     "ms_boy_base_00001_",
     "chibi cute boy character wearing viking horned helmet with upward curved horns, maple story style RPG game, transparent white background, brown leather helmet with grey metal rim, boy character unchanged, viking helmet equipment icon clean flat style",
     "维京头盔-男"),
    ("eq_girl_catears",
     "ms_girl_base_00001_",
     "chibi cute girl character wearing cute pink cat ear headband with ribbon bow, maple story style anime game, transparent white background, pink fluffy cat ears headband, girl character unchanged, kawaii cat ear accessory icon clean flat style",
     "猫咪发箍-女"),

    # --- 披风/翅膀 ---
    ("eq_boy_dragoncape",
     "ms_boy_base_00001_",
     "chibi cute boy character wearing long red dragon scale cape flowing behind, maple story style anime game, transparent white background, red flowing cape with scale texture and gold dragon embroidery, boy character unchanged, dragon cape equipment icon clean flat style",
     "龙鳞披风-男"),
    ("eq_girl_angelwings",
     "ms_girl_base_00001_",
     "chibi cute girl character wearing white feathered angel wings spread out with glowing golden halo above head, maple story style anime game, transparent white background, soft white wings with feather detail, glowing halo, girl character unchanged, angel wing equipment icon clean flat style",
     "天使之翼-女"),
    ("eq_boy_knightarmor",
     "ms_boy_base_00001_",
     "chibi cute boy character wearing silver shiny knight chestplate armor with blue gem emblem on chest, maple story style RPG game, transparent white background, shoulder pauldrons, grey metal armor, boy character unchanged, knight armor equipment icon clean flat style",
     "骑士胸甲-男"),
    ("eq_girl_fairydress",
     "ms_girl_base_00001_",
     "chibi cute girl character wearing pastel pink fairy dress with layered tulle petal skirt and small flower decorations, maple story style anime game, transparent white background, pink flowing skirt, flower accessories, girl character unchanged, fairy dress equipment icon clean flat style",
     "精灵仙裙-女"),

    # --- 宠物 ---
    ("eq_girl_slimepet",
     "ms_girl_base_00001_",
     "chibi cute girl character with small translucent cute slime pet creature floating beside shoulder, maple story style anime game, transparent white background, bouncy blue-green slime with cute smiley face, wobbling jelly body, girl character unchanged, slime pet companion icon clean flat style",
     "史莱姆宠物-女"),
    ("eq_boy_pandapet",
     "ms_boy_base_00001_",
     "chibi cute boy character with small round black and white panda bear companion sitting on shoulder, maple story style anime game, transparent white background, round panda cub with cute expression, holding bamboo leaf, boy character unchanged, panda pet companion icon clean flat style",
     "熊猫伙伴-男"),

    # --- 饰品 ---
    ("eq_girl_heartnecklace",
     "ms_girl_base_00001_",
     "chibi cute girl character wearing shiny golden heart-shaped pendant necklace on neck, maple story style anime game, transparent white background, golden chain necklace with glowing red heart gem, girl character unchanged, heart necklace accessory icon clean flat style",
     "心形项链-女"),
    ("eq_boy_redscarf",
     "ms_boy_base_00001_",
     "chibi cute boy character wearing long flowing red scarf wrapped around neck with white stripe pattern, maple story style RPG game, transparent white background, scarf ends flowing gently, boy character unchanged, red scarf accessory icon clean flat style",
     "红色围巾-男"),
    ("eq_girl_firegloves",
     "ms_girl_base_00001_",
     "chibi cute girl character wearing red fingerless gloves with flame patterns on back of hands, maple story style anime game, transparent white background, red open finger gloves, flame designs on back, girl character unchanged, flame glove equipment icon clean flat style",
     "火焰手套-女"),
]

# ========== 主程序 ==========
print("检查 ComfyUI...")
if not check_comfyui():
    print("❌ ComfyUI 未运行，请先启动")
    sys.exit(1)
print("✅ ComfyUI 运行正常\n")

# 逐个生成
generated = []
failed = []

for i, (filename, base_name, eng_prompt, cn_name) in enumerate(EQUIPMENTS):
    print(f"[{i+1}/{len(EQUIPMENTS)}] 生成 {cn_name}...", end=" ", flush=True)

    prompt = {
        # 加载角色底图
        "3": {
            "inputs": {
                "image": f"{base_name}.png",
                "mask": ""
            },
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
                "text": "realistic 3d render photograph dark nsfw ugly bad anatomy deformed low quality blurry complex background watermark text extra limbs extra fingers missing limbs",
                "clip": ["1", 1]
            },
            "class_type": "CLIPTextEncode"
        },

        # VAE 编码（img2img：编码原图为潜空间）
        "7": {
            "inputs": {"pixels": ["3", 0], "vae": ["1", 2]},
            "class_type": "VAEEncode"
        },

        # KSampler - denoise 0.55 平衡保真度和装备清晰度
        "9": {
            "inputs": {
                "seed": 88888 + i * 1000,
                "steps": 30,
                "cfg": 7.5,
                "sampler_name": "euler",
                "scheduler": "normal",
                "positive": ["2", 0],
                "negative": ["6", 0],
                "latent_image": ["7", 0],
                "model": ["1", 0],
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
            generated.append(cn_name)
            print("✅ 已提交")
        else:
            failed.append(cn_name)
            print(f"❌ 失败: {data}")
    except:
        failed.append(cn_name)
        print(f"❌ 响应解析失败: {resp[:80]}")

print(f"\n🎉 提交完成！")
print(f"  ✅ 成功: {len(generated)} 件")
if failed:
    print(f"  ❌ 失败 ({len(failed)}): {', '.join(failed)}")
print(f"\n图片输出到: D:\\ComfyUI\\output")
print("建议 denoise=0.55 效果不错，如需调整可修改脚本中 denoise 参数（0.4~0.7）")
