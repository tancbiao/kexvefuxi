const fs = require('fs');
const c = fs.readFileSync('C:/Users/tanc/Documents/WPSDrive/362543761/WPS云盘/谭政/科学复习系统/_kexvefuxi/5/2/index.html', 'utf8');

// Find inline script boundaries
const firstScriptEnd = c.indexOf('</script>'); // pos 42816, end of external script tag
const secondScriptStart = c.indexOf('<script>', firstScriptEnd); // pos 42826, start of inline script
const secondScriptEnd = c.lastIndexOf('</script>'); // pos 211892, end of inline script

console.log('External script ends at:', firstScriptEnd);
console.log('Inline script starts at:', secondScriptStart);
console.log('Inline script ends at:', secondScriptEnd);
console.log('Inline script length:', secondScriptEnd - secondScriptStart);

// Extract inline script and check for </script> INSIDE it (not counting the final </script>)
const inlineScript = c.slice(secondScriptStart + '<script>'.length, secondScriptEnd);
const embeddedTags = inlineScript.match(/<\/script>/g);
console.log('\nEmbedded </script> inside inline script:', embeddedTags ? embeddedTags.length : 0);

// Also check if questionData has </script> in it
const qdStart = c.indexOf('const questionData');
const qdJsonStart = c.indexOf('{', qdStart + 'const questionData'.length);
const qdEnd = c.indexOf(';', qdStart + 20);
const qdJson = c.slice(qdJsonStart, qdEnd);
const qdEmbedded = qdJson.match(/<\/script>/g);
console.log('\nEmbedded </script> in questionData JSON:', qdEmbedded ? qdEmbedded.length : 0);
if (qdEmbedded) {
    // Find positions
    let p = qdJsonStart;
    let count = 0;
    while ((p = c.indexOf('</script>', p + 1)) !== -1 && p < qdEnd) {
        count++;
        if (count <= 5) {
            console.log(`  Position ${p} (rel ${p - qdJsonStart}): ${c.slice(Math.max(qdJsonStart, p-30), Math.min(qdEnd, p+50))}`);
        }
    }
    if (count > 5) console.log(`  ... and ${count - 5} more`);
}

// Also check for any </script> between secondScriptStart and secondScriptEnd
let p = secondScriptStart;
let count = 0;
while ((p = c.indexOf('</script>', p + 1)) !== -1 && p < secondScriptEnd) {
    count++;
    if (count <= 5) {
        console.log(`\nInline </script> at pos ${p} (rel ${p - secondScriptStart}):`);
        console.log(c.slice(Math.max(secondScriptStart, p-50), Math.min(secondScriptEnd, p+80)));
    }
}
if (count > 5) console.log(`\n... total ${count} embedded </script> in inline script`);