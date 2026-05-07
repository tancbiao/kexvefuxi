const fs = require('fs');
const c = fs.readFileSync('C:/Users/tanc/Documents/WPSDrive/362543761/WPS云盘/谭政/科学复习系统/_kexvefuxi/5/2/index.html', 'utf8');

// Find the inline script boundaries
const firstScriptEnd = c.indexOf('</script>'); // external equipment-gen.js
const inlineScriptStart = c.indexOf('<script>', firstScriptEnd) + '<script>'.length;
const inlineScriptEnd = c.lastIndexOf('</script>');
const inline = c.slice(inlineScriptStart, inlineScriptEnd);

// Find UPLOAD_PASSWORD position within inline script
const upPos = inline.indexOf('const UPLOAD_PASSWORD');
const upLine = inline.slice(0, upPos).split('\n').length;
console.log('UPLOAD_PASSWORD at inline script line', upLine, '(absolute line', c.slice(0, inlineScriptStart + upPos).split('\n').length, ')');

// Find checkUploadPassword position
const checkPos = inline.indexOf('function checkUploadPassword');
const checkLine = inline.slice(0, checkPos).split('\n').length;
console.log('checkUploadPassword at inline script line', checkLine, '(absolute line', c.slice(0, inlineScriptStart + checkPos).split('\n').length, ')');

// Find showUploadPasswordPrompt position
const showPos = inline.indexOf('function showUploadPasswordPrompt');
const showLine = inline.slice(0, showPos).split('\n').length;
console.log('showUploadPasswordPrompt at inline script line', showLine, '(absolute line', c.slice(0, inlineScriptStart + showPos).split('\n').length, ')');

// Find DOMContentLoaded that binds the button
const dcPos = inline.indexOf('DOMContentLoaded');
const dcLine = inline.slice(0, dcPos).split('\n').length;
console.log('DOMContentLoaded at inline script line', dcLine);

// Show the DOMContentLoaded block
const dcBlock = inline.slice(dcPos, dcPos + 500);
console.log('\nDOMContentLoaded block:');
console.log(dcBlock);

// Check: is UPLOAD_PASSWORD defined at TOP LEVEL or inside a block?
// If it's inside a block, it won't be accessible from onclick handlers
const beforeUP = inline.slice(Math.max(0, upPos - 200), upPos);
const lastOpenBrace = beforeUP.lastIndexOf('{');
const lastCloseBrace = beforeUP.lastIndexOf('}');
const braceDepth = (beforeUP.match(/{/g) || []).length - (beforeUP.match(/}/g) || []).length;
console.log('\nBrace depth before UPLOAD_PASSWORD:', braceDepth);
console.log('Context before UPLOAD_PASSWORD:', JSON.stringify(inline.slice(Math.max(0, upPos - 100), upPos + 80)));

// Now check: what does the onclick attribute look like?
const onclickPos = c.indexOf('uploadQBtn52');
console.log('\nuploadQBtn52 HTML context:');
console.log(c.slice(onclickPos - 20, onclickPos + 200));

// Check if there's a var UPLOAD_PASSWORD (hoisted) vs const (TDZ)
const varUP = inline.indexOf('var UPLOAD_PASSWORD');
const letUP = inline.indexOf('let UPLOAD_PASSWORD');
console.log('\nvar UPLOAD_PASSWORD:', varUP);
console.log('let UPLOAD_PASSWORD:', letUP);

// Check for IIFE or module pattern wrapping the code
const iifeStart = inline.indexOf('(function()');
const modulePattern = inline.indexOf('define(');
console.log('\nIIFE pattern:', iifeStart >= 0 ? 'found at ' + iifeStart : 'not found');
console.log('Module pattern:', modulePattern >= 0 ? 'found at ' + modulePattern : 'not found');

// Check: does equipment-gen.js define UPLOAD_PASSWORD or affect the scope?
console.log('\n=== equipment-gen.js ===');
const eqTag = c.slice(c.indexOf('<script src="../../equipment-gen.js'), c.indexOf('</script>', c.indexOf('equipment-gen')) + 9);
console.log(eqTag);
