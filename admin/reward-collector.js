/**
 * 科学复习系统 - 奖励领取模块
 * 
 * 使用方法：
 * 将此文件路径添加到各年级 index.html 中，
 * 在 <script src="..."> 之后添加:
 *   <script src="../../admin/reward-collector.js"></script>
 * 
 * 然后在 loadUserData() 函数末尾（在 .then() 回调末尾）添加调用：
 *   collectPendingRewards(gameState.studentId);
 * 
 * 文件位置：admin/reward-collector.js
 */

// 奖励标题定义（与 reward-manager.html 保持一致）
const REWARD_DEFINITIONS = {
  // 称号
  'title_legendary_1': { type: 'title', name: '👑 年级第一', icon: '👑', rarity: 'legendary', description: '年级总分第一名专属荣誉' },
  'title_legendary_2': { type: 'title', name: '🥈 年级第二', icon: '🥈', rarity: 'epic', description: '年级总分第二名专属荣誉' },
  'title_legendary_3': { type: 'title', name: '🥉 年级第三', icon: '🥉', rarity: 'epic', description: '年级总分第三名专属荣誉' },
  'title_epic_10': { type: 'title', name: '🌟 年级前十', icon: '🌟', rarity: 'epic', description: '年级总分前10名专属荣誉' },
  'title_class_1': { type: 'title', name: '🏆 班级冠军', icon: '🏆', rarity: 'rare', description: '班级总分第一名专属荣誉' },
  'title_class_2': { type: 'title', name: '🥇 班级亚军', icon: '🥇', rarity: 'rare', description: '班级总分第二名专属荣誉' },
  'title_class_3': { type: 'title', name: '🥉 班级季军', icon: '🥉', rarity: 'rare', description: '班级总分第三名专属荣誉' },
  'title_class_top': { type: 'title', name: '🎖️ 班级精英', icon: '🎖️', rarity: 'fine', description: '班级总分前5名专属荣誉' },
  'title_score_master': { type: 'title', name: '⭐ 学霸之星', icon: '⭐', rarity: 'fine', description: '90分以上学生专属荣誉' },
  'title_class_prefix': { type: 'title', name: '🏫 班级成员', icon: '🏫', rarity: 'common', description: '班级前缀匹配荣誉' },
  // 宠物
  'pet_dragon': { type: 'pet', name: '🐉 神龙宝宝', icon: '🐉', rarity: 'mythical' },
  'pet_phoenix': { type: 'pet', name: '🦅 凤凰雏鸟', icon: '🦅', rarity: 'mythical' },
  'pet_qilin': { type: 'pet', name: '🦄 麒麟幼崽', icon: '🦄', rarity: 'mythical' },
  'pet_white_tiger': { type: 'pet', name: '🐅 白虎幼崽', icon: '🐅', rarity: 'mythical' },
  'pet_black_tortoise': { type: 'pet', name: '🐢 玄武幼崽', icon: '🐢', rarity: 'mythical' },
};

// 已领取记录（防止重复发放）
const CLAIMED_KEY = 'scienceGameClaimedRewards';
const REWARDS_API = 'https://api.xixitime.cn/api/rewards';

/**
 * 领取待发放奖励（支持服务器API + localStorage 双模式）
 * @param {string} studentId - 学生学号
 * @param {Function} showNotification - 显示通知的回调函数 (title, icon, message)
 */
async function collectPendingRewards(studentId, showNotification) {
  if (!studentId || studentId === 'guest') return;
  
  try {
    let serverRewards = [];
    
    // 先从服务器API获取奖励
    try {
      const resp = await fetch(`${REWARDS_API}?studentId=${encodeURIComponent(studentId)}`, {
        cache: 'no-cache'
      });
      if (resp.ok) {
        const data = await resp.json();
        if (data.rewards && data.rewards.length > 0) {
          serverRewards = data.rewards;
        }
      }
    } catch (e) {
      console.log('[奖励领取] 服务器API不可用，仅使用本地奖励');
    }
    
    // 再读取本地待发放批次（兼容旧方式）
    const pendingRaw = localStorage.getItem('scienceGamePendingRewards');
    let localRewards = [];
    if (pendingRaw) {
      try {
        const batch = JSON.parse(pendingRaw);
        if (batch && batch.students) {
          const rec = batch.students.find(s => String(s.studentId) === String(studentId));
          if (rec) localRewards = rec.rewards || [];
        }
      } catch (e) {}
    }
    
    // 合并奖励（服务器 + 本地）
    const allRewards = [...serverRewards, ...localRewards];
    if (allRewards.length === 0) return;
    
    // 获取已领取记录
    const claimedRaw = localStorage.getItem(CLAIMED_KEY);
    const claimed = claimedRaw ? JSON.parse(claimedRaw) : {};
    
    // 过滤未领取的奖励（用 学号+奖励id 作为唯一键）
    const studentClaimKey = 's_' + studentId;
    if (!claimed[studentClaimKey]) claimed[studentClaimKey] = [];
    
    const newRewards = allRewards.filter(r => {
      const key = `${r.type}:${r.id}`;
      return !claimed[studentClaimKey].includes(key);
    });
    
    if (newRewards.length === 0) return;
    
    // 发放奖励
    const granted = [];
    
    newRewards.forEach(reward => {
      if (reward.type === 'title') {
        if (typeof gameState !== 'undefined' && gameState.unlockedAchievements) {
          const def = REWARD_DEFINITIONS[reward.id];
          if (def && !gameState.unlockedAchievements.includes(reward.id)) {
            gameState.unlockedAchievements.push(reward.id);
            granted.push({ type: 'title', id: reward.id, def });
          }
        }
      } else if (reward.type === 'equip') {
        if (typeof gameState !== 'undefined' && Array.isArray(gameState.equipment)) {
          const emptySlot = gameState.equipment.findIndex(e => e === null);
          if (emptySlot >= 0) {
            gameState.equipment[emptySlot] = {
              id: reward.id,
              obtainedAt: Date.now(),
              from: 'reward'
            };
            granted.push({ type: 'equip', id: reward.id });
          }
        }
      } else if (reward.type === 'pet') {
        if (typeof gameState !== 'undefined' && gameState.petSystem) {
          const petState = gameState.petSystem;
          if (!petState.unlockedPets) petState.unlockedPets = [];
          if (!petState.unlockedPets.includes(reward.id)) {
            petState.unlockedPets.push(reward.id);
            granted.push({ type: 'pet', id: reward.id });
          }
        }
      }
    });
    
    // 记录已领取
    newRewards.forEach(r => {
      claimed[studentClaimKey].push(`${r.type}:${r.id}`);
    });
    localStorage.setItem(CLAIMED_KEY, JSON.stringify(claimed));
    
    // 保存游戏数据
    if (typeof saveUserData === 'function') {
      saveUserData();
    }
    
    // 显示通知
    if (granted.length > 0) {
      const names = granted.map(g => {
        const def = REWARD_DEFINITIONS[g.id];
        return def ? def.name : g.id;
      }).join('、');
      
      const title = '🎁 恭喜获得奖励！';
      const icon = '🏆';
      const message = `你获得了：${names}`;
      
      if (typeof showNotification === 'function') {
        showNotification(title, icon, message);
      } else {
        showRewardNotification(title, icon, message);
      }
    }
    
    console.log('[奖励领取] 学号', studentId, '获得', granted.length, '个奖励');
    
  } catch (e) {
    console.error('[奖励领取] 错误:', e);
  }
}

// 显示奖励通知（可自定义样式）
function showRewardNotification(title, icon, message) {
  // 如果游戏系统有自定义通知，使用它
  if (typeof showAchievementUnlock === 'function') {
    showAchievementUnlock({
      name: title,
      icon: icon,
      description: message
    });
    return;
  }
  
  // 否则用浏览器通知
  if (Notification.permission === 'granted') {
    new Notification(title, { body: message, icon: '🎁' });
  } else if (Notification.permission !== 'denied') {
    Notification.requestPermission().then(perm => {
      if (perm === 'granted') {
        new Notification(title, { body: message, icon: '🎁' });
      }
    });
  }
  
  // 尝试在页面上显示
  let notif = document.getElementById('rewardNotification');
  if (!notif) {
    notif = document.createElement('div');
    notif.id = 'rewardNotification';
    notif.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: linear-gradient(135deg, #ffd700, #ff8c00);
      color: #1a1a2e;
      padding: 16px 24px;
      border-radius: 12px;
      font-weight: bold;
      z-index: 10000;
      box-shadow: 0 4px 20px rgba(255,215,0,0.4);
      animation: slideIn 0.3s ease;
      max-width: 300px;
    `;
    document.body.appendChild(notif);
  }
  
  notif.innerHTML = `<div style="font-size:2em;">${icon}</div><div>${title}</div><div style="font-size:0.8em;font-weight:normal;margin-top:4px;">${message}</div>`;
  notif.style.display = 'block';
  
  setTimeout(() => {
    notif.style.display = 'none';
  }, 5000);
}
