const fs = require('fs');
const c = fs.readFileSync('C:/Users/tanc/Documents/WPSDrive/362543761/WPS云盘/谭政/科学复习系统/_kexvefuxi/5/2/index.html', 'utf8');

// Check if questionData has parse issues near UPLOAD_PASSWORD position
// UPLOAD_PASSWORD is at pos 209762
// Check the structure around it
console.log('Context around UPLOAD_PASSWORD (pos 209762):');
console.log(c.slice(209600, 209900));
console.log('\n---\n');

// Look for any syntax issues before UPLOAD_PASSWORD
// Check the line/char count near this position
const lines = c.slice(0, 209762).split('\n');
console.log(`Line count at UPLOAD_PASSWORD: ${lines.length} lines`);
console.log(`Last 3 lines before UPLOAD_PASSWORD:`);
for (let i = Math.max(0, lines.length-4); i < lines.length; i++) {
    console.log(`L${i+1}: ${lines[i]}`);
}

// Check: is there any </script> or premature script end before UPLOAD_PASSWORD?
const headSection = c.slice(0, 209762);
const scriptEndTags = [...headSection.matchAll(/<\/script>/g)];
console.log(`\n</script> tags before UPLOAD_PASSWORD (pos 209762): ${scriptEndTags.length}`);
scriptEndTags.forEach(m => {
    const lineNum = c.slice(0, m.index).split('\n').length;
    console.log(`  pos ${m.index} (line ~${lineNum}): ${c.slice(Math.max(0,m.index-60), m.index+80)}`);
});

// Check document.readyState workaround
if (c.includes('DOMContentLoaded')) {
    const dcPos = c.indexOf('DOMContentLoaded');
    const lines2 = c.slice(0, dcPos).split('\n');
    console.log(`\nDOMContentLoaded at line ${lines2.length}:`);
    console.log(c.slice(dcPos-100, dcPos+200));
}

// Check equipment-gen.js loading
const eqPos = c.indexOf('equipment-gen.js');
if (eqPos > 0) {
    const lines3 = c.slice(0, eqPos).split('\n');
    console.log(`\nequipment-gen.js at line ${lines3.length}`);
    console.log(c.slice(eqPos, eqPos+100));
}