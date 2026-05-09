/**
 * cloud-config.js - 云存储配置模块
 * 
 * 使用自建 API (腾讯云轻量服务器)：
 * - 排行榜数据读写
 * - 学生进度云同步
 * 
 * API 地址：https://159.75.134.151 (Let's Encrypt SSL)
 */

const API_BASE = 'https://159.75.134.151/api';

function setCloudKey(key) {}
function getCloudKey() { return ''; }

async function getRanking(gradeKey) {
  try {
    const res = await fetch(`${API_BASE}/ranking/${gradeKey}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) { console.error('获取排行榜失败:', e); return {}; }
}

async function updateRanking(gradeKey, studentId, data) {
  try {
    const res = await fetch(`${API_BASE}/ranking/${gradeKey}`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return true;
  } catch (e) { console.error('更新排行榜失败:', e); return false; }
}

async function saveStudent(gradeKey, studentId, data) {
  try {
    const res = await fetch(`${API_BASE}/student/${gradeKey}/${studentId}`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return true;
  } catch (e) { console.error('云同步保存失败:', e); return false; }
}

async function loadStudent(gradeKey, studentId) {
  try {
    const res = await fetch(`${API_BASE}/student/${gradeKey}/${studentId}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data && Object.keys(data).length > 0 ? data : null;
  } catch (e) { console.error('云同步加载失败:', e); return null; }
}
