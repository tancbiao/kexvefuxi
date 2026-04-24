/**
 * 打乱题库选项顺序脚本 v2（纯字符串处理，不走 JSON）
 * - 打乱 A/B/C/D 选项顺序
 * - 更新 answer 索引
 * - 跳过包含"以上都"的题目
 * - 跳过判断题(tf)
 */
const fs = require('fs');
const path = require('path');

function shuffle(array) {
  const arr = [...array];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

// 从一道题的 JSON 字符串中提取信息
function parseQuestionBlock(str) {
  // 找到 opts 数组
  const optsMatch = str.match(/"opts":\s*\[([^\]]+)\]/);
  if (!optsMatch) return null;
  const optsStr = optsMatch[1];

  // 解析每个选项（处理中文引号）
  const opts = [];
  const optMatches = optsStr.matchAll(/"([^"]*)"/g);
  for (const m of optMatches) {
    opts.push(m[1]);
  }

  // 找 answer
  const answerMatch = str.match(/"answer":\s*(\d+|true|false)/);
  if (!answerMatch) return null;
  let answer = answerMatch[1];
  const isTrueFalse = answer === 'true' || answer === 'false';
  if (isTrueFalse) {
    return { type: 'tf', opts, answer: answer === 'true' };
  }
  answer = parseInt(answer);

  // 判断是否跳过
  const correctText = opts[answer];
  if (!correctText) return null;
  const skip = correctText.includes('以上都') || correctText.includes('以上各');
  if (skip) return { type: 'choice', opts, answer, skip: true };

  // 打乱
  const indexed = opts.map((text, idx) => ({ text, idx }));
  const shuffled = shuffle(indexed);
  const newAnswer = shuffled.findIndex(item => item.text === correctText);

  return { type: 'choice', opts: shuffled.map(s => s.text), answer: newAnswer, skip: false };
}

// 将处理后的题重建为 JSON 字符串（保留原始引号风格）
function rebuildQuestion(q) {
  const optsStr = q.opts.map(o => `"${o}"`).join(', ');
  const answerStr = typeof q.answer === 'boolean' ? q.answer : q.answer;
  return `{"type": "choice", "q": "${q.q || ''}", "opts": [${optsStr}], "answer": ${answerStr}, "hint": "${q.hint || ''}"}`;
}

// 处理判断题（不变）
function rebuildTfQuestion(str) {
  return str; // 原样返回
}

// 核心：用状态机遍历 JS 文件，找到每个 choice 题并处理
function processFile(filePath) {
  console.log(`\n处理文件: ${path.basename(filePath)}`);

  const content = fs.readFileSync(filePath, 'utf8');
  let result = '';
  let i = 0;
  let total = 0, shuffled = 0, skipped = 0;

  while (i < content.length) {
    // 找到下一个 {"type": "choice 开头的位置
    const choiceStart = content.indexOf('{"type": "choice"', i);
    if (choiceStart === -1) {
      result += content.substring(i);
      break;
    }

    // 找到这个对象的结束位置（匹配 {}）
    let brace = 0;
    let objStart = -1;
    let j = choiceStart;
    while (j < content.length) {
      if (content[j] === '{') {
        if (objStart === -1) objStart = j;
        brace++;
      } else if (content[j] === '}') {
        brace--;
        if (brace === 0 && objStart !== -1) {
          break;
        }
      }
      j++;
    }

    const objStr = content.substring(choiceStart, j + 1);
    const parsed = parseQuestionBlock(objStr);

    if (parsed && parsed.type === 'choice' && !parsed.skip) {
      total++;
      shuffled++;
      // 找到 q, opts, answer, hint 的位置并替换
      let newStr = objStr;

      // 替换 opts
      newStr = newStr.replace(/"opts":\s*\[([^\]]+)\]/, (m, oldOpts) => {
        return `"opts": [${parsed.opts.map(o => `"${o}"`).join(', ')}]`;
      });

      // 替换 answer
      newStr = newStr.replace(/"answer":\s*\d+/, `"answer": ${parsed.answer}`);

      result += content.substring(i, choiceStart) + newStr;
      i = j + 1;
    } else if (parsed && parsed.skip) {
      total++;
      skipped++;
      result += content.substring(i, j + 1);
      i = j + 1;
    } else {
      result += content.substring(i, choiceStart + 1);
      i = choiceStart + 1;
    }
  }

  fs.writeFileSync(filePath, result, 'utf8');
  console.log(`  ✅ 完成！共${total}选择题，打乱${shuffled}题，跳过${skipped}题`);
}

const dataDir = path.join(__dirname, '..', 'data');
const files = ['4-2.js', '5-2.js', '6-2.js'];

files.forEach(file => {
  const filePath = path.join(dataDir, file);
  if (fs.existsSync(filePath)) {
    processFile(filePath);
  }
});

console.log('\n🎉 全部处理完成！记得 git 提交推送。');
