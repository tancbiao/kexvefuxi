"""
科学复习系统 - 奖励发放管理服务器
运行: python server.py
浏览器打开: http://localhost:8888/admin/reward-manager.html
"""
import http.server
import socketserver
import os
import json
import re
import tempfile
import urllib.parse

PORT = int(os.environ.get('PORT', 8888))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # admin/ 目录
REWARDS_FILE = os.path.join(BASE_DIR, 'rewards.json')

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        # 奖励查询接口：/get-rewards?studentId=xxx
        if self.path.startswith('/get-rewards'):
            self._handle_get_rewards()
            return
        # 默认静态文件服务
        super().do_GET()
    
    def _handle_get_rewards(self):
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        student_id = params.get('studentId', [None])[0]
        
        if not student_id:
            self.send_json({'error': '缺少 studentId 参数'})
            return
        
        if not os.path.exists(REWARDS_FILE):
            self.send_json({'rewards': []})
            return
        
        try:
            with open(REWARDS_FILE, 'r', encoding='utf-8') as f:
                rewards_data = json.load(f)
            
            student_rewards = []
            for record in rewards_data.get('students', []):
                if str(record.get('studentId', '')) == str(student_id):
                    student_rewards.extend(record.get('rewards', []))
            
            self.send_json({'rewards': student_rewards})
        except Exception as e:
            self.send_json({'error': str(e)})

    def send_json(self, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)
    
    def do_POST(self):
        if self.path == '/parse':
            try:
                content_type = self.headers.get('Content-Type', '')
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                
                if 'multipart/form-data' not in content_type:
                    self.send_json({'error': '需要 multipart/form-data 格式'})
                    return
                
                # 解析 multipart body
                boundary_match = re.search(r'boundary=(.+)', content_type)
                if not boundary_match:
                    self.send_json({'error': '无法解析 boundary'})
                    return
                
                boundary = boundary_match.group(1).encode()
                
                # 找到文件内容（找到 filename= 之后的数据）
                pattern = b'filename="([^"]+)"'
                match = re.search(pattern, body)
                if not match:
                    self.send_json({'error': '未找到文件名'})
                    return
                
                filename = match.group(1).decode('utf-8', errors='replace')
                
                # 找到文件内容的起始位置（找到两个 CRLF 之后）
                header_end = body.find(b'\r\n\r\n', match.end())
                if header_end == -1:
                    self.send_json({'error': '无法定位文件内容'})
                    return
                
                file_start = header_end + 4
                file_end = len(body)
                
                # 找到文件内容的结束位置（boundary 之前）
                for sep in [b'\r\n--', b'--']:
                    idx = body.find(sep, file_start)
                    if idx > 0 and idx < file_end:
                        file_end = idx
                        if body[idx:idx+2] == b'--':
                            file_end = idx  # final boundary
                        else:
                            file_end = idx  # regular boundary
                        break
                
                file_data = body[file_start:file_end].rstrip(b'\r\n')
                
                # 保存临时文件
                with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False, mode='wb') as tmp:
                    tmp.write(file_data)
                    tmp_path = tmp.name
                
                try:
                    import pandas as pd
                    
                    # 尝试读取 Excel 文件，先获取所有 sheet 名称
                    xl = pd.ExcelFile(tmp_path)
                    sheet_names = xl.sheet_names
                    
                    # 尝试找到包含学生数据的 sheet
                    target_sheet = None
                    df = None
                    
                    # 策略1: 找"总数据" sheet
                    if '总数据' in sheet_names:
                        target_sheet = '总数据'
                        df = pd.read_excel(tmp_path, sheet_name=target_sheet, dtype={'学号': str})
                    else:
                        # 策略2: 尝试其他常见 sheet 名称
                        possible_sheets = ['数据', '成绩', '分析', 'Sheet1', '成绩分析', '总分']
                        for name in possible_sheets:
                            if name in sheet_names:
                                target_sheet = name
                                df = pd.read_excel(tmp_path, sheet_name=target_sheet, dtype={'学号': str})
                                break
                        
                        # 策略3: 尝试第一个 sheet
                        if df is None:
                            target_sheet = sheet_names[0]
                            df = pd.read_excel(tmp_path, sheet_name=target_sheet, dtype={'学号': str})
                    
                    # 自动检测列名映射
                    col_map = {}
                    for col in df.columns:
                        col_lower = str(col).strip().lower()
                        if col_lower in ['姓名', 'name']:
                            col_map[col] = '姓名'
                        elif col_lower in ['学号', 'student_id', 'studentid', '编号']:
                            col_map[col] = '学号'
                        elif col_lower in ['班级', 'class', 'class_name', '班级名称']:
                            col_map[col] = '班级'
                        elif col_lower in ['得分', 'score', '分数', '总分', '成绩', '得分率']:
                            col_map[col] = '得分'
                    
                    # 确保必需列存在
                    if len(col_map) < 2:
                        self.send_json({
                            'error': f'未能识别数据列。当前 sheet "{target_sheet}" 的列：{list(df.columns)}。请确保 Excel 包含"姓名"、"学号"、"班级"、"得分"等列。'
                        })
                        return
                    
                    students = []
                    for _, row in df.iterrows():
                        # 根据映射获取值
                        name_col = [k for k, v in col_map.items() if v == '姓名']
                        id_col = [k for k, v in col_map.items() if v == '学号']
                        class_col = [k for k, v in col_map.items() if v == '班级']
                        score_col = [k for k, v in col_map.items() if v == '得分']
                        
                        name = str(row[name_col[0]]).strip() if name_col else ''
                        student_id = str(row[id_col[0]]).strip() if id_col else ''
                        class_name = str(row[class_col[0]]).strip() if class_col else ''
                        score_val = row[score_col[0]] if score_col else None
                        
                        # 跳过无效行
                        if not name or name == 'nan' or not student_id or student_id == 'nan':
                            continue
                        if class_name == 'nan' or not class_name:
                            continue
                        
                        # 处理得分
                        score = None
                        if score_val is not None and str(score_val) not in ['nan', '缺考', 'NaT', '']:
                            try:
                                # 如果是得分率（如0.95），转换为得分（95）
                                val = float(score_val)
                                if 0 < val <= 1:
                                    score = round(val * 100, 1)
                                else:
                                    score = val
                            except:
                                continue
                        
                        # 标准化学号
                        student_id = student_id.replace('.0', '').strip()
                        
                        students.append({
                            '姓名': name,
                            '学号': student_id,
                            '班级': class_name,
                            '得分': score
                        })
                    
                    self.send_json({
                        'students': students,
                        'total': len(students),
                        'sheet_used': target_sheet,
                        'columns_found': list(col_map.values())
                    })
                    
                except Exception as e:
                    import traceback
                    self.send_json({'error': str(e) + '\n' + traceback.format_exc()})
                finally:
                    try: os.unlink(tmp_path)
                    except: pass
                    
            except Exception as e:
                import traceback
                self.send_json({'error': str(e) + '\n' + traceback.format_exc()})
        else:
            self.send_json({'error': '未知路径'})

if __name__ == '__main__':
    os.chdir(BASE_DIR)
    print(f'''
╔═══════════════════════════════════════════╗
║   🎁 科学复习系统 - 奖励发放管理          ║
╠═══════════════════════════════════════════╣
║   服务器已启动                           ║
║                                           ║
║   📂 打开管理界面:                       ║
║   http://localhost:{PORT}/admin/reward-manager.html
║                                           ║
║   按 Ctrl+C 停止服务器                   ║
╚═══════════════════════════════════════════╝
''')
    with socketserver.TCPServer(('localhost', PORT), Handler) as httpd:
        httpd.serve_forever()
