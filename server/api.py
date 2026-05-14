#!/usr/bin/env python3
"""
科学复习系统 - 云端存储 API
轻量级 JSON 文件存储，支持排行榜 + 学生存档
"""

import json, os, time, shutil
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATA_DIR = '/data/kexvefuxi'
os.makedirs(DATA_DIR, exist_ok=True)

def _data_path(name):
    return os.path.join(DATA_DIR, f'{name}.json')

def _read_json(name):
    path = _data_path(name)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        print(f'[WARN] JSON 文件损坏: {path}，尝试恢复...')
        # 尝试读取临时文件
        tmp_path = path + '.tmp'
        if os.path.exists(tmp_path):
            try:
                with open(tmp_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        # 都不行，返回空
        print(f'[ERROR] 无法恢复 {path}，返回空数据')
        return {}

def _write_json(name, data):
    """原子写入：先写 .tmp 再 rename，防止写入中断导致文件损坏"""
    path = _data_path(name)
    tmp_path = path + '.tmp'
    # 先写临时文件
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    # 确保写入完成再 rename（原子操作）
    shutil.move(tmp_path, path)

# ==================== 排行榜 API ====================
# GET /api/ranking/{grade}
# POST /api/ranking/{grade}
#   body: { studentId, totalPoints, ... }
#   body: { studentId, totalPoints, ... }

@app.route('/api/ranking/<grade>', methods=['GET', 'POST'])
def ranking(grade):
    if request.method == 'GET':
        data = _read_json(f'rankings_{grade}')
        return jsonify(data)
    
    body = request.json
    if not body or 'studentId' not in body:
        return jsonify({'error': '缺少 studentId'}), 400
    
    data = _read_json(f'rankings_{grade}')
    data[body['studentId']] = body
    _write_json(f'rankings_{grade}', data)
    return jsonify({'ok': True})

# ==================== 学生存档 API ====================
# GET /api/student/{grade}/{studentId}
# POST /api/student/{grade}/{studentId}
#   body: { totalPoints, lessonProgress, ... }

@app.route('/api/student/<grade>/<studentId>', methods=['GET', 'POST'])
def student(grade, studentId):
    key = f'{grade}_{studentId}'
    if request.method == 'GET':
        data = _read_json('students')
        return jsonify(data.get(key, {}))
    
    body = request.json
    if not body:
        return jsonify({'error': '数据为空'}), 400
    
    data = _read_json('students')
    data[key] = body
    data[key]['lastUpdated'] = int(time.time() * 1000)
    _write_json('students', data)
    return jsonify({'ok': True})

# ==================== 健康检查 ====================

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'time': time.time()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
