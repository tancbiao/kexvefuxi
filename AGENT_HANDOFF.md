# 科学趣味闯关网站 · AI Agent 交接指南

> 本文档用于指导后续 AI Agent 维护科学趣味闯关网站。

---

## 一、项目基本信息

| 项目 | 内容 |
|------|------|
| **GitHub 仓库** | https://github.com/tancbiao/kexvefuxi |
| **部署分支** | master |
| **在线地址** | https://kexvefuxi.cn |
| **本地代码路径** | `C:\Users\Administrator\Desktop\四2班科学\_kexvefuxi\` |

**维护重点**：`4/2/index.html`（四年级下册闯关游戏）

---

## 二、项目结构

```
kexvefuxi/
├── index.html          # 首页：年级/学期选择
├── data/
│   ├── 4-2.js          # 四年级下册题库（主力）
│   └── 6-2.js          # 六年级下册题库
├── 4/2/
│   ├── index.html       # 闯关模式
│   └── vs.html         # 对战模式
└── ...
```

---

## 三、题库格式（data/4-2.js）

题库挂载在全局变量 `questionBank`：

```javascript
questionBank = {
  1: {  // 单元编号 1-4
    basic: [      // 基础难度 5题
      {
        type: 'choice',           // 题型: choice / truefalse / sort / match
        question: '题目文字',
        options: ['A', 'B', 'C', 'D'],  // choice题必填
        answer: 0,                 // 正确选项索引
        hint: ['提示1', '提示2', '提示3'],  // 三级提示
        explanation: '解析'
      }
    ],
    advance: [ /* 5题 */ ],
    challenge: [ /* 3题 */ ]
  },
  2: { /* ... */ },
  3: { /* ... */ },
  4: { /* ... */ }
}
```

**排序题（sort）**：
```javascript
{
  type: 'sort',
  question: '请将以下步骤排序',
  items: ['步骤A', '步骤B', '步骤C'],
  answer: [2, 0, 1],  // 正确顺序的索引
  hint: [...],
  explanation: '...'
}
```

**连连看（match）**：
```javascript
{
  type: 'match',
  question: '将左列与右列连线',
  leftItems: ['左1', '左2', '左3'],
  rightItems: ['右1', '右2', '右3'],
  answer: [[0,1], [1,0], [2,2]],  // [左索引, 右索引] 配对
  hint: [...],
  explanation: '...'
}
```

---

## 四、Git 操作流程

```bash
cd C:\Users\Administrator\Desktop\四2班科学\_kexvefuxi
git add .
git commit -m "更新说明"
git push origin master
```

推送后约 1-2 分钟自动部署上线。

---

## 五、常见任务

### 1. 新增/修改题目
→ 直接编辑 `data/4-2.js`，按上方格式添加题库

### 2. 修改游戏逻辑
→ 编辑 `4/2/index.html`（闯关）或 `4/2/vs.html`（对战）

### 3. 本地预览
→ 用浏览器打开 `file:///C:/Users/Administrator/Desktop/四2班科学/_kexvefuxi/4/2/index.html`

### 4. 添加新单元/难度
→ 在 `questionBank` 中对应位置添加 `basic`/`advance`/`challenge` 数组

---

## 六、已知状态

- **今日修复（待提交）**：成就解锁后单元按钮消失的 bug

---

## 七、教材背景

- **教材**：粤教版四年级下册科学
- **四个单元**：
  1. 植物大观园
  2. 动物的需求
  3. 运动和力
  4. 太阳地球月球

---

> 有问题联系项目负责人谭政（谭谭）
