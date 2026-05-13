#!/usr/bin/env python3
"""Sync tower modal and bug fixes from grade 6 to grades 3/4/5"""
import os, re

BASE = r'C:\Users\tanc\Documents\WPSDrive\362543761\WPS云盘\谭政\科学复习系统\_kexvefuxi'
G6_PATH = os.path.join(BASE, '6', '2', 'index.html')

def get_grade_key(grade):
    return {
        'grade_key': f'grade{grade}',
        'ranking_key': f'grade{grade}2',
        'equip_fn': f'calcEquippedBonus{grade}2',
        'data_key': f'{grade}-2-lessons.js',
        'grade_label': f'{grade}年级'
    }

def patch_grade(grade):
    with open(G6_PATH, 'r', encoding='utf-8') as f:
        g6 = f.read()
    
    path = os.path.join(BASE, grade, '2', 'index.html')
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changed = False
    
    # 1. Check if tower CSS exists
    if '.tower-modal' not in content:
        # Find the pet-modal CSS end and add tower CSS after it
        tower_css_start = g6.find('/* ====== 爬塔弹窗 ====== */')
        tower_css_end = g6.find('</style>')
        tower_css = g6[tower_css_start:tower_css_end]
        
        # Insert tower CSS before </style>
        content = content.replace('</style>', tower_css + '\n</style>')
        changed = True
        print(f'  Grade {grade}: added tower CSS')
    
    # 2. Check if tower modal HTML exists
    if 'towerModal' not in content:
        # Find the tower modal HTML from grade 6
        tower_html_start = g6.find('<!-- ====== 爬塔弹窗 ====== -->')
        tower_html_end = g6.find('<script>\nconst equipmentSystem = {')
        tower_html = g6[tower_html_start:tower_html_end]
        
        # Insert before <script>const equipmentSystem
        content = content.replace('<script>\nconst equipmentSystem = {', 
                                  tower_html + '\n<script>\nconst equipmentSystem = {')
        changed = True
        print(f'  Grade {grade}: added tower HTML')
    
    # 3. Check if tower button exists in status bar
    if 'showTowerModal()' not in content:
        # Add tower button after pet button
        content = content.replace(
            'id="petBtn"',
            'id="towerBtn"\n    <div class="status-item" style="cursor:pointer;" onclick="showTowerModal()">\n      🏰 <span class="status-label">爬塔</span>\n    </div>\n    <div class="status-item" id="petBtn"'
        )
        changed = True
        print(f'  Grade {grade}: added tower button')
    
    # 4. Check if tower modal functions exist
    if 'function showTowerModal' not in content:
        # Add tower modal functions before "// 切换排行榜Tab"
        tower_js = '''
// ====== 爬塔弹窗 ======
function showTowerModal() {
  const modal = document.getElementById('towerModal');
  const iframe = document.getElementById('towerIframe');
  modal.classList.add('show');
  iframe.src = '../../tower.html?' + Date.now();
  iframe.onload = function() {
    iframe.contentWindow.postMessage({
      type: 'init_tower',
      studentId: gameState.studentId,
      saveData: {
        totalPoints: gameState.totalPoints || 0,
        equipment: gameState.equipment || [],
        unlockedAchievements: gameState.unlockedAchievements || [],
        lessonProgress: gameState.lessonProgress || {}
      }
    }, '*');
  };
}
function closeTowerModal() {
  document.getElementById('towerModal').classList.remove('show');
}

// 监听爬塔发来的积分变动
window.addEventListener('message', function(e) {
  if (e.data && e.data.type === 'tower_change') {
    if (gameState) {
      gameState.totalPoints = e.data.points || gameState.totalPoints;
      updateStatusBar();
      saveUserData();
    }
  }
});

'''
        content = content.replace('// 切换排行榜Tab', tower_js + '\n// 切换排行榜Tab')
        changed = True
        print(f'  Grade {grade}: added tower JS')
    
    # 5. Update tower button if it uses window.location.href
    if 'window.location.href' in (content[content.find('towerBtn'):content.find('towerBtn')+200] if 'towerBtn' in content else ''):
        content = content.replace(
            'onclick="window.location.href=\'../../tower.html\'"',
            'onclick="showTowerModal()"'
        )
        changed = True
        print(f'  Grade {grade}: updated tower button to modal')
    
    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'  Grade {grade}: ALL CHANGES APPLIED')
    else:
        print(f'  Grade {grade}: no changes needed')

for g in ['3', '4', '5']:
    print(f'Processing Grade {g}...')
    patch_grade(g)

print('DONE')
