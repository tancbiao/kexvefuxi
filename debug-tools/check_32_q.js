const fs = require('fs');
const c = fs.readFileSync('C:/Users/tanc/Documents/WPSDrive/362543761/WPS云盘/谭政/科学复习系统/_kexvefuxi/3/2/index.html', 'utf8');
let depth = 0, i = c.indexOf('const questionData'), endi = i;
while (i < c.length) {
    if (c[i] === '{') depth++;
    else if (c[i] === '}') { depth--; if (depth === 0) { endi = i + 2; break; } }
    i++;
}
const jsonStart = c.indexOf('{', c.indexOf('const questionData'));
const jsonStr = c.substring(jsonStart, endi);
const data = JSON.parse(jsonStr);
const units = Object.keys(data);
console.log('单元数:', units.length, '个');
let total = 0, totalMedium = 0, totalHard = 0;
units.forEach(function(u) {
    const lessons = data[u].lessons;
    console.log(data[u].name, ':', lessons.length, '课');
    lessons.forEach(function(l) {
        total += (l.basic || []).length;
        totalMedium += (l.medium || []).length;
        totalHard += (l.hard || []).length;
    });
});
console.log('基础题:', total, '进阶题:', totalMedium, '挑战题:', totalHard);
