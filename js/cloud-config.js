/**
 * cloud-config.js - 云存储配置模块
 * 
 * 使用自建 API (腾讯云轻量服务器) 通过 Cloudflare Tunnel 代理
 * 
 * Tunnel URL 变化时需更新 TUNNEL_API_BASE
 * 当前 tunnel 地址: 服务器上 systemctl status cloudflared-tunnel 查看
 * 
 * v3: Cloudflare Tunnel 代理，绕过 DNSPod 域名拦截
 * 优先级: Tunnel > 直连域名（ICP 备案后生效）
 */

// Cloudflare Tunnel 代理地址（服务器重启后可能变化，需更新）
const TUNNEL_API_BASE = 'https://hire-inserted-lying-camera.trycloudflare.com/api';
// 直连域名备案后启用
const DIRECT_API_BASE = 'https://api.kexvefuxi.cn/api';
// 当前生效的 API 地址
const API_BASE = TUNNEL_API_BASE;
const FETCH_TIMEOUT = 8000; // 8 秒超时

function setCloudKey(key) {}
function getCloudKey() { return ''; }

/** 带超时的 fetch 封装 */
function fetchWithTimeout(url, options) {
  var ctrl = new AbortController();
  var timer = setTimeout(function() { ctrl.abort(); }, FETCH_TIMEOUT);
  var opts = Object.assign({}, options || {}, { signal: ctrl.signal });
  return fetch(url, opts).finally(function() { clearTimeout(timer); });
}

async function getRanking(gradeKey) {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/ranking/${gradeKey}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) { console.error('获取排行榜失败:', e); return {}; }
}

async function updateRanking(gradeKey, studentId, data) {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/ranking/${gradeKey}`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return true;
  } catch (e) { console.error('更新排行榜失败:', e); return false; }
}

async function saveStudent(gradeKey, studentId, data) {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/student/${gradeKey}/${studentId}`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return true;
  } catch (e) { console.error('云同步保存失败:', e); return false; }
}

async function loadStudent(gradeKey, studentId) {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/student/${gradeKey}/${studentId}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data && Object.keys(data).length > 0 ? data : null;
  } catch (e) { console.error('云同步加载失败:', e); return null; }
}
