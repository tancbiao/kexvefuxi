"""将内嵌题库JS转换为小程序 require 格式"""
import re
import os

BASE = r"C:\Users\tanc\Documents\WPSDrive\362543761\WPS云盘\谭政\科学复习系统\_kexvefuxi"
OUT_DIR = r"C:\Users\tanc\Documents\WPSDrive\362543761\WPS云盘\谭政\科学复习系统\_kexvefuxi-miniprogram\data"

# 确保输出目录存在
os.makedirs(OUT_DIR, exist_ok=True)

# 读取源文件
src = os.path.join(BASE, "data", "4-2-embedded.js")
with open(src, 'r', encoding='utf-8') as f:
    content = f.read()

# 替换 const questionData = { 为 module.exports = {
content = content.replace("const questionData = {", "module.exports = {")

# 写入小程序 data 目录
out_path = os.path.join(OUT_DIR, "4-2.js")
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(content)

# 统计
lessons = content.count("'u")
units = len(re.findall(r'unit\d+:', content))
print(f"转换完成：{units}个单元，约{lessons}课")
print(f"输出：{out_path}")
print(f"文件大小：{os.path.getsize(out_path) / 1024:.1f} KB")

# 小程序有 2MB 单包限制，检查文件大小
size_kb = os.path.getsize(out_path) / 1024
if size_kb > 2048:
    print("[WARN] file > 2MB, need subpackages!")
else:
    print("[OK] file size normal (< 2MB)")
