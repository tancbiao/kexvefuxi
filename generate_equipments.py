# -*- coding: utf-8 -*-
"""
冒险岛风格装备图标批量生成脚本
用法: python generate_equipments.py
"""
import json
import urllib.request
import urllib.error
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

COMFYUI_URL = "http://localhost:8188"

EQUIPMENTS = [
    # 角色底稿
    {"name": "girl_base", "prefix": "girl_base",
     "prompt": "1girl chibi Q version, front-facing standing pose, arms slightly open at sides, bare feet, simple white tank top and white shorts base outfit, clean minimalist style, big head small body proportions, pure white background, maple story inspired anime art style, clean lineart, soft pastel colors, long pink hair with bangs, big bright eyes, cute round face, no shadows, flat 2D style, single character, ultra detailed, masterpiece, best quality"},
    {"name": "boy_base", "prefix": "boy_base",
     "prompt": "1boy chibi Q version, front-facing standing pose, arms slightly open at sides, bare feet, simple white tank top and white shorts base outfit, clean minimalist style, big head small body proportions, pure white background, maple story inspired anime art style, clean lineart, soft pastel colors, short black messy hair with bangs, big bright eyes, cute round face, no shadows, flat 2D style, single character, ultra detailed, masterpiece, best quality"},

    # 武器
    {"name": "sword", "prefix": "weapon_sword",
     "prompt": "maple story style chibi cute sword weapon icon, anime illustration, white background, silver and blue color, magic glow effect, clean lineart, pastel colors, flat icon style, transparent background, high quality, transparent PNG"},
    {"name": "staff", "prefix": "weapon_staff",
     "prompt": "maple story style chibi cute magic staff wand icon, anime illustration, white background, purple and pink color, star magic glow, clean lineart, pastel colors, flat icon style, transparent background, high quality, transparent PNG"},
    {"name": "orb", "prefix": "weapon_orb",
     "prompt": "maple story style chibi cute magic orb sphere icon, anime illustration, white background, cyan and blue lightning color, electric glow effect, clean lineart, pastel colors, flat icon style, transparent background, high quality, transparent PNG"},

    # 帽子
    {"name": "hat_explorer", "prefix": "hat_explorer",
     "prompt": "maple story style chibi cute adventurer explorer hat icon, anime illustration, white background, green and brown color, clean lineart, pastel colors, flat icon style, high quality, transparent PNG"},
    {"name": "hat_wizard", "prefix": "hat_wizard",
     "prompt": "maple story style chibi cute wizard wizard hat icon with star, anime illustration, white background, purple and gold color, magic sparkle, clean lineart, pastel colors, flat icon style, high quality, transparent PNG"},
    {"name": "hat_crown", "prefix": "hat_crown",
     "prompt": "maple story style chibi cute golden royal crown icon, anime illustration, white background, gold and red color, jewel decorations, clean lineart, pastel colors, flat icon style, high quality, transparent PNG"},

    # 上衣
    {"name": "top_explorer", "prefix": "top_explorer",
     "prompt": "maple story style chibi cute explorer adventurer jacket coat icon, anime illustration, white background, green and khaki color, clean lineart, pastel colors, flat icon style, high quality, transparent PNG"},
    {"name": "top_mage", "prefix": "top_mage",
     "prompt": "maple story style chibi cute mage wizard robe coat icon, anime illustration, white background, purple and blue color, magic stars decoration, clean lineart, pastel colors, flat icon style, high quality, transparent PNG"},
    {"name": "top_hero", "prefix": "top_hero",
     "prompt": "maple story style chibi cute hero warrior cape jacket icon, anime illustration, white background, red and gold color, flowing cape, clean lineart, pastel colors, flat icon style, high quality, transparent PNG"},

    # 下装
    {"name": "bottom_pants", "prefix": "bottom_pants",
     "prompt": "maple story style chibi cute adventurer pants trousers icon, anime illustration, white background, brown and green color, cargo pockets, clean lineart, pastel colors, flat icon style, high quality, transparent PNG"},
    {"name": "bottom_skirt", "prefix": "bottom_skirt",
     "prompt": "maple story style chibi cute mage wizard skirt icon, anime illustration, white background, purple and blue color, magical pattern, clean lineart, pastel colors, flat icon style, high quality, transparent PNG"},
    {"name": "bottom_shorts", "prefix": "bottom_shorts",
     "prompt": "maple story style chibi cute sporty running shorts icon, anime illustration, white background, orange and white color, athletic style, clean lineart, pastel colors, flat icon style, high quality, transparent PNG"},

    # 披风
    {"name": "cape_red", "prefix": "cape_red",
     "prompt": "maple story style chibi cute red hero cape cloak icon, anime illustration, white background, red and gold color, flowing fabric, clean lineart, pastel colors, flat icon style, high quality, transparent PNG"},
    {"name": "cape_blue", "prefix": "cape_blue",
     "prompt": "maple story style chibi cute blue magic starry cape cloak icon, anime illustration, white background, deep blue and silver color, starry pattern, flowing fabric, clean lineart, pastel colors, flat icon style, high quality, transparent PNG"},

    # 盾牌
    {"name": "shield_small", "prefix": "shield_small",
     "prompt": "maple story style chibi cute small round shield icon, anime illustration, white background, blue and silver color, clean lineart, pastel colors, flat icon style, high quality, transparent PNG"},
    {"name": "shield_big", "prefix": "shield_big",
     "prompt": "maple story style chibi cute large ornate shield icon with star emblem, anime illustration, white background, gold and purple color, magic rune, clean lineart, pastel colors, flat icon style, high quality, transparent PNG"},

    # 鞋子
    {"name": "shoe_speed", "prefix": "shoe_speed",
     "prompt": "maple story style chibi cute wind speed running shoes icon, anime illustration, white background, orange and white color, wind trail effect, clean lineart, pastel colors, flat icon style, high quality, transparent PNG"},
    {"name": "shoe_magic", "prefix": "shoe_magic",
     "prompt": "maple story style chibi cute floating magic boots icon with sparkle, anime illustration, white background, purple and pink color, magical glow, clean lineart, pastel colors, flat icon style, high quality, transparent PNG"},

    # 饰品
    {"name": "acc_badge", "prefix": "acc_badge",
     "prompt": "maple story style chibi cute explorer adventurer badge emblem icon, anime illustration, white background, gold and green color, leaf and compass design, clean lineart, pastel colors, flat icon style, high quality, transparent PNG"},
    {"name": "acc_glasses", "prefix": "acc_glasses",
     "prompt": "maple story style chibi cute smart wizard glasses spectacles icon, anime illustration, white background, purple and blue color, star shaped frames, clean lineart, pastel colors, flat icon style, high quality, transparent PNG"},
    {"name": "acc_bracelet", "prefix": "acc_bracelet",
     "prompt": "maple story style chibi cute strength power wristband bracelet icon, anime illustration, white background, red and gold color, power symbol, clean lineart, pastel colors, flat icon style, high quality, transparent PNG"},
    {"name": "acc_ring", "prefix": "acc_ring",
     "prompt": "maple story style chibi cute agility speed ring icon, anime illustration, white background, green and silver color, wind swirl design, clean lineart, pastel colors, flat icon style, high quality, transparent PNG"},
]


def submit_prompt(prompt_dict, seed):
    """提交生图任务"""
    workflow = {
        "1": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": "AnythingXL_xl.safetensors"}},
        "2": {"class_type": "CLIPTextEncode",
              "inputs": {"text": prompt_dict["prompt"], "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode",
              "inputs": {"text": "realistic, 3d render, photograph, dark, nsfw, ugly, bad anatomy, deformed, low quality, blurry, complex background, watermark, text", "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage",
              "inputs": {"width": 512, "height": 512, "batch_size": 1}},
        "5": {"class_type": "KSampler",
              "inputs": {"seed": seed, "steps": 25, "cfg": 7.0,
                         "sampler_name": "euler", "scheduler": "normal",
                         "denoise": 1.0, "model": ["1", 0],
                         "positive": ["2", 0], "negative": ["3", 0],
                         "latent_image": ["4", 0]}},
        "6": {"class_type": "VAEDecode",
              "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage",
              "inputs": {"filename_prefix": prompt_dict["prefix"], "images": ["6", 0]}}
    }

    data = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(
        f"{COMFYUI_URL}/prompt",
        data=data,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("prompt_id")
    except Exception as e:
        print(f"  提交失败: {e}")
        return None


def wait_for_completion(timeout_sec=120, check_interval=8):
    """等待队列清空"""
    start = time.time()
    while time.time() - start < timeout_sec:
        try:
            req = urllib.request.Request(f"{COMFYUI_URL}/queue")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                queue_len = len(data.get("queue_running", [])) + len(data.get("queue_pending", []))
                if queue_len == 0:
                    return True
                print(f"  队列中还有 {queue_len} 个任务...")
        except Exception as e:
            print(f"  检查队列失败: {e}")
        time.sleep(check_interval)
    return False


def main():
    print(f"🚀 开始批量生成 {len(EQUIPMENTS)} 个装备图标")
    print("=" * 50)

    success_count = 0
    for i, equip in enumerate(EQUIPMENTS):
        print(f"\n[{i+1}/{len(EQUIPMENTS)}] 生成: {equip['name']} ({equip['prefix']})")
        seed = 40000 + i
        pid = submit_prompt(equip, seed)
        if pid:
            print(f"  ✅ 提交成功 (prompt_id: {pid})")
            success_count += 1
        else:
            print(f"  ❌ 提交失败")
        time.sleep(1)

    print(f"\n{'=' * 50}")
    print(f"✅ 全部提交完成 ({success_count}/{len(EQUIPMENTS)})")
    print("⏳ 等待生成完成（预计 5-15 分钟）...")
    done = wait_for_completion()
    if done:
        print("🎉 所有装备生成完毕！")
    else:
        print("⏰ 等待超时，请在 ComfyUI 界面查看进度")


if __name__ == "__main__":
    main()
