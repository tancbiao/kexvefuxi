const fs = require('fs');
const c = fs.readFileSync('C:/Users/tanc/Documents/WPSDrive/362543761/WPS云盘/谭政/科学复习系统/_kexvefuxi/3/2/index.html', 'utf8');
const matches = [];
let idx = c.indexOf('桥梁');
while (idx !== -1) { matches.push(idx); idx = c.indexOf('桥梁', idx + 1); }
console.log('桥梁出现', matches.length, '次');
if (matches.length > 0) {
    matches.slice(0, 5).forEach(function(i) {
        console.log('  位置', i, ':', c.substring(i - 20, i + 40));
    });
}
// Check achievements
const achMatches = [];
let ai = c.indexOf('unit1_master');
while (ai !== -1) { achMatches.push(ai); ai = c.indexOf('unit1_master', ai + 1); }
console.log('unit1_master出现', achMatches.length, '次');
if (achMatches.length > 0) {
    console.log(c.substring(achMatches[0] - 50, achMatches[0] + 200));
}
