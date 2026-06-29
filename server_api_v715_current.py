#!/usr/bin/env python3
"""
科学复习系统 API v715 — 合并赠礼 & 亲密系统
改动：
1. v714 全部功能（弹幕、在线状态、发现系统）
2. v713 赠礼系统（gift/send, accept, revoke, pending, sent）
3. v713 亲密系统（intimacy/<studentId>, intimacy/claim）
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import time
import contextlib
import fcntl
import shutil
import uuid as _uuid
import requests

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

DATA_DIR = '/data/kexvefuxi'


# ==================== 数据读写（原子 + 竞态修复） ====================

def _data_path(name):
    return os.path.join(DATA_DIR, f'{name}.json')


def _read_json(name):
    """读取 JSON 文件，带损坏恢复"""
    path = _data_path(name)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        print(f'[WARN] JSON 文件损坏: {path}，尝试恢复...')
        # 尝试 .tmp 恢复
        for suffix in ['.tmp', '.tmp.recover']:
            tmp_path = path + suffix
            if os.path.exists(tmp_path):
                try:
                    with open(tmp_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f'[INFO] 从 {tmp_path} 恢复成功')
                    return data
                except:
                    pass
        print(f'[ERROR] 无法恢复 {path}，返回空数据')
        return {}


def _write_json_internal(name, data):
    """
    内部写入：竞态修复版
    - os.replace() 替代 shutil.move()（同文件系统原子 rename）
    - PID 隔离 tmp 文件（防止多 worker 竞争）
    """
    path = _data_path(name)
    tmp_path = f'{path}.tmp.{os.getpid()}'
    try:
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
        os.replace(tmp_path, path)  # 原子替换，不跨文件系统
    except Exception:
        # 清理残留在 finally 前
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except:
                pass
        raise


@contextlib.contextmanager
def _file_lock(name):
    """文件锁上下文管理器"""
    path = _data_path(name)
    lock_path = path + '.lock'
    lock_fd = open(lock_path, 'w')
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
    except (IOError, OSError):
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
    try:
        yield
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()
        try:
            os.remove(lock_path)
        except:
            pass


def _atomic_read_write(name, updater):
    """原子读取-修改-写入（锁保护）"""
    with _file_lock(name):
        data = _read_json(name)
        data = updater(data)
        _write_json_internal(name, data)
    return data


# ==================== 排行榜 API ====================

@app.route('/api/ranking/<grade>', methods=['GET', 'POST'])
def ranking(grade):
    if request.method == 'GET':
        data = _read_json(f'rankings_{grade}')
        return jsonify(data)
    
    body = request.json
    if not body or 'studentId' not in body:
        return jsonify({'error': '缺少 studentId'}), 400
    
    # 零分守卫
    total_points = body.get('totalPoints', 0)
    
    def updater(data):
        sid = body['studentId']
        existing = data.get(sid, {})
        existing_points = existing.get('totalPoints', 0)
        
        if total_points == 0 and existing_points > 0:
            print(f'[GUARD] ranking 零分守卫: {sid} local=0 cloud={existing_points}, 拒绝写入')
            return data  # 不覆盖
        
        data[sid] = body
        return data
    
    _atomic_read_write(f'rankings_{grade}', updater)
    return jsonify({'ok': True})


# ==================== 学生姓名映射 API ====================
# 缓存：避免每次请求都读 648KB 的 student_info.json
_names_cache = {'data': None, 'mtime': 0}

@app.route('/api/students/names')
def students_names():
    import os
    path = _data_path('student_info')
    try:
        mtime = os.path.getmtime(path)
        if _names_cache['data'] is not None and _names_cache['mtime'] == mtime:
            return jsonify(_names_cache['data'])
        with open(path, 'r', encoding='utf-8') as f:
            info = json.load(f)
        names = {sid: v['name'] for sid, v in info.items() if v.get('name')}
        _names_cache['data'] = names
        _names_cache['mtime'] = mtime
        return jsonify(names)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 学生存档 API（v706 智能合并） ====================
# 限流：防止客户端疯狂重试导致 73MB 文件写入积压
_save_throttle = {}  # {key: timestamp}

@app.route('/api/student/<grade>/<studentId>', methods=['GET', 'POST'])
def student(grade, studentId):
    key = f'{grade}_{studentId}'
    
    if request.method == 'GET':
        data = _read_json('students')
        return jsonify(data.get(key, {}))
    
    body = request.json
    if not body:
        return jsonify({'error': '数据为空'}), 400
    
    # === 限流：同一学生 10 秒内只允许保存一次 ===
    now = time.time()
    last = _save_throttle.get(key, 0)
    if now - last < 10:
        return jsonify({'ok': True, 'throttled': True})
    _save_throttle[key] = now
    # 定期清理过期限流记录（每次保存时顺带清理，避免内存泄漏）
    if len(_save_throttle) > 200:
        _save_throttle.clear()
    
    def updater(data):
        existing = data.get(key, {})
        
        # === 零分守卫 ===
        local_points = body.get('totalPoints', 0)
        cloud_points = existing.get('totalPoints', 0)
        if local_points == 0 and cloud_points > 0:
            print(f'[GUARD] student 零分守卫: {key} local=0 cloud={cloud_points}')
            # 仍然合并其他字段，但积分保留云端值
            body['totalPoints'] = cloud_points
        
        # === 智能合并 ===
        merged = {}
        
        # 数值字段：取最大值（totalPoints 除外——信任客户端值，仅零分守卫保护）
        numeric_max_keys = [
            'totalQuestionsAnswered', 'totalCorrectAnswers',
            'towerHighestFloor', 'towerCoins', 'ladderBestScore',
            'dailyStamina', 'xuanbaBestScore', 'xuanbaBestPct'
        ]
        for k in numeric_max_keys:
            merged[k] = max(
                existing.get(k, 0) if existing.get(k) is not None else 0,
                body.get(k, 0) if body.get(k) is not None else 0
            )
        
        # totalPoints: 信任客户端值（零分守卫已在上面处理）
        merged['totalPoints'] = body.get('totalPoints', 0)
        
        # 装备：以body为准（信任用户操作：赠送/合成/丢弃）
        body_equip = [e for e in (body.get('equipment', []) or []) if e and isinstance(e, dict)]
        existing_equip = [e for e in (existing.get('equipment', []) or []) if e and isinstance(e, dict)]
        # 🔒 v716 装备保护: body为空且云端有数据 → 绝不覆盖
        if len(body_equip) == 0:
            if len(existing_equip) > 0:
                merged['equipment'] = existing_equip
                print(f"[EQUIP-PROTECT] {studentId}: body空,保留云{len(existing_equip)}件")
            else:
                # 双方都空 → 检查是否有旧key的装备数据
                merged['equipment'] = []
        else:
            # body有数据 → 以body为准(赠送/合成后的真实状态)
            merged['equipment'] = body_equip
        
        # 装备掉落标记：合并
        merged['equipDropped'] = {}
        merged['equipDropped'].update(existing.get('equipDropped', {}) or {})
        merged['equipDropped'].update(body.get('equipDropped', {}) or {})
        
        # 成就：并集去重
        existing_ach = existing.get('unlockedAchievements', []) or []
        body_ach = body.get('unlockedAchievements', []) or []
        ach_set = set()
        for a in existing_ach:
            ach_set.add(a)
        for a in body_ach:
            ach_set.add(a)
        merged['unlockedAchievements'] = list(ach_set)
        
        # 课时进度：合并并集，每课取 max 星级
        merged['lessonProgress'] = {}
        existing_lp = existing.get('lessonProgress', {}) or {}
        body_lp = body.get('lessonProgress', {}) or {}
        all_lessons = set(list(existing_lp.keys()) + list(body_lp.keys()))
        for lk in all_lessons:
            merged['lessonProgress'][lk] = max(
                existing_lp.get(lk, 0) or 0,
                body_lp.get(lk, 0) or 0
            )
        
        # 错题：合并去重（按 question + correctAnswer 为 key）
        wq_map = {}
        for wq in (existing.get('wrongQuestions', []) or []):
            if wq and isinstance(wq, dict):
                wk = f"{wq.get('question', '')}|{wq.get('correctAnswer', '')}"
                if wk not in wq_map or (wq.get('count', 0) or 0) > (wq_map[wk].get('count', 0) or 0):
                    wq_map[wk] = wq
        for wq in (body.get('wrongQuestions', []) or []):
            if wq and isinstance(wq, dict):
                wk = f"{wq.get('question', '')}|{wq.get('correctAnswer', '')}"
                if wk not in wq_map or (wq.get('count', 0) or 0) > (wq_map[wk].get('count', 0) or 0):
                    wq_map[wk] = wq
        merged['wrongQuestions'] = list(wq_map.values())
        
        # 同步错题：合并去重（按 question + correctAnswer + syncDate）
        sw_map = {}
        for sw in (existing.get('syncedWrongQuestions', []) or []):
            if sw and isinstance(sw, dict):
                sk = f"{sw.get('question', '')}|{sw.get('correctAnswer', '')}|{sw.get('syncDate', '')}"
                sw_map[sk] = sw
        for sw in (body.get('syncedWrongQuestions', []) or []):
            if sw and isinstance(sw, dict):
                sk = f"{sw.get('question', '')}|{sw.get('correctAnswer', '')}|{sw.get('syncDate', '')}"
                sw_map[sk] = sw
        merged['syncedWrongQuestions'] = list(sw_map.values())
        
        # 宠物碎片：云端和本地合并取 max
        merged['petPieces'] = {}
        existing_pp = existing.get('petPieces', {}) or {}
        body_pp = body.get('petPieces', {}) or {}
        all_pet_ids = set(list(existing_pp.keys()) + list(body_pp.keys()))
        for pid in all_pet_ids:
            merged['petPieces'][pid] = max(
                existing_pp.get(pid, 0) or 0,
                body_pp.get(pid, 0) or 0
            )
        
        # 云端题库：合并
        merged['cloudQBank'] = {}
        merged['cloudQBank'].update(existing.get('cloudQBank', {}) or {})
        merged['cloudQBank'].update(body.get('cloudQBank', {}) or {})
        
        # 体力日期：取较新的
        merged['lastStaminaDate'] = body.get('lastStaminaDate') or existing.get('lastStaminaDate')
        
        # 装备槽：body 优先
        merged['equippedSlots'] = body.get('equippedSlots') or existing.get('equippedSlots', {})
        
        # 天梯相关
        merged['ladderPoints'] = max(
            existing.get('ladderPoints', 0) or 0,
            body.get('ladderPoints', 0) or 0
        )
        merged['ladderTier'] = body.get('ladderTier') or existing.get('ladderTier')
        
        # 标记
        merged['gradeDataMerged'] = True
        
        # 时间戳
        merged['lastUpdated'] = int(time.time() * 1000)
        merged['lastSyncTime'] = max(
            existing.get('lastSyncTime', 0) or 0,
            body.get('lastSyncTime', 0) or 0
        )
        
        data[key] = merged
        return data
    
    _atomic_read_write('students', updater)
    return jsonify({'ok': True, 'merged': True})


# ==================== AI错题讲解 ====================

# DeepSeek API 配置（从环境变量读取）
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'

AI_TUTOR_SYSTEM_PROMPT = """你是一位资深的小学科学老师，专门帮助小学生分析错题并推荐针对性训练。

## 你的任务
根据学生提供的错题列表，做两件事：
1. **错题分析**：对每道错题用通俗易懂的语言解释知识点，指出易错点
2. **每日训练推荐**：根据错题涉及的知识点，推荐3-5道针对性练习题

## 输出格式（严格遵守JSON）
{
  "analysis": [
    {
      "question": "错题原文",
      "myAnswer": "学生的错误答案",
      "correctAnswer": "正确答案", 
      "explanation": "通俗讲解（50-100字）",
      "knowledgePoint": "涉及的知识点名称"
    }
  ],
  "dailyTraining": [
    {
      "topic": "训练主题",
      "targetKnowledge": "针对的知识点",
      "questions": ["题目1", "题目2", "题目3"]
    }
  ],
  "encouragement": "一句鼓励学生的话"
}

## 要求
- 用小学生能听懂的语言，避免过于学术化
- 讲解要具体，指出"为什么会错"而不仅仅是"正确答案是什么"
- 每日训练题目要与错题知识点匹配，且难度递进
- 回复必须是合法的JSON，不要有其他内容"""

@app.route('/api/ai-tutor', methods=['POST'])
def ai_tutor():
    """AI错题讲解 + 每日训练推荐（v716：恢复多题批量分析格式）"""
    if not DEEPSEEK_API_KEY:
        return jsonify({'error': 'AI服务未配置'}), 503

    body = request.json
    if not body or 'wrongQuestions' not in body:
        return jsonify({'error': '缺少错题数据'}), 400

    wrong_questions = body['wrongQuestions']
    if not wrong_questions or len(wrong_questions) == 0:
        return jsonify({'error': '错题列表为空'}), 400

    student_name = body.get('studentName', '同学')
    grade = body.get('grade', '')

    # 限制错题数量（最多20道，控制token消耗）
    if len(wrong_questions) > 20:
        wrong_questions = wrong_questions[:20]

    # 构建用户prompt
    questions_text = ''
    for i, wq in enumerate(wrong_questions, 1):
        questions_text += f"""
第{i}题：
- 课程：{wq.get('lessonName', '未知')}
- 题目：{wq.get('question', '')}
- 我的答案：{wq.get('userAnswer', '')}
- 正确答案：{wq.get('correctAnswer', '')}
"""

    user_prompt = f"""学生：{student_name}（{grade}年级）

以下是我的错题，请帮我分析并推荐训练：

{questions_text}
"""

    try:
        resp = requests.post(
            DEEPSEEK_API_URL,
            headers={
                'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'deepseek-chat',
                'messages': [
                    {'role': 'system', 'content': AI_TUTOR_SYSTEM_PROMPT},
                    {'role': 'user', 'content': user_prompt}
                ],
                'temperature': 0.7,
                'max_tokens': 3000,
                'response_format': {'type': 'json_object'}
            },
            timeout=60
        )

        if resp.status_code != 200:
            print(f'[AI-TUTOR] DeepSeek API error: {resp.status_code} {resp.text[:200]}')
            return jsonify({'error': f'AI服务异常 ({resp.status_code})'}), 502

        result = resp.json()
        ai_content = result['choices'][0]['message']['content']

        # 解析AI返回的JSON
        try:
            parsed = json.loads(ai_content)
        except json.JSONDecodeError:
            parsed = {
                'analysis': [],
                'dailyTraining': [],
                'encouragement': '继续加油！',
                'rawContent': ai_content
            }

        # 记录日志
        usage = result.get('usage', {})
        print(f'[AI-TUTOR] 成功 | 学生:{student_name} | 错题:{len(wrong_questions)}道 | '
              f'tokens: {usage.get("total_tokens", "?")} | '
              f'费用约 ¥{usage.get("total_tokens", 0) * 0.002 / 1000:.4f}')

        return jsonify({
            'ok': True,
            'data': parsed,
            'meta': {
                'questionsCount': len(wrong_questions),
                'tokens': usage.get('total_tokens', 0)
            }
        })

    except requests.exceptions.Timeout:
        return jsonify({'error': 'AI响应超时，请稍后重试'}), 504
    except requests.exceptions.RequestException as e:
        print(f'[AI-TUTOR] 网络错误: {e}')
        return jsonify({'error': 'AI服务连接失败'}), 502
    except Exception as e:
        print(f'[AI-TUTOR] 未知错误: {e}')
        return jsonify({'error': f'AI讲解出错: {str(e)}'}), 500


# ==================== 排行榜相关 ====================

@app.route('/api/ranking/score/<grade>', methods=['GET'])
def ranking_score(grade):
    data = _read_json(f'rankings_{grade}')
    sorted_data = sorted(data.values(), key=lambda x: x.get('totalPoints', 0), reverse=True)
    return jsonify(sorted_data[:100])

@app.route('/api/ranking/accuracy/<grade>', methods=['GET'])
def ranking_accuracy(grade):
    data = _read_json(f'rankings_{grade}')
    def accuracy(d):
        total = d.get('totalQuestionsAnswered', 0)
        correct = d.get('totalCorrectAnswers', 0)
        return (correct / total * 100) if total > 0 else 0
    sorted_data = sorted(data.values(), key=accuracy, reverse=True)
    return jsonify(sorted_data[:100])
    
# ==================== 题库 API ====================
@app.route('/api/questionbank/<grade>', methods=['GET', 'POST'])
def questionbank(grade):
    if request.method == 'GET':
        data = _read_json(f'questionbank_{grade}')
        return jsonify(data)
    body = request.json
    if not body or 'questions' not in body:
        return jsonify({'error': '缺少 questions'}), 400
    _write_json_internal(f'questionbank_{grade}', body)
    return jsonify({'ok': True, 'count': len(body['questions'])})


# ==================== 天梯 API ====================

@app.route('/api/ladder/ranking/score/<grade>', methods=['GET'])
def ladder_score(grade):
    data = _read_json('rankings_ladder')
    grade_data = data.get(str(grade), {})
    sorted_data = sorted(grade_data.values(), key=lambda x: x.get('score', 0), reverse=True)
    return jsonify(sorted_data[:100])

@app.route('/api/ladder/ranking/accuracy/<grade>', methods=['GET'])
def ladder_accuracy(grade):
    data = _read_json('rankings_ladder')
    grade_data = data.get(str(grade), {})
    def acc(d):
        total = d.get('totalQuestions', 0)
        correct = d.get('totalCorrect', 0)
        return (correct / total * 100) if total > 0 else 0
    sorted_data = sorted(grade_data.values(), key=acc, reverse=True)
    return jsonify(sorted_data[:100])

@app.route('/api/ladder/ranking', methods=['POST'])
def ladder_ranking():
    body = request.json
    if not body or 'studentId' not in body:
        return jsonify({'error': '缺少 studentId'}), 400
    
    grade = str(body.get('gradeKey', '6'))
    
    def updater(data):
        if grade not in data:
            data[grade] = {}
        sid = body['studentId']
        existing = data[grade].get(sid, {})
        # 高积分保护
        if body.get('score', 0) > existing.get('score', 0) or not existing:
            data[grade][sid] = body
        return data
    
    _atomic_read_write('rankings_ladder', updater)
    return jsonify({'ok': True})

@app.route('/api/ladder/profile/<studentId>', methods=['GET'])
def ladder_profile_get(studentId):
    data = _read_json('ladder_profiles')
    return jsonify(data.get(studentId, {}))

@app.route('/api/ladder/profile', methods=['POST'])
def ladder_profile_save():
    body = request.json
    if not body or 'studentId' not in body:
        return jsonify({'error': '缺少 studentId'}), 400
    
    def updater(data):
        data[body['studentId']] = body
        return data
    
    _atomic_read_write('ladder_profiles', updater)
    return jsonify({'ok': True})


# ==================== 装备合成 API (v713) ====================

@app.route('/api/synthesis/compose', methods=['POST'])
def synthesis_compose():
    """装备合成：原子删除3件原料 + 添加1件新装备"""
    body = request.json
    if not body:
        return jsonify({'error': '数据为空'}), 400

    required = ['studentId', 'grade', 'ingredientIds', 'resultEquip']
    for field in required:
        if field not in body:
            return jsonify({'error': f'缺少 {field}'}), 400

    student_id = body['studentId']
    grade = body['grade']  # e.g., 'grade_all'
    ingredient_ids = body['ingredientIds']  # list of 3 equipment IDs
    result_equip = body['resultEquip']  # new equipment object

    if not isinstance(ingredient_ids, list) or len(ingredient_ids) != 3:
        return jsonify({'error': '需要3件装备ID作为原料'}), 400
    if not isinstance(result_equip, dict) or 'id' not in result_equip:
        return jsonify({'error': 'resultEquip 格式不正确'}), 400

    key = f'{grade}_{student_id}'

    def updater(data):
        existing = data.get(key, {})
        equip_list = [e for e in (existing.get('equipment', []) or []) if e and isinstance(e, dict)]

        # 操作1：删除对应的原始装备（按 ID 匹配）
        found_count = 0
        new_equip_list = []
        for eq in equip_list:
            if eq.get('id') in ingredient_ids:
                found_count += 1
            else:
                new_equip_list.append(eq)

        print(f'[SYNTHESIS] {key}: 找到 {found_count}/3 件原料, 生成新装备 {result_equip.get("id","?")[:16]}')

        # 操作2：生成对应的新装备
        new_equip_list.append(result_equip)

        # 更新装备数据
        updated = dict(existing)
        updated['equipment'] = new_equip_list
        updated['lastUpdated'] = int(time.time() * 1000)
        data[key] = updated
        return data

    _atomic_read_write('students', updater)
    return jsonify({'ok': True})


# ==================== 校队选拔 API (v710) ====================

@app.route('/api/xuanba/save', methods=['POST'])
def xuanba_save():
    """保存学生选拔测试结果"""
    body = request.json
    if not body or 'studentId' not in body:
        return jsonify({'error': '缺少 studentId'}), 400
    
    student_id = body['studentId']
    
    def updater(data):
        if student_id not in data:
            data[student_id] = {
                'studentId': student_id,
                'studentName': body.get('studentName', ''),
                'grade': body.get('grade', ''),
                'attempts': [],
                'bestScore': 0,
                'bestRA': 0,
                'bestPercentile': 0,
                'attemptCount': 0
            }
        
        entry = data[student_id]
        attempt = {
            'date': body.get('date', time.strftime('%Y-%m-%dT%H:%M:%S')),
            'score': body.get('score', 0),
            'ra': body.get('ra', 0),
            'percentile': body.get('percentile', 0),
            'timeSeconds': body.get('timeSeconds', 0),
            'levelStats': body.get('levelStats', {}),
            'completed': body.get('completed', True)
        }
        
        # 追加尝试记录（最多保留2次）
        entry['attempts'].append(attempt)
        if len(entry['attempts']) > 2:
            entry['attempts'] = entry['attempts'][-2:]
        
        entry['attemptCount'] = len(entry['attempts'])
        
        # 保留最高分
        if attempt['score'] > entry['bestScore']:
            entry['bestScore'] = attempt['score']
        if attempt['ra'] > entry.get('bestRA', 0):
            entry['bestRA'] = attempt['ra']
        if attempt['percentile'] > entry.get('bestPercentile', 0):
            entry['bestPercentile'] = attempt['percentile']
        if attempt['iq'] > entry['bestIQ']:
            entry['bestIQ'] = attempt['iq']
        if attempt['percentile'] > entry['bestPercentile']:
            entry['bestPercentile'] = attempt['percentile']
        
        return data
    
    _atomic_read_write('xuanba_results', updater)
    return jsonify({'ok': True})


@app.route('/api/xuanba/load/<studentId>', methods=['GET'])
def xuanba_load(studentId):
    """加载学生选拔测试历史"""
    data = _read_json('xuanba_results')
    entry = data.get(studentId, {})
    return jsonify(entry)


@app.route('/api/xuanba/ranking', methods=['GET'])
def xuanba_ranking():
    """校队选拔排行（按RA推理指数排序）"""
    data = _read_json('xuanba_results')
    rankings = []
    for sid, entry in data.items():
        if entry.get('bestScore', 0) > 0:
            rankings.append({
                'studentId': sid,
                'studentName': entry.get('studentName', ''),
                'grade': entry.get('grade', ''),
                'bestScore': entry.get('bestScore', 0),
                'bestRA': entry.get('bestRA', 0),
                'bestPercentile': entry.get('bestPercentile', 0),
                'attemptCount': entry.get('attemptCount', 0)
            })
    # 按RA降序
    rankings.sort(key=lambda x: x['bestRA'], reverse=True)
    return jsonify(rankings[:200])


# ==================== 🆕 在线状态 & 弹幕系统 API (v714) ====================

HEARTBEAT_TTL = 60       # 心跳有效期（秒）：超过此时间视为离线
DANMAKU_CLEANUP = 3600   # 弹幕过期清理间隔：1小时

def _cleanup_online_users(data):
    """清理过期在线用户"""
    now = time.time()
    data['onlineUsers'] = {
        uid: info for uid, info in data.get('onlineUsers', {}).items()
        if now - info.get('lastSeen', 0) < HEARTBEAT_TTL
    }
    return data

def _cleanup_danmaku_queue(data):
    """清理过期弹幕"""
    now = time.time()
    data['queue'] = [
        item for item in data.get('queue', [])
        if item.get('expireAt', 0) > now
    ]
    return data


@app.route('/api/online/heartbeat', methods=['POST'])
def online_heartbeat():
    """学生心跳上报：记录在线状态 + 返回在线人数"""
    body = request.json or {}
    student_id = body.get('studentId', '')
    if not student_id:
        return jsonify({'error': '缺少 studentId'}), 400

    now = time.time()

    def updater(data):
        if 'onlineUsers' not in data:
            data['onlineUsers'] = {}
        data['onlineUsers'][student_id] = {
            'name': body.get('name', ''),
            'lastSeen': now,
            'title': body.get('title', '探索者'),
            'rank': body.get('rank', '黑铁'),
            'achievement': body.get('achievement', '')
        }
        data = _cleanup_online_users(data)
        return data

    data = _atomic_read_write('online', updater)
    online_count = len(data.get('onlineUsers', {}))
    return jsonify({'ok': True, 'onlineCount': online_count})


@app.route('/api/online/status', methods=['GET'])
def online_status():
    """获取在线状态 + 弹幕队列"""
    online_data = _read_json('online')
    danmaku_data = _read_json('danmaku')

    # 清理过期数据
    online_data = _cleanup_online_users(online_data)
    danmaku_data = _cleanup_danmaku_queue(danmaku_data)

    # 提取弹幕中待显示的项（用 repeatCount 控制显示频率）
    now = time.time()
    danmaku_items = []
    for item in danmaku_data.get('queue', []):
        repeat_count = item.get('repeatCount', 0)
        max_repeat = item.get('maxRepeat', 0)
        if repeat_count < max_repeat:
            danmaku_items.append({
                'id': item['id'],
                'type': item.get('type', 'achievement'),
                'userId': item.get('userId', ''),
                'name': item.get('name', ''),
                'title': item.get('title', ''),
                'rank': item.get('rank', ''),
                'content': item.get('content', ''),
                'achievementName': item.get('achievementName', '')
            })

    online_count = len(online_data.get('onlineUsers', {}))
    online_users = list(online_data.get('onlineUsers', {}).values())

    return jsonify({
        'onlineCount': online_count,
        'onlineUsers': online_users,
        'danmakuItems': danmaku_items
    })


@app.route('/api/danmaku/broadcast', methods=['POST'])
def danmaku_broadcast():
    """记录成就广播事件"""
    body = request.json or {}
    dan_type = body.get('type', 'achievement')
    student_id = body.get('studentId', '')
    if not student_id:
        return jsonify({'error': '缺少 studentId'}), 400

    now = time.time()

    def updater(data):
        if 'queue' not in data:
            data['queue'] = []

        # 清理过期弹幕
        data = _cleanup_danmaku_queue(data)

        # 设置重复参数
        if dan_type == 'login':
            max_repeat = 1
            repeat_interval = 0
            expire_sec = 10  # 登录弹幕只存活10秒
        elif dan_type == 'legend':
            max_repeat = 10
            repeat_interval = 180  # 传说成就3分钟一次
            expire_sec = 86400  # 当天
        elif dan_type == 'tower_king':
            max_repeat = 3
            repeat_interval = 600  # 10分钟一次
            expire_sec = 86400
        else:  # achievement
            max_repeat = 5
            repeat_interval = 300  # 5分钟一次
            expire_sec = 86400

        danmaku_id = f"dan_{student_id}_{dan_type}_{body.get('achievementId', '')}_{int(now)}"

        # 检查是否已有相同类型的弹幕（去重）
        for item in data['queue']:
            if item.get('userId') == student_id and item.get('achievementName') == body.get('achievementName', ''):
                return data  # 已存在，不重复添加

        data['queue'].append({
            'id': danmaku_id,
            'type': dan_type,
            'userId': student_id,
            'name': body.get('name', ''),
            'title': body.get('title', ''),
            'rank': body.get('rank', '黑铁'),
            'content': body.get('content', ''),
            'achievementName': body.get('achievementName', ''),
            'createdAt': now,
            'expireAt': now + expire_sec,
            'repeatCount': 0,
            'maxRepeat': max_repeat,
            'repeatInterval': repeat_interval
        })
        return data

    _atomic_read_write('danmaku', updater)
    return jsonify({'ok': True})


@app.route('/api/danmaku/repeat_tick', methods=['POST'])
def danmaku_repeat_tick():
    """弹幕重复计数器递增（前端定时调用，触发重复弹幕）"""
    now = time.time()

    def updater(data):
        if 'queue' not in data:
            return data
        data = _cleanup_danmaku_queue(data)
        for item in data['queue']:
            rc = item.get('repeatCount', 0)
            mx = item.get('maxRepeat', 0)
            if rc < mx:
                item['repeatCount'] = rc + 1
        return data

    _atomic_read_write('danmaku', updater)
    return jsonify({'ok': True})


# ==================== 🆕 v714: 发现者榜 API ====================

@app.route('/api/discovery/list', methods=['GET'])
def discovery_list():
    """获取所有发现者记录（永久荣誉榜）"""
    data = _read_json('discoveries')
    return jsonify(data)


@app.route('/api/discovery/claim', methods=['POST'])
def discovery_claim():
    """
    首次发现者申领（原子操作，防并发）
    同一个人不能多次"首次发现"同一内容
    """
    body = request.json or {}
    discovery_id = body.get('discoveryId', '')
    student_id = body.get('studentId', '')
    student_name = body.get('studentName', '')
    discovery_name = body.get('discoveryName', '')
    equip_id = body.get('equipId', '')

    if not discovery_id or not student_id:
        return jsonify({'error': '缺少 discoveryId 或 studentId'}), 400

    def updater(data):
        if discovery_id in data and data[discovery_id].get('discovererId'):
            # 已被发现
            return data
        
        now = time.time()
        data[discovery_id] = {
            'discoveryId': discovery_id,
            'discoveryName': discovery_name,
            'discovererId': student_id,
            'discovererName': student_name,
            'discoveredAt': now,
            'equipId': equip_id
        }
        return data

    # 原子操作：只有第一个到达的请求能成功写入
    result = _atomic_read_write('discoveries', updater)

    # 检查是否真的是我们写入的（第一个发现者）
    if result.get(discovery_id, {}).get('discovererId') == student_id:
        return jsonify({'ok': True, 'firstDiscoverer': True})
    else:
        # 已被他人抢先发现
        existing = result.get(discovery_id, {})
        return jsonify({
            'ok': True,
            'firstDiscoverer': False,
            'alreadyDiscoveredBy': existing.get('discovererName', '未知'),
            'discoveredAt': existing.get('discoveredAt', 0)
        })


# ==================== 赠礼 & 亲密系统 API ====================

def _gen_gift_id():
    return str(_uuid.uuid4())[:12]

@app.route('/api/gift/send', methods=['POST'])
def gift_send():
    try:
        body = request.get_json(force=True)
        from_id = str(body.get('fromId', ''))
        to_id = str(body.get('toId', ''))
        equip_data = body.get('equipData')
        if not from_id or not to_id or not equip_data:
            return jsonify({'error': 'missing params'}), 400
        pending = _read_json('gifts_pending')
        gift_id = _gen_gift_id()
        gift = {'giftId': gift_id, 'fromId': from_id, 'toId': to_id, 'equipData': equip_data, 'createdAt': time.time(), 'status': 'pending'}
        pending[gift_id] = gift
        _write_json_internal('gifts_pending', pending)
        return jsonify({'success': True, 'giftId': gift_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gift/accept', methods=['POST'])
def gift_accept():
    try:
        body = request.get_json(force=True)
        gift_id = str(body.get('giftId', ''))
        student_id = str(body.get('studentId', ''))
        pending = _read_json('gifts_pending')
        gift = pending.get(gift_id)
        if not gift:
            return jsonify({'error': 'not found'}), 404
        if gift.get('toId') != student_id:
            return jsonify({'error': 'forbidden'}), 403
        gift['status'] = 'accepted'
        gift['acceptedAt'] = time.time()
        history = _read_json('gifts_history')
        history[gift_id] = gift
        del pending[gift_id]
        _write_json_internal('gifts_pending', pending)
        _write_json_internal('gifts_history', history)
        return jsonify({'success': True, 'equipData': gift['equipData']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gift/revoke', methods=['POST'])
def gift_revoke():
    try:
        body = request.get_json(force=True)
        gift_id = str(body.get('giftId', ''))
        from_id = str(body.get('fromId', ''))
        pending = _read_json('gifts_pending')
        gift = pending.get(gift_id)
        if not gift:
            return jsonify({'error': 'not found'}), 404
        if gift.get('fromId') != from_id:
            return jsonify({'error': 'forbidden'}), 403
        if time.time() - gift['createdAt'] > 86400:
            return jsonify({'error': 'expired'}), 400
        del pending[gift_id]
        _write_json_internal('gifts_pending', pending)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gift/pending/<studentId>', methods=['GET'])
def gift_pending(studentId):
    pending = _read_json('gifts_pending')
    return jsonify([v for v in pending.values() if v.get('toId') == str(studentId)])

@app.route('/api/gift/sent/<studentId>', methods=['GET'])
def gift_sent(studentId):
    history = _read_json('gifts_history')
    pending = _read_json('gifts_pending')
    sent = [v for v in history.values() if v.get('fromId') == str(studentId)]
    pending_sent = [v for v in pending.values() if v.get('fromId') == str(studentId)]
    return jsonify(sent + pending_sent)

@app.route('/api/intimacy/<studentId>', methods=['GET'])
def intimacy_get(studentId):
    intimacy = _read_json('intimacy')
    result = {}
    for key, pair in intimacy.items():
        ids = key.split('_')
        if str(studentId) in ids:
            other = ids[0] if ids[1] == str(studentId) else ids[1]
            result[other] = pair
    return jsonify(result)

@app.route('/api/intimacy/claim', methods=['POST'])
def intimacy_claim():
    try:
        body = request.get_json(force=True)
        student_id = str(body.get('studentId', ''))
        pair_id = str(body.get('pairId', ''))
        level = int(body.get('level', 0))
        if not student_id or not pair_id or level < 1:
            return jsonify({'error': 'missing params'}), 400
        intimacy = _read_json('intimacy')
        ids = sorted([student_id, pair_id])
        key = '{}_{}'.format(ids[0], ids[1])
        if key not in intimacy:
            intimacy[key] = {'points': 0, 'claimedLevels': []}
        if 'claimedLevels' not in intimacy[key]:
            intimacy[key]['claimedLevels'] = []
        if level in intimacy[key]['claimedLevels']:
            return jsonify({'error': 'already claimed'}), 400
        intimacy[key]['claimedLevels'].append(level)
        _write_json_internal('intimacy', intimacy)
        return jsonify({'success': True, 'level': level})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 健康检查 ====================

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'time': time.time(), 'version': 'v715'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
