const fs = require('fs');
const c = fs.readFileSync('C:/Users/tanc/Documents/WPSDrive/362543761/WPS云盘/谭政/科学复习系统/_kexvefuxi/5/2/index.html', 'utf8');

// Extract only the inline script
const firstEnd = c.indexOf('</script>'); // 42816
const inlineStart = c.indexOf('<script>', firstEnd) + '<script>'.length; // 42829
const inlineEnd = c.lastIndexOf('</script>'); // 211892
const inlineScript = c.slice(inlineStart, inlineEnd);

// Write to file for syntax check
fs.writeFileSync('C:/Users/tanc/Desktop/52_inline_only.js', inlineScript);
console.log('Inline script length:', inlineScript.length);

// Also extract equipment-gen.js referenced position
const eqEnd = c.indexOf('</script>'); // pos 42816
const eqStart = c.indexOf('<script', eqEnd - 100); // look back for opening <script>
console.log('equipment-gen.js script tag:');
console.log(c.slice(Math.max(0, eqStart - 50), eqEnd + 20));

// Check if there's a <style> or other <script> inside the inline script
const inlineSection = c.slice(inlineStart, inlineEnd);
const styleInScript = inlineSection.match(/<style[^>]*>/g);
const scriptInScript = inlineSection.match(/<script/g);
console.log('\n<style> in inline script:', styleInScript ? styleInScript.length : 0);
console.log('<script> in inline script:', scriptInScript ? scriptInScript.length : 0);

// Check for unescaped </ inside string literals - look for patterns
// that might confuse the HTML parser but not JS parser
// Specifically look for any "question text" that might contain HTML-like content
const qdMatch = c.match(/const questionData\s*=\s*\{/);
if (qdMatch) {
    const qdStart = qdMatch.index + qdMatch[0].length;
    // Find the matching } for this const
    let depth = 0;
    let endPos = qdStart;
    for (let i = qdStart; i < c.length; i++) {
        if (c[i] === '{') depth++;
        else if (c[i] === '}') {
            depth--;
            if (depth === 0) { endPos = i + 1; break; }
        }
    }
    const qdContent = c.slice(qdMatch.index, endPos);
    console.log('\nquestionData length:', qdContent.length);
    
    // Check if it contains any HTML script-like content
    const scriptLike = qdContent.match(/<script|<\/script>/gi);
    console.log('HTML script-like content in questionData:', scriptLike ? scriptLike.length : 0);
    if (scriptLike) {
        scriptLike.forEach((m, i) => {
            const pos = qdContent.indexOf(m, i > 0 ? qdContent.indexOf(m) + 1 : 0);
            console.log(`  ${i+1}. ${m} at pos ${pos}`);
        });
    }
}