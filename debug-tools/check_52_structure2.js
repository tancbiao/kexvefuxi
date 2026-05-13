const fs = require('fs');
const c = fs.readFileSync('C:/Users/tanc/Documents/WPSDrive/362543761/WPS云盘/谭政/科学复习系统/_kexvefuxi/5/2/index.html', 'utf8');

// Find ALL <script> and </script> tags
const scriptOpens = [...c.matchAll(/<script[^>]*>/g)].map(m => ({pos: m.index, tag: m[0]}));
const scriptCloses = [...c.matchAll(/<\/script>/g)].map(m => ({pos: m.index}));

console.log('Script OPEN tags:');
scriptOpens.forEach((s, i) => {
    const lines = c.slice(0, s.pos).split('\n').length;
    console.log(`  ${i+1}. pos=${s.pos} line~${lines}: ${s.tag}`);
});

console.log('\nScript CLOSE tags:');
scriptCloses.forEach((s, i) => {
    const lines = c.slice(0, s.pos).split('\n').length;
    console.log(`  ${i+1}. pos=${s.pos} line~${lines}: ${c.slice(Math.max(0,s.pos-40), s.pos+20)}`);
});

// Now understand the structure
console.log('\n=== Structure Analysis ===');
// Each script block: open tag -> close tag
for (let i = 0; i < scriptOpens.length; i++) {
    const open = scriptOpens[i];
    const close = scriptCloses[i];
    if (close) {
        const content = c.slice(open.pos, close.pos + '</script>'.length);
        const isExternal = open.tag.includes('src=');
        console.log(`Block ${i+1}: ${isExternal ? 'EXTERNAL' : 'INLINE'} - ${content.length} chars`);
        console.log(`  From: ${open.pos} to ${close.pos + '</script>'.length}`);
        if (isExternal) {
            const src = open.tag.match(/src="([^"]+)"/);
            console.log(`  Src: ${src ? src[1] : 'unknown'}`);
        }
        // Show start and end of content
        console.log(`  Starts: ${content.slice(0, 100)}`);
        console.log(`  Ends: ...${content.slice(-100)}`);
        console.log('');
    }
}