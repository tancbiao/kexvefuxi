const fs = require('fs');
const c = fs.readFileSync('C:/Users/tanc/Documents/WPSDrive/362543761/WPS云盘/谭政/科学复习系统/_kexvefuxi/5/2/index.html', 'utf8');

// Extract inline script (between second <script> and last </script>)
const firstScriptEnd = c.indexOf('</script>'); // 42816
const inlineStart = c.indexOf('<script>', firstScriptEnd) + '<script>'.length; // 42829
const inlineEnd = c.lastIndexOf('</script>'); // 211892
const inlineScript = c.slice(inlineStart, inlineEnd);

// Check for </script> INSIDE the inline script (before the final </script>)
const embedded = inlineScript.match(/<\/script>/g);
console.log('Embedded </script> in inline script:', embedded ? embedded.length : 0);

// Check for any other early script terminations
// Write to temp file for node check
fs.writeFileSync('C:/Users/tanc/Desktop/52_inline.js', inlineScript);
console.log('Written inline script to 52_inline.js, length:', inlineScript.length);