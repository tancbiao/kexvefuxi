# -*- coding: utf-8 -*-
"""补全装备图标生成"""
import json
import urllib.request
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
COMFYUI_URL = "http://localhost:8188"

REMAINING = [
    # 重试失败的
    {"name": "hat_explorer", "prefix": "hat_explorer",
     "prompt": "maple story style chibi cute green explorer adventurer hat icon, anime illustration, white background, green and brown color, leaf decoration, clean lineart, pastel colors, flat icon style, high quality"},
    # 后续因崩溃缺失的
    {"name": "top_explorer", "prefix": "top_explorer",
     "prompt": "maple story style chibi cute explorer jacket coat top icon, anime illustration, white background, green and khaki color, adventure style, clean lineart, pastel colors, flat icon style, high quality"},
    {"name": "top_mage", "prefix": "top_mage",
     "prompt": "maple story style chibi cute mage wizard robe coat top icon, anime illustration, white background, purple and blue color, magic stars decoration, clean lineart, pastel colors, flat icon style, high quality"},
    {"name": "top_hero", "prefix": "top_hero",
     "prompt": "maple story style chibi cute hero warrior red cape jacket top icon, anime illustration, white background, red and gold color, flowing cape detail, clean lineart, pastel colors, flat icon style, high quality"},
    {"name": "bottom_pants", "prefix": "bottom_pants",
     "prompt": "maple story style chibi cute adventurer explorer pants trousers bottom icon, anime illustration, white background, brown and green color, cargo pockets detail, clean lineart, pastel colors, flat icon style, high quality"},
    {"name": "bottom_skirt", "prefix": "bottom_skirt",
     "prompt": "maple story style chibi cute mage wizard purple skirt bottom icon, anime illustration, white background, purple and blue color, magical pattern decoration, clean lineart, pastel colors, flat icon style, high quality"},
    {"name": "bottom_shorts", "prefix": "bottom_shorts",
     "prompt": "maple story style chibi cute sporty athletic orange shorts bottom icon, anime illustration, white background, orange and white color, athletic running style, clean lineart, pastel colors, flat icon style, high quality"},
    {"name": "cape_red", "prefix": "cape_red",
     "prompt": "maple story style chibi cute red flowing hero cape cloak icon, anime illustration, white background, red and gold trim color, wind flowing fabric, clean lineart, pastel colors, flat icon style, high quality"},
    {"name": "cape_blue", "prefix": "cape_blue",
     "prompt": "maple story style chibi cute deep blue magic starry cape cloak icon, anime illustration, white background, deep blue and silver color, constellation pattern, flowing fabric, clean lineart, pastel colors, flat icon style, high quality"},
    {"name": "shield_small", "prefix": "shield_small",
     "prompt": "maple story style chibi cute blue silver small round shield icon, anime illustration, white background, blue and silver metallic color, clean lineart, pastel colors, flat icon style, high quality"},
    {"name": "shield_big", "prefix": "shield_big",
     "prompt": "maple story style chibi cute gold purple large ornate shield with star rune icon, anime illustration, white background, gold and purple color, magic rune symbol, clean lineart, pastel colors, flat icon style, high quality"},
    {"name": "shoe_speed", "prefix": "shoe_speed",
     "prompt": "maple story style chibi cute orange white wind speed running shoes icon, anime illustration, white background, orange and white color, wind trail motion effect, clean lineart, pastel colors, flat icon style, high quality"},
    {"name": "shoe_magic", "prefix": "shoe_magic",
     "prompt": "maple story style chibi cute purple pink floating magic boots icon, anime illustration, white background, purple and pink color, magical sparkle glow, clean lineart, pastel colors, flat icon style, high quality"},
    {"name": "acc_badge", "prefix": "acc_badge",
     "prompt": "maple story style chibi cute gold green explorer adventurer badge emblem icon, anime illustration, white background, gold and green color, compass and leaf design, clean lineart, pastel colors, flat icon style, high quality"},
    {"name": "acc_glasses", "prefix": "acc_glasses",
     "prompt": "maple story style chibi cute purple blue smart wizard glasses spectacles icon, anime illustration, white background, purple and blue color, star shaped frame design, clean lineart, pastel colors, flat icon style, high quality"},
    {"name": "acc_bracelet", "prefix": "acc_bracelet",
     "prompt": "maple story style chibi cute red gold strength power wristband bracelet icon, anime illustration, white background, red and gold color, power fist symbol, clean lineart, pastel colors, flat icon style, high quality"},
    {"name": "acc_ring", "prefix": "acc_ring",
     "prompt": "maple story style chibi cute green silver agility speed ring icon, anime illustration, white background, green and silver color, wind swirl design, clean lineart, pastel colors, flat icon style, high quality"},
]


def submit(p, seed):
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": "AnythingXL_xl.safetensors"}},
        "2": {"class_type": "CLIPTextEncode",
              "inputs": {"text": p["prompt"], "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode",
              "inputs": {"text": "realistic 3d render photograph dark nsfw ugly bad anatomy deformed low quality blurry complex background watermark text", "clip": ["1", 1]}},
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
              "inputs": {"filename_prefix": p["prefix"], "images": ["6", 0]}}
    }
    data = json.dumps({"prompt": wf}).encode("utf-8")
    req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8")).get("prompt_id")
    except Exception as e:
        print(f"  失败: {e}")
        return None


def wait_queue():
    for _ in range(20):
        try:
            with urllib.request.urlopen(f"{COMFYUI_URL}/queue", timeout=5) as r:
                d = json.loads(r.read().decode("utf-8"))
                n = len(d.get("queue_running", [])) + len(d.get("queue_pending", []))
                if n == 0:
                    return True
                print(f"  队列剩余 {n} 个...")
        except:
            pass
        time.sleep(6)
    return False


print(f"🚀 补全 {len(REMAINING)} 个装备...")
ok = 0
for i, item in enumerate(REMAINING):
    print(f"[{i+1}/{len(REMAINING)}] {item['name']}...", end=" ")
    pid = submit(item, 41000 + i)
    if pid:
        print("✅")
        ok += 1
    else:
        print("❌")
    time.sleep(0.5)

print(f"\n提交完成 {ok}/{len(REMAINING)}")
print("等待生成（约 5-8 分钟）...")
done = wait_queue()
print("🎉 完成！" if done else "⏰ 超时，请查看 ComfyUI 界面")
