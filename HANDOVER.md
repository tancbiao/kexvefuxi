# 科学复习系统 · 交接文档

> 最后更新：2026-05-23
> 项目名称：西西时光（xixitime.cn / kexvefuxi.cn）

---

## 一、项目概览

| 项目 | 内容 |
|------|------|
| **本地主目录** | `D:\kexvefuxi\`（2026-05-23 从 WPS 云盘迁移） |
| **旧路径（废弃）** | `C:\Users\tanc\Documents\WPSDrive\362543761\WPS云盘\谭政\科学复习系统\_kexvefuxi\` |
| **GitHub** | `tancbiao/kexvefuxi`，分支 `main` |
| **推送代理** | 需走 Clash Verge 代理 `http://127.0.0.1:7897` |
| **在线访问** | https://xixitime.cn/kexvefuxi / https://kexvefuxi.cn |
| **部署方式** | GitHub Pages + 自定义域名（CNAME） |
| **服务器** | 159.75.134.151，API 服务 `/data/api.py` v706，systemctl 管理 |
| **负责人** | 谭政（谭谭），广东江门范罗冈小学科学教师 |

---

## 二、系统架构

```
┌──────────────────────────────────────────────────────┐
│  学生端                                              │
│  index.html → index_v705.html                        │
│  ├── 闯关模式（年级/学期选择）                        │
│  ├── 爬塔送神桩 → tower.html（iframe）               │
│  └── 尖峰时刻 → ladder.html（iframe）                │
│  域名：xixitime.cn/kexvefuxi                         │
├──────────────────────────────────────────────────────┤
│  教师端                                              │
│  fenxi.html（成绩分析系统，1.96MB独立页面）            │
│  密码：ketan2026                                     │
│  域名：xixitime.cn/fenxi.html                        │
├──────────────────────────────────────────────────────┤
│  服务端                                              │
│  159.75.134.151, /data/api.py v706                   │
│  api.xixitime.cn / api.kexvefuxi.cn                  │
│  systemctl restart kexvefuxi-api                     │
├──────────────────────────────────────────────────────┤
│  CDN                                                 │
│  GitHub Pages → Cloudflare → 自定义域名               │
└──────────────────────────────────────────────────────┘
```

---

## 三、核心文件结构

```
D:\kexvefuxi\
├── index.html                  # Git LFS 追踪的大型入口页面
├── CNAME                       # kexvefuxi.cn
├── data/
│   ├── 3-2-lessons.js ~ 6-2-lessons.js  # 各年级题库
│   └── *.py                    # 题库处理脚本
├── 1/ ~ 6/                     # 各年级目录（25个HTML）
├── _kexvefuxi/                 # 子项目
│   ├── index_v705.html         # 🎮 主游戏页面（最活跃维护）
│   ├── tower.html              # 🏰 爬塔送神桩
│   ├── ladder.html             # ⚡ 尖峰时刻（天梯）
│   ├── fenxi.html              # 📊 成绩分析系统
│   └── cloud-config.js         # 云端配置
├── icons/                      # 图标资源（82个文件）
├── generated-assets/           # AI生成的素材
├── admin/                      # 管理后台
├── debug-tools/                # 调试工具（34个文件）
└── .workbuddy/                 # WorkBuddy 工作记忆
    └── memory/
        ├── MEMORY.md           # 长期记忆
        └── YYYY-MM-DD.md       # 每日日志
```

---

## 四、服务端 API（159.75.134.151, /data/api.py v706）

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/ranking/<grade>` | GET/POST | 排行榜 |
| `/api/student/<grade>/<studentId>` | GET/POST | 学生存档（v706智能合并） |
| `/api/student/info/<studentId>` | GET/POST | 学生错题信息 |
| `/api/students/batch` | POST | 批量学生同步 |
| `/api/questionbank/<grade>` | GET/POST | 题库存储 |
| `/api/ai-tutor` | POST | AI错题讲解 |
| `/api/ladder/ranking/score/<grade>` | GET | 天梯积分榜 |
| `/api/ladder/ranking/accuracy/<grade>` | GET | 天梯正确率榜 |
| `/api/ladder/ranking` | POST | 天梯提交排行 |
| `/api/ladder/profile/<studentId>` | GET | 天梯云存档读取 |
| `/api/ladder/profile` | POST | 天梯云存档保存 |

---

## 五、关键修复记录

### v706 云存档三大P0修复（2026-05-22）
1. **Bug 1（根因）**: 服务端 `data[key] = body` 直接覆盖 → 新增智能合并（Math.max/装备去重/成就并集/错题合并/零分守卫）
2. **Bug 2**: 统一 `.tmp` 并发竞态 → `os.replace()` + PID 隔离
3. **Bug 3**: 数据丢失 → 从 6 个 corrupted 备份恢复至 52 条，548名学生完整存档待学生重新登录从 localStorage 恢复

### 云合并策略
- `totalPoints`: `new==0 && cloud>0 ? cloud : new`（零分守卫，信任客户端）
- 装备去重、成就并集、错题合并

### 爬塔修复（2026-05-23）
- 死亡后禁止继续
- 初始攻击力 10→20
- 材料题显示（【材料】金色高亮 + 配图）
- 回血卡牌即时刷新
- CDN缓存刷新：URL版本号差异化

### 账号隔离
- 受影响函数：`loginWithId()`, `logout()`, `loginAsGuest()`
- 必须重置：wrongQuestions, towerHighestFloor, towerCoins, ladderBestScore 等
- commit: `26ab3b9`

---

## 六、Git 状态（2026-05-23）

| 项目 | 状态 |
|------|------|
| **最新提交** | `40f9d69`（回血卡牌修复） |
| **D盘当前** | `a134fb8` — 缺少 `40f9d69` |
| **待操作** | D盘项目需 `git pull` 拉取最新提交 |
| **BGM恢复提交** | `b2cbd2c`（如果已合并到main），可能是本地未推送 |

执行：
```bash
cd /d/kexvefuxi
git pull origin main
```

> 注：D盘项目已配置代理 `http://127.0.0.1:7897`，确保 Clash Verge 开启。

---

## 七、CDN 缓存刷新

GitHub Pages 不支持自定义 Cache-Control，需用 **URL 差异化** 破缓存：

1. 入口重定向加版本号：`index.html` → `index_v705.html?v=20260521`
2. 页面级 meta：`<meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate">`
3. 资源加版本号：`<script src="cloud-config.js?v=20260521">`
4. iframe 动态刷新：`src = 'tower.html?' + Date.now()`

每次重要部署后更新版本号日期。

---

## 八、已知问题（2026-05-23）

| 问题 | 状态 | 说明 |
|------|------|------|
| 学生完整存档丢失 | ⚠️ 恢复中 | 548名学生仅52人有完整存档，其余需重新登录从 localStorage 恢复 |
| D盘项目缺最新提交 | ⚠️ 待处理 | `git pull` 拉取 `40f9d69`（回血卡牌修复） |
| 材料题前10题无材料文本 | ✅ 正常 | 设计如此 |
| CDN缓存导致旧代码 | ⚠️ 需监控 | 部署后更新版本号日期 |

---

## 九、实用命令

```bash
# Git 推送（需代理）
cd /d/kexvefuxi
git pull origin main
# 修改后
git add .
git commit -m "描述"
git push origin main

# 服务端
ssh root@159.75.134.151
systemctl status kexvefuxi-api
systemctl restart kexvefuxi-api
tail -f /var/log/kexvefuxi-api.log
```

---

## 十、本地技能资源

WorkBuddy 已安装的项目技能：

| 技能名 | 用途 |
|--------|------|
| `kexvefuxi-project` | 项目开发、bug修复、功能添加 |
| `kexvefuxi-tower` | 爬塔系统开发 |
| `kexvefuxi-syntax-check` | JS语法错误诊断 |
| `git-deploy` | Git 推送部署 |
| `github-push-with-proxy` | GitHub推送代理管理 |
| `tencent-cloud-server` | 服务器管理 |
| `exam-to-question-bank` | 试卷转题库 |

---

*由 WorkBuddy 千寻整理，2026-05-23。如本文档与 MEMORY.md 有冲突，以 MEMORY.md 为准。*
