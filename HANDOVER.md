# 科学趣味闯关网站 · 交接文档

> 本文档由 WorkBuddy 生成，交接给本地 IMA 小龙虾维护。
> 日期：2026-04-22

---

## 一、GitHub 账号信息

| 项目 | 内容 |
|------|------|
| **GitHub 用户名** | `tancbiao` |
| **仓库名** | `kexvefuxi` |
| **仓库地址** | https://github.com/tancbiao/kexvefuxi |
| **部署分支** | `master` |
| **在线访问地址** | https://tancbiao.github.io/kexvefuxi |
| **自定义域名** | https://kexvefuxi.cn（CNAME 已配置） |

> ⚠️ GitHub 账号密码由用户谭政自行保管，如需 push 代码请让用户在本地操作或使用已配置好的 Git credential。

---

## 二、项目文件结构

本项目代码位于：`C:\Users\Administrator\Desktop\四2班科学\_kexvefuxi\`

```
kexvefuxi/
├── index.html              # 首页：年级/学期选择界面
├── CNAME                   # 自定义域名配置：kexvefuxi.cn
├── README.md               # 项目说明
├── data/
│   ├── 4-2.js              # 四年级下册题库数据（主力题库）
│   └── 6-2.js              # 六年级下册题库数据
├── css/                    # 公共样式
├── js/                     # 公共脚本
├── 4/
│   ├── 1/                  # 四年级上册（已上线）
│   └── 2/
│       ├── index.html      # 🎮 四年级下册·闯关模式（主要维护对象）
│       └── vs.html         # ⚔️ 四年级下册·对战模式
├── 5/                      # 五年级（结构预留，内容待填）
├── 6/
│   └── 2/                  # 六年级下册（已有题库）
└── ...
```

**重点文件**：`4/2/index.html` 是目前最活跃的文件，四年级下册闯关游戏。

---

## 三、四年级下册闯关游戏说明（4/2/index.html）

### 游戏结构

- **四个单元**：植物大观园 🌿 / 动物的需求 🦁 / 运动和力 🚗 / 太阳地球月球 🌙
- **三级难度**：基础（5题）→ 提升（5题）→ 挑战（3道综合题）
- **解锁机制**：第 N 单元的当前难度，需要第 N-1 单元完成同级难度才解锁
- **题型**：单选题、判断题、排序题、连连看

### 进度存储

使用 `localStorage`，key 为 `scienceGameState`，存储字段：

```js
{
  totalPoints: 0,
  unlockedAchievements: [],
  unitProgress: [0, 0, 0, 0]  // 每个单元完成的难度级别（0=未开始, 1=完成基础, 2=完成提升, 3=完成挑战）
}
```

### 成就系统（10个）

| ID | 名称 | 解锁条件 |
|----|------|---------|
| first_blood | 首战告捷 | 完成第一题 |
| streak_3 | 三连斩 | 连续答对3题 |
| streak_5 | 五福临门 | 连续答对5题 |
| no_hint | 独立思考 | 不使用提示通关 |
| perfect | 满分答卷 | 一次通关满分 |
| plant_master | 植物专家 | 完成植物单元全部三级难度 |
| animal_master | 动物专家 | 完成动物单元全部三级难度 |
| motion_master | 运动达人 | 完成运动单元全部三级难度 |
| space_master | 太空探索者 | 完成天文单元全部三级难度 |
| all_complete | 科学探险家 | 完成所有关卡 |

---

## 四、题库数据结构（data/4-2.js）

题库挂载在全局变量 `questionBank`，结构如下：

```js
questionBank = {
  1: {  // 单元编号（1~4）
    basic: [      // 基础难度，5道题
      {
        type: 'choice',      // 题型: choice / truefalse / sort / match
        question: '题目文字',
        options: ['A', 'B', 'C', 'D'],  // choice 题必填
        answer: 0,           // choice: 正确选项索引；truefalse: true/false
        hint: ['提示1', '提示2', '提示3'],  // 三级提示
        explanation: '解析文字'
      },
      // ...
    ],
    advance: [ /* 5道提升题 */ ],
    challenge: [ /* 3道挑战题 */ ]
  },
  2: { /* 单元2 */ },
  3: { /* 单元3 */ },
  4: { /* 单元4 */ }
}
```

**排序题（sort）**格式：
```js
{
  type: 'sort',
  question: '请将以下步骤排序',
  items: ['步骤A', '步骤B', '步骤C'],
  answer: [2, 0, 1],  // 正确顺序的索引
  hint: [...],
  explanation: '...'
}
```

**连连看（match）**格式：
```js
{
  type: 'match',
  question: '将左列与右列连线',
  leftItems: ['左1', '左2', '左3'],
  rightItems: ['右1', '右2', '右3'],
  answer: [[0,1], [1,0], [2,2]],  // [左索引, 右索引] 对应关系
  hint: [...],
  explanation: '...'
}
```

---

## 五、后续更新网站的操作流程

### 场景A：修改/新增题目

1. 打开 `data/4-2.js`
2. 找到对应单元和难度，按上面的数据结构格式增删改题目
3. 保存后，进行 Git 提交（见下方步骤）

### 场景B：修改游戏逻辑/界面

1. 打开 `4/2/index.html`（闯关模式）或 `4/2/vs.html`（对战模式）
2. 直接修改 HTML 文件内的 CSS / JS / HTML 结构
3. 用浏览器打开本地文件预览效果：`file:///C:/Users/Administrator/Desktop/四2班科学/_kexvefuxi/4/2/index.html`
4. 确认无误后 Git 提交

### 场景C：新增年级/学期

1. 在对应年级目录（如 `5/1/`）新建 `index.html`
2. 参照 `4/2/index.html` 的结构复制改造
3. 在 `data/` 目录创建对应的题库文件（如 `5-1.js`）
4. 修改根目录 `index.html`，在年级选择界面加上对应入口

### Git 提交流程（每次改完都要做）

```bash
cd C:\Users\Administrator\Desktop\四2班科学\_kexvefuxi
git add .
git commit -m "说明这次改了什么"
git push origin master
```

提交后约 1~2 分钟，GitHub Pages 自动更新上线，访问 https://tancbiao.github.io/kexvefuxi 即可看到最新版本。

> ⚠️ **注意**：当前有一处未提交的修改：`4/2/index.html`（修复了成就解锁后单元按钮消失的bug + 返回选关逻辑优化）。需要先执行一次 `git add . && git commit -m "fix: 修复成就解锁后单元消失问题" && git push` 把这次修复上线。

---

## 六、已知问题和注意事项

| 问题描述 | 状态 | 说明 |
|---------|------|------|
| 成就解锁后关卡选择单元按钮消失 | ✅ 已修复（待提交） | `showLevelSelect()` 新增 tab 状态同步，`renderLevelGrid()` 加防御性检查 |
| 结果页面完成挑战后难度不重置 | ✅ 已修复（待提交） | `finishQuiz()` 完成后自动重置难度为 `basic` |
| 结果页面只剩"返回选关"一个按钮 | ✅ 已调整 | 之前是"再闯一关 + 返回首页"，现已合并为"返回选关" |
| 排序题操作方式 | ✅ 已修复 | 改为单击交换，添加选中高亮 |
| 对战模式不支持 sort/match 题型 | ✅ 已修复 | 自动过滤这两种题型 |

---

## 七、教材背景信息

- **教材**：粤教粤科版（广东省地方教材）四年级下册科学
- **四个单元**：
  1. 植物大观园（叶、茎、根、花、果实、种子）
  2. 动物的需求（食物、栖息地、繁殖）
  3. 运动和力（参照物、摩擦力、弹力、重力）
  4. 太阳地球月球（昼夜、四季、月相）
- **使用场景**：广东江门小学四年级期末复习课

---

## 八、联系信息

- **项目负责人**：谭政（谭谭）
- **学校**：广东省江门市小学
- **GitHub 主页**：https://github.com/tancbiao

---

*文档由 WorkBuddy 整理，2026-04-22。如有疑问，查 git log 或直接问谭谭。*
