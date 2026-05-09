/**
 * 暗黑装备生成器 - 核心逻辑
 * 科学复习系统装备掉落模块
 * 
 * 使用方式：
 *   const equip = generateEquipment(4);  // 生成一件稀有装备
 *   const rarity = getRandomRarity();     // 权重随机稀有度
 *   if (checkDrop(0.05)) { ... }         // 检查是否掉落（5%基础概率）
 */

// ==================== 稀有度定义 ====================
const EQUIP_RARITY = {
  1: { name: '普通', color: '#9e9e9e', multiplier: 1.01 },
  2: { name: '精致', color: '#4caf50', multiplier: 1.03 },
  3: { name: '良好', color: '#2196f3', multiplier: 1.06 },
  4: { name: '稀有', color: '#9c27b0', multiplier: 1.12 },
  5: { name: '史诗', color: '#e91e63', multiplier: 1.30 },
  6: { name: '传说', color: '#ffd700', multiplier: 2.00 },
  7: { name: '神话', color: '#ff6600', multiplier: 3.00 }
};

// 稀有度属性范围
const EQUIP_RARITY_SCALE = {
  1: { min: 1, max: 5 },
  2: { min: 3, max: 12 },
  3: { min: 6, max: 20 },
  4: { min: 12, max: 35 },
  5: { min: 25, max: 60 },
  6: { min: 50, max: 120 },
  7: { min: 80, max: 200 }
};

// ==================== 装备类型 ====================

// 🔬 科学宝物（12种）
const SCIENCE_TYPES = [
  { id: 'magnifier', name: '放大镜', icon: '🔍', slot: '宝物', mainStat: 'int', mainStat2: null, desc: '观察微观世界' },
  { id: 'microscope', name: '显微镜', icon: '🔬', slot: '宝物', mainStat: 'int', mainStat2: null, desc: '探索细胞结构' },
  { id: 'flask', name: '烧杯', icon: '🧪', slot: '宝物', mainStat: 'int', mainStat2: 'dex', desc: '化学反应容器' },
  { id: 'compass', name: '指南针', icon: '🧭', slot: '宝物', mainStat: 'dex', mainStat2: null, desc: '指引方向' },
  { id: 'telescope', name: '望远镜', icon: '🔭', slot: '宝物', mainStat: 'int', mainStat2: null, desc: '观测星空' },
  { id: 'tube', name: '试管', icon: '🧫', slot: '宝物', mainStat: 'dex', mainStat2: 'int', desc: '精确实验' },
  { id: 'globe', name: '地球仪', icon: '🌍', slot: '宝物', mainStat: 'int', mainStat2: 'str', desc: '了解地球' },
  { id: 'magnet', name: '磁铁', icon: '🧲', slot: '宝物', mainStat: 'str', mainStat2: null, desc: '探索磁性' },
  { id: 'battery', name: '电池', icon: '🔋', slot: '宝物', mainStat: 'int', mainStat2: 'str', desc: '储存电能' },
  { id: 'thermometer', name: '温度计', icon: '🌡️', slot: '宝物', mainStat: 'dex', mainStat2: null, desc: '测量温度' },
  { id: 'scales', name: '天平', icon: '⚖️', slot: '宝物', mainStat: 'int', mainStat2: null, desc: '精确称量' },
  { id: 'prism', name: '三棱镜', icon: '💎', slot: '宝物', mainStat: 'int', mainStat2: 'dex', desc: '分解光线' }
];

// ⚔️ 冒险岛风格装备（26种）
const MAPLE_TYPES = [
  { id: 'sword', name: '剑', icon: '⚔️', slot: '武器', mainStat: 'str', mainStat2: null, desc: '物理攻击' },
  { id: 'bow', name: '弓箭', icon: '🏹', slot: '武器', mainStat: 'dex', mainStat2: null, desc: '远程攻击' },
  { id: 'staff', name: '魔法杖', icon: '🪄', slot: '武器', mainStat: 'int', mainStat2: null, desc: '魔法攻击' },
  { id: 'wand', name: '魔杖', icon: '⚡', slot: '武器', mainStat: 'int', mainStat2: 'dex', desc: '魔法近战' },
  { id: 'dagger', name: '短剑', icon: '🗡️', slot: '武器', mainStat: 'dex', mainStat2: 'str', desc: '快速攻击' },
  { id: 'spear', name: '长矛', icon: '🔱', slot: '武器', mainStat: 'str', mainStat2: 'dex', desc: '穿刺攻击' },
  { id: 'helmet', name: '头盔', icon: '🪖', slot: '头盔', mainStat: 'str', mainStat2: null, desc: '防护头部' },
  { id: 'hat', name: '帽子', icon: '🎩', slot: '头盔', mainStat: 'int', mainStat2: 'dex', desc: '魔法防护' },
  { id: 'crown', name: '王冠', icon: '👑', slot: '头盔', mainStat: 'int', mainStat2: 'str', desc: '王者之冠' },
  { id: 'armor', name: '铠甲', icon: '🛡️', slot: '上衣', mainStat: 'str', mainStat2: null, desc: '物理防护' },
  { id: 'robe', name: '长袍', icon: '🥋', slot: '上衣', mainStat: 'int', mainStat2: null, desc: '魔法防护' },
  { id: 'cloth', name: '布衣', icon: '👕', slot: '上衣', mainStat: 'dex', mainStat2: 'int', desc: '轻便防护' },
  { id: 'pants', name: '长裤', icon: '👖', slot: '下装', mainStat: 'str', mainStat2: null, desc: '腿部防护' },
  { id: 'skirt', name: '短裙', icon: '👗', slot: '下装', mainStat: 'dex', mainStat2: null, desc: '轻便下身' },
  { id: 'glove', name: '手套', icon: '🧤', slot: '手套', mainStat: 'dex', mainStat2: null, desc: '提升命中' },
  { id: 'gauntlet', name: '护手', icon: '🥊', slot: '手套', mainStat: 'str', mainStat2: null, desc: '力量增强' },
  { id: 'cape', name: '披风', icon: '🧣', slot: '披风', mainStat: 'str', mainStat2: 'int', desc: '神秘披风' },
  { id: 'cloak', name: '斗篷', icon: '🧥', slot: '披风', mainStat: 'int', mainStat2: null, desc: '魔法斗篷' },
  { id: 'shield', name: '盾牌', icon: '🛡', slot: '盾牌', mainStat: 'str', mainStat2: null, desc: '物理格挡' },
  { id: 'orb', name: '魔法盾', icon: '🔮', slot: '盾牌', mainStat: 'int', mainStat2: null, desc: '魔法护盾' },
  { id: 'boot', name: '战靴', icon: '👢', slot: '鞋子', mainStat: 'str', mainStat2: null, desc: '力量移动' },
  { id: 'shoe', name: '轻鞋', icon: '👟', slot: '鞋子', mainStat: 'dex', mainStat2: null, desc: '速度提升' },
  { id: 'glasses', name: '眼镜', icon: '👓', slot: '脸饰', mainStat: 'int', mainStat2: null, desc: '观察辅助' },
  { id: 'mask', name: '面具', icon: '🎭', slot: '脸饰', mainStat: 'dex', mainStat2: 'str', desc: '神秘伪装' },
  { id: 'eyepatch', name: '眼罩', icon: '🩹', slot: '眼饰', mainStat: 'str', mainStat2: null, desc: '单眼视界' },
  { id: 'lens', name: '隐形眼镜', icon: '👁️', slot: '眼饰', mainStat: 'int', mainStat2: null, desc: '洞察一切' }
];

// 全部装备类型合并
const ALL_EQUIP_TYPES = [...SCIENCE_TYPES, ...MAPLE_TYPES];

// ==================== 掉落配置 ====================
const EQUIP_DROP_CONFIG = {
  baseChance: 0.05,
  rarityWeights: [50, 25, 15, 7, 2, 0.8, 0.2]
};

// ==================== 特殊词缀 ====================
const EQUIP_AFFIXES = {
  crit_rate: { name: '暴击率', effect: '+10%正确率', color: '#ff6b6b' },
  crit_dmg: { name: '暴击伤害', effect: '暴击×1.5倍积分', color: '#ff4500' },
  exp_bonus: { name: '经验加成', effect: '+20%积分', color: '#4ecdc4' },
  extra_hint: { name: '额外提示', effect: '+1提示次数', color: '#45b7d1' },
  skip_chance: { name: '跳过机会', effect: '5%跳过题目', color: '#96ceb4' },
  recover_life: { name: '生命恢复', effect: '答错恢复1题', color: '#ffeaa7' },
  combo_bonus: { name: '连击加成', effect: '连击+5%积分', color: '#dfe6e9' },
  treasure_hunter: { name: '寻宝猎人', effect: '掉率+3%', color: '#fdcb6e' },
  perfect_bonus: { name: '满分奖励', effect: '满分+50积分', color: '#e056fd' },
  hp_boost: { name: '生命强化', effect: 'HP+50', color: '#ef4444' },
  mp_boost: { name: '魔力强化', effect: 'MP+30', color: '#3b82f6' }
};

// ==================== 工具函数 ====================

/**
 * 随机整数 [min, max]
 */
function equipRand(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

/**
 * 权重随机选择稀有度（1-7）
 */
function getEquipRarity() {
  const weights = EQUIP_DROP_CONFIG.rarityWeights;
  const total = weights.reduce((s, v) => s + v, 0);
  let r = Math.random() * total;
  for (let i = 0; i < weights.length; i++) {
    r -= weights[i];
    if (r <= 0) return i + 1;
  }
  return 1;
}

/**
 * 检查是否掉落（传入基础掉落率，可叠加buff）
 * @param {number} baseChance - 基础掉落率（如 0.05 表示 5%）
 * @param {number} bonusChance - 额外加成（如装备的 treasure_hunter 词缀 +3%）
 */
function checkEquipDrop(baseChance, bonusChance) {
  return Math.random() < (baseChance + (bonusChance || 0));
}

// ==================== 核心生成函数 ====================

/**
 * 生成一件装备对象
 * @param {number} rarity - 稀有度 1-7（不传则随机）
 * @param {string} typeId - 指定装备类型（如 'sword'，不传则随机）
 * @returns {object} 装备对象
 */
function generateEquip(rarity, typeId) {
  rarity = rarity || getEquipRarity();
  
  // 选择类型
  let equipType;
  if (typeId) {
    equipType = ALL_EQUIP_TYPES.find(t => t.id === typeId);
  }
  if (!equipType) {
    equipType = ALL_EQUIP_TYPES[Math.floor(Math.random() * ALL_EQUIP_TYPES.length)];
  }
  
  const rarityInfo = EQUIP_RARITY[rarity];
  const scale = EQUIP_RARITY_SCALE[rarity];
  
  // 生成主属性值
  const mainVal = equipRand(scale.min, scale.max);
  let str = 0, dex = 0, int = 0;
  
  if (equipType.mainStat === 'str') str = mainVal;
  else if (equipType.mainStat === 'dex') dex = mainVal;
  else if (equipType.mainStat === 'int') int = mainVal;
  
  // 副属性
  if (equipType.mainStat2) {
    const minor = Math.floor(mainVal * 0.3);
    if (equipType.mainStat2 === 'str') str += minor;
    else if (equipType.mainStat2 === 'dex') dex += minor;
    else if (equipType.mainStat2 === 'int') int += minor;
  }
  
  // 稀有装备随机给少量其他属性
  if (rarity >= 4) {
    const others = ['str', 'dex', 'int'].filter(s =>
      s !== equipType.mainStat && s !== equipType.mainStat2
    );
    if (others.length > 0) {
      const bonusStat = others[Math.floor(Math.random() * others.length)];
      if (bonusStat === 'str') str += Math.floor(mainVal * 0.2);
      else if (bonusStat === 'dex') dex += Math.floor(mainVal * 0.2);
      else if (bonusStat === 'int') int += Math.floor(mainVal * 0.2);
    }
  }
  
  // HP/MP加成（史诗及以上）
  let hpBonus = 0, mpBonus = 0;
  if (rarity >= 5) {
    hpBonus = equipRand(10, 50);
    mpBonus = equipRand(5, 30);
  }
  if (rarity >= 7) {
    hpBonus += equipRand(20, 100);
    mpBonus += equipRand(10, 50);
  }
  
  const equip = {
    id: `${equipType.id}_${rarity}_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
    typeId: equipType.id,
    icon: equipType.icon,
    name: `${rarityInfo.name}的${equipType.name}`,
    type: equipType.name,
    slot: equipType.slot,
    rarity: rarity,
    rarityName: rarityInfo.name,
    rarityColor: rarityInfo.color,
    multiplier: rarityInfo.multiplier,
    desc: equipType.desc,
    str: str,
    dex: dex,
    int: int,
    hpBonus: hpBonus,
    mpBonus: mpBonus,
    timestamp: Date.now()
  };
  
  // 传说/神话附加随机词缀
  if (rarity >= 6) {
    const affixCount = rarity === 7 ? 4 : 2;
    const keys = Object.keys(EQUIP_AFFIXES);
    const chosen = [];
    while (chosen.length < affixCount) {
      const k = keys[Math.floor(Math.random() * keys.length)];
      if (!chosen.includes(k)) chosen.push(k);
    }
    equip.affixes = chosen.map(k => ({ id: k, ...EQUIP_AFFIXES[k] }));
  }
  
  return equip;
}

/**
 * 获取装备稀有度颜色（CSS颜色值）
 */
function getEquipRarityColor(rarity) {
  return EQUIP_RARITY[rarity] ? EQUIP_RARITY[rarity].color : '#9e9e9e';
}

/**
 * 获取装备稀有度名称
 */
function getEquipRarityName(rarity) {
  return EQUIP_RARITY[rarity] ? EQUIP_RARITY[rarity].name : '普通';
}

/**
 * 获取装备积分倍率
 */
function getEquipMultiplier(rarity) {
  return EQUIP_RARITY[rarity] ? EQUIP_RARITY[rarity].multiplier : 1.0;
}

/**
 * 获取装备稀有度边框CSS
 */
function getEquipRarityCSS(rarity) {
  const colors = {
    1: '#9e9e9e', 2: '#4caf50', 3: '#2196f3',
    4: '#9c27b0', 5: '#e91e63', 6: '#ffd700', 7: '#ff6600'
  };
  return colors[rarity] || '#9e9e9e';
}

/**
 * 生成装备掉落提示HTML（用于答题页的掉落弹窗）
 */
function genEquipDropHTML(equip) {
  let statsHtml = '';
  if (equip.str > 0) statsHtml += `<div style="color:#ff6b6b">💪 力量 +${equip.str}</div>`;
  if (equip.dex > 0) statsHtml += `<div style="color:#4ecdc4">🏃 敏捷 +${equip.dex}</div>`;
  if (equip.int > 0) statsHtml += `<div style="color:#a78bfa">🧠 智力 +${equip.int}</div>`;
  if (equip.hpBonus > 0) statsHtml += `<div style="color:#ef4444">❤️ HP +${equip.hpBonus}</div>`;
  if (equip.mpBonus > 0) statsHtml += `<div style="color:#3b82f6">💧 MP +${equip.mpBonus}</div>`;
  
  let affixesHtml = '';
  if (equip.affixes && equip.affixes.length > 0) {
    affixesHtml = '<div style="margin-top:6px;font-size:0.8em;color:#888;">' +
      equip.affixes.map(a => `<span style="color:${a.color}">✦ ${a.effect}</span>`).join(' · ') +
      '</div>';
  }
  
  return `
    <div style="text-align:center;">
      <div style="font-size:4em;margin:10px 0;"><img src="../../maplestory_sprites/${equip.typeId}_icon.png" style="width:64px;height:64px;vertical-align:middle;" onerror="this.style.display='none';this.nextElementSibling.style.display='inline'"><span style="display:none;font-size:2em">${equip.icon}</span></div>
      <div style="font-size:1.2em;font-weight:bold;color:${equip.rarityColor};">${equip.name}</div>
      <div style="color:#888;font-size:0.85em;margin-bottom:12px;">${equip.slot} · ${equip.multiplier.toFixed(2)}x 积分倍率</div>
      <div style="text-align:left;background:rgba(0,0,0,0.3);border-radius:8px;padding:10px;font-size:0.9em;">
        ${statsHtml}
      </div>
      ${affixesHtml}
    </div>
  `;
}
