# 科学复习系统 - 长期记忆

## 天梯系统 (ladder.html) ✅ 基本完成
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

## 服务端云合并策略 — 关键修复记录
- **🔥 根因 BUGFIX_pet_points_cloud_sync**: 服务端 `/data/api.py` 对 `totalPoints` 使用 `Math.max(cloud, new)` 阻止了合法积分降低（如宠物消费）
- **修复后逻辑**: `new==0 && cloud>0 ? cloud : new` — 仅零分守卫，信任客户端数据
- **文件**: 服务器 `159.75.134.151` 上的 `/data/api.py`，需要 SSH 修改后重启 `systemctl restart kexvefuxi-api`
- **文档**: `_kexvefuxi/.workbuddy/BUGFIX_pet_points_cloud_sync.md`（调用链7步 + 代码对比 + 验证命令）
