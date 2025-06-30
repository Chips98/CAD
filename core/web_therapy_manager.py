#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Web治疗管理器
专门为Web界面设计的治疗会话管理器，支持实时状态推送和详细显示
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict

from .ai_to_ai_therapy_manager import AIToAITherapyManager, TherapyProgress, DialogueTurn
from .therapy_session_manager import TherapySessionManager
from utils.psychology_display import format_psychological_state_for_web


@dataclass
class WebTherapyMessage:
    """Web治疗消息格式"""
    type: str  # 'system', 'therapist', 'patient', 'analysis', 'state'
    content: str
    timestamp: str
    metadata: Dict[str, Any] = None
    
    def to_dict(self):
        return asdict(self)


class WebTherapyManager:
    """Web治疗管理器 - 专门为Web界面优化"""
    
    def __init__(self, ai_client, patient_log_path: str, socketio_emit_func: Callable):
        """
        初始化Web治疗管理器
        
        Args:
            ai_client: AI客户端实例
            patient_log_path: 患者数据日志路径
            socketio_emit_func: SocketIO发送函数
        """
        self.ai_client = ai_client
        self.patient_log_path = patient_log_path
        self.emit = socketio_emit_func
        
        # 创建底层治疗管理器
        self.therapy_manager = AIToAITherapyManager(ai_client, patient_log_path)
        
        # Web会话状态
        self.session_id = f"web_therapy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.messages: List[WebTherapyMessage] = []
        self.current_turn = 0
        
    def _send_message(self, msg_type: str, content: str, metadata: Dict[str, Any] = None):
        """发送消息到Web界面"""
        message = WebTherapyMessage(
            type=msg_type,
            content=content,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        self.messages.append(message)
        
        # 通过SocketIO发送到Web界面
        self.emit('therapy_message', message.to_dict())
    
    def _send_psychology_state(self, state_data: Dict[str, Any], turn: int):
        """发送心理状态详情到Web界面"""
        # 格式化心理状态数据
        formatted_state = format_psychological_state_for_web(state_data)
        
        self._send_message(
            'psychology_state',
            f"📊 患者心理状态详情 - 第{turn}轮",
            {
                'turn': turn,
                'state_data': formatted_state,
                'raw_data': state_data
            }
        )
    
    def _send_therapy_analysis(self, analysis_data: Dict[str, Any], turn: int):
        """发送治疗分析到Web界面"""
        analysis_content = f"""
💡 治疗效果分析 - 第{turn}轮

🎯 技巧运用效果: {analysis_data.get('technique_effectiveness', 0):.1f}/10
🤝 患者开放程度: {analysis_data.get('patient_openness', 0):.1f}/10  
❤️ 情感连接质量: {analysis_data.get('emotional_connection', 0):.1f}/10
🧠 认知洞察深度: {analysis_data.get('cognitive_insight', 0):.1f}/10
📈 整体效果评分: {analysis_data.get('overall_effectiveness', 0):.1f}/10

📝 分析说明: {analysis_data.get('analysis_notes', '暂无')}
        """.strip()
        
        self._send_message(
            'therapy_analysis',
            analysis_content,
            {
                'turn': turn,
                'analysis_data': analysis_data
            }
        )
    
    def _send_therapy_progress(self, progress: TherapyProgress):
        """发送治疗进展到Web界面"""
        progress_content = f"""
📈 治疗进展评估 - 第{progress.turn_number}轮

🎯 治疗效果: {progress.therapy_effectiveness:.1f}/10
🤝 治疗联盟: {progress.therapeutic_alliance:.1f}/10
😊 情绪状态: {progress.patient_emotional_state:.1f}/10
        """
        
        if progress.breakthrough_moment:
            progress_content += "\n🎉 检测到突破性治疗时刻！"
        
        if progress.risk_indicators:
            progress_content += f"\n⚠️ 风险指标: {', '.join(progress.risk_indicators)}"
        
        self._send_message(
            'therapy_progress',
            progress_content.strip(),
            {
                'turn': progress.turn_number,
                'effectiveness': progress.therapy_effectiveness,
                'alliance': progress.therapeutic_alliance,
                'emotional_state': progress.patient_emotional_state,
                'breakthrough': progress.breakthrough_moment,
                'risks': progress.risk_indicators
            }
        )
    
    def _send_session_header(self, patient_name: str, session_info: Dict[str, Any]):
        """发送会话头部信息"""
        header_content = f"""
🎭 AI对AI心理治疗会话

👤 患者: {patient_name}
🆔 会话ID: {self.session_id}
⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🤖 AI提供商: {session_info.get('ai_provider', '未知')}
        """.strip()
        
        self._send_message(
            'session_header',
            header_content,
            session_info
        )
    
    async def start_ai_to_ai_therapy(self, max_turns: int = 15) -> Dict[str, Any]:
        """启动AI对AI治疗会话"""
        try:
            # 发送会话开始信息
            patient_name = self.therapy_manager.patient_data.get('protagonist_character_profile', {}).get('name', '患者')
            self._send_session_header(patient_name, {
                'max_turns': max_turns,
                'ai_provider': 'AI模型'
            })
            
            self._send_message('system', '🚀 正在启动AI对AI治疗会话...')
            
            # 修改原始治疗管理器以支持Web回调
            original_dialogue_history = []
            
            for turn in range(1, max_turns + 1):
                self.current_turn = turn
                
                # 发送回合开始信息
                self._send_message('system', f'💬 第{turn}轮对话开始')
                
                # 生成治疗师消息
                self._send_message('system', '🤖 AI治疗师正在分析患者状态...')
                
                # 获取治疗师回应
                therapist_message = await self.therapy_manager._generate_therapist_response()
                clean_therapist_message = self.therapy_manager._clean_therapist_message(therapist_message)
                
                # 显示治疗师消息
                self._send_message(
                    'therapist',
                    clean_therapist_message,
                    {'turn': turn, 'raw_message': therapist_message}
                )
                
                # 生成患者回应
                self._send_message('system', '👤 患者正在回应...')
                patient_response = await self.therapy_manager._generate_patient_response(clean_therapist_message)
                
                # 显示患者回应
                self._send_message(
                    'patient',
                    patient_response,
                    {'turn': turn}
                )
                
                # 获取患者状态
                patient_state = self.therapy_manager._get_patient_state_snapshot()
                self._send_psychology_state(patient_state, turn)
                
                # 分析对话效果
                self._send_message('system', '📊 正在分析对话效果...')
                analysis = await self.therapy_manager._analyze_dialogue_turn(therapist_message, patient_response)
                self._send_therapy_analysis(analysis, turn)
                
                # 记录对话轮次
                dialogue_turn = DialogueTurn(
                    turn_number=turn,
                    timestamp=datetime.now().isoformat(),
                    therapist_message=therapist_message,
                    patient_response=patient_response,
                    therapy_analysis=analysis,
                    patient_state_change=patient_state
                )
                self.therapy_manager.dialogue_history.append(dialogue_turn)
                
                # 评估治疗进展
                if turn % self.therapy_manager.evaluation_interval == 0:
                    self._send_message('system', '📈 正在评估治疗进展...')
                    progress = await self.therapy_manager._evaluate_therapy_progress()
                    self._send_therapy_progress(progress)
                    self.therapy_manager.progress_history.append(progress)
                
                # 短暂延迟以便Web界面显示
                await asyncio.sleep(1)
            
            # 生成最终总结
            self._send_message('system', '📋 正在生成治疗总结...')
            
            final_summary = {
                'session_id': self.session_id,
                'total_turns': max_turns,
                'patient_name': patient_name,
                'average_effectiveness': sum(d.therapy_analysis.get('overall_effectiveness', 0) 
                                           for d in self.therapy_manager.dialogue_history) / len(self.therapy_manager.dialogue_history),
                'final_progress': self.therapy_manager.progress_history[-1] if self.therapy_manager.progress_history else None
            }
            
            # 保存会话记录
            self._save_web_session_log(final_summary)
            
            self._send_message('system', '✅ AI对AI治疗会话完成！')
            
            return final_summary
            
        except Exception as e:
            self._send_message('system', f'❌ 治疗会话出错: {str(e)}')
            raise
    
    def _save_web_session_log(self, summary: Dict[str, Any]):
        """保存Web会话记录"""
        try:
            # 保存到对应的模拟目录
            patient_log_path = Path(self.patient_log_path)
            if patient_log_path.name == 'final_report.json':
                sim_dir = patient_log_path.parent
            else:
                sim_dir = patient_log_path.parent
            
            # 创建Web会话记录
            web_session_file = sim_dir / f"web_therapy_{self.session_id}.json"
            
            session_data = {
                'session_metadata': {
                    'session_id': self.session_id,
                    'start_time': datetime.now().isoformat(),
                    'session_type': 'web_ai_to_ai',
                    'patient_file': str(self.patient_log_path)
                },
                'summary': summary,
                'messages': [msg.to_dict() for msg in self.messages],
                'dialogue_history': [asdict(d) for d in self.therapy_manager.dialogue_history],
                'progress_history': [asdict(p) for p in self.therapy_manager.progress_history]
            }
            
            with open(web_session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self._send_message('system', f'⚠️ 保存会话记录失败: {str(e)}')


async def run_web_ai_to_ai_therapy(ai_client, patient_log_path: str, max_turns: int = 15, socketio_emit_func: Callable = None) -> Dict[str, Any]:
    """
    运行Web AI对AI治疗会话的便捷函数
    
    Args:
        ai_client: AI客户端
        patient_log_path: 患者数据路径
        max_turns: 最大对话轮数
        socketio_emit_func: SocketIO发送函数
        
    Returns:
        治疗会话总结
    """
    manager = WebTherapyManager(ai_client, patient_log_path, socketio_emit_func or (lambda event, data: None))
    return await manager.start_ai_to_ai_therapy(max_turns)