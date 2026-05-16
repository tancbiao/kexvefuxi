/**
 * cloud-config.js - 云存储配置模块 v4
 * 
 * 使用 Cloudflare Tunnel 代理绕过 DNSPod 域名拦截
 * 
 * 自动发现机制：
 * 1. 页面加载时从 tunnel-config.json 获取最新 tunnel URL
 * 2. 如果获取失败，使用内置 fallback URL
 * 3. 服务器 cron 每 5 分钟更新 tunnel-config.json
 * 
 * ICP 备案完成后，改回 DIRECT_API_BASE 即可直连
 */

// 内置 fallback（服务器重启后可能变化，tunnel-config.json 会自动更新）
const TUNNEL_API_BASE = 'https://hire-inserted-lying-camera.trycloudflare.com/api';
// 直连域名（ICP 备案后启用）
const DIRECT_API_BASE = 'https://api.kexvefuxi.cn/api';
// 当前生效的 API 地址（初始值，会被 initAPIConfig 更新）
var API_BASE = TUNNEL_API_BASE;
const FETCH_TIMEOUT = 8000; // 8 秒超时

/** 页面加载时调用，从 tunnel-config.json 获取最新 API 地址 */
async function initAPIConfig() {
  try {
    const res = await fetch('/tunnel-config.json?_=' + Date.now(), { cache: 'no-store' });
    if (res.ok) {
      const config = await res.json();
      if (config.apiBase) {
        API_BASE = config.apiBase;
        console.log('[CloudConfig] 使用 tunnel API:', API_BASE);
        return;
      }
    }
  } catch (e) { /* fallback */ }
  console.log('[CloudConfig] 使用 fallback API:', API_BASE);
}

// 脚本加载时自动初始化
initAPIConfig();

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
