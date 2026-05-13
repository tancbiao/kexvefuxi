const fs = require('fs');
const c = fs.readFileSync('C:/Users/tanc/Documents/WPSDrive/362543761/WPS云盘/谭政/科学复习系统/_kexvefuxi/3/2/index.html', 'utf8');
let depth = 0;
const start = c.indexOf('const questionData');
let endi = start;
for (let i = start; i < c.length; i++) {
    if (c[i] === '{') depth++;
    else if (c[i] === '}') {
        depth--;
        if (depth === 0) { endi = i + 1; break; }
    }
}
console.log('JSON end position:', endi);
console.log('After JSON:');
console.log(c.slice(endi, endi + 500));
