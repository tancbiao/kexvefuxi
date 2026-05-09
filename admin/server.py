"""
科学复习系统 - 奖励发放管理服务器 (Railway 部署版)
"""
import asyncio
from aiohttp import web
import os
import json
import re
import tempfile

PORT = int(os.environ.get('PORT', 8888))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REWARDS_FILE = os.path.join(BASE_DIR, 'rewards.json')


async def get_rewards(request):
    """奖励查询接口：/get-rewards?studentId=xxx"""
    student_id = request.query.get('studentId', '')
    
    if not student_id:
        return web.json_response({'error': '缺少 studentId 参数'})
    
    if not os.path.exists(REWARDS_FILE):
        return web.json_response({'rewards': []})
    
    try:
        with open(REWARDS_FILE, 'r', encoding='utf-8') as f:
            rewards_data = json.load(f)
        
        student_rewards = []
        for record in rewards_data.get('students', []):
            if str(record.get('studentId', '')) == str(student_id):
                student_rewards.extend(record.get('rewards', []))
        
        return web.json_response({'rewards': student_rewards})
    except Exception as e:
        return web.json_response({'error': str(e)})


async def parse_excel(request):
    """Excel 上传解析接口：POST /parse"""
    try:
        reader = await request.multipart()
        field = await reader.next()
        
        if not field or not field.filename:
            return web.json_response({'error': '未找到上传文件'})
        
        # 读取文件内容到临时文件
        content = await field.read()
        import pandas as pd
        import io
        
        xl = pd.ExcelFile(io.BytesIO(content))
        sheet_names = xl.sheet_names
        
        target_sheet = None
        df = None
        
        if '总数据' in sheet_names:
            target_sheet = '总数据'
            df = pd.read_excel(io.BytesIO(content), sheet_name=target_sheet, dtype={'学号': str})
        else:
            possible_sheets = ['数据', '成绩', '分析', 'Sheet1', '成绩分析', '总分']
            for name in possible_sheets:
                if name in sheet_names:
                    target_sheet = name
                    df = pd.read_excel(io.BytesIO(content), sheet_name=target_sheet, dtype={'学号': str})
                    break
            
            if df is None:
                target_sheet = sheet_names[0]
                df = pd.read_excel(io.BytesIO(content), sheet_name=target_sheet, dtype={'学号': str})
        
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
        
        if len(col_map) < 2:
            return web.json_response({
                'error': f'未能识别数据列。当前列：{list(df.columns)}'
            })
        
        students = []
        for _, row in df.iterrows():
            name_col = [k for k, v in col_map.items() if v == '姓名']
            id_col = [k for k, v in col_map.items() if v == '学号']
            class_col = [k for k, v in col_map.items() if v == '班级']
            score_col = [k for k, v in col_map.items() if v == '得分']
            
            name = str(row[name_col[0]]).strip() if name_col else ''
            student_id = str(row[id_col[0]]).strip().replace('.0', '') if id_col else ''
            class_name = str(row[class_col[0]]).strip() if class_col else ''
            score_val = row[score_col[0]] if score_col else None
            
            if not name or name == 'nan' or not student_id or student_id == 'nan':
                continue
            if class_name == 'nan' or not class_name:
                continue
            
            score = None
            if score_val is not None and str(score_val) not in ['nan', '缺考', 'NaT', '']:
                try:
                    val = float(score_val)
                    score = round(val * 100, 1) if 0 < val <= 1 else val
                except:
                    continue
            
            students.append({
                '姓名': name,
                '学号': student_id,
                '班级': class_name,
                '得分': score
            })
        
        return web.json_response({
            'students': students,
            'total': len(students),
            'sheet_used': target_sheet,
            'columns_found': list(col_map.values())
        })
        
    except Exception as e:
        import traceback
        return web.json_response({'error': str(e) + '\n' + traceback.format_exc()})


app = web.Application()
app.router.add_get('/get-rewards', get_rewards)
app.router.add_post('/parse', parse_excel)
# 添加静态文件服务
app.router.add_static('/', path=BASE_DIR, show_index=True)


if __name__ == '__main__':
    print(f'🚀 奖励发放系统启动于 http://0.0.0.0:{PORT}')
    web.run_app(app, host='0.0.0.0', port=PORT)
