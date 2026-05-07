const fs = require('fs');
const c = fs.readFileSync('C:/Users/tanc/Documents/WPSDrive/362543761/WPS云盘/谭政/科学复习系统/_kexvefuxi/5/2/index.html', 'utf8');

console.log('uploadPwdOverlay found:', c.includes('uploadPwdOverlay'));
console.log('uploadPwdInput found:', c.includes('uploadPwdInput'));
const p = c.indexOf('uploadPwdOverlay');
console.log('uploadPwdOverlay pos:', p, 'line:', c.slice(0,p).split('\n').length);

if (p > 0) {
    // Check if it's inside a <script> tag or in HTML
    const before = c.slice(Math.max(0, p-100), p);
    const isInScript = before.includes('</script>');
    console.log('Is in script section:', isInScript);
    console.log('Context:', before.slice(-200));
    
    // Also check if id attribute exists
    const after = c.slice(p, p+200);
    console.log('After:', after);
}

// Check if the overlay HTML exists
const overlayPattern = /id="uploadPwdOverlay"/g;
const matches = [...c.matchAll(overlayPattern)];
console.log('\nid="uploadPwdOverlay" count:', matches.length);

// Find all element IDs
const idPattern = /id="(uploadPwd[^"]+)"/g;
const idMatches = [...c.matchAll(idPattern)];
console.log('\nAll uploadPwd IDs:');
idMatches.forEach(m => {
    const line = c.slice(0, m.index).split('\n').length;
    console.log('  line', line + ':', m[1]);
});