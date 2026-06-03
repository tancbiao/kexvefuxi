"""Patch index_v712.html with gift/synthesis system + v712 cloud changes"""
import re

with open('D:/kexvefuxi/1/1/index_v712.html', 'r', encoding='utf-8') as f:
    content = f.read()

patches = 0

# 1. Update title and PAGE_VERSION
content = content.replace(
    '<title>🔮 科学探险家 · 统一闯关系统 v710</title>',
    '<title>🔮 科学探险家 · 统一闯关系统 v712</title>'
)
content = content.replace(
    "var PAGE_VERSION = '20260603';",
    "var PAGE_VERSION = '20260603b';"
)
content = content.replace(
    '<!-- v710: 校队选拔推理测试 + v709: 天梯队位彩色徽章+爬塔换号隔离+共享月考题库+错题本AI讲解 -->',
    '<!-- v712: 装备赠送+亲密值+合成系统+纯云端存档; v710: 校队选拔推理测试 -->'
)
patches += 1

# 2. Add gift CSS before </style>
css_extra = """
/* ========== 礼物中心弹窗 (v712) ========== */
.gift-overlay,.synthesis-overlay,.intimacy-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.85); display: none; justify-content: center; align-items: center;
  z-index: 2100;
}
.gift-overlay.show,.synthesis-overlay.show,.intimacy-overlay.show { display: flex; }
.gift-card,.synthesis-card,.intimacy-card {
  background: linear-gradient(135deg,#2a2a4a,#1a1a2e);
  border-radius: 16px; padding: 20px 24px; max-width: 620px; width: 95%;
  max-height: 85vh; overflow-y: auto; border: 1px solid rgba(255,255,255,0.1);
}
.gift-header,.synthesis-header,.intimacy-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.gift-title,.synthesis-title,.intimacy-title { font-size: 1.2em; font-weight: 900; color: #ffd700; }
.gift-close,.synthesis-close,.intimacy-close {
  width: 32px; height: 32px; border-radius: 50%; border: none;
  background: rgba(255,255,255,0.1); color: #aaa; cursor: pointer; font-size: 1.1em;
}
.gift-close:hover,.synthesis-close:hover,.intimacy-close:hover { background: rgba(255,100,100,0.2); color: #ff6b6b; }
.gift-tabs,.intimacy-tabs { display: flex; gap: 8px; margin-bottom: 12px; }
.gift-tab,.intimacy-tab {
  padding: 6px 16px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.15);
  background: transparent; color: #aaa; cursor: pointer; font-size: 0.85em;
}
.gift-tab.active,.intimacy-tab.active { background: rgba(255,215,0,0.15); border-color: #ffd700; color: #ffd700; }
.gift-item {
  display: flex; align-items: center; gap: 12px; padding: 10px 12px;
  background: rgba(255,255,255,0.04); border-radius: 10px; margin-bottom: 8px;
  border: 1px solid rgba(255,255,255,0.06);
}
.gift-item-icon { font-size: 1.5em; min-width: 36px; text-align: center; }
.gift-item-info { flex: 1; min-width: 0; }
.gift-item-name { font-size: 0.9em; font-weight: 600; margin-bottom: 2px; }
.gift-item-from { font-size: 0.75em; color: #888; }
.gift-item-status { font-size: 0.75em; }
.gift-item-status.pending { color: #ff9800; }
.gift-item-status.accepted { color: #4caf50; }
.gift-item-status.revoked { color: #f44336; }
.gift-item-status.expired { color: #666; }
.gift-item-btns { display: flex; gap: 6px; flex-shrink: 0; }
.gift-btn {
  padding: 5px 12px; border-radius: 6px; border: none; cursor: pointer; font-size: 0.75em;
  color: #fff; white-space: nowrap;
}
.gift-btn-accept { background: rgba(76,175,80,0.5); }
.gift-btn-revoke { background: rgba(255,100,100,0.4); }
.gift-empty { text-align: center; color: #666; padding: 30px; }
.intimacy-friend {
  display: flex; align-items: center; gap: 12px; padding: 12px;
  background: rgba(255,255,255,0.04); border-radius: 10px; margin-bottom: 8px;
  border: 1px solid rgba(255,255,255,0.06);
}
.intimacy-friend-avatar { font-size: 1.8em; min-width: 40px; text-align: center; }
.intimacy-friend-info { flex: 1; min-width: 0; }
.intimacy-friend-name { font-size: 0.9em; font-weight: 600; }
.intimacy-friend-level { font-size: 0.75em; color: #ffd700; margin-bottom: 4px; }
.intimacy-friend-bar {
  height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden;
}
.intimacy-friend-bar-fill { height: 100%; background: linear-gradient(90deg,#ff9800,#ffd700); border-radius: 3px; transition: width 0.5s; }
.intimacy-friend-value { font-size: 0.7em; color: #888; margin-top: 2px; }
.intimacy-reward-btn {
  padding: 4px 10px; border-radius: 6px; border: 1px solid #ffd700;
  background: rgba(255,215,0,0.15); color: #ffd700; cursor: pointer; font-size: 0.7em; white-space: nowrap;
}
.intimacy-reward-btn.claimed { opacity: 0.4; cursor: not-allowed; }
.gift-send-modal {
  background: linear-gradient(135deg,#2a2a4a,#1a1a2e);
  border-radius: 16px; padding: 24px; max-width: 400px; width: 90%;
  border: 1px solid rgba(255,255,255,0.1); text-align: center;
}
.gift-send-preview { padding: 12px; background: rgba(255,255,255,0.04); border-radius: 8px; margin: 12px 0; }
.gift-send-preview-name { font-size: 1em; font-weight: 600; margin-bottom: 4px; }
.gift-send-input {
  width: 100%; padding: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2);
  background: rgba(0,0,0,0.3); color: #fff; font-size: 0.95em; text-align: center;
  box-sizing: border-box; margin-bottom: 8px;
}
.gift-send-input::placeholder { color: #666; }
.gift-send-cost { font-size: 0.8em; color: #ff9800; margin-bottom: 12px; }
.gift-send-btns { display: flex; gap: 8px; justify-content: center; }
.gift-send-btn {
  padding: 8px 24px; border-radius: 8px; border: none; cursor: pointer; font-size: 0.9em;
}
.gift-send-btn.confirm { background: rgba(255,215,0,0.3); color: #ffd700; }
.gift-send-btn.cancel { background: rgba(255,255,255,0.1); color: #aaa; }
.gift-badge {
  display: none; position: absolute; top: -4px; right: -4px;
  width: 8px; height: 8px; background: #f44336; border-radius: 50%;
}
.gift-badge.show { display: block; }
.gift-entry { position: relative; display: inline-flex; }
.synthesis-slots { display: flex; gap: 12px; justify-content: center; margin-bottom: 16px; flex-wrap: wrap; }
.synthesis-slot {
  width: 80px; height: 80px; border-radius: 12px; border: 2px dashed rgba(255,255,255,0.2);
  display: flex; align-items: center; justify-content: center; cursor: pointer;
  background: rgba(255,255,255,0.04); flex-direction: column;
}
.synthesis-slot.filled { border-style: solid; }
.synthesis-slot-icon { font-size: 1.8em; }
.synthesis-slot-name { font-size: 0.6em; color: #888; margin-top: 4px; max-width: 70px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.synthesis-arrow { display: flex; align-items: center; font-size: 1.5em; color: #ffd700; }
.synthesis-result {
  text-align: center; padding: 12px; background: rgba(255,215,0,0.05); border-radius: 8px;
  margin-bottom: 12px; border: 1px solid rgba(255,215,0,0.2);
}
.synthesis-result-title { font-size: 0.8em; color: #888; margin-bottom: 6px; }
.synthesis-result-icon { font-size: 2em; margin-bottom: 4px; }
.synthesis-result-name { font-size: 0.9em; font-weight: 600; }
.synthesis-rarity-filter { display: flex; gap: 4px; justify-content: center; margin-bottom: 12px; flex-wrap: wrap; }
.synthesis-rarity-opt {
  padding: 3px 10px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.15);
  background: transparent; color: #aaa; cursor: pointer; font-size: 0.7em;
}
.synthesis-rarity-opt.active { border-color: #ffd700; color: #ffd700; background: rgba(255,215,0,0.1); }
.synthesis-pick-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; max-height: 200px; overflow-y: auto; margin-bottom: 12px; }
.synthesis-pick-item {
  padding: 6px; border-radius: 6px; cursor: pointer; text-align: center;
  border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.03);
  font-size: 0.7em;
}
.synthesis-pick-item:hover { border-color: rgba(255,215,0,0.4); }
.synthesis-pick-item.selected { border-color: #ffd700; background: rgba(255,215,0,0.1); }
.synthesis-pick-item.in-slot { opacity: 0.4; pointer-events: none; }
.synthesis-btn {
  width: 100%; padding: 10px; border-radius: 10px; border: none; cursor: pointer;
  font-size: 0.95em; font-weight: 600; color: #000; margin-top: 8px;
}
.synthesis-btn.ready { background: linear-gradient(135deg,#ffd700,#ff9800); }
.synthesis-btn.disabled { background: rgba(255,255,255,0.1); color: #666; cursor: not-allowed; }
.synthesis-cost { font-size: 0.7em; color: #888; text-align: center; margin-top: 6px; }
.equip-detail-extras { display: flex; gap: 6px; margin-top: 8px; justify-content: center; }
.equip-detail-extras .bp-detail-btn { font-size: 0.75em; padding: 4px 10px; }
"""
content = content.replace('</style>', css_extra + '\n</style>')
patches += 1

# 3. Add HTML overlays before </body>
html_extra = """
<!-- 礼物中心弹窗 (v712) -->
<div class="gift-overlay" id="giftCenterOverlay">
  <div class="gift-card">
    <div class="gift-header">
      <div class="gift-title">💝 礼物中心 <span style="font-size:0.65em;color:#888;font-weight:normal;">该功能由 01200112 提出</span></div>
      <button class="gift-close" onclick="closeGiftCenter()">✕</button>
    </div>
    <div class="gift-tabs">
      <button class="gift-tab active" onclick="switchGiftTab('received',this)">📥 收到的礼物</button>
      <button class="gift-tab" onclick="switchGiftTab('sent',this)">📤 送出的礼物</button>
      <button class="gift-tab" onclick="switchGiftTab('intimacy',this)">💕 亲密好友</button>
    </div>
    <div id="giftTabContent"></div>
  </div>
</div>

<!-- 合成台弹窗 (v712) -->
<div class="synthesis-overlay" id="synthesisOverlay">
  <div class="synthesis-card">
    <div class="synthesis-header">
      <div class="synthesis-title">⚗️ 装备合成台</div>
      <button class="synthesis-close" onclick="closeSynthesis()">✕</button>
    </div>
    <div class="synthesis-slots" id="synthesisSlots">
      <div class="synthesis-slot" onclick="synthesisPickSlot(0)"><span style="color:#666;">槽位1</span></div>
      <div class="synthesis-arrow">→</div>
      <div class="synthesis-slot" onclick="synthesisPickSlot(1)"><span style="color:#666;">槽位2</span></div>
      <div class="synthesis-arrow">→</div>
      <div class="synthesis-slot" onclick="synthesisPickSlot(2)"><span style="color:#666;">槽位3</span></div>
      <div class="synthesis-arrow">=</div>
      <div class="synthesis-result" id="synthesisResult">
        <div class="synthesis-result-title">合成预览</div>
        <div style="color:#666;">放入3件同稀有度装备</div>
      </div>
    </div>
    <div class="synthesis-rarity-filter" id="synthesisRarityFilter"></div>
    <div id="synthesisPickGrid"></div>
    <button class="synthesis-btn disabled" id="synthesisBtn" onclick="executeSynthesis()">放入3件装备开始合成</button>
    <div class="synthesis-cost">💡 3件同稀有度装备 → 1件更高级装备（最高史诗）</div>
  </div>
</div>

<!-- 赠送确认弹窗 (v712) -->
<div class="gift-overlay" id="giftSendOverlay">
  <div class="gift-send-modal">
    <h3 style="color:#ffd700;margin-top:0;">🎁 赠送装备</h3>
    <div class="gift-send-preview" id="giftSendPreview"></div>
    <input type="text" class="gift-send-input" id="giftSendTarget" placeholder="输入接收方8位学号" maxlength="8">
    <div class="gift-send-cost">⚠️ 赠送消耗 <strong>50</strong> 积分</div>
    <div class="gift-send-btns">
      <button class="gift-send-btn confirm" onclick="confirmSendGift()">确认赠送</button>
      <button class="gift-send-btn cancel" onclick="closeGiftSend()">取消</button>
    </div>
  </div>
</div>

"""
content = content.replace('</body>', html_extra + '\n</body>')
patches += 1

# 4. Add gift/synthesis buttons to backpack actions
content = content.replace(
    '<div class="bp-action-btn" onclick="bpClear62()">🧹 清理</div>',
    '<div class="bp-action-btn" onclick="showSynthesis()">⚗️ 合成</div>\n          <div class="bp-action-btn" onclick="showGiftCenter()">💝 礼物</div>\n          <div class="bp-action-btn" onclick="bpClear62()">🧹 清理</div>'
)
patches += 1

# 5. Add gift button to status bar
content = content.replace(
    '<div class="status-item" id="backpackBtn" style="cursor:pointer;" onclick="showBackpack()">',
    '<div class="status-item gift-entry" id="giftBtn" style="cursor:pointer;display:none;" onclick="showGiftCenter()">\n      <span class="status-icon">💝</span>\n      <span>礼物</span>\n      <span class="gift-badge" id="giftBadge"></span>\n    </div>\n    <div class="status-item" id="backpackBtn" style="cursor:pointer;" onclick="showBackpack()">'
)
patches += 1

# 6. Update updateStatusBar to show gift button
content = content.replace(
    "document.getElementById('userBadge').textContent = gameState.isGuest ? '🚶 游客' : '👤 ' + displayName;",
    "document.getElementById('userBadge').textContent = gameState.isGuest ? '🚶 游客' : '👤 ' + displayName;\n  // v712: 礼物按钮\n  var giftBtn = document.getElementById('giftBtn');\n  if (giftBtn) { giftBtn.style.display = (!gameState.isGuest && gameState.studentId) ? 'inline-flex' : 'none'; }"
)
patches += 1

# 7. v712: saveUserData - remove localStorage write
old_save = """    lastUpdated: Date.now()
  };
  localStorage.setItem('scienceGame_user_' + gameState.studentId, JSON.stringify(data));
  saveToCloud(gameState.studentId, data);"""
new_save = """    lastUpdated: Date.now()
  };
  // v712: 纯云端存储，不再写 localStorage
  saveToCloud(gameState.studentId, data);"""
if old_save in content:
    content = content.replace(old_save, new_save)
    patches += 1
else:
    print("WARN: saveUserData pattern not found")

# 8. v712: applyUserData - remove saveUserData at end
old_apply = """  loadEquippedState62();
  saveUserData();
}"""
new_apply = """  loadEquippedState62();
  // v712: applyUserData 不触发 save（防循环）
}"""
if old_apply in content:
    content = content.replace(old_apply, new_apply)
    patches += 1
else:
    print("WARN: applyUserData pattern not found")

# Write result
with open('D:/kexvefuxi/1/1/index_v712.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Patches applied: {patches}')
print(f'File size: {len(content)} bytes, {len(content.splitlines())} lines')
