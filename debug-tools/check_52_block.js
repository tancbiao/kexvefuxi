const fs = require('fs');
const c = fs.readFileSync('C:/Users/tanc/Documents/WPSDrive/362543761/WPS云盘/谭政\科学复习系统\_kexvefuxi/5/2/index.html', 'utf8');

const firstScriptEnd = c.indexOf('</script>');
const inlineScriptStart = c.indexOf('<script>', firstScriptEnd) + '<script>'.length;
const inlineScriptEnd = c.lastIndexOf('</script>');
const inline = c.slice(inlineScriptStart, inlineScriptEnd);
const lines = inline.split('\n');

// Show context from DOMContentLoaded through checkUploadPassword
// to understand the block structure
console.log('=== Lines 3520-3600 with brace depth ===');
let d = 0;
for (let i = 0; i < 3520; i++) {
    for (const ch of lines[i]) {
        if (ch === '{') d++;
        else if (ch === '}') d--;
    }
}

for (let i = 3520; i < Math.min(lines.length, 3600); i++) {
    const prevD = d;
    for (const ch of lines[i]) {
        if (ch === '{') d++;
        else if (ch === '}') d--;
    }
    const trimmed = lines[i].trim().slice(0, 100);
    if (trimmed) {
        console.log(`L${i+1} [${prevD}→${d}] ${trimmed}`);
    }
}
