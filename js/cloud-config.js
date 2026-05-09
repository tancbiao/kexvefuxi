/**
 * cloud-config.js - 云存储配置模块
 * 
 * 使用腾讯云轻量服务器自建 API 实现：
 * - 排行榜数据读写
 * - 学生进度云同步
 * 
 * 服务器地址：http://159.75.134.151:5000
 */

// ==================== 配置区 ====================

const API_BASE = 'http://159.75.134.151:5000/api';

// ==================== 兼容旧函数（空实现） ====================

function setCloudKey(key) {}
function getCloudKey() { return ''; }

// ==================== 排行榜 API ====================

/**
 * 读取全年级排行榜数据
 * @param {string} gradeKey - 'grade32' | 'grade42' | 'grade52' | 'grade62'
 * @returns {Promise<object>}  { studentId: rankingData, ... }
 */
async function getRanking(gradeKey) {
  try {
    const res = await fetch(`${API_BASE}/ranking/${gradeKey}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    console.error('获取排行榜失败:', e);
    return {};
  }
}

/**
 * 更新当前学生的排行数据
 * @param {string} gradeKey 
 * @param {string} studentId 
 * @param {object} data - 排行数据对象
 */
async function updateRanking(gradeKey, studentId, data) {
  try {
    const res = await fetch(`${API_BASE}/ranking/${gradeKey}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return true;
  } catch (e) {
    console.error('更新排行榜失败:', e);
    return false;
  }
}

// ==================== 云同步 API ====================

/**
 * 保存学生进度到云端
 */
async function saveStudent(gradeKey, studentId, data) {
  try {
    const res = await fetch(`${API_BASE}/student/${gradeKey}/${studentId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return true;
  } catch (e) {
    console.error('云同步保存失败:', e);
    return false;
  }
}

/**
 * 从云端加载学生进度
 */
async function loadStudent(gradeKey, studentId) {
  try {
    const res = await fetch(`${API_BASE}/student/${gradeKey}/${studentId}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data && Object.keys(data).length > 0 ? data : null;
  } catch (e) {
    console.error('云同步加载失败:', e);
    return null;
  }
}
