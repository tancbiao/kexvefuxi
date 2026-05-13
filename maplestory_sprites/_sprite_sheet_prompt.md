# 装备图标精灵图生成需求

## 技术规格

- **画布尺寸**: 1024 × 1536 像素
- **单元格**: 128 × 128 像素
- **网格**: 8列 × 12行 = 96个格子
- **网格线**: 每个格子之间用 1px 的 #cccccc 细线分隔（方便程序切割）
- **背景**: 纯白色 #FFFFFF
- **风格**: 冒险岛（MapleStory）风格的像素风装备图标，正面展示，带轻微阴影，色彩鲜艳
- **禁止**: 不要在图标上写任何文字、编号、标签

## 格子布局（从左到右，从上到下）

### 第0行 — 帽子（8个）
| 列 | 装备名 | 视觉描述 |
|----|--------|----------|
| 0,0 | 绿色力量头盔 | A green sci-fi helmet with visor, mechanical details |
| 0,1 | 花饰头巾 | A colorful floral bandana with flower patterns |
| 0,2 | 蓝色棒球帽 | A blue baseball cap with visor |
| 0,3 | 淑女粉帽 | A cute pink lady's hat with ribbon |
| 0,4 | 圣诞女孩帽 | A red Santa girl hat with white trim and pom-pom |
| 0,5 | 红色头巾 | A red bandana tied as headband |
| 0,6 | 夜色赛琳 | A dark elegant night-themed hat with star detail |
| 0,7 | 绿色巫师帽 | A green pointed wizard hat with brim |

### 第1行 — 帽子（8个）
| 列 | 装备名 | 视觉描述 |
|----|--------|----------|
| 1,0 | 翡翠圆帽 | A round emerald green cap, dome-shaped |
| 1,1 | 青铜维京盔 | A bronze Viking helmet with horns |
| 1,2 | 蓝色头巾 | A blue bandana tied as headband |
| 1,3 | 黑羽帽 | A black hat with feather decoration |
| 1,4 | 绿色宽松帽 | A loose-fitting green cap |
| 1,5 | 蓝色奏鸣曲 | An elegant blue musical-themed hat |
| 1,6 | 白夜狐 | A white fox-ear themed hat/cap |
| 1,7 | 蓝色下士帽 | A blue military corporal cap |

### 第2行 — 帽子(2) + 上衣(6)
| 列 | 装备名 | 视觉描述 |
|----|--------|----------|
| 2,0 | 绿色头巾 | A green bandana headband |
| 2,1 | 蓝色阿里克盔 | A blue Arlic-style helmet with visor |
| 2,2 | 复古校服外套 | An old-school blazer jacket, retro style |
| 2,3 | 皮皮黑指节背心 | A black knuckle vest with studded details |
| 2,4 | 橙色迪斯科衬衫 | An orange disco-style shirt, 70s vibe |
| 2,5 | 绿色训练服 | A green training uniform top |
| 2,6 | 紫色开衩衫 | A purple split-design top |
| 2,7 | 血色潜行服 | A blood-red sneaking suit, ninja style |

### 第3行 — 上衣（8个）
| 列 | 装备名 | 视觉描述 |
|----|--------|----------|
| 3,0 | 粉色连帽背心 | A pink hooded vest |
| 3,1 | 红色半衫 | A red half-jacket top |
| 3,2 | 蓝骷髅连帽背心 | A blue skull-pattern hooded vest |
| 3,3 | 特工上衣 | A sleek black agent/operative top |
| 3,4 | 蓝色水手上衣 | A blue sailor-style top |
| 3,5 | 柠檬清新衫 | A lemon-yellow fresh casual top |
| 3,6 | 泰迪野餐衬衫 | A cute teddy bear picnic shirt |
| 3,7 | 恶魔熊T恤 | A devil bear design T-shirt |

### 第4行 — 裤裙（8个）
| 列 | 装备名 | 视觉描述 |
|----|--------|----------|
| 4,0 | 赭色肩铠裤 | Ocher-colored pants with shoulder armor |
| 4,1 | 夏威夷裙 | A Hawaiian-style tropical skirt |
| 4,2 | 蓝色牛仔裙 | A blue denim skirt |
| 4,3 | 黑色布裤 | Plain black cloth pants |
| 4,4 | 红色爱莫莉亚裙 | A red elegant Amoria skirt |
| 4,5 | 红色暗影裤 | Red shadow-style pants |
| 4,6 | 蓝色月亮裤 | Blue moon-pattern pants |
| 4,7 | 斯特格曼实用裙MK2 | A utility skirt with tactical details |

### 第5行 — 裤裙(4) + 披风(4)
| 列 | 装备名 | 视觉描述 |
|----|--------|----------|
| 5,0 | 天津四裙 | A Deneb star-themed skirt |
| 5,1 | 偶像明星链裤 | Idol star chain-decorated pants |
| 5,2 | 异界休闲裤 | Otherworldly casual slacks |
| 5,3 | 真恶魔睡衣下装 | Demon pajama bottom, dark theme |
| 5,4 | 冒险岛披风 | A classic adventure cape |
| 5,5 | 圣诞披风 | A Christmas-themed red and white cape |
| 5,6 | 枫叶披风 | A maple leaf patterned cape |
| 5,7 | 狮心战斗披风 | A lionheart battle cape, majestic |

### 第6行 — 披风(1) + 脸饰(7)
| 列 | 装备名 | 视觉描述 |
|----|--------|----------|
| 6,0 | 童话披风 | A fairytale-themed magical mantle |
| 6,1 | 极道伤疤 | A yakuza-style facial scar accessory |
| 6,2 | 白眼阴郁脸饰 | White-eyed sullen face accessory |
| 6,3 | 紫色愤怒 | A purple rage expression face accessory |
| 6,4 | 不朽面具 | An immortal/ancient mask |
| 6,5 | 蓝色弓箭手标记 | A blue archer symbol face mark |
| 6,6 | 鲁道夫红鼻子 | Rudolph's red nose accessory |
| 6,7 | 前沿白口香糖 | A white bubble gum face accessory |

### 第7行 — 脸饰(2) + 眼饰(4)
| 列 | 装备名 | 视觉描述 |
|----|--------|----------|
| 7,0 | 灰色魔法师标记 | A gray magician meister symbol |
| 7,1 | 爱心纹身（鼻子） | A heart tattoo on nose |
| 7,2 | 太阳镜 | Classic sunglasses |
| 7,3 | 黑色眼罩 | A black eyepatch |
| 7,4 | 浣熊面具 | A raccoon-style eye mask |
| 7,5 | 暗黑追猎者眼饰 | A darkness chaser eye accessory |

### 第8-11行 — 留空（32个格子）
这些格子暂时留为纯白色背景（#FFFFFF），后续用于宠物和成就图标。

---

## 最终使用的英文 Prompt（可直接复制）

```
Generate a sprite sheet for game equipment icons.

Canvas: 1024x1536 pixels, white background (#FFFFFF).
Grid: 8 columns x 12 rows, each cell 128x128 pixels.
1px light gray (#cccccc) grid lines between cells for slicing.
Style: MapleStory-inspired pixel art game item icons, front-facing, vibrant colors, slight shadow beneath each item.
NO text, NO labels, NO numbers on any icon.

Layout (left to right, top to bottom):

ROW 0 (Hats): [0,0] Green sci-fi helmet with visor | [0,1] Colorful floral bandana | [0,2] Blue baseball cap | [0,3] Cute pink lady hat with ribbon | [0,4] Red Santa girl hat with white pom-pom | [0,5] Red bandana headband | [0,6] Dark elegant night hat with stars | [0,7] Green pointed wizard hat

ROW 1 (Hats): [1,0] Round emerald green dome cap | [1,1] Bronze Viking helmet with horns | [1,2] Blue bandana headband | [1,3] Black hat with feather | [1,4] Loose green cap | [1,5] Blue musical-themed elegant hat | [1,6] White fox-ear hat | [1,7] Blue military corporal cap

ROW 2 (Hats+Top): [2,0] Green bandana | [2,1] Blue helmet with visor | [2,2] Retro old-school blazer jacket | [2,3] Black studded knuckle vest | [2,4] Orange 70s disco shirt | [2,5] Green training uniform top | [2,6] Purple split-design top | [2,7] Blood-red ninja sneaking suit

ROW 3 (Tops): [3,0] Pink hooded vest | [3,1] Red half-jacket | [3,2] Blue skull hooded vest | [3,3] Sleek black agent top | [3,4] Blue sailor top | [3,5] Lemon-yellow casual top | [3,6] Teddy bear picnic shirt | [3,7] Devil bear T-shirt

ROW 4 (Bottoms): [4,0] Ocher pants with armor | [4,1] Hawaiian tropical skirt | [4,2] Blue denim skirt | [4,3] Black cloth pants | [4,4] Red elegant skirt | [4,5] Red shadow pants | [4,6] Blue moon-pattern pants | [4,7] Tactical utility skirt

ROW 5 (Bottoms+Capes): [5,0] Star-themed skirt | [5,1] Chain-decorated idol pants | [5,2] Otherworldly casual slacks | [5,3] Dark demon pajama bottom | [5,4] Classic adventure cape | [5,5] Red Christmas cape | [5,6] Maple leaf cape | [5,7] Majestic lionheart battle cape

ROW 6 (Cape+Faces): [6,0] Fairytale magical mantle | [6,1] Yakuza facial scar | [6,2] White-eyed sullen face accessory | [6,3] Purple rage face accessory | [6,4] Ancient immortal mask | [6,5] Blue archer symbol face mark | [6,6] Rudolph red nose | [6,7] White bubble gum face accessory

ROW 7 (Faces+Eyes): [7,0] Gray magician symbol | [7,1] Heart nose tattoo | [7,2] Classic sunglasses | [7,3] Black eyepatch | [7,4] Raccoon eye mask | [7,5] Darkness chaser eye accessory

ROWS 8-11 (32 cells): Leave as pure white background (#FFFFFF). These are reserved for future pet and achievement icons. Do NOT draw anything in these cells.

IMPORTANT:
- Each icon must be fully contained within its 128x128 cell, centered with padding
- Use 1px grid lines between all cells for programmatic slicing
- Absolutely NO text, words, letters, numbers, or labels on any icon
- Consistent lighting from top-left
- Each icon should be clearly recognizable as its described item
```

---

## 使用说明

1. 把上面的英文 Prompt 复制到 GPT/DALL-E 或 ComfyUI
2. 生成后得到 1024×1536 的精灵图
3. 我用脚本直接按 128×128 切割，文件名 = `{行}_{列}.png`
4. 按行列顺序自动映射到装备ID，无需手动调整
