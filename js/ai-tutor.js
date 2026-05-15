/**
 * AI讲解系统 — 错题分析 + 每日训练推荐
 * 依赖: gameState.wrongQuestions, API_BASE (来自 cloud-config.js)
 * v1.0 - 2026-05-15
 */

(function() {
  'use strict';

  var API_BASE = (typeof window.API_BASE_URL !== 'undefined') ? window.API_BASE_URL : 'https://api.kexvefuxi.cn';

  // ==================== CSS 样式 ====================
  function injectStyles() {
    if (document.getElementById('aiTutorStyles')) return;
    var styles = document.createElement('style');
    styles.id = 'aiTutorStyles';
    styles.textContent = `
.ai-tutor-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.85);
  display: none; justify-content: center; align-items: center;
  z-index: 10100; animation: fadeIn 0.3s ease;
}
.ai-tutor-overlay.show { display: flex; }
.ai-tutor-card {
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
  border-radius: 20px; width: 92%; max-width: 700px; max-height: 85vh;
  overflow: hidden; border: 1px solid rgba(100,140,255,0.25);
  box-shadow: 0 20px 60px rgba(0,0,0,0.6), 0 0 80px rgba(100,140,255,0.1);
  display: flex; flex-direction: column;
}
.ai-tutor-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 18px 24px;
  background: linear-gradient(90deg, rgba(100,140,255,0.15), rgba(100,200,255,0.05));
  border-bottom: 1px solid rgba(100,140,255,0.2);
}
.ai-tutor-title {
  font-size: 20px; font-weight: 700; color: #fff;
  display: flex; align-items: center; gap: 10px;
}
.ai-tutor-close {
  background: none; border: none; color: rgba(255,255,255,0.5);
  font-size: 24px; cursor: pointer; padding: 4px 10px; border-radius: 8px;
  transition: all 0.2s;
}
.ai-tutor-close:hover { color: #fff; background: rgba(255,255,255,0.1); }

/* Tabs */
.ai-tutor-tabs {
  display: flex; border-bottom: 1px solid rgba(100,140,255,0.15);
  background: rgba(0,0,0,0.2);
}
.ai-tutor-tab {
  flex: 1; padding: 14px 20px; text-align: center; cursor: pointer;
  color: rgba(255,255,255,0.5); font-size: 15px; font-weight: 600;
  border-bottom: 2px solid transparent; transition: all 0.25s;
}
.ai-tutor-tab:hover { color: rgba(255,255,255,0.8); background: rgba(100,140,255,0.05); }
.ai-tutor-tab.active {
  color: #64b5f6; border-bottom-color: #64b5f6;
  background: rgba(100,140,255,0.08);
}

/* Content Area */
.ai-tutor-content {
  flex: 1; overflow-y: auto; padding: 20px 24px;
}
.ai-tutor-content::-webkit-scrollbar { width: 6px; }
.ai-tutor-content::-webkit-scrollbar-thumb { background: rgba(100,140,255,0.3); border-radius: 3px; }

/* Loading */
.ai-tutor-loading {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 60px 20px; color: rgba(255,255,255,0.6);
}
.ai-tutor-spinner {
  width: 48px; height: 48px; border: 3px solid rgba(100,140,255,0.2);
  border-top: 3px solid #64b5f6; border-radius: 50%;
  animation: aiSpin 0.8s linear infinite; margin-bottom: 16px;
}
@keyframes aiSpin { to { transform: rotate(360deg); } }
.ai-tutor-loading-text { font-size: 16px; }
.ai-tutor-loading-hint { font-size: 13px; margin-top: 8px; color: rgba(255,255,255,0.35); }

/* Error */
.ai-tutor-error {
  text-align: center; padding: 40px 20px; color: #ef5350;
}
.ai-tutor-error-icon { font-size: 48px; margin-bottom: 12px; }
.ai-tutor-retry-btn {
  margin-top: 16px; padding: 10px 28px; background: linear-gradient(135deg, #ef5350, #e53935);
  border: none; border-radius: 10px; color: #fff; font-size: 15px; cursor: pointer;
}

/* Analysis Card */
.ai-analysis-card {
  background: rgba(255,255,255,0.05); border-radius: 14px; padding: 18px;
  margin-bottom: 14px; border: 1px solid rgba(255,255,255,0.08);
  transition: all 0.2s;
}
.ai-analysis-card:hover { border-color: rgba(100,140,255,0.3); background: rgba(255,255,255,0.07); }
.ai-analysis-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 10px;
}
.ai-analysis-question {
  color: #e0e0e0; font-size: 14px; line-height: 1.6; flex: 1;
}
.ai-analysis-badge {
  font-size: 11px; padding: 3px 10px; border-radius: 12px; white-space: nowrap;
  margin-left: 12px;
}
.ai-badge-wrong { background: rgba(239,83,80,0.2); color: #ef5350; }
.ai-badge-correct { background: rgba(102,187,106,0.2); color: #66bb6a; }
.ai-analysis-answers {
  display: flex; gap: 16px; margin: 8px 0; font-size: 13px;
}
.ai-answer-wrong { color: #ef5350; }
.ai-answer-right { color: #66bb6a; }
.ai-analysis-explain {
  color: rgba(255,255,255,0.65); font-size: 13px; line-height: 1.7;
  margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.06);
}
.ai-knowledge-tag {
  display: inline-block; margin-top: 8px; padding: 4px 12px;
  background: rgba(100,140,255,0.15); color: #90caf9;
  border-radius: 10px; font-size: 12px;
}

/* Training Card */
.ai-training-card {
  background: rgba(255,255,255,0.05); border-radius: 14px; padding: 18px;
  margin-bottom: 14px; border: 1px solid rgba(255,255,255,0.08);
}
.ai-training-topic {
  font-size: 16px; font-weight: 700; color: #fff; margin-bottom: 4px;
}
.ai-training-target {
  font-size: 12px; color: rgba(255,255,255,0.45); margin-bottom: 12px;
}
.ai-training-question {
  background: rgba(0,0,0,0.25); border-radius: 10px; padding: 12px 16px;
  margin-bottom: 8px; color: rgba(255,255,255,0.8); font-size: 13px;
  line-height: 1.6; border-left: 3px solid rgba(100,140,255,0.3);
}

/* Encouragement */
.ai-encourage {
  text-align: center; padding: 16px; margin-top: 8px;
  color: rgba(255,255,255,0.5); font-size: 14px; font-style: italic;
}
.ai-encourage-icon { font-size: 32px; display: block; margin-bottom: 8px; }

/* No data */
.ai-tutor-empty {
  text-align: center; padding: 60px 20px; color: rgba(255,255,255,0.45);
}
.ai-tutor-empty-icon { font-size: 64px; display: block; margin-bottom: 12px; }

/* Fix button in wrong-question-actions */
.wrong-ai-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none; border-radius: 12px;
  color: #fff; font-size: 15px; font-weight: 600;
  cursor: pointer; transition: all 0.2s;
  box-shadow: 0 4px 15px rgba(102,126,234,0.3);
}
.wrong-ai-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102,126,234,0.5);
}
.wrong-ai-btn:active { transform: translateY(0); }

/* Responsive tab content */
.ai-tab-content { display: none; }
.ai-tab-content.active { display: block; }

/* Raw content fallback */
.ai-raw-content {
  color: rgba(255,255,255,0.7); font-size: 14px;
  line-height: 1.8; white-space: pre-wrap;
  padding: 16px; background: rgba(0,0,0,0.2);
  border-radius: 12px;
}
`;
    document.head.appendChild(styles);
  }

  // ==================== UI 创建 ====================
  function createUI() {
    if (document.getElementById('aiTutorOverlay')) return;
    var html = '' +
'<div class="ai-tutor-overlay" id="aiTutorOverlay">' +
'  <div class="ai-tutor-card">' +
'    <div class="ai-tutor-header">' +
'      <div class="ai-tutor-title">🤖 AI 智能讲解</div>' +
'      <button class="ai-tutor-close" onclick="closeAITutor()">✕</button>' +
'    </div>' +
'    <div class="ai-tutor-tabs">' +
'      <div class="ai-tutor-tab active" onclick="switchAITab(\'analysis\', this)">📖 错题讲解</div>' +
'      <div class="ai-tutor-tab" onclick="switchAITab(\'training\', this)">🎯 每日训练</div>' +
'    </div>' +
'    <div class="ai-tutor-content" id="aiTutorContent">' +
'      <div class="ai-tutor-empty">' +
'        <span class="ai-tutor-empty-icon">🧠</span>' +
'        <p>点击下方按钮，让 AI 帮你分析错题</p>' +
'      </div>' +
'    </div>' +
'    <div class="ai-tutor-actions" style="padding: 16px 24px; border-top: 1px solid rgba(255,255,255,0.06); display: flex; gap: 10px; justify-content: center;">' +
'      <button class="wrong-ai-btn" onclick="startAIAnalysis()" id="aiStartBtn">✨ 开始分析</button>' +
'    </div>' +
'  </div>' +
'</div>';
    document.body.insertAdjacentHTML('beforeend', html);
  }

  // ==================== 暴露到全局 ====================
  window.showAITutor = function() {
    injectStyles();
    createUI();
    document.getElementById('aiTutorOverlay').classList.add('show');
    // 重置内容
    var content = document.getElementById('aiTutorContent');
    if (content) {
      content.innerHTML = '<div class="ai-tutor-empty"><span class="ai-tutor-empty-icon">🧠</span><p>点击下方按钮，让 AI 帮你分析错题</p><p style="font-size:12px;color:rgba(255,255,255,0.3);">当前错题数：' + ((window.gameState && window.gameState.wrongQuestions) ? window.gameState.wrongQuestions.length : 0) + ' 道</p></div>';
    }
    // 重置tabs
    var tabs = document.querySelectorAll('.ai-tutor-tab');
    if (tabs.length > 0) {
      tabs.forEach(function(t) { t.classList.remove('active'); });
      tabs[0].classList.add('active');
    }
    var startBtn = document.getElementById('aiStartBtn');
    if (startBtn) { startBtn.style.display = ''; startBtn.textContent = '✨ 开始分析'; }
  };

  window.closeAITutor = function() {
    var overlay = document.getElementById('aiTutorOverlay');
    if (overlay) overlay.classList.remove('show');
  };

  window.switchAITab = function(tab, el) {
    // highlight tab
    document.querySelectorAll('.ai-tutor-tab').forEach(function(t) { t.classList.remove('active'); });
    if (el) el.classList.add('active');
    // show content
    var analysisEl = document.getElementById('aiAnalysisContent');
    var trainingEl = document.getElementById('aiTrainingContent');
    if (tab === 'analysis') {
      if (analysisEl) analysisEl.style.display = 'block';
      if (trainingEl) trainingEl.style.display = 'none';
    } else {
      if (analysisEl) analysisEl.style.display = 'none';
      if (trainingEl) trainingEl.style.display = 'block';
    }
  };

  window.startAIAnalysis = function() {
    var wrongQuestions = window.gameState && window.gameState.wrongQuestions ? window.gameState.wrongQuestions : [];
    if (!wrongQuestions || wrongQuestions.length === 0) {
      var content = document.getElementById('aiTutorContent');
      if (content) {
        content.innerHTML = '<div class="ai-tutor-error"><div class="ai-tutor-error-icon">😅</div><p>还没有错题记录哦！</p><p style="font-size:13px;color:rgba(255,255,255,0.4);">先去答题，做错的题目会自动记录下来</p></div>';
      }
      return;
    }

    // 显示加载状态
    var content = document.getElementById('aiTutorContent');
    if (content) {
      content.innerHTML = '' +
        '<div class="ai-tutor-loading">' +
        '  <div class="ai-tutor-spinner"></div>' +
        '  <div class="ai-tutor-loading-text">AI 正在分析你的 ' + wrongQuestions.length + ' 道错题...</div>' +
        '  <div class="ai-tutor-loading-hint">这可能需要 5-15 秒，请耐心等待</div>' +
        '</div>';
    }
    var startBtn = document.getElementById('aiStartBtn');
    if (startBtn) { startBtn.style.display = 'none'; }

    // 调用API
    var studentName = (window.gameState && window.gameState.studentName) || '同学';
    var grade = (window.gameState && window.gameState.currentGrade) || '';
    var payload = {
      wrongQuestions: wrongQuestions.slice(0, 20),
      studentName: studentName,
      grade: grade
    };

    fetch(API_BASE + '/api/ai-tutor', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    .then(function(resp) {
      if (!resp.ok) {
        return resp.json().then(function(err) { throw new Error(err.error || 'HTTP ' + resp.status); });
      }
      return resp.json();
    })
    .then(function(result) {
      if (!result.ok || !result.data) {
        throw new Error('AI 返回数据异常');
      }
      renderResult(result.data, result.meta);
    })
    .catch(function(err) {
      var content = document.getElementById('aiTutorContent');
      if (content) {
        content.innerHTML = '' +
          '<div class="ai-tutor-error">' +
          '  <div class="ai-tutor-error-icon">⚠️</div>' +
          '  <p>' + (err.message || '未知错误') + '</p>' +
          '  <button class="ai-tutor-retry-btn" onclick="startAIAnalysis()">🔄 重试</button>' +
          '</div>';
      }
      var startBtn = document.getElementById('aiStartBtn');
      if (startBtn) { startBtn.style.display = ''; startBtn.textContent = '🔄 重新分析'; }
      console.error('[AI-Tutor] Error:', err);
    });
  };

  function renderResult(data, meta) {
    var content = document.getElementById('aiTutorContent');
    if (!content) return;

    var analysisHTML = '';
    var trainingHTML = '';
    var encouragement = data.encouragement || '';

    // 错题讲解
    if (data.analysis && data.analysis.length > 0) {
      data.analysis.forEach(function(item, i) {
        analysisHTML += '' +
          '<div class="ai-analysis-card">' +
          '  <div class="ai-analysis-header">' +
          '    <div class="ai-analysis-question"><strong>#' + (i + 1) + '</strong> ' + escapeHTML(item.question || '') + '</div>' +
          '  </div>' +
          '  <div class="ai-analysis-answers">' +
          '    <span class="ai-answer-wrong">❌ 你的答案：' + escapeHTML(item.myAnswer || '') + '</span>' +
          '    <span class="ai-answer-right">✅ 正确答案：' + escapeHTML(item.correctAnswer || '') + '</span>' +
          '  </div>' +
          '  <div class="ai-analysis-explain">💡 ' + escapeHTML(item.explanation || '') + '</div>' +
          (item.knowledgePoint ? '<span class="ai-knowledge-tag">📚 ' + escapeHTML(item.knowledgePoint) + '</span>' : '') +
          '</div>';
      });
    } else if (data.rawContent) {
      // 如果AI没返回结构化数据，显示原始文本
      analysisHTML = '<div class="ai-raw-content">' + escapeHTML(data.rawContent) + '</div>';
    } else {
      analysisHTML = '<div class="ai-tutor-empty"><span class="ai-tutor-empty-icon">🤷</span><p>暂无分析结果</p></div>';
    }

    // 每日训练
    if (data.dailyTraining && data.dailyTraining.length > 0) {
      data.dailyTraining.forEach(function(group, i) {
        trainingHTML += '' +
          '<div class="ai-training-card">' +
          '  <div class="ai-training-topic">📝 ' + escapeHTML(group.topic || '训练主题 ' + (i + 1)) + '</div>' +
          '  <div class="ai-training-target">🎯 ' + escapeHTML(group.targetKnowledge || '') + '</div>';
        if (group.questions && group.questions.length > 0) {
          group.questions.forEach(function(q, j) {
            trainingHTML += '<div class="ai-training-question"><strong>' + (j + 1) + '.</strong> ' + escapeHTML(q) + '</div>';
          });
        }
        trainingHTML += '</div>';
      });
    } else {
      trainingHTML = '<div class="ai-tutor-empty"><span class="ai-tutor-empty-icon">🎯</span><p>暂无训练推荐</p></div>';
    }

    content.innerHTML = '' +
      '<div class="ai-tab-content active" id="aiAnalysisContent">' + analysisHTML + '</div>' +
      '<div class="ai-tab-content" id="aiTrainingContent" style="display:none;">' + trainingHTML + '</div>' +
      (encouragement ? '<div class="ai-encourage"><span class="ai-encourage-icon">🌟</span>' + escapeHTML(encouragement) + '</div>' : '') +
      (meta ? '<div style="text-align:center;padding:8px;font-size:11px;color:rgba(255,255,255,0.2);">分析了 ' + meta.questionsCount + ' 道错题 · 消耗约 ' + meta.tokens + ' tokens</div>' : '');

    // 重置tab状态
    var tabs = document.querySelectorAll('.ai-tutor-tab');
    if (tabs.length > 0) {
      tabs.forEach(function(t) { t.classList.remove('active'); });
      tabs[0].classList.add('active');
    }

    // Start按钮改为重新分析
    var startBtn = document.getElementById('aiStartBtn');
    if (startBtn) { startBtn.style.display = ''; startBtn.textContent = '🔄 重新分析'; }
  }

  function escapeHTML(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // ==================== 初始化 ====================
  // 在错题弹窗的actions区域动态添加AI讲解按钮
  function injectAIButton() {
    if (document.getElementById('aiTutorBtn')) return;
    // 等待 DOM 加载
    var check = setInterval(function() {
      var actions = document.querySelector('.wrong-question-actions');
      if (actions) {
        clearInterval(check);
        var btn = document.createElement('button');
        btn.id = 'aiTutorBtn';
        btn.className = 'wrong-ai-btn';
        btn.textContent = '🤖 AI讲解';
        btn.onclick = function() { window.showAITutor(); };
        actions.appendChild(btn);
      }
    }, 300);
    // 最多等10秒
    setTimeout(function() { clearInterval(check); }, 10000);
  }

  // 页面加载后注入按钮
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      injectStyles();
      createUI();
      injectAIButton();
    });
  } else {
    injectStyles();
    createUI();
    injectAIButton();
  }

})();
