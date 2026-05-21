# 科学复习系统 - 长期记忆

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
- API：`api.xixitime.cn/api/ladder/*`（4端点，待服务器部署）
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

## 服务端云合并策略 — 关键修复记录
- **🔥 根因 BUGFIX_pet_points_cloud_sync**: 服务端 `/data/api.py` 对 `totalPoints` 使用 `Math.max(cloud, new)` 阻止了合法积分降低（如宠物消费）
- **修复后逻辑**: `new==0 && cloud>0 ? cloud : new` — 仅零分守卫，信任客户端数据
- **文件**: 服务器 `159.75.134.151` 上的 `/data/api.py`，需要 SSH 修改后重启 `systemctl restart kexvefuxi-api`
- **文档**: `_kexvefuxi/.workbuddy/BUGFIX_pet_points_cloud_sync.md`（调用链7步 + 代码对比 + 验证命令）
