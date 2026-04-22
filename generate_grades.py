# -*- coding: utf-8 -*-
"""生成四年级和六年级单人选关页面"""

GRADE = "6"
GRADE_NAME = "六年级"
GRADE_FILE = "6-2"
SUBTITLE = "六年级下册 · 科学趣味闯关"

# 六年级单元信息
UNITS_6 = [
    {"id": 1, "emoji": "💡", "name": "设计与技术",
     "lessons": [
         {"id": 1, "name": "好设计", "desc": "构思·制作·改进", "color": "#4ade80"},
         {"id": 2, "name": "热传递", "desc": "热的传导", "color": "#60a5fa"},
         {"id": 3, "name": "改造物品", "desc": "变废为宝", "color": "#f97316"},
         {"id": 4, "name": "仿生学", "desc": "大自然的启发", "color": "#c084fc"},
     ]},
    {"id": 2, "emoji": "⚡", "name": "能量",
     "lessons": [
         {"id": 5, "name": "能量的形式", "desc": "光能·电能·热能·磁能", "color": "#60a5fa"},
         {"id": 6, "name": "能量转换", "desc": "从一种变成另一种", "color": "#fbbf24"},
         {"id": 7, "name": "风能与水能", "desc": "清洁可再生能源", "color": "#4ade80"},
         {"id": 8, "name": "电磁铁", "desc": "电与磁的结合", "color": "#a78bfa"},
     ]},
    {"id": 3, "emoji": "🌿", "name": "生物与环境",
     "lessons": [
         {"id": 9, "name": "动物与环境", "desc": "适应与生存", "color": "#f97316"},
         {"id": 10, "name": "食物链", "desc": "吃与被吃的关系", "color": "#fb923c"},
         {"id": 11, "name": "生态系统", "desc": "生物与环境整体", "color": "#34d399"},
     ]},
    {"id": 4, "emoji": "🌍", "name": "自然资源",
     "lessons": [
         {"id": 12, "name": "可再生与不可再生", "desc": "资源的分类", "color": "#c084fc"},
         {"id": 13, "name": "水资源保护", "desc": "珍惜每一滴水", "color": "#60a5fa"},
         {"id": 14, "name": "空气与垃圾分类", "desc": "保护环境", "color": "#94a3b8"},
         {"id": 15, "name": "绿色生活", "desc": "从身边做起", "color": "#4ade80"},
     ]},
]

DIFFICULTY = [
    {"id": "basic", "label": "🌱 基础关", "emoji": "🌱", "color": "#4ade80", "desc": "课本基础知识"},
    {"id": "advance", "label": "🚀 挑战关", "emoji": "🚀", "color": "#f97316", "desc": "综合运用能力"},
]

UNIT_CSS = """  .unit-card { cursor: pointer; transition: all 0.3s; }
  .unit-card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(0,0,0,0.3); }
  .lesson-btn { transition: all 0.2s; }
  .lesson-btn:hover { opacity: 0.85; transform: scale(1.03); }
  .diff-btn { transition: all 0.2s; cursor: pointer; border: 2px solid rgba(255,255,255,0.15); }
  .diff-btn:hover { transform: scale(1.05); }
  .diff-btn.selected { border-width: 3px; transform: scale(1.06); }
  .progress-ring { transform: rotate(-90deg); transform-origin: 50% 50%; }
  .hint-text { font-size: 0.9em; color: #ffd93d; margin-top: 10px; padding: 10px; background: rgba(255,217,61,0.1); border-radius: 10px; }
"""

HTML_TEMPLATE = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>科学探险家 · {SUBTITLE}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: "微软雅黑", "PingFang SC", sans-serif;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    min-height: 100vh;
    color: #fff;
    overflow-x: hidden;
  }}
  .particles {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 0; overflow: hidden; }}
  .particle {{ position: absolute; width: 6px; height: 6px; background: rgba(255,255,255,0.3); border-radius: 50%; animation: float 15s infinite; }}
  @keyframes float {{ 0%,100% {{ transform: translateY(100vh) rotate(0deg); opacity: 0; }} 10% {{ opacity: 1; }} 90% {{ opacity: 1; }} 100% {{ transform: translateY(-100vh) rotate(720deg); opacity: 0; }} }}
  .container {{ position: relative; z-index: 1; max-width: 900px; margin: 0 auto; padding: 20px 15px; }}
  .header {{ text-align: center; margin-bottom: 30px; padding: 30px 20px; background: rgba(255,255,255,0.05); border-radius: 24px; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px); }}
  .header h1 {{ font-size: 2em; margin-bottom: 10px; background: linear-gradient(90deg, #4ade80, #60a5fa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
  .header p {{ color: rgba(255,255,255,0.6); font-size: 0.95em; }}
  .units-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 30px; }}
  .unit-card {{ border-radius: 20px; padding: 20px; border: 2px solid rgba(255,255,255,0.1); background: rgba(255,255,255,0.05); transition: all 0.3s; cursor: pointer; }}
  .unit-card:hover {{ transform: translateY(-4px); box-shadow: 0 12px 40px rgba(0,0,0,0.3); border-color: rgba(255,255,255,0.3); }}
  .unit-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 15px; }}
  .unit-emoji {{ font-size: 2.5em; }}
  .unit-title {{ font-size: 1.2em; font-weight: bold; }}
  .unit-sub {{ font-size: 0.8em; color: rgba(255,255,255,0.5); }}
  .lessons-list {{ display: flex; flex-direction: column; gap: 8px; }}
  .lesson-btn {{ padding: 10px 14px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); background: rgba(255,255,255,0.05); color: #fff; cursor: pointer; font-family: inherit; font-size: 0.9em; text-align: left; transition: all 0.2s; }}
  .lesson-btn:hover {{ background: rgba(255,255,255,0.12); transform: scale(1.02); }}
  .lesson-name {{ font-weight: bold; }}
  .lesson-desc {{ font-size: 0.8em; opacity: 0.7; }}
  .lesson-nums {{ font-size: 0.75em; opacity: 0.5; margin-top: 2px; }}
  .back-btn {{ display: inline-flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: rgba(255,255,255,0.7); padding: 12px 24px; border-radius: 30px; font-size: 0.9em; cursor: pointer; font-family: inherit; transition: all 0.3s; text-decoration: none; }}
  .back-btn:hover {{ background: rgba(255,255,255,0.2); color: #fff; }}

  /* 游戏界面 */
  #gameScreen {{ display: none; }}
  .game-card {{ background: rgba(255,255,255,0.07); border-radius: 24px; padding: 25px; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px); }}
  .game-top {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px; }}
  .game-info {{ display: flex; align-items: center; gap: 15px; }}
  .progress-ring-wrap {{ position: relative; width: 70px; height: 70px; }}
  .progress-ring {{ transform: rotate(-90deg); transform-origin: 50% 50%; }}
  .progress-ring-bg {{ fill: none; stroke: rgba(255,255,255,0.1); stroke-width: 6; }}
  .progress-ring-fill {{ fill: none; stroke-width: 6; stroke-linecap: round; transition: stroke-dashoffset 0.3s; }}
  .progress-ring-text {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); font-size: 1.1em; font-weight: bold; }}
  .game-title {{ font-size: 1.1em; font-weight: bold; }}
  .game-sub {{ font-size: 0.8em; color: rgba(255,255,255,0.5); }}
  .back-to-units {{ background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: #fff; padding: 10px 20px; border-radius: 20px; font-size: 0.9em; cursor: pointer; font-family: inherit; transition: all 0.3s; }}
  .back-to-units:hover {{ background: rgba(255,255,255,0.2); }}
  .q-card {{ background: rgba(255,255,255,0.08); border-radius: 20px; padding: 20px; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1); text-align: center; }}
  .q-unit-tag {{ display: inline-block; padding: 3px 14px; border-radius: 20px; font-size: 0.8em; margin-bottom: 10px; }}
  .q-text {{ font-size: 1.25em; font-weight: bold; line-height: 1.6; }}
  .opts-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
  .opt-btn {{ background: rgba(255,255,255,0.1); border: 2px solid rgba(255,255,255,0.15); border-radius: 14px; padding: 14px 12px; color: #fff; font-size: 1em; cursor: pointer; font-family: inherit; transition: all 0.15s; text-align: center; min-height: 54px; touch-action: manipulation; -webkit-tap-highlight-color: transparent; user-select: none; }}
  .opt-btn:hover:not(.disabled):not(.correct):not(.wrong) {{ background: rgba(255,255,255,0.18); border-color: rgba(255,255,255,0.35); }}
  .opt-btn.correct {{ background: rgba(76,175,80,0.3); border-color: #4caf50; color: #4caf50; animation: pop 0.4s; }}
  .opt-btn.wrong {{ background: rgba(244,67,54,0.3); border-color: #f44336; color: #f44336; animation: shake 0.4s; }}
  .opt-btn.disabled {{ opacity: 0.5; cursor: not-allowed; }}
  @keyframes pop {{ 0%{{transform:scale(1)}} 50%{{transform:scale(1.08)}} 100%{{transform:scale(1)}} }}
  @keyframes shake {{ 0%,100%{{transform:translateX(0)}} 25%{{transform:translateX(-5px)}} 75%{{transform:translateX(5px)}} }}
  .hint-box {{ margin-top: 12px; padding: 10px 16px; background: rgba(255,217,61,0.1); border: 1px solid rgba(255,217,61,0.3); border-radius: 12px; font-size: 0.88em; color: #ffd93d; display: none; }}
  .hint-box.show {{ display: block; animation: fadeIn 0.3s; }}
  @keyframes fadeIn {{ from{{opacity:0;transform:translateY(-5px)}} to{{opacity:1;transform:translateY(0)}} }}
  .hint-btn {{ background: rgba(255,217,61,0.15); border: 1px solid rgba(255,217,61,0.3); color: #ffd93d; padding: 8px 16px; border-radius: 20px; font-size: 0.85em; cursor: pointer; font-family: inherit; margin-top: 10px; transition: all 0.2s; }}
  .hint-btn:hover {{ background: rgba(255,217,61,0.25); }}
  .next-btn {{ background: linear-gradient(135deg, #4ade80, #22c55e); border: none; color: #fff; padding: 14px 30px; border-radius: 30px; font-size: 1em; font-weight: bold; cursor: pointer; font-family: inherit; margin-top: 15px; transition: all 0.3s; display: none; }}
  .next-btn.show {{ display: inline-block; }}
  .next-btn:hover {{ transform: scale(1.05); box-shadow: 0 6px 20px rgba(74,222,128,0.4); }}
  .stats-row {{ display: flex; gap: 20px; margin-bottom: 15px; flex-wrap: wrap; }}
  .stat-item {{ flex: 1; text-align: center; background: rgba(255,255,255,0.05); border-radius: 16px; padding: 15px; min-width: 100px; }}
  .stat-val {{ font-size: 2em; font-weight: 900; }}
  .stat-lbl {{ font-size: 0.8em; color: rgba(255,255,255,0.5); }}
  .result-panel {{ text-align: center; }}
  .result-stars {{ font-size: 3em; margin-bottom: 15px; }}
  .result-title {{ font-size: 1.8em; font-weight: 900; margin-bottom: 10px; }}
  .result-sub {{ color: rgba(255,255,255,0.6); font-size: 0.95em; margin-bottom: 20px; }}
  .result-btns {{ display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; }}
  .replay-btn {{ background: linear-gradient(135deg, #4ade80, #22c55e); border: none; color: #fff; padding: 14px 30px; border-radius: 30px; font-size: 1em; font-weight: bold; cursor: pointer; font-family: inherit; transition: all 0.3s; }}
  .replay-btn:hover {{ transform: scale(1.05); box-shadow: 0 6px 20px rgba(74,222,128,0.4); }}
  .replay-btn.secondary {{ background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); font-weight: normal; }}
  @media(max-width:768px){{ .units-grid{{grid-template-columns:1fr}} .opts-grid{{grid-template-columns:1fr}} .stat-item{{min-width:80px}} }}
  @media(max-width:480px){{ .header h1{{font-size:1.5em}} .q-text{{font-size:1.1em}} }}
</style>
</head>
<body>
<div class="particles" id="particles"></div>

<div class="container" id="homeScreen">
  <div class="header">
    <h1>🔬 科学探险家</h1>
    <p>{SUBTITLE} · 选择单元开始闯关</p>
  </div>
  <div class="units-grid" id="unitsGrid"></div>
  <a class="back-btn" href="../">← 返回首页</a>
</div>

<div class="container" id="gameScreen">
  <div class="game-card">
    <div class="game-top">
      <div class="game-info">
        <div class="progress-ring-wrap">
          <svg class="progress-ring" width="70" height="70">
            <circle class="progress-ring-bg" cx="35" cy="35" r="28"/>
            <circle class="progress-ring-fill" id="progressRing" cx="35" cy="35" r="28" stroke-dasharray="175.9" stroke-dashoffset="0"/>
          </svg>
          <span class="progress-ring-text" id="progressText">0/0</span>
        </div>
        <div>
          <div class="game-title" id="gameTitle">—</div>
          <div class="game-sub" id="gameSub">—</div>
        </div>
      </div>
      <button class="back-to-units" onclick="backToUnits()">← 重选单元</button>
    </div>

    <div class="stats-row">
      <div class="stat-item"><div class="stat-val" id="correctCount" style="color:#4ade80">0</div><div class="stat-lbl">答对</div></div>
      <div class="stat-item"><div class="stat-val" id="wrongCount" style="color:#f97316">0</div><div class="stat-lbl">答错</div></div>
      <div class="stat-item"><div class="stat-val" id="scoreDisplay" style="color:#ffd93d">0</div><div class="stat-lbl">积分</div></div>
    </div>

    <div class="q-card">
      <div class="q-unit-tag" id="qUnitTag"></div>
      <div class="q-text" id="qText">—</div>
    </div>

    <div class="opts-grid" id="optsGrid"></div>
    <div class="hint-box" id="hintBox"></div>
    <button class="hint-btn" id="hintBtn" onclick="showHint()">💡 提示</button>
    <div style="text-align:center"><button class="next-btn" id="nextBtn" onclick="nextQ()">下一题 →</button></div>
  </div>

  <div style="text-align:center; margin-top:20px;">
    <div class="result-panel" id="resultPanel" style="display:none;"></div>
  </div>
</div>

<script src="../data/{GRADE_FILE}.js"></script>
<script>
const bank = window.QUESTION_BANK_{GRADE.replace("-","_").upper()};
const G = {{
  unit: 1, lesson: null, difficulty: 'basic',
  questions: [], qIndex: 0,
  correct: 0, wrong: 0, score: 0,
  hintUsed: false, done: false
}};

const UNITS = {UNITS_6};
const DIFF = {DIFFICULTY};

// 粒子
(function(){{
  const c = document.getElementById('particles');
  for(let i=0;i<25;i++){{
    const p = document.createElement('div');
    p.className='particle';
    p.style.left=Math.random()*100+'%';
    p.style.animationDelay=Math.random()*15+'s';
    p.style.animationDuration=(10+Math.random()*10)+'s';
    c.appendChild(p);
  }}
}})();

// 渲染单元选择
function renderUnits() {{
  const grid = document.getElementById('unitsGrid');
  grid.innerHTML = '';
  UNITS.forEach(unit => {{
    const card = document.createElement('div');
    card.className = 'unit-card';
    card.innerHTML = `
      <div class="unit-header">
        <span class="unit-emoji">{{{{unit.emoji}}}}</span>
        <div><div class="unit-title">{{{{unit.name}}}}</div><div class="unit-sub">共{{{{unit.lessons.length}}}}课</div></div>
      </div>
      <div class="lessons-list">
        {{{unit.lessons.map(l => `
          <button class="lesson-btn" style="background:{{l.color}}22;border-color:{{l.color}}55"
            onclick="selectLesson({{unit.id}},{{l.id}},'basic')">
            <div class="lesson-name">{{{{l.emoji}}}} {{{{/l.name}}}}</div>
            <div class="lesson-desc">{{{{l.desc}}}}</div>
          </button>
        `).join('')}}}
      </div>
    `;
    grid.appendChild(card);
  }});
}}

function selectLesson(unitId, lessonId, difficulty) {{
  G.unit = unitId;
  G.difficulty = difficulty;
  const unit = UNITS.find(u=>u.id===unitId);
  const lesson = unit.lessons.find(l=>l.id===lessonId);
  const lessonData = bank[unitId].lessons[lessonId];
  if (!lessonData || !lessonData[difficulty]) {{ alert('本题库暂缺此课内容'); return; }}
  G.questions = [...lessonData[difficulty]].sort(()=>Math.random()-0.5);
  G.qIndex = 0; G.correct=0; G.wrong=0; G.score=0; G.hintUsed=false; G.done=false;
  document.getElementById('homeScreen').style.display='none';
  document.getElementById('gameScreen').style.display='block';
  document.getElementById('gameTitle').textContent = `${{unit.emoji}} ${{unit.name}} · ${{lesson.name}}`;
  document.getElementById('gameSub').textContent = DIFF.find(d=>d.id===difficulty).label;
  document.getElementById('resultPanel').style.display='none';
  showQ();
}}

function showQ() {{
  const q = G.questions[G.qIndex];
  const total = G.questions.length;
  const pct = G.qIndex / total * 100;
  const circumference = 2 * Math.PI * 28;
  const offset = circumference * pct / 100;
  document.getElementById('progressRing').setAttribute('stroke-dashoffset', offset);
  document.getElementById('progressText').textContent = `${{G.qIndex+1}}/${{total}}`;
  document.getElementById('qText').textContent = q.q;
  const unit = UNITS.find(u=>u.id===G.unit);
  document.getElementById('qUnitTag').textContent = `${{unit.emoji}} ${{unit.name}}`;
  document.getElementById('qUnitTag').style.background = 'rgba(255,255,255,0.1)';
  document.getElementById('correctCount').textContent = G.correct;
  document.getElementById('wrongCount').textContent = G.wrong;
  document.getElementById('scoreDisplay').textContent = G.score;
  const grid = document.getElementById('optsGrid');
  grid.innerHTML = q.opts.map((opt,i)=>`
    <button class="opt-btn" id="opt-${{i}}" onclick="ans(${{i}})">${{opt}}</button>
  `).join('');
  document.getElementById('hintBox').className='hint-box';
  document.getElementById('hintBox').textContent='💡 '+q.hint;
  document.getElementById('hintBtn').style.display='';
  document.getElementById('nextBtn').className='next-btn';
}}

function ans(idx) {{
  const q = G.questions[G.qIndex];
  const btns = document.querySelectorAll('.opt-btn');
  btns.forEach(b=>b.classList.add('disabled'));
  const ok = idx===q.answer;
  if(ok) {{
    btns[idx].classList.add('correct');
    G.correct++;
    G.score += G.difficulty==='basic' ? 10 : 15;
  }} else {{
    btns[idx].classList.add('wrong');
    btns[q.answer].classList.add('correct');
    G.wrong++;
  }}
  document.getElementById('correctCount').textContent=G.correct;
  document.getElementById('wrongCount').textContent=G.wrong;
  document.getElementById('scoreDisplay').textContent=G.score;
  document.getElementById('hintBtn').style.display='none';
  setTimeout(()=>{{
    document.getElementById('hintBox').classList.add('show');
  }},300);
  document.getElementById('nextBtn').className='next-btn show';
}}

function showHint() {{
  document.getElementById('hintBox').classList.add('show');
}}

function nextQ() {{
  G.qIndex++;
  if(G.qIndex>=G.questions.length) {{ showResult(); }}
  else {{ showQ(); }}
}}

function showResult() {{
  G.done=true;
  const total=G.questions.length;
  const pct=Math.round(G.correct/total*100);
  const stars = pct>=90?3:pct>=70?2:pct>=50?1:0;
  const titles=['加油！','不错！','很棒！','太厉害了！'];
  const resultTitles=['继续努力','表现不错','很优秀','满分通关！'];
  const resultPanel=document.getElementById('resultPanel');
  resultPanel.style.display='block';
  resultPanel.innerHTML=`
    <div class="result-stars">${{'⭐'.repeat(stars)}}</div>
    <div class="result-title">${{resultTitles[stars]}}</div>
    <div class="result-sub">答对 ${{G.correct}} / ${{total}} 题 · 得分 ${{G.score}} 分</div>
    <div class="result-btns">
      <button class="replay-btn" onclick="replay()">再闯一次</button>
      <button class="replay-btn secondary" onclick="backToUnits()">返回选课</button>
    </div>
  `;
  document.getElementById('nextBtn').className='next-btn';
}

function replay() {{
  G.questions.sort(()=>Math.random()-0.5);
  G.qIndex=0; G.correct=0; G.wrong=0; G.score=0;
  document.getElementById('resultPanel').style.display='none';
  showQ();
}}

function backToUnits() {{
  document.getElementById('homeScreen').style.display='block';
  document.getElementById('gameScreen').style.display='none';
  document.getElementById('gameScreen').scrollIntoView();
}}

renderUnits();
</script>
</body>
</html>
"""

# Fix the JS variable name issue
html_out = HTML_TEMPLATE.format(
    UNITS_6=str(UNITS_6).replace("'", "'").replace("'", "'"),
    DIFFICULTY=str(DIFFICULTY).replace("'", "'").replace("'", "'")
)
# Actually don't format, just write
import re
# Replace Python-format strings with JS-safe content
html_out = HTML_TEMPLATE

# Fix the UNITS_6 and DIFFICULTY JS arrays
units_str = str(UNITS_6).replace("'", "\\'")
diff_str = str(DIFFICULTY).replace("'", "\\'")
html_out = html_out.replace('"{{UNITS_6}}"', units_str)
html_out = html_out.replace('"{{DIFFICULTY}}"', diff_str)

# Fix double braces in template literals
html_out = html_out.replace('{{{{', '${')
html_out = html_out.replace('}}}}', '}')
# Fix the f-string remaining issues
# Actually let me just do it properly

units_js = str(UNITS_6).replace("'", "\\'")
diff_js = str(DIFFICULTY).replace("'", "\\'")

# Build properly
units_lines = []
for u in UNITS_6:
    lessons_lines = []
    for l in u['lessons']:
        lessons_lines.append(
            f'{{id:{l["id"]}, name:"{l["name"]}", desc:"{l["desc"]}", color:"{l["color"]}"}}'
        )
    units_lines.append(
        f'{{id:{u["id"]}, emoji:"{u["emoji"]}", name:"{u["name"]}", lessons:[{",".join(lessons_lines)}]}}'
    )
units_js = '[' + ','.join(units_lines) + ']'

diff_lines = []
for d in DIFFICULTY:
    diff_lines.append(f'{{id:"{d["id"]}", label:"{d["label"]}", emoji:"{d["emoji"]}", color:"{d["color"]}"}}')
diff_js = '[' + ','.join(diff_lines) + ']'

html_out = HTML_TEMPLATE
html_out = html_out.replace('"{{UNITS_6}}"', units_js)
html_out = html_out.replace('"{{DIFFICULTY}}"', diff_js)
html_out = html_out.replace('{{{{', '${{')
html_out = html_out.replace('}}}}', '}}$')

# Also fix UNITS variable name
html_out = html_out.replace('const UNITS = {UNITS_6};', 'const UNITS = ' + units_js + ';')
html_out = html_out.replace('const DIFF = {DIFFICULTY};', 'const DIFF = ' + diff_js + ';')

# Fix bank variable name
html_out = html_out.replace(
    "const bank = window.QUESTION_BANK_{GRADE.replace(\\"-\\",\"_\\").upper()};",
    f"const bank = window.QUESTION_BANK_{GRADE.replace('-','_').upper()};"
)

# Write output
output_path = rf'c:\Users\Administrator\Desktop\四2班科学\_kexvefuxi\{GRADE_FILE}\index.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_out)

print(f'生成完成: {output_path}')
