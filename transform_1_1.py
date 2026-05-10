#!/usr/bin/env python3
"""
Transform 6/2/index.html → 1/1/index.html (unified login + course selection)
"""
import re, os

PATH = r'C:\Users\tanc\Documents\WPSDrive\362543761\WPS云盘\谭政\科学复习系统\_kexvefuxi\1\1\index.html'

with open(PATH, 'r', encoding='utf-8') as f:
    c = f.read()

orig = c

# ========== 1. Update title ==========
c = c.replace(
    '🌟 科学探险家 · 六年级科学趣味闯关',
    '🌟 科学探险家 · 统一闯关系统'
)

# ========== 2. Add course selection CSS before </style> ==========
course_css = '''
/* ====== 选课界面 ====== */
.course-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  padding: 20px 0;
  max-width: 500px;
  margin: 0 auto;
}
.course-card {
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 16px;
  padding: 24px 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}
.course-card:hover {
  background: rgba(255,255,255,0.15);
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.3);
}
.course-card .grade-icon { font-size: 2.5em; margin-bottom: 8px; }
.course-card .grade-name { font-size: 1.2em; font-weight: 700; margin-bottom: 4px; }
.course-card .grade-sub {
  display: flex; gap: 8px; justify-content: center; margin-top: 8px;
}
.course-card .grade-sub span {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.85em;
  background: rgba(255,255,255,0.1);
  cursor: pointer;
  transition: all 0.2s;
}
.course-card .grade-sub span:hover {
  background: rgba(255,255,255,0.25);
}
.course-card .grade-sub span.active {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
}
.course-header {
  text-align: center;
  margin-bottom: 12px;
}
.course-header h2 { font-size: 1.5em; margin-bottom: 4px; }
.course-header p { color: rgba(255,255,255,0.6); font-size: 0.9em; }
.course-logout {
  display: inline-block;
  margin-top: 16px;
  padding: 8px 20px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 10px;
  color: rgba(255,255,255,0.7);
  cursor: pointer;
  font-size: 0.9em;
}
.course-logout:hover { background: rgba(255,255,255,0.2); }
'''
c = c.replace('</style>', course_css + '\n</style>')

# ========== 3. Add course selection screen HTML ==========
course_screen = '''
<!-- ====== 选课界面 ====== -->
<div class="screen" id="courseScreen">
  <div class="course-header">
    <h2>📚 选择要学习的课程</h2>
    <p>欢迎回来，<span id="studentDisplay">同学</span></p>
  </div>
  <div class="course-grid" id="courseGrid">
    <div class="course-card" data-grade="3" onclick="showSemesters('3')">
      <div class="grade-icon">🐟</div>
      <div class="grade-name">三年级</div>
      <div class="grade-sub" id="sem3">
        <span data-sem="1" onclick="event.stopPropagation();startCourse('3','1')">上册</span>
        <span data-sem="2" onclick="event.stopPropagation();startCourse('3','2')">下册</span>
      </div>
    </div>
    <div class="course-card" data-grade="4" onclick="showSemesters('4')">
      <div class="grade-icon">🦋</div>
      <div class="grade-name">四年级</div>
      <div class="grade-sub" id="sem4">
        <span data-sem="1" onclick="event.stopPropagation();startCourse('4','1')">上册</span>
        <span data-sem="2" onclick="event.stopPropagation();startCourse('4','2')">下册</span>
      </div>
    </div>
    <div class="course-card" data-grade="5" onclick="showSemesters('5')">
      <div class="grade-icon">🌿</div>
      <div class="grade-name">五年级</div>
      <div class="grade-sub" id="sem5">
        <span data-sem="1" onclick="event.stopPropagation();startCourse('5','1')">上册</span>
        <span data-sem="2" onclick="event.stopPropagation();startCourse('5','2')">下册</span>
      </div>
    </div>
    <div class="course-card" data-grade="6" onclick="showSemesters('6')">
      <div class="grade-icon">🏆</div>
      <div class="grade-name">六年级</div>
      <div class="grade-sub" id="sem6">
        <span data-sem="1" onclick="event.stopPropagation();startCourse('6','1')">上册</span>
        <span data-sem="2" onclick="event.stopPropagation();startCourse('6','2')">下册</span>
      </div>
    </div>
  </div>
  <div style="text-align:center;">
    <button class="course-logout" onclick="logout()">🚪 退出登录</button>
  </div>
</div>
'''

# Insert after login overlay 
login_overlay_end = '<!-- ====== 主界面（状态栏 + 内容区） ====== -->'
c = c.replace(login_overlay_end, course_screen + '\n\n' + login_overlay_end)

# ========== 4. Modify login flow ==========
old_login = '''function loginWithId() {
  const id = document.getElementById('studentIdInput').value.trim();
  if (id.length !== 8 || !/^\d+$/.test(id)) { alert('请输入正确的8位数字学号！'); return; }
  gameState.studentId = id;
  gameState.isGuest = false;
  hideLoginScreen();
  loadUserData();
  pushRankingData();
  checkAndResetStamina();
  updateStaminaDisplay();
  showLevelSelect();
}'''

new_login = '''let currentCourse = null; // { grade: '6', sem: '2' }

function loginWithId() {
  const id = document.getElementById('studentIdInput').value.trim();
  if (id.length !== 8 || !/^\d+$/.test(id)) { alert('请输入正确的8位数字学号！'); return; }
  gameState.studentId = id;
  gameState.isGuest = false;
  hideLoginScreen();
  loadUserData();
  pushRankingData();
  checkAndResetStamina();
  updateStaminaDisplay();
  // 显示选课界面
  document.getElementById('studentDisplay').textContent = id + ' 同学';
  showScreen('courseScreen');
}'''

c = c.replace(old_login, new_login)

# Also change loginAsGuest
old_guest = '''function loginAsGuest() {
  gameState.studentId = null;
  gameState.isGuest = true;
  hideLoginScreen();
  checkAndResetStamina();
  updateStaminaDisplay();
  showLevelSelect();
}'''

new_guest = '''function loginAsGuest() {
  gameState.studentId = null;
  gameState.isGuest = true;
  hideLoginScreen();
  checkAndResetStamina();
  updateStaminaDisplay();
  // 显示选课界面（游客）
  document.getElementById('studentDisplay').textContent = '游客';
  showScreen('courseScreen');
}'''

c = c.replace(old_guest, new_guest)

# ========== 5. Add course selection + logout functions ==========
# Find a good insertion point (after login functions)
insert_after = 'function loginAsGuest()'
new_fns = '''

// 高亮选中上下册
function showSemesters(grade) {
  document.querySelectorAll('.grade-sub span').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('#sem' + grade + ' span').forEach(s => s.classList.add('active'));
}

// 退出到选课
function logout() {
  gameState.studentId = null;
  showScreen('courseScreen');
  hideLoginScreen();
}

// 根据年级学期加载题库并开始答题
function startCourse(grade, sem) {
  currentCourse = { grade, sem };
  
  // 设置动态 key
  const semLabel = sem === '2' ? '下册' : '上册';
  document.querySelector('.level-select-title').textContent = grade + '年级科学 · ' + semLabel;
  
  // 加载对应题库
  _lessonsLoaded = false;
  var grid = document.getElementById('levelGrid');
  if (grid) grid.innerHTML = '<div style="text-align:center;padding:40px;">📚 正在加载题库...</div>';
  
  // 动态创建 script 标签加载题库
  var script = document.createElement('script');
  var dataFile = '../data/' + grade + '-' + sem + '-lessons.js?v=20260507';
  script.src = dataFile;
  script.onload = function() {
    var key = 'QUESTION_BANK_' + grade + '_' + sem + '_LESSONS';
    if (window[key]) {
      Object.assign(questionData, window[key]);
    }
    // 加载当前课程进度
    var progressKey = 'progress_grade' + grade + sem + '_' + gameState.studentId;
    try {
      var saved = localStorage.getItem(progressKey);
      if (saved) {
        gameState.lessonProgress = JSON.parse(saved);
      } else {
        gameState.lessonProgress = {};
      }
    } catch(e) { gameState.lessonProgress = {}; }
    _lessonsLoaded = true;
    renderLevelGrid();
    showScreen('levelScreen');
  };
  script.onerror = function() {
    if (grid) grid.innerHTML = '<div style="text-align:center;padding:40px;color:#ff6b6b;">题库加载失败: ' + dataFile + '</div>';
  };
  document.head.appendChild(script);
}
'''

c = c.replace(insert_after, insert_after + new_fns)

# ========== 6. Modify save/load to use separate global + progress storage ==========
old_save = '''async function saveUserData() {
  if (gameState.isGuest || !gameState.studentId) return;
  try {
    const key = 'scienceGame' + CLOUD_GRADE_KEY.replace('grade','') + '_user_' + gameState.studentId;
    const data = { ... };
  } catch(e) {}
}'''

# Replace the saveUserData function
old_save_fn = '''function saveUserData() {
  if (gameState.isGuest || !gameState.studentId) return;
  try {
    const key = 'scienceGame' + CLOUD_GRADE_KEY.replace('grade','') + '_user_' + gameState.studentId;
    localStorage.setItem(key, JSON.stringify(gameState));
  } catch(e) {}
  // 保存当前课程进度到独立 key
  if (currentCourse) {
    try {
      const progressKey = 'progress_grade' + currentCourse.grade + currentCourse.sem + '_' + gameState.studentId;
      localStorage.setItem(progressKey, JSON.stringify(gameState.lessonProgress || {}));
    } catch(e) {}
  }
  // 云同步
  saveToCloud(gameState.studentId, gameState);'''

new_save_fn = '''function saveUserData() {
  if (gameState.isGuest || !gameState.studentId) return;
  try {
    const key = 'scienceGame_user_' + gameState.studentId;
    // 只保存全局数据（不保留 lessonProgress，因为那是按课程分开的）
    const globalData = {
      totalPoints: gameState.totalPoints,
      equipment: gameState.equipment,
      equippedSlots: gameState.equippedSlots,
      pets: gameState.pets,
      petPieces: gameState.petPieces,
      unlockedAchievements: gameState.unlockedAchievements,
      totalQuestionsAnswered: gameState.totalQuestionsAnswered,
      totalCorrectAnswers: gameState.totalCorrectAnswers
    };
    localStorage.setItem(key, JSON.stringify(globalData));
  } catch(e) {}
  // 保存当前课程进度到独立 key
  if (currentCourse) {
    try {
      const progressKey = 'progress_grade' + currentCourse.grade + currentCourse.sem + '_' + gameState.studentId;
      localStorage.setItem(progressKey, JSON.stringify(gameState.lessonProgress || {}));
    } catch(e) {}
  }
  // 云同步
  saveToCloud(gameState.studentId, gameState);'''

c = c.replace(old_save_fn, new_save_fn)

# ========== 7. Change loadUserData ==========
old_load = "const key = 'scienceGame' + CLOUD_GRADE_KEY.replace('grade','') + '_user_' + gameState.studentId;"
new_load = "const key = 'scienceGame_user_' + gameState.studentId;"
c = c.replace(old_load, new_load)

# ========== 8. Save changes ==========
if c != orig:
    with open(PATH, 'w', encoding='utf-8') as f:
        f.write(c)
    print('Transform complete!')
else:
    print('No changes needed')
