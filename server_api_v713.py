#!/usr/bin/env python3

"""

科学复习系统 API v713 — 新增装备合成原子端点

改动：

1. _write_json_internal: os.replace() + PID 隔离 (修复竞态)

2. student 端点: 智能合并 (Math.max/去重/并集/零分守卫)

3. ranking 端点: 零分守卫 (保留原有)

4. 新增 /api/xuanba/* 校队选拔 API

5. v713: 新增 /api/synthesis/compose 装备合成原子端点（删除原料+生成新装备）

"""

from flask import Flask, request, jsonify

from flask_cors import CORS

import json

import os

import time

import contextlib

import fcntl

import shutil



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

            json.dump(data, f, ensure_ascii=False, indent=2)

            f.flush()

            os.fsync(f.fileno())

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





# ==================== 学生存档 API（v706 智能合并） ====================



@app.route('/api/student/<grade>/<studentId>', methods=['GET', 'POST'])

def student(grade, studentId):

    key = f'{grade}_{studentId}'

    

    if request.method == 'GET':

        data = _read_json('students')

        return jsonify(data.get(key, {}))

    

    body = request.json

    if not body:

        return jsonify({'error': '数据为空'}), 400

    

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

        if len(body_equip) == 0 and len(existing_equip) > 0:

            # body为空(新设备/数据丢失) → 用云端数据恢复

            merged['equipment'] = existing_equip

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



@app.route('/api/ai-tutor', methods=['POST'])

def ai_tutor():

    body = request.json

    if not body or 'question' not in body:

        return jsonify({'error': '缺少题目'}), 400

    

    import os

    api_key = os.environ.get('DEEPSEEK_API_KEY', '')

    if not api_key:

        return jsonify({'error': 'AI 服务未配置'}), 503

    

    try:

        import requests

        resp = requests.post(

            'https://api.deepseek.com/v1/chat/completions',

            headers={

                'Authorization': f'Bearer {api_key}',

                'Content-Type': 'application/json'

            },

            json={

                'model': 'deepseek-chat',

                'messages': [

                    {'role': 'system', 'content': '你是一位耐心的小学科学老师，用简单易懂的语言讲解科学题目的正确答案和解题思路。'},

                    {'role': 'user', 'content': f"题目：{body['question']}\n正确答案：{body.get('correctAnswer', '')}\n学生的错误答案：{body.get('studentAnswer', '')}\n\n请用小学生能理解的语言讲解这道题。"}

                ],

                'max_tokens': 500,

                'temperature': 0.7

            },

            timeout=15

        )

        if resp.status_code == 200:

            result = resp.json()

            return jsonify({

                'explanation': result['choices'][0]['message']['content']

            })

        else:

            return jsonify({'error': f'AI 调用失败: {resp.status_code}'}), 502

    except Exception as e:

        return jsonify({'error': str(e)}), 500





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

        if attempt.get('percentile', 0) > entry.get('bestPercentile', 0):
            entry['bestPercentile'] = attempt['percentile']

        if attempt.get('iq', 0) > entry.get('bestIQ', 0):
            entry['bestIQ'] = attempt['iq']

        return data

    

    _atomic_read_write('xuanba_results', updater)

    # v715fix: 同步 xuanbaScore 到全局排行榜
    try:
        entry = _read_json('xuanba_results').get(student_id, {})
        def ranking_updater(data):
            existing = data.get(student_id, {})
            existing['studentId'] = student_id
            existing['studentName'] = existing.get('studentName') or entry.get('studentName', '')
            existing['xuanbaScore'] = entry.get('bestScore', 0)
            existing['xuanbaRA'] = entry.get('bestRA', 0)
            data[student_id] = existing
            return data
        _atomic_read_write('rankings_grade_all', ranking_updater)
    except Exception as e:
        print(f'[xuanba] 同步排行榜失败: {e}')

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





# ==================== 赠礼 & 亲密系统 API (v713部署) ====================
import uuid as _uuid

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

    return jsonify({'status': 'ok', 'time': time.time(), 'version': 'v713'})





if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=False)

