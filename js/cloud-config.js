/**
 * cloud-config.js - 云存储配置模块
 * 
 * 使用自建 API (腾讯云轻量服务器)：
 * - 排行榜数据读写  
 * - 学生进度云同步
 * 
 * API 地址：https://api.kexvefuxi.cn (Let's Encrypt SSL)
 * 如遇连接问题，检查腾讯云安全组是否开放 443 端口
 * 
 * v2: 所有 fetch 加 8 秒超时（AbortController），防止安全组封端口时页面卡死
 */

const API_BASE = 'https://api.kexvefuxi.cn/api';
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
