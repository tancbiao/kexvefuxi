const fs = require('fs');

// Read local file
const local = fs.readFileSync('C:/Users/tanc/Documents/WPSDrive/362543761/WPS云盘/谭政/科学复习系统/_kexvefuxi/5/2/index.html', 'utf8');
console.log('Local file size:', local.length, 'chars');

// Fetch from GitHub via https
const https = require('https');
https.get('https://raw.githubusercontent.com/tancbiao/kexvefuxi/main/5/2/index.html', (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
        console.log('GitHub file size:', data.length, 'chars');
        console.log('Difference:', local.length - data.length, 'chars');
        
        if (local === data) {
            console.log('\n✅ Local and GitHub are IDENTICAL');
        } else {
            console.log('\n❌ Files differ!');
            
            // Find first difference
            for (let i = 0; i < Math.min(local.length, data.length); i++) {
                if (local[i] !== data[i]) {
                    console.log('First diff at pos', i);
                    console.log('Local context:', JSON.stringify(local.slice(Math.max(0,i-50), i+50)));
                    console.log('GitHub context:', JSON.stringify(data.slice(Math.max(0,i-50), i+50)));
                    break;
                }
            }
            
            // Check UPLOAD_PASSWORD in both
            const localUP = local.indexOf('UPLOAD_PASSWORD');
            const remoteUP = data.indexOf('UPLOAD_PASSWORD');
            console.log('\nUPLOAD_PASSWORD in local at pos:', localUP);
            console.log('UPLOAD_PASSWORD in GitHub at pos:', remoteUP);
            
            // Check if GitHub has the upload overlay
            const localOverlay = local.indexOf('uploadPwdOverlay');
            const remoteOverlay = data.indexOf('uploadPwdOverlay');
            console.log('\nuploadPwdOverlay in local at pos:', localOverlay);
            console.log('uploadPwdOverlay in GitHub at pos:', remoteOverlay);
            
            // Count </script> in both
            const localEndTags = (local.match(/<\/script>/gi) || []).length;
            const remoteEndTags = (data.match(/<\/script>/gi) || []).length;
            console.log('\n</script> count - local:', localEndTags, ', GitHub:', remoteEndTags);
            
            // Check </script> positions
            let p = 0;
            console.log('\nLocal </script> positions:');
            while ((p = local.indexOf('</script>', p)) !== -1) {
                console.log('  pos', p, 'line', local.slice(0,p).split('\n').length);
                p++;
            }
            p = 0;
            console.log('\nGitHub </script> positions:');
            while ((p = data.indexOf('</script>', p)) !== -1) {
                console.log('  pos', p, 'line', data.slice(0,p).split('\n').length);
                p++;
            }
        }
    });
}).on('error', e => console.error('Fetch error:', e.message));
