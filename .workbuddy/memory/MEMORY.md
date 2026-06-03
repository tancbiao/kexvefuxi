# 科学复习系统 - 长期记忆

## 环境限制（2026-05-27）
- **禁用 Microsoft Store**：谭谭的 Windows 打不开 Store，不要尝试用 `start ms-windows-store:` 或 winget 等会触发 Store 的操作
- 安装软件用 Chocolatey 或直接下载 exe/msi

## 项目位置（2026-05-23 更新）
- **主目录**: `D:\kexvefuxi\`（已从 WPS 云盘迁移）
- **旧路径（废弃）**: `C:\Users\tanc\Documents\WPSDrive\362543761\WPS云盘\谭政\科学复习系统\_kexvefuxi\`
- GitHub: `https://github.com/tancbiao/kexvefuxi` (branch: `main`)
- 服务端: 159.75.134.151, `/data/api.py` v706

## 域名备案（2026-05-24）
- 备案进行中，通过后云同步稳定性大幅提升

## 小程序备案（2026-05-24 建议）
- **域名备案 ≠ 小程序备案**，小程序需要单独备案
- 备案周期 1-3 周，现在就该开始
- 流程：小程序后台 → 设置 → 备案 → 填写信息 → 提交审核
- 需准备：营业执照（眼镜店）+ 身份证 + 小程序名称和简介
- 小程序名称建议和网站一致："西西时光" 或 "科学探险家"

## 防跨设备重复领取（2026-05-23 修复）
- 补偿/S0/连续登录等一次性标记已同步到云端（saveUserData/applyUserData）
- 连续登录追踪(loginStreakG6/G45)也同步云端
- 标记在云端/本地双重检查，换设备不会重复领取

## 云端同步容错（2026-05-23 新增）
- `saveToCloudWithRetry`: 3次重试 + 2s/4s递增退避
- `pendingCloudSync`: localStorage暂存失败数据，最多5条
- `flushPendingSync`: 登录5秒后+每次saveUserData自动刷新pending队列

## 账号隔离安全清单（2026-05-21 新增）
**受影响函数**: `loginWithId()`, `logout()`, `loginAsGuest()` — 修改时需同步更新三个函数
**必须重置的 gameState 字段**:
- `wrongQuestions`, `syncedWrongQuestions`, `cloudQBank`, `lastSyncTime`
- `totalQuestionsAnswered`, `totalCorrectAnswers`, `retrySuccessCount`
- `towerHighestFloor`, `towerCoins`, `ladderBestScore`
- `window._wrongQuestionsLoaded = false`（防止渲染缓存串号）
- 已有字段（原已重置）：totalPoints, lessonProgress, unlockedAchievements, equipment, equippedSlots, pets, petPieces, currentStreak, maxStreak
- 修复 commit: `26ab3b9`

## 天梯系统
- 路径：`_kexvefuxi/ladder.html`（与 tower.html 同级，~1878行）
- 风格：暗黑冒险岛（继承 tower.html CSS 体系）
- 题库：`data/3-2-lessons.js` ~ `6-2-lessons.js` 自动转换为 `{id, question, options, answer}` 格式
- 年级识别：`studentId.substring(2,4)` → 20=六,21=五,22=四,23=三
- 存储：localStorage + 云存储双写，智能合并取最大值
- API：`api.xixitime.cn/api/ladder/*`（4端点，✅ 2026-05-21 已部署）
  - `GET /api/ladder/ranking/score/<grade>` 积分榜
  - `GET /api/ladder/ranking/accuracy/<grade>` 正确率榜
  - `POST /api/ladder/ranking` 提交排行
  - 数据存储: `/data/kexvefuxi/rankings_ladder.json`
- **已实现**：登录页/首页/挑战页/结算页/排行榜/每日10次上限
- **✅ v705**: index_v705.html 添加"⚡尖峰时刻"按钮（"爬塔送神桩"旁边），iframe弹窗模式
- **✅ iframe模式**: ladder.html 支持 postMessage `init_ladder` 跳过登录，`ladder_change` 同步积分回主页面
- **✅ 积分算法修复**: `calcQuestionReward` 除以 `totalQuestions`，每题奖励 = 整局奖励 / 题数

## 成绩分析系统 (fenxi.html) — 2026-05-20 集成
- **路径**: `_kexvefuxi/fenxi.html`（1.96MB，独立页面，非iframe）
- **来源**: 从 tancbiao/score-analysis-system 迁移
- **功能**: 上传Excel成绩文件 → 多维度分析 → 导出质量报告 → 同步错题到复习系统
- **密码保护**: `ketan2026`，sessionStorage 记住验证状态
- **API 端点**（统一使用 api.xixitime.cn）:
  - `POST /api/students/batch` — 批量同步学生错题（v708新增）
  - `POST /api/questionbank/{grade}` — 同步题库（已有）
  - `GET /api/student/info/{sid}` — 拉取学生错题（已有）
- **依赖文件**: `template.docx`（27KB，质量报告模板）
- **同步函数**: `syncToReviewSystem()` (line ~43205), `syncStudents()` (line ~46472), `syncQuestions()` (line ~46437)
- **复习系统端**: `syncFromCloudData()` 在 index_v705.html line 2946，学生点击"成绩分析"拉取同步的错题
- **访问方式**: 教师直接访问 xixitime.cn/fenxi.html，输入密码后使用
- **✅ v2026-05-20**: loadQuestionBank() 适配新版题库模板（课程序号/题目/题型/选项A-D/正确答案/难度/备注/图表列），支持 DISPIMG 图片提取、材料题拆分（【材料名】前缀）、判断题答案标准化（√/×）、syncQuestions/syncToReviewSystem 携带 type 和 difficulty 字段。向下兼容旧版（题号列）。commit `e1b7dc6`
- **✅ v2026-05-20**: 同步显示修复 - syncToReviewSystem() answers默认值[]→{}、syncFromCloudData()题库匹配增强、判断答案T/F标准化、无题库明确提示。commit `e31d88c`
- **✅ v2026-05-21**: _parseXlsx()命题卷分析适配新版模板（课程序号/课程名称），列映射（题号从备注提取、选项A-D合并）。commit `9fb4652`

## 服务端 API 端点一览（159.75.134.151, /data/api.py）
| 端点 | 方法 | 说明 | 版本 |
|------|------|------|------|
| `/api/health` | GET | 健康检查 | - |
| `/api/ranking/<grade>` | GET/POST | 排行榜 | - |
| `/api/student/<grade>/<studentId>` | GET/POST | 学生存档 | - |
| `/api/student/info/<studentId>` | GET/POST | 学生错题信息 | v704 |
| `/api/students/batch` | POST | 批量学生同步 | v708 |
| `/api/questionbank/<grade>` | GET/POST | 题库存储 | v704 |
| `/api/ai-tutor` | POST | AI错题讲解 | v704 |
| `/api/ladder/ranking/score/<grade>` | GET | 天梯积分榜 | v705_ladder |
| `/api/ladder/ranking/accuracy/<grade>` | GET | 天梯正确率榜 | v705_ladder |
| `/api/ladder/ranking` | POST | 天梯提交排行 | v705_ladder |
| `/api/ladder/profile/<studentId>` | GET | 天梯云存档读取 | v705_profile |
| `/api/ladder/profile` | POST | 天梯云存档保存 | v705_profile |
| `/api/xuanba/save` | POST | 校队选拔保存结果 | v710 |
| `/api/xuanba/load/<sid>` | GET | 校队选拔加载历史 | v710 |
| `/api/xuanba/ranking` | GET | 校队选拔排行 | v710 |
| `/api/gift/send` | POST | 发起装备赠送 | v711 |
| `/api/gift/accept` | POST | 接受装备赠送 | v711 |
| `/api/gift/revoke` | POST | 撤回装备赠送 | v711 |
| `/api/gift/pending/<sid>` | GET | 查询待领取礼物 | v711 |
| `/api/gift/sent/<sid>` | GET | 查询已发送礼物 | v711 |
| `/api/intimacy/<sid>` | GET | 查询亲密关系 | v711 |
| `/api/intimacy/claim` | POST | 领取亲密等级奖励 | v711 |

## 装备赠送系统 (v711, 2026-06-03)
- **提出者**: 01200112
- **安全**: 接收方确认 + 24h撤回 + 每日限额(3件/天,同对1件) + 消耗50积分
- **亲密值**: 双向共享, 5等级(Lv1-Lv5), 带奖励
- **合成**: 3件同稀有度 → 1件高1级(最高史诗5级)
- **数据文件**: gifts_pending.json, gifts_history.json, intimacy.json
- **客户端**: 1/1/index.html 新增礼物中心弹窗+合成台弹窗

## _write_json 原子写入竞态修复（v705_ladder）
- **问题**: `.tmp` 统一命名 → 并发请求共享同一tmp → 第一个rename移走后第二个报 `FileNotFoundError: students.json.tmp`
- **修复**: `.tmp.{os.getpid()}` 按PID隔离 + `os.replace()` 替代 `shutil.move()`（POSIX原子rename）
- **文件**: 服务器 `/data/api.py`

## 服务端云合并策略 — 关键修复记录
- **🔥 根因 BUGFIX_pet_points_cloud_sync**: 服务端 `/data/api.py` 对 `totalPoints` 使用 `Math.max(cloud, new)` 阻止了合法积分降低（如宠物消费）
- **修复后逻辑**: `new==0 && cloud>0 ? cloud : new` — 仅零分守卫，信任客户端数据
- **文件**: 服务器 `159.75.134.151` 上的 `/data/api.py`，需要 SSH 修改后重启 `systemctl restart kexvefuxi-api`
- **文档**: `_kexvefuxi/.workbuddy/BUGFIX_pet_points_cloud_sync.md`（调用链7步 + 代码对比 + 验证命令）

## API v706 云存档Bug综合修复（2026-05-22）
**三大 P0 Bug 已修复并部署**:

### Bug 1: 服务端缺失智能合并（🔴 根因）
- **现象**: `student` 端点 `data[key] = body` 直接覆盖，无任何合并
- **影响**: 不同设备互相覆盖存档，数据一致性问题根源
- **修复**: 新增完整的 v706 智能合并逻辑（Math.max/装备去重/成就并集/错题合并/零分守卫）
- **文件**: `/data/api.py` (v706), commit 待推送

### Bug 2: _write_json_internal 竞态条件
- **现象**: 统一 `.tmp` + `shutil.move()` → 多 worker 并发 → FileNotFoundError → JSON 损坏
- **修复**: `os.replace()` + PID 隔离 (`tmp_path + '.' + str(os.getpid())`)
- **此前 v705_ladder 修复只改了 ladder 端点，未改 students 端点**

### Bug 3: 数据丢失恢复
- **现状**: students.json 仅 18→52 条记录，student_info.json 有 548 条（排名信息仍在）
- **恢复**: 从 6 个 corrupted 备份用 raw_decode 提取合并，恢复至 52 条
- **损失**: 大部分学生完整存档仍丢失（548 名学生有排名信息，但仅 52 人有完整存档）
- **补救**: 学生重新登录后将自动从 localStorage 恢复存档并上传（现有了智能合并保护）

### ✅ P1 修复 (commit `ad8d642`)
- **`applyUserData()` 末尾 `saveUserData(true)`** — skipCloud=true，仅保存 localStorage
- **`saveUserData(skipCloud)`** — 新增参数，调用方按需控制云端上传
- **双重上传消除**: `manualCloudDownload` 和 `loadUserData` 云合并流程不再因 applyUserData 触发额外 upload

### 发现但未修复的 P1 问题
- **`applyUserData()` 末尾调 `saveUserData()` → `saveToCloud()`** — 每次数据加载都触发云端写入
- **解决方案**: 将 `applyUserData` 末尾的 `saveUserData()` 调用改为仅保存 localStorage，不触发云端上传

### 数据规模参考
| 文件 | 条数 | 说明 |
|------|------|------|
| student_info.json | 548 | 学生姓名/班级/错题 |
| rankings_global_ranking.json | 190 | 排行榜摘要 |
| students.json | 52 | 完整游戏存档（曾丢失大量） |

## CDN/浏览器缓存刷新策略（2026-05-23 升级为自动跳转）
**之前（手动）**: 根 index.html 静态写死版本号 → 每次部署需手动更新 → 容易遗忘
**现在（自动双层跳转）**:
1. **根 index.html**: JS 动态获取当天日期作为版本号。`xixitime.cn` → 自动跳转 `?v=YYYYMMDD`，**不再需要手动改**
2. **index_v705.html**: 顶部 `PAGE_VERSION` 常量 + URL 自检脚本。学生旧书签 `?v=旧版本` → 自动重定向到新版本
3. **以后每次部署**: 只需更新 index_v705.html 顶部的 `PAGE_VERSION = 'YYYYMMDD'` 一个地方
4. **过渡期注意**: 已缓存旧版 index_v705 的浏览器需 Ctrl+F5 一次，之后永久自动
- tower/ladder iframe 已有 `Date.now()` 动态刷新
- 关键资源加版本号: `<script src="cloud-config.js?v=20260521">`

## 新项目：校对选拔（瑞文智商测试）（2026-06-03 已完成 v710）
- **名称**: "校队选拔"
- **页面**: `xuanba.html`（iframe弹窗模式，与tower/ladder一致）
- **题库**: `data/xuanba-questions.js`（60题，6等级×10题，固定种子）
- **生成脚本**: `generate_xuanba.js`（移植MIT开源rpm-iq-exam puzzleGenerator）
- **题目形式**: 3×3矩阵图形推理，6选项，纯SVG渲染（圆/方/三角/菱/十字/星）
- **测试限制**: 每人2次，保留最高分
- **API**: `/api/xuanba/save`, `/api/xuanba/load/<sid>`, `/api/xuanba/ranking`
- **入口**: index_v705.html status-bar → 🧠「校队选拔」按钮
- **服务端**: api.py v710 已部署，数据存 `/data/kexvefuxi/xuanba_results.json`

## 2026科技节专属装备（2026-06-03）
- 141件神话装备已生成，138名学生已匹配学号
- 装备数据: `data/keji2026-equips.js`
- 奖励批次: `admin/keji2026_rewards.json`
- 3名未匹配学生: 莫梓轩、黄梓玲、龚芷琪
- 发放机制: 登录时 + 打开背包时双重触发，localStorage防重复
