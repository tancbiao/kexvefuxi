const fs = require('fs');
const c = fs.readFileSync('C:/Users/tanc/Documents/WPSDrive/362543761/WPS云盘/谭政/科学复习系统/_kexvefuxi/5/2/index.html', 'utf8');

// Extract inline script
const firstScriptEnd = c.indexOf('</script>');
const inlineScriptStart = c.indexOf('<script>', firstScriptEnd) + '<script>'.length;
const inlineScriptEnd = c.lastIndexOf('</script>');
const inline = c.slice(inlineScriptStart, inlineScriptEnd);

// Track brace depth at key positions
let depth = 0;
const checkpoints = [
    'DOMContentLoaded',
    'const UPLOAD_PASSWORD',
    'function showUploadPasswordPrompt',
    'function checkUploadPassword',
    '(function()', // IIFE
];

// Simple brace tracking (ignores strings/comments - rough but useful)
const lines = inline.split('\n');
let lineDepth = 0;
const depthMap = new Map();

for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    for (const ch of line) {
        if (ch === '{') lineDepth++;
        else if (ch === '}') lineDepth--;
    }
    
    for (const cp of checkpoints) {
        if (line.includes(cp)) {
            depthMap.set(cp, { line: i + 1, depth: lineDepth });
        }
    }
}

console.log('Brace depth at key positions:');
for (const [name, info] of depthMap) {
    console.log(`  ${name}: line ${info.line}, depth ${info.depth}`);
}

// Check overall brace balance
console.log('\nFinal brace depth:', lineDepth, lineDepth === 0 ? '✅ balanced' : '❌ UNBALANCED');

// Now let's do a more precise check: find where depth goes negative
depth = 0;
let maxDepth = 0;
let firstNegLine = -1;
for (let i = 0; i < lines.length; i++) {
    for (const ch of lines[i]) {
        if (ch === '{') { depth++; maxDepth = Math.max(maxDepth, depth); }
        else if (ch === '}') depth--;
    }
    if (depth < 0 && firstNegLine === -1) {
        firstNegLine = i + 1;
        console.log('\n⚠️ Depth went negative at line', i + 1, '(absolute', i + 1 + 1200, ')');
        console.log('Content:', lines[i].trim().slice(0, 100));
    }
}

console.log('\nMax depth:', maxDepth);

// Check what's around UPLOAD_PASSWORD more carefully
const upLine = depthMap.get('const UPLOAD_PASSWORD')?.line;
if (upLine) {
    console.log('\n=== Context around UPLOAD_PASSWORD (line ' + upLine + ') ===');
    for (let i = Math.max(0, upLine - 6); i <= Math.min(lines.length - 1, upLine + 5); i++) {
        // Calculate depth at this line
        let d = 0;
        for (let j = 0; j <= i; j++) {
            for (const ch of lines[j]) {
                if (ch === '{') d++;
                else if (ch === '}') d--;
            }
        }
        console.log(`  L${i+1} [depth:${d}] ${lines[i].trim().slice(0, 80)}`);
    }
}
