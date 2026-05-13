const fs = require('fs');
const c = fs.readFileSync('C:/Users/tanc/Documents/WPSDrive/362543761/WPS云盘/谭政/科学复习系统/_kexvefuxi/5/2/index.html', 'utf8');

// Check file size
console.log('File size:', c.length);

// Check </script> occurrences
const scriptTagCount = (c.match(/<\/script>/g) || []).length;
console.log('</script> total count:', scriptTagCount);

let pos = c.indexOf('</script>');
let idx = 0;
while (pos !== -1) {
    idx++;
    const ctx = c.slice(Math.max(0, pos-80), pos+120);
    console.log(`Occurrence ${idx} at pos ${pos}:`);
    console.log(ctx);
    console.log('---');
    pos = c.indexOf('</script>', pos + 1);
}

// Check UPLOAD_PASSWORD
const upPos = c.indexOf('UPLOAD_PASSWORD');
if (upPos > 0) {
    console.log('\nUPLOAD_PASSWORD first occurrence at pos', upPos, ':');
    console.log(c.slice(Math.max(0, upPos-50), upPos+200));
}

// Check showUploadPasswordPrompt
const showPos = c.indexOf('showUploadPasswordPrompt');
if (showPos > 0) {
    console.log('\nshowUploadPasswordPrompt first occurrence at pos', showPos, ':');
    console.log(c.slice(Math.max(0, showPos-100), showPos+300));
}