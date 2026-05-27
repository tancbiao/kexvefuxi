/**
 * cloud-config.js - 云存储配置模块 v4
 * 
 * API 连接策略（按优先级）：
 * 1. tunnel-config.json: 服务器 cron 自动更新的 Cloudflare Tunnel URL（实时自动发现）
 * 2. DIRECT_API_BASE: https://api.kexvefuxi.cn（直连 SSL，2026-05-19 证书已扩展）
 * 
 * SSL 证书覆盖: api.kexvefuxi.cn + api.kexvefuxi.cn (Let's Encrypt, 过期 2026-08-17)
 */

// 直连域名（主域名，SSL 证书已配置）
const DIRECT_API_BASE = 'https://api.kexvefuxi.cn/api';
// 当前生效的 API 地址（默认直连，会被 initAPIConfig 更新为 tunnel）
var API_BASE = DIRECT_API_BASE;
const FETCH_TIMEOUT = 8000; // 8 秒超时

/** 页面加载时调用，从 tunnel-config.json 获取最新 tunnel URL（优先 tunnel 自动发现） */
async function initAPIConfig() {
  try {
    const res = await fetch('/tunnel-config.json?_=' + Date.now(), { cache: 'no-store' });
    if (res.ok) {
      const config = await res.json();
      // 🆕 过滤未备案域名（xixitime.cn），只用备案过的
      if (config.apiBase && config.apiBase.indexOf('xixitime.cn') === -1) {
        API_BASE = config.apiBase;
        console.log('[CloudConfig] 使用 tunnel API:', API_BASE);
        return;
      }
    }
  } catch (e) { /* tunnel 不可用，保持直连 */ }
  console.log('[CloudConfig] 使用直连 API:', API_BASE);
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

/** 🆕 带超时+重试的 fetch 封装（3次递增退避） */
async function fetchWithRetry(url, options, maxRetries, label) {
  maxRetries = maxRetries || 2;
  label = label || url;
  var lastErr = null;
  for (var i = 0; i <= maxRetries; i++) {
    try {
      return await fetchWithTimeout(url, options);
    } catch (e) {
      lastErr = e;
      if (i < maxRetries) {
        var delay = 1500 * (i + 1);
        console.warn('[fetchRetry]', label, '第' + (i+1) + '次失败，' + delay + 'ms后重试...');
        await new Promise(function(r) { setTimeout(r, delay); });
      }
    }
  }
  throw lastErr;
}

async function getRanking(gradeKey) {
  try {
    const res = await fetchWithRetry(`${API_BASE}/ranking/${gradeKey}`, {}, 2, 'getRanking:'+gradeKey);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) { console.error('获取排行榜失败:', e); return {}; }
}

async function updateRanking(gradeKey, studentId, data) {
  try {
    const res = await fetchWithRetry(`${API_BASE}/ranking/${gradeKey}`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }, 2, 'updateRanking:'+gradeKey);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return true;
  } catch (e) { console.error('更新排行榜失败:', e); return false; }
}

async function saveStudent(gradeKey, studentId, data) {
  try {
    const res = await fetchWithRetry(`${API_BASE}/student/${gradeKey}/${studentId}`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }, 2, 'saveStudent:'+studentId);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return true;
  } catch (e) { console.error('云同步保存失败:', e); return false; }
}

async function loadStudent(gradeKey, studentId) {
  try {
    const res = await fetchWithRetry(`${API_BASE}/student/${gradeKey}/${studentId}`, {}, 2, 'loadStudent:'+studentId);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data && Object.keys(data).length > 0 ? data : null;
  } catch (e) { console.error('云同步加载失败:', e); return null; }
}
