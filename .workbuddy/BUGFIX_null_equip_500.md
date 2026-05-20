# BUG修复：宠物系统购买后云同步 HTTP 500

## 问题描述
宠物系统购买物品扣减积分后，`saveUserData()` → `saveToCloud()` → `saveStudent()` → POST API 返回 **500 INTERNAL SERVER ERROR**。同步失败导致积分被"复原"（其实根本没存进去，本地刷新后从云端读到旧数据覆盖了新值）。

## 报错信息
```
POST https://api.xixitime.cn/api/student/grade_all/01210221 500 (INTERNAL SERVER ERROR)
```

## 根因分析

### 服务器端崩溃点
```
File "/data/api.py", line 160, in student
    eid = e.get('id', '')
          ^^^^^
AttributeError: 'NoneType' object has no attribute 'get'
```

### 调用链（完整）
```
1. pet-system.html line 1487: openGiftBox() → 扣积分 → notifyPointsChange()
2. pet-system.html line 1333: postMessage {type:'pet_points_change', points:reduced}
3. index_v705.html line 5363: gameState.totalPoints = reduced → saveUserData()
4. index_v705.html line 2908: equipment: gameState.equipment  // 含 null！
5. index_v705.html line 2927: saveToCloud() → saveStudent()
6. cloud-config.js line 68: POST /api/student/grade_all/{id}
7. ★ 服务端 api.py line 159-160: for e in new_equip: eid = e.get('id', '')
   → e 为 None（JSON null）时崩溃 → HTTP 500
```

### 根本原因
**客户端 `gameState.equipment` 是 100 格定长数组**，空槽用 `null` 填充（如 `[equip1, null, null, ..., equip3]`）。这些都是合法数据。

**服务器遍历时没有跳过 `None`**：
- `for e in new_equip:` → `e` = `None`
- `e.get('id', '')` → `AttributeError: 'NoneType' object has no attribute 'get'` → 500

### 为什么之前没发现？
- 以前小程序/爬塔获得的装备数量少，前几个槽全是有效装备，`null` 在后面
- 服务器遍历可能遇到 `null` 在中间时才崩溃
- 宠物系统频繁触发 `saveUserData()`（每次消费都同步），导致碰撞频率高

### 额外影响
- 服务器 500 错误 **每秒钟触发多次**（多个学生同时操作时）
- 所有学生的云同步都会被阻塞（共享 gunicorn worker）
- 这就是"为什么云同步一直失败"的真相——服务器在反复崩溃

## 修复方案

### 服务器端修复（立即）

**文件**: 服务器 `159.75.134.151` → `/data/api.py`
**位置**: line 158-163，装备合并块

**当前代码（有bug）**:
```python
# 合并装备：去重保留（以云端为准，新装备追加）
old_equip = existing.get('equipment', [])
new_equip = body.get('equipment', [])
if old_equip or new_equip:
    # 用 id 去重
    seen = {e.get('id', ''): e for e in old_equip if e.get('id')}
    for e in new_equip:
        eid = e.get('id', '')
        if eid and eid not in seen:
            seen[eid] = e
    body['equipment'] = list(seen.values())
```

**修复后代码**:
```python
# 合并装备：去重保留（以云端为准，新装备追加）
old_equip = existing.get('equipment', [])
new_equip = body.get('equipment', [])
if old_equip or new_equip:
    # 用 id 去重（跳过 None/null 装备）
    seen = {e.get('id', ''): e for e in old_equip if e is not None and e.get('id')}
    for e in new_equip:
        if e is None:  # 🆕 跳过空槽位
            continue
        eid = e.get('id', '')
        if eid and eid not in seen:
            seen[eid] = e
    body['equipment'] = list(seen.values())
```

**改动**: 仅加 2 处 None 检查（line 158 字典推导 + line 160 循环内）

### 客户端修复（建议，但非紧急）

**文件**: `1/1/index_v705.html` line 2908

```javascript
// 当前
equipment: gameState.equipment,

// 建议改为：发送前过滤掉 null
equipment: (gameState.equipment || []).filter(function(e) { return e !== null && e !== undefined; }),
```

这与 tower.html 的 `saveTowerToCloud()` (line 1075) 一致——tower 已经在发送前过滤了 null。

### 客户端过滤带来的好处
- 减小请求体大小（不用发 100 个 null）
- 减少服务器处理开销
- 防御性编程：客户端先清理，服务器再兜底

## 执行步骤

### 1. SSH 到服务器 159.75.134.151
```
ssh root@159.75.134.151
密码: sC,/{8v*!b9EQ2$
```

### 2. 备份旧版
```bash
cp /data/api.py /data/api.py.bak_v707_$(date +%Y%m%d_%H%M)
```

### 3. 修改文件
找到 line 158-163 的装备合并块，添加 None 检查：
- Line 158: `if e is not None and e.get('id')`
- Line 160: `if e is None: continue`

### 4. 重启服务
```bash
systemctl restart kexvefuxi-api
```

### 5. 验证
```bash
# 发送含 null 的装备数组，应返回 200 OK
curl -s -X POST 'https://api.xixitime.cn/api/student/grade_all/TEST_NULL_EQ' \
  -H 'Content-Type: application/json' \
  -d '{"studentId":"TEST_NULL_EQ","totalPoints":100,"equipment":[{"id":"eq001","name":"测试","rarity":1},null,null,{"id":"eq002","name":"测试2","rarity":3}]}'
# 预期: {"ok":true}
```

### 6. 清理测试数据
```bash
python3 -c "
import json
for f in ['students']:
    path = f'/data/kexvefuxi/{f}.json'
    data = json.load(open(path))
    if 'TEST_NULL_EQ' in data:
        del data['TEST_NULL_EQ']
        json.dump(data, open(path, 'w'), ensure_ascii=False, indent=2)
        print(f'Cleaned {f}')
"
```

## 影响范围
- **服务器**: 影响所有学生（不仅是宠物系统使用者）
- **症状**: 任何 `gameState.equipment` 含 null 的学生在云同步时都会触发 500
- **严重性**: 🔴 P0 — 完全阻断云存档功能

## 双重保护策略
1. **服务器端** ← 立即修复（兜底，防崩溃）
2. **客户端** ← 后续优化（减小请求体积 + 防御性编程）
