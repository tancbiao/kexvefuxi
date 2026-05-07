const fs = require('fs');
const c = fs.readFileSync('C:/Users/tanc/Documents/WPSDrive/362543761/WPS云盘/谭政/科学复习系统/_kexvefuxi/5/2/index.html', 'utf8');

// 1. Find all </script> occurrences - check positions relative to script boundaries
const scriptEnds = [];
let pos = 0;
while ((pos = c.indexOf('</script>', pos)) !== -1) {
    scriptEnds.push({ pos, line: c.slice(0, pos).split('\n').length });
    pos++;
}
console.log('All </script> positions:');
scriptEnds.forEach(s => console.log(`  pos ${s.pos}, line ${s.line}`));

// 2. Check for </script with variations (case, whitespace)
const variations = ['</script>', '</Script>', '</SCRIPT>', '</script >', '</script\t>'];
variations.forEach(v => {
    const idx = c.indexOf(v);
    if (idx >= 0 && v !== '</script>') {
        console.log(`\nFound variant "${v}" at pos ${idx}`);
    }
});

// 3. Check for </sc + ript> pattern (split to avoid HTML parser detection)
const splitPattern = /<\/\s*script/gi;
let m;
while ((m = splitPattern.exec(c)) !== null) {
    console.log(`</script pattern at pos ${m.index}: "${c.slice(m.index, m.index + 20)}"`);
}

// 4. Check for any HTML comments inside script that might cause issues
const htmlComments = [];
let cp = 0;
while ((cp = c.indexOf('<!--', cp)) !== -1) {
    // Is this inside the inline script?
    const inlineStart = c.indexOf('<script>', c.indexOf('</script>') + 9) + 8;
    const inlineEnd = c.lastIndexOf('</script>');
    if (cp > inlineStart && cp < inlineEnd) {
        htmlComments.push({ pos: cp, line: c.slice(0, cp).split('\n').length, ctx: c.slice(cp, cp + 50) });
    }
    cp++;
}
console.log('\nHTML comments inside inline script:', htmlComments.length);
htmlComments.forEach(h => console.log(`  line ${h.line}: ${JSON.stringify(h.ctx)}`));

// 5. Check for template literals (backticks) that might contain </script>
const backtickPositions = [];
let bp = 0;
const inlineStart2 = c.indexOf('<script>', c.indexOf('</script>') + 9) + 8;
const inlineEnd2 = c.lastIndexOf('</script>');
const inlineSection = c.slice(inlineStart2, inlineEnd2);

while ((bp = inlineSection.indexOf('`', bp)) !== -1) {
    backtickPositions.push(bp + inlineStart2);
    bp++;
}
console.log('\nBacktick count in inline script:', backtickPositions.length);

// 6. Check for </ in string literals within questionData
const qdStart = c.indexOf('const questionData');
const qdEndMarker = c.indexOf('};', c.indexOf('const questionData') + 100);
// Find proper end of questionData object
let depth = 0;
let qdEnd = qdStart;
for (let i = qdStart; i < c.length; i++) {
    if (c[i] === '{') depth++;
    else if (c[i] === '}') {
        depth--;
        if (depth === 0) { qdEnd = i + 1; break; }
    }
}
const qdContent = c.slice(qdStart, qdEnd);
console.log('\nquestionData: pos', qdStart, 'to', qdEnd, ', length:', qdContent.length);

// Search for </ in questionData
const ltSlash = [];
let lsp = 0;
while ((lsp = qdContent.indexOf('</', lsp)) !== -1) {
    const ctx = qdContent.slice(Math.max(0, lsp - 10), lsp + 30);
    ltSlash.push({ pos: lsp + qdStart, line: c.slice(0, lsp + qdStart).split('\n').length, ctx });
    lsp++;
}
console.log('"</" occurrences in questionData:', ltSlash.length);
ltSlash.forEach(l => console.log(`  line ${l.line}: ${JSON.stringify(l.ctx)}`));

// 7. Most important: Check if the inline script has a syntax error that causes
//    the browser to stop parsing at UPLOAD_PASSWORD
// Let's extract and check with node
const inlineScript = c.slice(inlineStart2, inlineEnd2);
const tmpFile = 'C:/Users/tanc/Desktop/52_check.js';
fs.writeFileSync(tmpFile, inlineScript);
console.log('\nInline script written to', tmpFile, ', length:', inlineScript.length);
