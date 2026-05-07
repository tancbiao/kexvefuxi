const fs = require('fs');
const c = fs.readFileSync('C:/Users/tanc/Documents/WPSDrive/362543761/WPS云盘/谭政/科学复习系统/_kexvefuxi/5/2/index.html', 'utf8');

// Find all uses of 'const' for UPLOAD_PASSWORD
const positions = [];
let p = 0;
while ((p = c.indexOf('const UPLOAD_PASSWORD', p)) !== -1) {
    const line = c.slice(0, p).split('\n').length;
    positions.push({ pos: p, line, ctx: c.slice(p, p+80) });
    p++;
}
console.log('const UPLOAD_PASSWORD declarations:', positions.length);
positions.forEach(x => console.log('Line', x.line + ':', JSON.stringify(x.ctx)));

// Check for 'use strict' before UPLOAD_PASSWORD
const usPos = c.indexOf('"use strict"');
const usPos2 = c.indexOf("'use strict'");
const upPos = c.indexOf('const UPLOAD_PASSWORD');
console.log('\n"use strict" pos:', usPos, 'line:', usPos > 0 ? c.slice(0, usPos).split('\n').length : 'N/A');
console.log("'use strict' pos:", usPos2, 'line:', usPos2 > 0 ? c.slice(0, usPos2).split('\n').length : 'N/A');
console.log('UPLOAD_PASSWORD pos:', upPos, 'line:', c.slice(0, upPos).split('\n').length);

// Check ALL uses of 'UPLOAD_PASSWORD' as an identifier (not in string)
const uses = [];
let up = 0;
while ((up = c.indexOf('UPLOAD_PASSWORD', up)) !== -1) {
    // Check if it's in a string (preceded by " or ' or inside a string)
    const before = c.slice(Math.max(0, up - 20), up);
    const after = c.slice(up + 'UPLOAD_PASSWORD'.length, up + 'UPLOAD_PASSWORD'.length + 5);
    const isString = before.match(/["']\s*$/) || after.match(/^["']/);
    const line = c.slice(0, up).split('\n').length;
    if (!isString) {
        uses.push({ pos: up, line, ctx: c.slice(Math.max(0,up-40), up+60) });
    }
    up++;
}
console.log('\nAll non-string UPLOAD_PASSWORD uses:', uses.length);
uses.forEach(u => {
    console.log(`Line ${u.line} (pos ${u.pos}): ${JSON.stringify(u.ctx)}`);
});

// Check: are there any eval() or Function() calls that might affect scoping?
const evalCount = (c.match(/eval\s*\(|new Function\s*\(|Function\s*\(/g) || []).length;
console.log('\neval/new Function/Function() calls:', evalCount);

// Check DOMContentLoaded pattern
const dcPos = c.indexOf('DOMContentLoaded');
if (dcPos > 0) {
    const dcLine = c.slice(0, dcPos).split('\n').length;
    const content = c.slice(dcPos, dcPos + 500);
    console.log('\nDOMContentLoaded at line', dcLine);
    console.log(content);
}

// Check if UPLOAD_PASSWORD is defined BEFORE the equipment-gen.js external script
const eqStart = c.indexOf('<script src="../../equipment-gen.js');
const upDefPos = c.indexOf('const UPLOAD_PASSWORD');
console.log('\nequipment-gen.js at pos:', eqStart, 'line:', eqStart > 0 ? c.slice(0, eqStart).split('\n').length : 'N/A');
console.log('UPLOAD_PASSWORD def at pos:', upDefPos, 'line:', c.slice(0, upDefPos).split('\n').length);

// So UPLOAD_PASSWORD is AFTER equipment-gen.js... but equipment-gen.js is loaded first
// And UPLOAD_PASSWORD is inside the inline script (comes after external script)
// So by the time the inline script runs, equipment-gen.js should be loaded

// But wait - the onclick in HTML references showUploadPasswordPrompt
// which references UPLOAD_PASSWORD. When is this callback executed?
// It's executed when the button is clicked, which is LONG after the script runs.
// So UPLOAD_PASSWORD should be defined by then...

// Unless... there are TWO UPLOAD_PASSWORD const declarations?
// That would cause TDZ for the second one...
console.log('\n=== Checking for multiple const declarations ===');
const constDecls = [];
let cd = 0;
while ((cd = c.indexOf('const UPLOAD_PASSWORD', cd)) !== -1) {
    const line = c.slice(0, cd).split('\n').length;
    constDecls.push({ pos: cd, line });
    cd++;
}
console.log('Total const UPLOAD_PASSWORD found:', constDecls.length);