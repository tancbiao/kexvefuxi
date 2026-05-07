const fs = require('fs');
const c = fs.readFileSync('C:/Users/tanc/Documents/WPSDrive/362543761/WPS云盘/谭政/科学复习系统/_kexvefuxi/5/2/index.html', 'utf8');
const positions = [];
let p = 0;
while ((p = c.indexOf('UPLOAD_PASSWORD', p)) !== -1) {
    const line = c.slice(0, p).split('\n').length;
    positions.push({ pos: p, line, ctx: c.slice(Math.max(0, p-60), p+100) });
    p++;
}
console.log('UPLOAD_PASSWORD occurrences:', positions.length);
positions.forEach(x => console.log('Line ' + x.line + ': ' + x.ctx));