const fs = require('fs');
const c = fs.readFileSync('C:/Users/tanc/Documents/WPSDrive/362543761/WPS云盘/谭政/科学复习系统/_kexvefuxi/3/2/index.html', 'utf8');
// Count how many times </script> appears (not as actual tag)
const tagCount = (c.match(/<\/script>/g) || []).length;
console.log('</script> total count:', tagCount);
// Check position of each one
let pos = c.indexOf('</script>');
let idx = 0;
while (pos !== -1) {
    idx++;
    console.log('Occurrence', idx, 'at position', pos, ':', c.slice(Math.max(0, pos-30), pos+50));
    pos = c.indexOf('</script>', pos + 1);
}
