# 科学复习系统 - 长期记忆

## 项目位置（2026-05-23 更新）
- **主目录**: `D:\kexvefuxi\`（已从 WPS 云盘迁移）
- **旧路径（废弃）**: `C:\Users\tanc\Documents\WPSDrive\362543761\WPS云盘\谭政\科学复习系统\_kexvefuxi\`
- GitHub: `https://github.com/tancbiao/kexvefuxi` (branch: `main`)
- 服务端: 159.75.134.151, `/data/api.py` v706

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

## CDN/浏览器缓存刷新策略（2026-05-21 确认有效）
**问题**: GitHub Pages 部署后旧 JS/HTML 被浏览器长期缓存，学生用旧代码导致同步失败
**方案**（三层防护）:
1. **入口重定向加版本号**: `index.html` → `index_v705.html?v=20260521`（URL不同强制CDN回源）
2. **页面级 meta 标签**: `<meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate">`
3. **关键资源加版本号**: `<script src="cloud-config.js?v=20260521">`（每次改版更新日期）
4. **已有保护**: tower/ladder iframe 使用 `src = 'tower.html?' + Date.now()` 动态刷新

**关键认知**: GitHub Pages 不支持自定义 HTTP Cache-Control 头，只能靠 URL 差异化破缓存。每次重要部署后更新版本号日期即可。
