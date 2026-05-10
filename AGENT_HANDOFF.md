# AGENT_HANDOFF.md — 白龙接手说明

> 编写日期：2026-05-11
> 编写人：千寻（Chihiro）
> 接手人：白龙

## 项目概况

科学复习系统 `kexvefuxi.cn`，当前入口：
- **正式版**：`/1/1/index_v5.html`（正在使用的版本）
- 根域名 `index.html` 302 跳转到 v5

GitHub 仓库：`tancbiao/kexvefuxi`，GitHub Pages 自动部署。

## 当前已知问题

### P0 — 功能故障

| 问题 | 表现 | 根因猜测 |
|------|------|----------|
| 成就按钮 → 打开的是通知公告 | 状态栏🏆按钮调用 `showNotices()`，成就殿堂已被通知弹窗替换 | 成就弹窗HTML和`showAchievements()`函数已被移除 |
| 课程选择正常但选课后闪空白 | 点击"下册"后显示反馈提示，然后屏幕变空白再出现课程 | `showScreen('levelScreen')` 可能在CSS和JS之间竞争。已改过showScreen两次，但可能仍有问题 |
| 通知弹窗关闭按钮 (×) 按不了 | 早期版本就有此问题 | 可能是关闭函数的触发条件问题 |
| 背包按钮打不开 | `showBackpack()` 执行后背包不显示 | 可能是 `initInventory62()` 等函数抛出错误，或 `.backpack-overlay.show { display:flex }` 被覆盖 |

### P1 — 显示异常

| 问题 | 表现 |
|------|------|
| 残留的更新公告内容可见 | 页面底部（背包之前）有一整个 `<div class="version-notice">` 显示"更新公告 v1.1"等内容 |
| 爬塔和宠物 iframe 已延迟加载 | 已修复，页面加载时不再自动加载 |
| 首页无通知公告预览 | 通知公告已被移除但用户希望加回来 |

### P2 — 后台服务

| 问题 | 表现 |
|------|------|
| 腾讯云API不稳定 | `/api/ranking/*` 和 `/api/notifications` 偶尔 500，JSON文件损坏 |
| 防火墙规则重置 | 腾讯云轻量服务器重启后防火墙（5000/443）会重置，需手动添加 |

## 根因分析 — CRLF 编码地狱（⚠️最重要）

`1/1/index_v5.html` 文件的换行符极其混乱：
- 每行包含 **16个 `\r`（回车符）** 后跟一个 `\n`（换行符）
- 这不是标准的 Windows CRLF（`\r\n`），而是：`\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\r\n`
- 这种编码导致 **所有 Python 字符串替换操作都不稳定**

典型案例（本次踩过的坑）：

| 想做的事情 | Python写的模式 | 实际文件中的模式 | 结果 |
|-----------|---------------|-----------------|------|
| 加 `startDailyAchievementCheck()` 函数定义 | 普通字符串 | 16个`\r`的CRLF | 定义未生效 |
| 加 `startDailyAchievementCheck()` 函数调用 | 普通字符串匹配 | 匹配到了部分 | 调用生效但定义缺失 |
| 删除残留的 `version-notice` HTML | 普通字符串删除 | 破坏了周围的HTML结构 | 课程选择崩溃 |
| 用 `<div style="display:none">` 包裹 | 匹配到`version-notice` | 包裹范围出错 | 背包也被包进去了 |
| 修复 `ddocument` → `document` | 全局替换 `ddocument` | 有些替换了，有些没替换 | 修复不全 |

**该文件的CRLF特征**（可用于检测）：
```python
with open("file.html", "rb") as f:
    data = f.read()
# 查看换行符
import re
crlf = re.findall(b'[\\r]{10,}', data[:1000])
print([len(x) for x in crlf])  # 应该看到 [16, 16, 16, ...]
```

## 建议的修改方式

**不要使用 Python 字符串替换**来修改此文件。建议方法：

1. **用二进制字节精确匹配**：
   ```python
   with open("file.html", "rb") as f:
       data = f.read()
   idx = data.find(b"目标字符串")
   data = data[:idx] + b"新内容" + data[idx+len(b"旧内容"):]
   ```

2. **或用 sed 处理**（Git Bash）：
   ```bash
   sed -i 's/旧内容/新内容/g' file.html
   ```

3. **最可靠的方法**：用 `git show f8b4b43:1/1/index_v5.html` 获取干净的基准版本，重新从头构建。

## 已确认可用的基准版本

| 版本 | 提交 | 状态 |
|------|------|------|
| V2 | `e4edff3` | ✅ 选课正常、成就弹窗正常、背包正常 |
| V4 | `...` | 介于V2和V5之间 |
| V5 | `f8b4b43` | 选课正常，但成就弹窗已被替换为通知、有残留内容 |
| V5 (当前) | `11c0e09` | 同上 + 爬塔/宠物延迟加载 但隐藏包裹未生效 |

## 需要恢复/添加的功能清单

按用户反馈的理想状态排列：

1. **成就按钮 → 成就殿堂**（恢复 `showAchievements()` 和对应的HTML弹窗）
2. **通知公告 → 铃铛🔔面板**（右侧滑出通知面板 `notify-panel`）
3. **首页通知预览**（在"开始挑战"下方显示通知摘要）
4. **残留的更新公告**用 `<div style="display:none">` 包裹（不要删除HTML）
5. **排行榜显示学生姓名**（中间字\*号）
6. **弹幕公告系统**（登录时显示通知，每5分钟飘成就）
7. **爬塔按年级加载不同题库**
8. **科技节通知弹窗**（23点自动关闭）

## 服务器信息

- **腾讯云轻量服务器**：`159.75.134.151`
- **SSH密码**：`sC,/{8v*!b9EQ2$`
- **API域名**：`https://api.kexvefuxi.cn`（Let's Encrypt SSL）
- **API端口**：5000（Flask/gunicorn）
- **服务名**：`kexvefuxi-api`
- **数据目录**：`/data/kexvefuxi/`
- **API代码**：`/data/api.py`
- **Nginx**：宝塔面板管理，`/www/server/nginx/`

> 注意：服务器重启后防火墙规则会重置，需手动添加5000和443端口

## 推荐调试路径

1. 先从 `git show f8b4b43:1/1/index_v5.html` 提取干净基准
2. 确认基准版本选课正常、背包正常
3. 用二进制字节匹配法（不是字符串替换）逐步添加功能
4. 每加一个功能后，在浏览器按F12检查Console有无报错
5. 部署前用 `git diff --ignore-cr-at-eol` 确认真正改了什么
