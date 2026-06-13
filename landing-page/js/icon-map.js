/**
 * 科学探险家 — 表情符号到 PNG 图标映射
 * 
 * 使用方式：
 *   <script src="js/icon-map.js"></script>
 *   然后用 iconImg('🔮', 24) 生成 <img> 标签
 *   或用 iconUrl('🔮') 获取图标URL
 * 
 * 图标来源：ComfyUI 生成 128×128 PNG（当前使用占位图标）
 * 图标目录：landing-page/icons/
 */

// Emoji → 图标文件名（不含扩展名）
var ICON_MAP = {
  // === UI 图标 (index.html) ===
  '🔮': 'icon_crystal',
  '🚀': 'icon_rocket',
  '🎒': 'icon_backpack',
  '👀': 'icon_eyes',
  '🎮': 'icon_controller',
  '📚': 'icon_books',
  '🗼': 'icon_tower',
  '🏆': 'icon_trophy',
  '📢': 'icon_megaphone',
  '🎯': 'icon_target',
  
  // === 登录页 (login.html) ===
  '👤': 'icon_avatar',
  
  // === 冒险大厅 (hub.html) ===
  '🧑‍🔬': 'icon_scientist',
  '⭐': 'icon_star',
  '🔥': 'icon_fire',
  '🐾': 'icon_paw',
  '🏅': 'icon_medal',
  '🎁': 'icon_gift',
  '📖': 'icon_notebook',
  '🧪': 'icon_test_tube',
  '⚗️': 'icon_alchemy',
  '📦': 'icon_box',
  '📋': 'icon_clipboard',
  '📝': 'icon_pencil',
  '✅': 'icon_check',
  '💡': 'icon_bulb',
  '🎉': 'icon_celebrate',
  '👍': 'icon_thumbsup',
  '💪': 'icon_muscle',
  '🔄': 'icon_refresh',
  '⇄': 'icon_exit',
  
  // === 装备图标 ===
  '🔍': 'equip_magnifier',
  '🔬': 'equip_microscope',
  '🌍': 'equip_globe',
  '🧲': 'equip_magnet',
  '🔋': 'equip_battery',
  '🌡️': 'equip_thermometer',
  '⚖️': 'equip_scales',
  '💎': 'equip_prism',
  '🔭': 'equip_telescope',
  '🧫': 'equip_tube',
  '🧭': 'equip_compass',
  '⚔️': 'equip_sword',
  '🏹': 'equip_bow',
  '🪄': 'equip_staff',
  '⚡': 'equip_wand',
  '🗡️': 'equip_dagger',
  '🔱': 'equip_spear',
  '🪖': 'equip_helmet',
  '🎩': 'equip_hat',
  '👑': 'equip_crown',
  '🛡️': 'equip_armor',
  '🥋': 'equip_robe',
  '👕': 'equip_cloth',
  '👖': 'equip_pants',
  '👗': 'equip_skirt',
  '🧤': 'equip_glove',
  '🥊': 'equip_gauntlet',
  '🧣': 'equip_cape',
  '🧥': 'equip_cloak',
  '🛡': 'equip_shield',
  '👢': 'equip_boot',
  '👟': 'equip_shoe',
  '👓': 'equip_glasses',
  '🎭': 'equip_mask',
  '🩹': 'equip_eyepatch',
  '👁️': 'equip_lens',
};

// 图标基础路径（相对路径，相对于引用此文件的HTML）
var ICON_BASE = 'icons/';

/**
 * 获取 emoji 对应的图标 URL
 * @param {string} emoji - 表情符号
 * @returns {string|null} 图标 URL，如果没有映射则返回 null
 */
function iconUrl(emoji) {
  var name = ICON_MAP[emoji];
  if (!name) return null;
  return ICON_BASE + name + '.png';
}

/**
 * 根据装备 typeId 获取装备图标 URL
 * @param {string} typeId - 装备类型ID（如 'sword', 'magnifier'）
 * @returns {string} 图标 URL
 */
function equipIconUrl(typeId) {
  if (!typeId) return ICON_BASE + 'equip_box.png';
  // Sanitize: strip all non-alphanumeric chars to prevent path issues
  var clean = String(typeId).replace(/[^a-zA-Z0-9_-]/g, '');
  if (!clean || clean.length > 30) clean = 'box';
  return ICON_BASE + 'equip_' + clean + '.png';
}

/**
 * 生成带 fallback 的图标 img 标签
 * 如果图标未加载成功，fallback 显示原始 emoji
 * 
 * @param {string} emoji - 表情符号
 * @param {number} [size] - 图标尺寸（px），默认 24
 * @param {string} [className] - 附加的 CSS class
 * @returns {string} HTML 字符串
 */
function iconImg(emoji, size, className) {
  size = size || 24;
  var cls = className ? ' ' + className : '';
  // Pure emoji mode — no PNG icons
  return '<span class="icon-emoji' + cls + '" style="font-size:' + size + 'px;line-height:1;display:inline-block;vertical-align:middle;">' + emoji + '</span>';
}

/**
 * 根据装备 typeId 生成装备图标 img 标签（带 fallback）
 * @param {string} typeId - 装备类型ID
 * @param {number} [size] - 图标尺寸
 * @param {string} [fallbackEmoji] - fallback emoji
 * @returns {string} HTML 字符串
 */
function equipImg(typeId, size, fallbackEmoji) {
  size = size || 32;
  var fb = fallbackEmoji || '🎒';
  // Pure emoji mode — no PNG icons
  return '<span style="font-size:' + size + 'px;line-height:1;display:inline-block;vertical-align:middle;">' + fb + '</span>';
}

/**
 * 用 PNG 图标替换容器内的所有 emoji
 * @param {HTMLElement} container - 容器元素
 * @param {number} [size] - 图标尺寸
 */
function replaceEmojiInContainer(container, size) {
  size = size || 24;
  if (!container) return;
  
  // 遍历所有文本节点，替换 emoji
  var walker = document.createTreeWalker(
    container,
    NodeFilter.SHOW_TEXT,
    null,
    false
  );
  
  var textNodes = [];
  while (walker.nextNode()) {
    textNodes.push(walker.currentNode);
  }
  
  textNodes.forEach(function(node) {
    var text = node.textContent;
    var hasEmoji = false;
    for (var emoji in ICON_MAP) {
      if (text.indexOf(emoji) !== -1) {
        hasEmoji = true;
        break;
      }
    }
    if (!hasEmoji) return;
    
    var html = text;
    for (var e in ICON_MAP) {
      html = html.split(e).join(iconImg(e, size));
    }
    
    var span = document.createElement('span');
    span.innerHTML = html;
    node.parentNode.replaceChild(span, node);
  });
}
