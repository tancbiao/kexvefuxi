/**
 * 学生姓名映射表
 * 学号 → 真实姓名
 * 
 * 使用方法：
 *   getStudentName('学号') → '姓名'
 *   如果找不到返回空字符串 ''
 * 
 * 格式：'学号': '姓名'
 * 添加新学生直接在下面按格式追加即可
 */

const STUDENT_NAMES = {
  // === 一年级 ===
  // === 二年级 ===
  // === 三年级 ===
  // === 四年级 ===
  // === 五年级 ===
  // === 六年级 ===
};

/**
 * 根据学号获取学生姓名
 * @param {string} studentId - 学生学号
 * @returns {string} 学生姓名，找不到则返回空字符串
 */
function getStudentName(studentId) {
  if (!studentId) return '';
  // 精确匹配
  if (STUDENT_NAMES[studentId]) return STUDENT_NAMES[studentId];
  // 尝试去掉前导0匹配
  const trimmed = studentId.replace(/^0+/, '');
  for (const key in STUDENT_NAMES) {
    if (key.replace(/^0+/, '') === trimmed) return STUDENT_NAMES[key];
  }
  return '';
}
