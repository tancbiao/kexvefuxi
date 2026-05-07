const fs = require('fs');
const c = fs.readFileSync('C:/Users/tanc/Documents/WPSDrive/362543761/WPS云盘/谭政/科学复习系统/_kexvefuxi/5/2/index.html', 'utf8');

// The </script> at pos 42816 — what exactly is before it?
console.log('Chars 300 before first </script> (pos 42816):');
console.log(c.slice(42516, 42825));

console.log('\nChars 50 after first </script>:');
console.log(c.slice(42816, 42880));

// Also check the raw bytes around pos 42816
console.log('\nRaw bytes around pos 42816 (42810-42825):');
const raw = Buffer.from(c.slice(42810, 42826), 'utf8');
console.log(Buffer.from(raw).toString('hex'));
console.log(raw.toString('utf8'));

// Check: how many <script tags exist?
const scriptTagRegex = /<script/g;
let match;
let count = 0;
const positions = [];
while ((match = scriptTagRegex.exec(c)) !== null && count < 20) {
    positions.push(match.index);
    count++;
}
console.log(`\nTotal <script tags found: ${positions.length}`);
positions.forEach((pos, i) => {
    const line = c.slice(0, pos).split('\n').length;
    console.log(`  ${i+1}. pos=${pos} line~${line}: ${c.slice(pos, pos+80)}`);
});

// And count </script>
const closeRegex = /<\/script>/g;
let closeMatch;
const closePositions = [];
while ((closeMatch = closeRegex.exec(c)) !== null) {
    closePositions.push(closeMatch.index);
}
console.log(`\nTotal </script> found: ${closePositions.length}`);
closePositions.forEach((pos, i) => {
    const line = c.slice(0, pos).split('\n').length;
    console.log(`  ${i+1}. pos=${pos} line~${line}: ${c.slice(pos-30, pos+30)}`);
});