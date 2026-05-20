# BUG修复：宠物抽取后云存档恢复积分

## 问题描述
用户在宠物系统（pet-system.html iframe）中抽取宠物消耗积分后，积分被正确扣减，但云存档同步后又恢复到扣减前的最高分。

## 根因分析

### 完整调用链

```
1. 用户在 pet-system.html 抽取宠物 → gameState.points -= cost
2. pet-system.html line 1487: notifyPointsChange(gameState.points)
   → postMessage({type:'pet_points_change', points: reducedPoints}) 到父页面
3. index_v705.html line 5360-5364:
   gameState.totalPoints = Math.max(0, e.data.points);  // ✅ 正确设为扣减后的值
   saveUserData();  // ❌ 这里触发了云同步，但服务端拒绝接受降低的积分
4. saveUserData() line 2893-2929:
   → localStorage.setItem(...)  // ✅ 本地写入成功
   → saveToCloud(studentId, data)  // ❌ 见下一步
5. cloud-config.js line 66-75: saveStudent() → POST /api/student/grade_all/{id}
6. ★ 服务端 /data/api.py v705 "智能合并":
   totalPoints = Math.max(cloudData.totalPoints, newData.totalPoints)
   → 云端有 1000 分，新数据是 800 分 → Math.max = 1000 → 云端保留了旧高分！
7. 下次 loadUserData() 从云端拉取 → 积分回到 1000
```

### 罪魁祸首
**服务端 /data/api.py 的 v705 "智能合并"逻辑**。该逻辑对 `totalPoints` 使用 `Math.max(云端, 新值)`，原本是为了防止"学生登录新设备本地积分为 0 时覆盖云端高分"的 bug（零分守卫）。但这个保护太粗暴——它阻止了**所有**积分降低，包括宠物消费这种合法降低。

## 修复方案

### 方案A（推荐）：修改服务端总积分合并策略

**文件**: 服务器 `/data/api.py`，POST /api/student/<grade>/<studentId> 端点

**当前逻辑（有bug）**:
```python
# 数值字段取 max(云端, 新值) — 太粗暴！
totalPoints = max(cloudData.get('totalPoints', 0), newData.get('totalPoints', 0))
```

**修复后逻辑**:
```python
# 只保护 0 分覆盖的情况，允许合法降低（如宠物消费）
cloud_pts = cloudData.get('totalPoints', 0)
new_pts = newData.get('totalPoints', 0)
if new_pts == 0 and cloud_pts > 0:
    totalPoints = cloud_pts  # 零分守卫：拒绝 0 分覆盖
else:
    totalPoints = new_pts  # 信任客户端数据（含合法增减）
```

**原则**: 客户端是积分的唯一权威来源。服务端只防御一种明确异常：云端已有高分但客户端传来 0 分。

### 方案B（备选）：客户端加标记

在 `pet_points_change` handler 中发送时附带标记 `spendSource: 'pet'`，服务端识别此标记后跳过 Math.max 保护。

但这个方案复杂且易出错，不推荐。

## 需要修改的文件

### 1. 服务器端 (SSH 到 159.75.134.151)
- 文件: `/data/api.py` — 修改 POST /api/student 端点的 totalPoints 合并逻辑
- 备份: 修改前先 `cp /data/api.py /data/api.py.bak_v706_$(date +%Y%m%d)`
- 重启: `systemctl restart kexvefuxi-api`
- 验证: 
  ```bash
  # 测试：云端有 1000 分，POST 800 分 → 应接受 800（非 Math.max!）
  curl -s -X POST https://api.xixitime.cn/api/student/grade_all/TEST_STUDENT \
    -H 'Content-Type: application/json' \
    -d '{"totalPoints":800}' | python3 -m json.tool
  ```

### 2. 客户端 (可选，建议同步改)
- 文件: `_kexvefuxi/1/1/index_v705.html`
- 位置: line 5360-5365 (`pet_points_change` handler)
- 当前代码已正确，但可加一条 `showToast` 让用户感知同步状态：
  ```javascript
  if (e.data.type === 'pet_points_change') {
    gameState.totalPoints = Math.max(0, e.data.points);
    document.getElementById('petModalPoints').textContent = gameState.totalPoints.toLocaleString();
    updateStatusBar();
    saveUserData();
    showToast('积分已同步: ' + gameState.totalPoints.toLocaleString(), 'info', 2000);
  }
  ```

## 其他数值字段是否需要同样修改？

检查服务端 API 中对以下字段是否也有 `Math.max` 保护：
- `towerHighestFloor` — 应该保留 Math.max（爬塔只增不减）✅
- `towerCoins` — 爬塔币只增不减？如果宠物系统也会消费爬塔币，需要同样修改 ⚠️
- `totalQuestionsAnswered` — 只增不减 ✅
- `totalCorrectAnswers` — 只增不减 ✅
- `dailyStamina` — 应该信任客户端（体力消耗是正常的）⚠️

## SSH 连接信息
- 服务器: 159.75.134.151
- API 路径: /data/api.py
- 服务名: kexvefuxi-api
- 防火墙: 5000/443 端口，重启后需手动添加规则
- 数据目录: /data/kexvefuxi/*.json
