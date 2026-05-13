// 图标映射配置 - 将 emoji 映射到 SVG 图标
const ICON_MAP = {
    // 核心图标
    '📚': 'book',
    '🏆': 'trophy',
    '👑': 'crown',
    '🎒': 'bag',
    '✅': 'check',
    '❌': 'cross',
    '✕': 'cross',
    '💡': 'lightbulb',
    '🌟': 'star',
    '🔥': 'fire',
    '⚡': 'lightning',
    '🎯': 'target',
    '🔬': 'microscope',

    // 年级图标
    '📗': 'book-green',
    '📘': 'book-blue',
    '📙': 'book-orange',
    '📕': 'book-red',

    // 学期图标
    '🌸': 'spring',
    '🍂': 'autumn',

    // 装备图标
    '🥛': 'pants',
    '👔': 'top',
    '🛡': 'shield',
    '🏹': 'sword',
    '⚔': 'battle',

    // 其他
    '🏅': 'medal',
    '🎉': 'party',
    '🎊': 'party',
    '🎁': 'gift',
    '🚀': 'rocket',
    '💥': 'fire',
    '📖': 'wrong-book',
    '👤': 'user',
    '🔄': 'refresh',

    // 连击/成就
    '💫': 'star',
    '⭐': 'star',
};

// 获取图标 URL
function getIconPath(iconName) {
    return `icons/${iconName}.svg`;
}

// 将 emoji 替换为 SVG 图标
function replaceEmojiWithIcon(text) {
    let result = text;
    for (const [emoji, iconName] of Object.entries(ICON_MAP)) {
        if (result.includes(emoji)) {
            const imgTag = `<img src="${getIconPath(iconName)}" class="icon-img" alt="${iconName}" />`;
            result = result.split(emoji).join(imgTag);
        }
    }
    return result;
}

// 创建图标元素
function createIconElement(iconName, size = 32) {
    const img = document.createElement('img');
    img.src = getIconPath(iconName);
    img.className = 'icon-img';
    img.style.width = size + 'px';
    img.style.height = size + 'px';
    img.alt = iconName;
    return img;
}

// 检查浏览器是否支持 emoji
function checkEmojiSupport() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.fillText('📚', 0, 10);
    const data = ctx.getImageData(0, 0, 10, 10).data;
    // 如果像素全为 0，说明 emoji 未渲染
    let sum = 0;
    for (let i = 0; i < data.length; i++) {
        sum += data[i];
    }
    return sum > 0;
}

// 自动替换页面中的 emoji
function autoReplaceEmojis() {
    if (checkEmojiSupport()) {
        console.log('Browser supports emoji, no replacement needed');
        return;
    }

    console.log('Browser does not support emoji, replacing with SVG icons');

    // 替换所有文本节点中的 emoji
    const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
        null,
        false
    );

    const textNodes = [];
    while (walker.nextNode()) {
        if (walker.currentNode.textContent.match(/[\u{1F300}-\u{1F9FF}]/u)) {
            textNodes.push(walker.currentNode);
        }
    }

    textNodes.forEach(node => {
        const newText = replaceEmojiWithIcon(node.textContent);
        if (newText !== node.textContent) {
            const span = document.createElement('span');
            span.innerHTML = newText;
            node.parentNode.replaceChild(span, node);
        }
    });
}

// 添加样式
const style = document.createElement('style');
style.textContent = `
    .icon-img {
        display: inline-block;
        vertical-align: middle;
        width: 1.2em;
        height: 1.2em;
        margin: 0 0.1em;
    }
    .grade-icon .icon-img,
    .sem-icon .icon-img {
        width: 100%;
        height: 100%;
    }
    .achievement-badge .icon-img {
        width: 28px;
        height: 28px;
    }
`;
document.head.appendChild(style);

// DOM 加载完成后执行
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', autoReplaceEmojis);
} else {
    autoReplaceEmojis();
}
