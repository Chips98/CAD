#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
抑郁症模拟系统Web界面
基于Flask的Web应用，提供友好的用户界面
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_socketio import SocketIO, emit
import threading

# 导入系统核心模块
from core.simulation_engine import SimulationEngine
from core.ai_to_ai_therapy_manager import AIToAITherapyManager
from core.ai_client_factory import ai_client_factory
from config.config_loader import load_scenario, list_scenarios, load_simulation_params

app = Flask(__name__)
app.config['SECRET_KEY'] = 'depression_simulator_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局状态管理
simulation_manager = None
current_session = None

@app.route('/')
def index():
    """主页 - 系统概览"""
    return render_template('index.html')

@app.route('/simulation')
def simulation_page():
    """模拟配置页面"""
    try:
        # 获取可用场景列表
        scenarios = list_scenarios()
        scenario_info = []
        
        for scenario_name in scenarios:
            try:
                scenario = load_scenario(scenario_name)
                scenario_info.append({
                    'name': scenario_name,
                    'display_name': scenario.get('scenario_name', scenario_name),
                    'description': scenario.get('description', '无描述')
                })
            except:
                pass
        
        # 获取模拟参数
        sim_params = load_simulation_params()
        
        return render_template('simulation.html', 
                             scenarios=scenario_info, 
                             default_params=sim_params)
    
    except Exception as e:
        flash(f'加载配置失败: {e}', 'error')
        return render_template('simulation.html', scenarios=[], default_params={})

@app.route('/therapy')
def therapy_page():
    """AI对话治疗页面"""
    return render_template('therapy_enhanced.html')

@app.route('/therapy_old')
def therapy_old_page():
    """旧版AI对话治疗页面"""
    return render_template('therapy.html')

@app.route('/analysis')
def analysis_page():
    """数据分析页面"""
    # 扫描日志目录获取历史模拟数据
    logs_dir = Path("logs")
    simulation_logs = []
    
    if logs_dir.exists():
        for sim_dir in logs_dir.iterdir():
            if sim_dir.is_dir() and sim_dir.name.startswith("sim_"):
                final_report = sim_dir / "final_report.json"
                if final_report.exists():
                    try:
                        with open(final_report, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        simulation_logs.append({
                            'id': sim_dir.name,
                            'timestamp': data.get('simulation_metadata', {}).get('end_time', '未知'),
                            'protagonist': data.get('protagonist_character_profile', {}).get('name', '未知'),
                            'final_depression': data.get('final_psychological_state', {}).get('depression_level', '未知'),
                            'path': str(final_report)
                        })
                    except:
                        pass
    
    # 按时间排序（最新的在前）
    simulation_logs.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return render_template('analysis.html', simulation_logs=simulation_logs[:20])  # 最近20个

@app.route('/api/scenarios')
def api_scenarios():
    """API: 获取场景列表"""
    try:
        scenarios = list_scenarios()
        return jsonify({'success': True, 'scenarios': scenarios})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/start_simulation', methods=['POST'])
def api_start_simulation():
    """API: 启动模拟"""
    global simulation_manager
    
    try:
        data = request.json
        scenario_name = data.get('scenario', 'default_adolescent')
        sim_days = data.get('simulation_days', 30)
        ai_provider = data.get('ai_provider', 'deepseek')
        
        # 在后台线程启动模拟
        simulation_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 使用新的JSON配置系统创建模拟引擎
        from config.config_loader import load_complete_config
        config_data = load_complete_config(scenario_name)
        
        simulation_manager = SimulationEngine(
            simulation_id=simulation_id,
            config_data=config_data,
            model_provider=ai_provider
        )
        
        def run_simulation():
            try:
                # 初始化模拟引擎
                simulation_manager.setup_simulation()
                
                socketio.emit('simulation_status', {
                    'status': 'running', 
                    'message': '模拟正在运行中...',
                    'simulation_id': simulation_id
                })
                
                # 运行真实的模拟
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                async def simulation_with_progress():
                    # 创建进度报告任务
                    async def report_progress():
                        for day in range(1, sim_days + 1):
                            await asyncio.sleep(0.1)  # 短暂延迟
                            socketio.emit('simulation_progress', {
                                'day': day,
                                'total_days': sim_days,
                                'progress': (day / sim_days) * 100,
                                'message': f'正在模拟第{day}天...'
                            })
                    
                    # 启动进度报告
                    progress_task = asyncio.create_task(report_progress())
                    
                    # 运行实际模拟
                    final_report = await simulation_manager.run_simulation(sim_days)
                    
                    # 等待进度报告完成
                    await progress_task
                    
                    return final_report
                
                final_report = loop.run_until_complete(simulation_with_progress())
                
                socketio.emit('simulation_status', {
                    'status': 'completed',
                    'message': '模拟完成！',
                    'simulation_id': simulation_id,
                    'report_summary': {
                        'protagonist': final_report.get('protagonist_character_profile', {}).get('name', '未知'),
                        'final_depression_level': final_report.get('final_psychological_state', {}).get('depression_level', '未知'),
                        'total_events': len(final_report.get('all_daily_events_combined', []))
                    }
                })
                
            except Exception as e:
                import traceback
                error_msg = f'模拟失败: {str(e)}'
                print(f"Simulation error: {traceback.format_exc()}")
                socketio.emit('simulation_status', {
                    'status': 'error',
                    'message': error_msg
                })
        
        thread = threading.Thread(target=run_simulation)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True, 
            'message': '模拟已启动',
            'simulation_id': simulation_id
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/start_ai_therapy', methods=['POST'])
def api_start_ai_therapy():
    """API: 启动AI对AI治疗"""
    try:
        data = request.json
        patient_file = data.get('patient_file')
        max_turns = data.get('max_turns', 15)
        ai_provider = data.get('ai_provider', 'deepseek')
        
        if not patient_file:
            return jsonify({'success': False, 'error': '请选择患者数据文件'})
        
        # 创建AI客户端
        ai_client = ai_client_factory.get_client(ai_provider)
        
        # 生成会话ID
        session_id = f"therapy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        def run_therapy():
            try:
                # 使用新的Web治疗管理器
                from core.web_therapy_manager import run_web_ai_to_ai_therapy
                
                # 异步运行治疗会话
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # 发送初始状态
                socketio.emit('therapy_status', {
                    'status': 'starting',
                    'message': '正在启动AI对AI治疗会话...',
                    'session_id': session_id
                })
                
                # 运行增强的Web治疗会话
                summary = loop.run_until_complete(
                    run_web_ai_to_ai_therapy(
                        ai_client=ai_client,
                        patient_log_path=patient_file,
                        max_turns=max_turns,
                        socketio_emit_func=socketio.emit
                    )
                )
                
                # 发送完成状态
                socketio.emit('therapy_status', {
                    'status': 'completed',
                    'message': '✅ AI对AI治疗会话完成！',
                    'session_id': session_id,
                    'summary': summary
                })
                
            except Exception as e:
                import traceback
                error_msg = f'治疗会话失败: {str(e)}'
                print(f"Therapy error: {traceback.format_exc()}")
                socketio.emit('therapy_status', {
                    'status': 'error',
                    'message': error_msg,
                    'session_id': session_id
                })
        
        thread = threading.Thread(target=run_therapy)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'AI对AI治疗会话已启动',
            'session_id': session_id
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/patient_files')
def api_patient_files():
    """API: 获取患者数据文件列表"""
    try:
        logs_dir = Path("logs")
        simulations = []
        
        if logs_dir.exists():
            for sim_dir in sorted(logs_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
                if sim_dir.is_dir() and sim_dir.name.startswith("sim_"):
                    sim_info = {
                        'sim_id': sim_dir.name,
                        'status': '',
                        'patient_name': '未知',
                        'depression_level': '未知',
                        'therapy_sessions': 0,
                        'files': []
                    }
                    
                    # 检查最终报告
                    final_report = sim_dir / "final_report.json"
                    has_final_report = final_report.exists()
                    
                    # 检查每日记录
                    daily_files = [f for f in sim_dir.glob("day_*.json")]
                    daily_count = len(daily_files)
                    
                    # 检查治疗记录
                    therapy_files = [f for f in sim_dir.glob("therapy_*.json")]
                    therapy_count = len(therapy_files)
                    
                    # 设置状态
                    if has_final_report and daily_count >= 30:
                        sim_info['status'] = f'完整模拟 ({daily_count}天记录)'
                        
                        # 读取患者信息
                        try:
                            with open(final_report, 'r', encoding='utf-8') as f:
                                report_data = json.load(f)
                                sim_info['patient_name'] = report_data.get('protagonist_character_profile', {}).get('name', '未知')
                                sim_info['depression_level'] = report_data.get('final_psychological_state', {}).get('depression_level', '未知')
                        except:
                            pass
                    elif has_final_report:
                        sim_info['status'] = f'有最终报告 ({daily_count}天记录)'
                    elif daily_count > 0:
                        sim_info['status'] = f'部分完成 ({daily_count}天记录)'
                    else:
                        sim_info['status'] = '无记录'
                    
                    sim_info['therapy_sessions'] = therapy_count
                    
                    # 添加可用文件
                    if has_final_report:
                        sim_info['files'].append({
                            'type': 'complete',
                            'name': '完整历史数据',
                            'path': str(final_report),
                            'description': '整合final_report.json及所有每日事件'
                        })
                        sim_info['files'].append({
                            'type': 'report_only', 
                            'name': '最终报告',
                            'path': str(final_report),
                            'description': 'final_report.json'
                        })
                    
                    # 添加每日文件
                    for day_file in sorted(daily_files):
                        day_num = day_file.stem.split('_')[1]
                        sim_info['files'].append({
                            'type': 'daily',
                            'name': f'第{day_num}天状态',
                            'path': str(day_file),
                            'description': f'day_{day_num}_state.json'
                        })
                    
                    simulations.append(sim_info)
        
        return jsonify({'success': True, 'simulations': simulations})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/analysis/<simulation_id>')
def api_analysis(simulation_id):
    """API: 获取指定模拟的分析数据"""
    try:
        log_file = Path("logs") / simulation_id / "final_report.json"
        
        if not log_file.exists():
            return jsonify({'success': False, 'error': '找不到指定的模拟数据'})
        
        with open(log_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 提取关键分析数据
        analysis = {
            'protagonist_profile': data.get('protagonist_character_profile', {}),
            'final_state': data.get('final_psychological_state', {}),
            'daily_evolution': data.get('daily_psychological_evolution', []),
            'cad_analysis': data.get('cad_detailed_analysis', {}),
            'events_summary': data.get('all_daily_events_combined', [])[-10:],  # 最后10个事件
            'metadata': data.get('simulation_metadata', {})
        }
        
        return jsonify({'success': True, 'analysis': analysis})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/start_human_therapy', methods=['POST'])
def api_start_human_therapy():
    """API: 启动人工治疗对话"""
    try:
        data = request.json
        patient_file = data.get('patient_file')
        ai_provider = data.get('ai_provider', 'deepseek')
        
        if not patient_file:
            return jsonify({'success': False, 'error': '请选择患者数据文件'})
        
        # 验证文件存在
        if not Path(patient_file).exists():
            return jsonify({'success': False, 'error': '患者数据文件不存在'})
        
        # 创建会话ID
        session_id = f"human_therapy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 初始化治疗会话管理器
        from core.therapy_session_manager import TherapySessionManager
        from core.ai_client_factory import ai_client_factory
        
        ai_client = ai_client_factory.get_client(ai_provider)
        therapy_manager = TherapySessionManager(ai_client=ai_client)
        
        # 加载患者数据
        load_successful = therapy_manager.load_patient_data_from_file(patient_file, load_type="final_report")
        if not load_successful:
            return jsonify({'success': False, 'error': '无法加载患者数据'})
        
        # 存储会话信息
        app.therapy_sessions = getattr(app, 'therapy_sessions', {})
        app.therapy_sessions[session_id] = {
            'manager': therapy_manager,
            'patient_file': patient_file,
            'ai_provider': ai_provider,
            'created_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'message': '人工治疗会话已创建',
            'session_id': session_id,
            'patient_info': {
                'name': therapy_manager.patient_data.get('name', '未知'),
                'depression_level': getattr(therapy_manager, 'loaded_data_type', '未知')
            }
        })
    
    except Exception as e:
        import traceback
        print(f"Human therapy error: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/human_therapy_message', methods=['POST'])
def api_human_therapy_message():
    """API: 发送人工治疗消息"""
    try:
        data = request.json
        session_id = data.get('session_id')
        message = data.get('message')
        
        if not session_id or not message:
            return jsonify({'success': False, 'error': '缺少会话ID或消息内容'})
        
        # 获取会话
        if not hasattr(app, 'therapy_sessions') or session_id not in app.therapy_sessions:
            return jsonify({'success': False, 'error': '会话不存在或已过期'})
        
        session_info = app.therapy_sessions[session_id]
        therapy_manager = session_info['manager']
        
        # 处理消息
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        patient_response = loop.run_until_complete(
            therapy_manager.process_therapist_message(message)
        )
        
        return jsonify({
            'success': True,
            'patient_response': patient_response,
            'session_progress': therapy_manager.get_session_progress()
        })
    
    except Exception as e:
        import traceback
        print(f"Therapy message error: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/therapy_session/<session_id>')
def api_therapy_session_info(session_id):
    """API: 获取治疗会话信息"""
    try:
        if not hasattr(app, 'therapy_sessions') or session_id not in app.therapy_sessions:
            return jsonify({'success': False, 'error': '会话不存在'})
        
        session_info = app.therapy_sessions[session_id]
        therapy_manager = session_info['manager']
        
        return jsonify({
            'success': True,
            'session_info': {
                'session_id': session_id,
                'patient_info': therapy_manager.get_patient_info(),
                'session_progress': therapy_manager.get_session_progress(),
                'dialogue_history': therapy_manager.get_dialogue_history(),
                'created_at': session_info['created_at']
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@socketio.on('connect')
def handle_connect():
    """WebSocket连接处理"""
    emit('connected', {'message': '连接成功'})

@socketio.on('disconnect')
def handle_disconnect():
    """WebSocket断开处理"""
    print('Client disconnected')

if __name__ == '__main__':
    # 确保必要的目录存在
    Path("logs").mkdir(exist_ok=True)
    Path("web/static").mkdir(exist_ok=True)
    Path("web/templates").mkdir(exist_ok=True)
    
    print("🌐 启动抑郁症模拟系统Web界面...")
    print("📍 访问地址: http://localhost:5000")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True) 