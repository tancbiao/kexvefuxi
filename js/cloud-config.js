/**
 * cloud-config.js - 云存储配置模块
 * 
 * 使用 JSONBin.io v3 API 实现：
 * - 排行榜数据读写
 * - 学生进度云同步
 * 
 * ===== 配置方法 =====
 * 1. 登录 https://jsonbin.io → Settings → API Keys
 * 2. 复制你的 Master Key（原始字符串，不是哈希）
 * 3. 填入下方 JSONBIN_MASTER_KEY 变量
 * 
 * Collection ID: 69e9771aaaba8821972a04b6
 */

// ==================== 配置区 ====================

// ⚠️ 请将你的 JSONBin Master Key 填入此处（从 jsonbin.io 获取）
const JSONBIN_MASTER_KEY = localStorage.getItem('cloud_jsonbin_key') || '';

const COLLECTION_ID = '69e9771aaaba8821972a04b6';
const API_BASE = 'https://api.jsonbin.io/v3';

// 存储类型对应的 bin 名称
const BIN_NAMES = {
  RANKINGS: 'kexvefuxi_rankings',
  STUDENTS: 'kexvefuxi_students'
};

// ==================== 内部缓存 ====================
let _binCache = {}; // { binName: binId }

/**
 * 设置/更新 JSONBin Master Key（存入 localStorage）
 */
function setCloudKey(key) {
  localStorage.setItem('cloud_jsonbin_key', key);
}

function getCloudKey() {
  return localStorage.getItem('cloud_jsonbin_key') || '';
}

/**
 * 获取请求头
 */
function _headers() {
  const key = getCloudKey();
  const h = { 'Content-Type': 'application/json' };
  if (key) h['X-Master-Key'] = key;
  return h;
}

/**
 * 通过名称查找或创建 bin
 */
async function _getOrCreateBin(binName) {
  // 先从缓存查
  if (_binCache[binName]) return _binCache[binName];

  const key = getCloudKey();
  if (!key) throw new Error('未配置 JSONBin Master Key，请设置');

  try {
    // 列出集合中的所有 bin
    const listUrl = `${API_BASE}/c/${COLLECTION_ID}/bins`;
    const listRes = await fetch(listUrl, { headers: { 'X-Master-Key': key } });
    
    if (listRes.ok) {
      const bins = await listRes.json();
      // 查找匹配名称的 bin
      const found = (bins.record || bins).find(b => b.snippetName === binName || b.name === binName);
      if (found) {
        _binCache[binName] = found.snippetId || found.id;
        return _binCache[binName];
      }
    }

    // 没找到，创建新的
    const createUrl = `${API_BASE}/b`;
    const createRes = await fetch(createUrl, {
      method: 'POST',
      headers: {
        'X-Master-Key': key,
        'X-Bin-Name': binName,
        'X-Collection-Id': COLLECTION_ID,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    });

    if (createRes.ok) {
      const created = await createRes.json();
      const binId = created.metadata?.id || created.id;
      _binCache[binName] = binId;
      return binId;
    }
    throw new Error('创建 bin 失败');
  } catch (e) {
    console.error('JSONBin 错误:', e);
    throw e;
  }
}

/**
 * 读取一个 bin 的数据
 */
async function readBin(binName) {
  const key = getCloudKey();
  if (!key) throw new Error('未配置 JSONBin Master Key');

  try {
    const binId = await _getOrCreateBin(binName);
    const url = `${API_BASE}/b/${binId}/latest`;
    const res = await fetch(url, { headers: { 'X-Master-Key': key } });
    if (!res.ok) throw new Error(`读取失败: ${res.status}`);
    const data = await res.json();
    return data.record || data;
  } catch (e) {
    console.error('readBin 错误:', e);
    throw e;
  }
}

/**
 * 写入一个 bin 的数据（全量替换）
 */
async function writeBin(binName, data) {
  const key = getCloudKey();
  if (!key) throw new Error('未配置 JSONBin Master Key');

  try {
    const binId = await _getOrCreateBin(binName);
    const url = `${API_BASE}/b/${binId}`;
    const res = await fetch(url, {
      method: 'PUT',
      headers: {
        'X-Master-Key': key,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error(`写入失败: ${res.status}`);
    return true;
  } catch (e) {
    console.error('writeBin 错误:', e);
    throw e;
  }
}

// ==================== 排行榜 API ====================

/**
 * 读取全年级排行榜数据
 * @param {string} gradeKey - 'grade32' | 'grade42' | 'grade52' | 'grade62'
 * @returns {Promise<object>}  { studentId: rankingData, ... }
 */
async function getRanking(gradeKey) {
  try {
    const allRankings = await readBin(BIN_NAMES.RANKINGS);
    return allRankings[gradeKey] || {};
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
    let allRankings = {};
    try {
      allRankings = await readBin(BIN_NAMES.RANKINGS);
    } catch (e) {
      // 首次读取可能为空
    }
    if (!allRankings[gradeKey]) allRankings[gradeKey] = {};
    allRankings[gradeKey][studentId] = data;
    await writeBin(BIN_NAMES.RANKINGS, allRankings);
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
    let allStudents = {};
    try {
      allStudents = await readBin(BIN_NAMES.STUDENTS);
    } catch (e) {}
    const recordKey = gradeKey + '_' + studentId;
    allStudents[recordKey] = data;
    await writeBin(BIN_NAMES.STUDENTS, allStudents);
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
    const allStudents = await readBin(BIN_NAMES.STUDENTS);
    const recordKey = gradeKey + '_' + studentId;
    return allStudents[recordKey] || null;
  } catch (e) {
    console.error('云同步加载失败:', e);
    return null;
  }
}
