#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI对AI治疗管理器
管理AI心理咨询师与AI患者之间的自动对话会话
提供实时进展监测、治疗效果评估和会话记录功能
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from .therapy_session_manager import TherapySessionManager
from agents.ai_therapist_agent import AITherapistAgent
from agents.student_agent import StudentAgent
from agents.therapist_agent import TherapistAgent
from models.psychology_models import CognitiveAffectiveState, CoreBeliefs, CognitiveProcessing, BehavioralInclination
from utils.psychology_display import (
    display_therapist_response_with_strategy, 
    display_patient_response, 
    create_session_header,
    console
)
from config.config_loader import load_therapy_guidance_config

# 抑郁程度映射（10级精细分级系统）
DEPRESSION_LEVELS = {
    "OPTIMAL": 0,          # 最佳状态
    "HEALTHY": 1,          # 健康正常
    "MINIMAL_SYMPTOMS": 2, # 最小症状
    "MILD_RISK": 3,        # 轻度风险
    "MILD": 4,             # 轻度抑郁
    "MODERATE_MILD": 5,    # 中轻度抑郁
    "MODERATE": 6,         # 中度抑郁
    "MODERATE_SEVERE": 7,  # 中重度抑郁
    "SEVERE": 8,           # 重度抑郁
    "CRITICAL": 9          # 极重度抑郁
}

# 反向映射
DEPRESSION_LEVEL_NAMES = {v: k for k, v in DEPRESSION_LEVELS.items()}

@dataclass
class TherapyProgress:
    """治疗进展数据结构"""
    turn_number: int
    therapy_effectiveness: float  # 0-10
    therapeutic_alliance: float   # 0-10 
    patient_emotional_state: float  # 0-10
    breakthrough_moment: bool
    risk_indicators: List[str]
    
    
@dataclass
class DialogueTurn:
    """对话轮次数据结构"""
    turn_number: int
    timestamp: str
    therapist_message: str
    patient_response: str
    therapy_analysis: Dict[str, Any]
    patient_state_change: Dict[str, Any]


class AIToAITherapyManager:
    """AI对AI治疗会话管理器"""
    
    def __init__(self, ai_client, patient_log_path: str):
        """
        初始化AI对AI治疗管理器
        
        Args:
            ai_client: AI客户端实例
            patient_log_path: 患者数据日志路径
        """
        self.ai_client = ai_client
        self.patient_log_path = patient_log_path
        
        # 加载治疗引导配置
        self.therapy_config = load_therapy_guidance_config("ai_to_ai_therapy")
        
        # 加载患者数据
        self.patient_data = self._load_patient_data()
        
        # 创建AI治疗师和患者Agent
        self.therapist_agent = AITherapistAgent("Dr. AI", ai_client)
        self.patient_agent = self._create_patient_agent()
        
        # 添加督导Agent
        self.supervisor_agent = TherapistAgent("专业心理督导", ai_client)
        
        # 会话状态
        self.dialogue_history: List[DialogueTurn] = []
        self.progress_history: List[TherapyProgress] = []
        self.session_id = f"ai_therapy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_turn = 0
        
        # 从配置加载督导间隔
        supervision_config = self.therapy_config.get('supervision_settings', {})
        self.supervision_interval = supervision_config.get('supervision_interval', 3)
        self.evaluation_interval = 1  # 每轮都评估
        self.max_conversation_history = 10  # 保持最近10轮对话的上下文
        
        # 添加恢复追踪机制（类似TherapySessionManager）
        self.initial_depression_level = None
        self.current_depression_level = None
        self.recovery_progress = []
        self.therapeutic_alliance_score = 0.0
        self.session_effectiveness_scores = []
        
        # 初始化恢复追踪
        self._initialize_recovery_tracking()
        
    def _load_patient_data(self) -> Dict[str, Any]:
        """加载患者数据"""
        try:
            with open(self.patient_log_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 判断数据类型并进行适配
            if 'day' in data and 'protagonist' in data:
                # 这是day_X_state.json格式的数据
                return self._adapt_day_state_data(data)
            elif 'protagonist_character_profile' in data:
                # 这是final_report.json格式的数据
                return data
            else:
                raise ValueError("未识别的数据格式")
                
        except Exception as e:
            raise ValueError(f"无法加载患者数据: {e}")
    
    def _adapt_day_state_data(self, day_data: Dict[str, Any]) -> Dict[str, Any]:
        """将day_X_state.json格式的数据适配为AI-AI治疗所需的格式"""
        protagonist = day_data.get('protagonist', {})
        
        # 构建兼容的数据结构
        adapted_data = {
            'protagonist_character_profile': {
                'name': protagonist.get('name', '李明'),
                'age': protagonist.get('age', 17),
                'personality': protagonist.get('personality', {})
            },
            'final_psychological_state': {
                'depression_level': protagonist.get('current_mental_state', {}).get('depression_level', 'MODERATE'),
                'cad_state': protagonist.get('current_mental_state', {}).get('cad_state', {})
            },
            'daily_events': {
                f"day_{day_data.get('day', 1)}": day_data.get('events', [])
            },
            'simulation_metadata': {
                'end_time': day_data.get('timestamp', '未知时间'),
                'data_source': 'day_state',
                'source_day': day_data.get('day', 1)
            }
        }
        
        return adapted_data
    
    def _extract_strategy_analysis(self, therapist_message: str) -> Optional[str]:
        """从治疗师消息中提取策略分析"""
        # 查找策略分析部分
        if "（这个回应：" in therapist_message:
            start_idx = therapist_message.find("（这个回应：")
            end_idx = therapist_message.find("）", start_idx)
            if end_idx > start_idx:
                return therapist_message[start_idx+6:end_idx]
        
        # 查找其他格式的策略分析
        if "这个回应：" in therapist_message:
            lines = therapist_message.split('\n')
            strategy_lines = []
            in_strategy = False
            
            for line in lines:
                if "这个回应：" in line:
                    in_strategy = True
                    continue
                elif in_strategy and line.strip():
                    if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.')):
                        strategy_lines.append(line.strip())
                    elif not line.strip().startswith(('-', '•')):
                        break
            
            if strategy_lines:
                return '\n'.join(strategy_lines)
        
        return None
    
    def _clean_therapist_message(self, therapist_message: str) -> str:
        """清理治疗师消息，移除策略分析部分"""
        # 移除策略分析部分
        if "（这个回应：" in therapist_message:
            end_idx = therapist_message.find("）")
            if end_idx > 0:
                return therapist_message[:therapist_message.find("（这个回应：")].strip()
        
        # 移除引号
        message = therapist_message.strip()
        if message.startswith('"') and message.endswith('"'):
            message = message[1:-1]
        
        return message.strip()
    
    def _get_patient_display_data(self) -> Dict[str, Any]:
        """获取用于显示的患者数据"""
        cad_state = self.patient_agent.cad_state
        
        return {
            'name': self.patient_agent.name,
            'age': getattr(self.patient_agent, 'age', 17),
            'current_mental_state': {
                'emotion': getattr(self.patient_agent, 'current_emotion', '焦虑'),
                'depression_level': self.patient_agent.depression_level,
                'stress_level': getattr(self.patient_agent, 'stress_level', 8),
                'self_esteem': getattr(self.patient_agent, 'self_esteem', 3),
                'social_connection': getattr(self.patient_agent, 'social_connection', 4),
                'academic_pressure': getattr(self.patient_agent, 'academic_pressure', 7),
                'cad_state': {
                    'affective_tone': cad_state.affective_tone,
                    'core_beliefs': {
                        'self_belief': cad_state.core_beliefs.self_belief,
                        'world_belief': cad_state.core_beliefs.world_belief,
                        'future_belief': cad_state.core_beliefs.future_belief
                    },
                    'cognitive_processing': {
                        'rumination': cad_state.cognitive_processing.rumination,
                        'distortions': cad_state.cognitive_processing.distortions
                    },
                    'behavioral_inclination': {
                        'social_withdrawal': cad_state.behavioral_inclination.social_withdrawal,
                        'avolition': cad_state.behavioral_inclination.avolition
                    }
                }
            }
        }
    
    def _display_therapy_progress(self, progress: TherapyProgress, turn: int) -> None:
        """显示治疗进展评估"""
        from rich.table import Table
        from rich.panel import Panel
        from rich.box import ROUNDED
        
        # 创建进展表格
        progress_table = Table(title=f"📊 治疗进展评估 - 第{turn}轮", box=ROUNDED)
        progress_table.add_column("评估维度", style="bold cyan", width=15)
        progress_table.add_column("分数", justify="center", width=8)
        progress_table.add_column("状态", style="bold", width=12)
        progress_table.add_column("说明", width=20)
        
        # 治疗效果
        effect_color = "bright_green" if progress.therapy_effectiveness >= 7 else "green" if progress.therapy_effectiveness >= 5 else "yellow" if progress.therapy_effectiveness >= 3 else "red"
        progress_table.add_row(
            "治疗效果",
            f"{progress.therapy_effectiveness:.1f}/10",
            f"[{effect_color}]●[/{effect_color}]",
            self._get_effectiveness_description(progress.therapy_effectiveness)
        )
        
        # 治疗联盟
        alliance_color = "bright_green" if progress.therapeutic_alliance >= 7 else "green" if progress.therapeutic_alliance >= 5 else "yellow" if progress.therapeutic_alliance >= 3 else "red"
        progress_table.add_row(
            "治疗联盟",
            f"{progress.therapeutic_alliance:.1f}/10",
            f"[{alliance_color}]●[/{alliance_color}]",
            self._get_alliance_description(progress.therapeutic_alliance)
        )
        
        # 情绪状态
        emotion_color = "bright_green" if progress.patient_emotional_state >= 7 else "green" if progress.patient_emotional_state >= 5 else "yellow" if progress.patient_emotional_state >= 3 else "red"
        progress_table.add_row(
            "情绪状态",
            f"{progress.patient_emotional_state:.1f}/10",
            f"[{emotion_color}]●[/{emotion_color}]",
            self._get_emotion_description(progress.patient_emotional_state)
        )
        
        console.print()
        console.print(progress_table)
        
        # 显示特殊状态
        if progress.breakthrough_moment:
            breakthrough_panel = Panel(
                "[bold bright_green]🎉 检测到突破性治疗时刻！[/bold bright_green]\n"
                "[green]患者在本轮对话中表现出显著的认知或情感改善[/green]",
                border_style="bright_green",
                title="突破时刻"
            )
            console.print(breakthrough_panel)
        
        if progress.risk_indicators:
            risk_text = "⚠️  风险指标: " + ", ".join(progress.risk_indicators)
            risk_panel = Panel(
                f"[bold yellow]{risk_text}[/bold yellow]\n"
                "[yellow]需要特别关注的风险因素[/yellow]",
                border_style="yellow",
                title="风险警告"
            )
            console.print(risk_panel)
        
        console.print()
    
    def _get_effectiveness_description(self, score: float) -> str:
        """获取治疗效果描述"""
        if score >= 8: return "治疗效果显著"
        elif score >= 6: return "治疗效果良好"
        elif score >= 4: return "治疗效果一般"
        elif score >= 2: return "治疗效果较差"
        else: return "治疗效果很差"
    
    def _get_alliance_description(self, score: float) -> str:
        """获取治疗联盟描述"""
        if score >= 8: return "关系很好"
        elif score >= 6: return "关系良好"
        elif score >= 4: return "关系一般"
        elif score >= 2: return "关系较差"
        else: return "关系很差"
    
    def _get_emotion_description(self, score: float) -> str:
        """获取情绪状态描述"""
        if score >= 8: return "情绪很好"
        elif score >= 6: return "情绪较好"
        elif score >= 4: return "情绪一般"
        elif score >= 2: return "情绪较差"
        else: return "情绪很差"
    
    def _create_patient_agent(self) -> StudentAgent:
        """基于日志数据创建患者Agent"""
        # 从final_report中提取患者信息
        protagonist_data = self.patient_data.get('protagonist_character_profile', {})
        mental_state = self.patient_data.get('final_psychological_state', {})
        
        # 创建学生Agent实例
        patient_agent = StudentAgent(
            name=protagonist_data.get('name', '李明'),
            age=protagonist_data.get('age', 17),
            personality=protagonist_data.get('personality', {}),
            ai_client=self.ai_client
        )
        
        # 设置当前心理状态
        if 'cad_state' in mental_state:
            cad_data = mental_state['cad_state']
            core_beliefs = CoreBeliefs(
                self_belief=cad_data.get('core_beliefs', {}).get('self_belief', 0.0),
                world_belief=cad_data.get('core_beliefs', {}).get('world_belief', 0.0),
                future_belief=cad_data.get('core_beliefs', {}).get('future_belief', 0.0)
            )
            cognitive_processing = CognitiveProcessing(
                rumination=cad_data.get('cognitive_processing', {}).get('rumination', 0.0),
                distortions=cad_data.get('cognitive_processing', {}).get('distortions', 0.0)
            )
            behavioral_inclination = BehavioralInclination(
                social_withdrawal=cad_data.get('behavioral_inclination', {}).get('social_withdrawal', 0.0),
                avolition=cad_data.get('behavioral_inclination', {}).get('avolition', 0.0)
            )
            patient_agent.cad_state = CognitiveAffectiveState(
                affective_tone=cad_data.get('affective_tone', 0.0),
                core_beliefs=core_beliefs,
                cognitive_processing=cognitive_processing,
                behavioral_inclination=behavioral_inclination
            )
        
        # 设置抑郁程度
        patient_agent.depression_level = mental_state.get('depression_level', 'MODERATE')
        
        return patient_agent
    
    async def start_therapy_session(self, max_turns: int = 15) -> Dict[str, Any]:
        """
        开始AI对AI治疗会话 - 增强版本
        
        Args:
            max_turns: 最大对话轮数
            
        Returns:
            会话总结和分析结果
        """
        # 使用增强的会话头部显示
        create_session_header("AI对AI自动治疗会话（增强版）", self.patient_agent.name)
        console.print(f"[bold cyan]🤖 最大对话轮数: {max_turns}[/bold cyan]")
        console.print(f"[bold cyan]👨‍⚕️ AI治疗师 vs 👤 患者 {self.patient_agent.name}[/bold cyan]")
        console.print(f"[bold cyan]👨‍🎓 专业督导: 每{self.supervision_interval}轮提供建议[/bold cyan]")
        console.print("=" * 60)
        
        # 显示初始状态
        console.print(f"[cyan]🎯 初始抑郁程度: {self.initial_depression_level}[/cyan]")
        console.print(f"[cyan]📊 当前CAD状态: 自我信念={self.patient_agent.cad_state.core_beliefs.self_belief:.1f}, 情感基调={self.patient_agent.cad_state.affective_tone:.1f}[/cyan]")
        console.print()
        
        for turn in range(1, max_turns + 1):
            self.current_turn = turn
            
            try:
                console.print(f"[bold blue]🔄 第 {turn} 轮对话开始[/bold blue]")
                
                # AI治疗师发言
                therapist_message = await self._generate_therapist_response()
                
                # 安全的字符串处理，避免substitute错误
                if therapist_message is None:
                    therapist_message = "很抱歉，我需要重新组织一下我的想法。你现在感觉怎么样？"
                
                # 确保therapist_message是字符串类型
                therapist_message = str(therapist_message)
                
                # 提取策略分析（如果有的话）
                strategy_analysis = self._extract_strategy_analysis(therapist_message)
                clean_therapist_message = self._clean_therapist_message(therapist_message)
                
                # 使用增强显示功能显示治疗师回应
                display_therapist_response_with_strategy(
                    clean_therapist_message, 
                    strategy_analysis,
                    turn
                )
                
                # 患者回应
                patient_response = await self._generate_patient_response(clean_therapist_message)
                
                # 确保patient_response是字符串类型
                if patient_response is None:
                    patient_response = "我...不太知道该说什么。"
                patient_response = str(patient_response)
                
                # 获取患者当前状态用于显示
                patient_state_data = self._get_patient_display_data()
                
                # 使用增强显示功能显示患者回应和状态
                display_patient_response(
                    patient_response,
                    patient_state_data,
                    turn
                )
                
                # 分析本轮对话效果
                console.print(f"[grey50]📋 分析第{turn}轮对话效果...[/grey50]")
                analysis = await self._analyze_dialogue_turn(therapist_message, patient_response)
                
                # 记录本轮对话的效果分数
                effectiveness_score = analysis.get('overall_effectiveness', 5.0)
                self.session_effectiveness_scores.append(effectiveness_score)
                
                # 更新治疗联盟分数
                alliance_change = (effectiveness_score - 5.0) * 0.1  # 基于效果调整联盟分数
                self.therapeutic_alliance_score = max(0, min(10, self.therapeutic_alliance_score + alliance_change))
                
                # 记录对话轮次
                dialogue_turn = DialogueTurn(
                    turn_number=turn,
                    timestamp=datetime.now().isoformat(),
                    therapist_message=therapist_message,
                    patient_response=patient_response,
                    therapy_analysis=analysis,
                    patient_state_change=self._get_patient_state_snapshot()
                )
                self.dialogue_history.append(dialogue_turn)
                
                # 每隔几轮评估治疗进展和提供督导
                if turn % self.evaluation_interval == 0:
                    console.print(f"[grey50]📋 第{turn}轮：评估治疗进展...[/grey50]")
                    
                    try:
                        # 评估进展
                        progress = await self._evaluate_therapy_progress()
                        self.progress_history.append(progress)
                        
                        # 显示进展
                        self._display_therapy_progress(progress, turn)
                        
                        # 提供督导建议
                        if turn % self.supervision_interval == 0:
                            console.print(f"[grey50]👨‍🎓 专业督导分析中...[/grey50]")
                            try:
                                supervision = await self._get_therapist_supervision(therapist_message, patient_response)
                                
                                supervision_panel = Panel(
                                    supervision,
                                    title=f"💡 专业督导建议 (第{turn}轮)",
                                    border_style="green",
                                    expand=False
                                )
                                console.print(supervision_panel)
                            except Exception as supervision_error:
                                console.print(f"[yellow]⚠️ 督导功能暂时不可用: {str(supervision_error)}[/yellow]")
                                # 提供默认督导建议
                                default_supervision = "督导建议：继续当前治疗方向，关注患者情感反应和安全状态。"
                                supervision_panel = Panel(
                                    default_supervision,
                                    title=f"💡 基础督导建议 (第{turn}轮)",
                                    border_style="yellow",
                                    expand=False
                                )
                                console.print(supervision_panel)
                        
                        # 显示恢复进展
                        self._display_recovery_progress()
                        
                    except Exception as eval_error:
                        console.print(f"[yellow]⚠️ 进展评估出错: {str(eval_error)}[/yellow]")
                        # 继续会话，不中断治疗
                
                # 短暂延迟，模拟真实对话节奏
                await asyncio.sleep(0.5)
                console.print()  # 添加空行分隔
                
            except Exception as e:
                error_msg = str(e)
                console.print(f"[red]❌ 第 {turn} 轮对话出错: {error_msg}[/red]")
                
                # 详细错误信息用于调试
                if hasattr(e, '__traceback__'):
                    import traceback
                    console.print(f"[dim red]调试信息: {traceback.format_exc()}[/dim red]")
                
                # 特殊处理substitute错误
                if "substitute" in error_msg.lower():
                    console.print(f"[yellow]🔧 检测到模板错误，正在尝试修复...[/yellow]")
                    # 创建一个简单的备用对话
                    backup_therapist_msg = f"我想更好地理解你现在的感受。能告诉我你最近在想什么吗？"
                    backup_patient_response = f"嗯...我觉得有点累。"
                    
                    # 记录备用对话
                    dialogue_turn = DialogueTurn(
                        turn_number=turn,
                        timestamp=datetime.now().isoformat(),
                        therapist_message=backup_therapist_msg,
                        patient_response=backup_patient_response,
                        therapy_analysis=self._get_default_analysis_result("备用对话，由于系统错误"),
                        patient_state_change=self._get_patient_state_snapshot()
                    )
                    self.dialogue_history.append(dialogue_turn)
                    console.print(f"[green]✅ 已使用备用对话继续会话[/green]")
                    continue
                else:
                    console.print(f"[yellow]⚠️ 跳过当前轮次，继续治疗...[/yellow]")
                    continue
        
        # 生成会话总结
        session_summary = await self._generate_session_summary()
        
        # 保存会话记录
        self._save_session_log(session_summary)
        
        # 显示最终结果
        console.print("\n" + "=" * 60)
        console.print("🏁 AI对AI治疗会话结束")
        console.print(f"📁 会话记录已保存: logs/{self.session_id}_ai_therapy.json")
        
        # 显示最终进展
        self._display_recovery_progress()
        
        return session_summary
    
    async def _generate_therapist_response(self) -> str:
        """生成AI治疗师的回应"""
        # 准备患者档案
        patient_profile = {
            'name': self.patient_agent.name,
            'age': getattr(self.patient_agent, 'age', 17),
            'current_depression_level': self.patient_agent.depression_level,
            'cad_state': {
                'self_belief': self.patient_agent.cad_state.core_beliefs.self_belief,
                'world_belief': self.patient_agent.cad_state.core_beliefs.world_belief,
                'future_belief': self.patient_agent.cad_state.core_beliefs.future_belief,
                'rumination': self.patient_agent.cad_state.cognitive_processing.rumination,
                'distortions': self.patient_agent.cad_state.cognitive_processing.distortions,
                'social_withdrawal': self.patient_agent.cad_state.behavioral_inclination.social_withdrawal,
                'avolition': self.patient_agent.cad_state.behavioral_inclination.avolition,
                'affective_tone': self.patient_agent.cad_state.affective_tone
            },
            'recent_events': self._get_recent_patient_events()
        }
        
        # 准备对话历史
        recent_dialogue = self._get_recent_dialogue_context()
        
        # 生成治疗师回应
        return await self.therapist_agent.generate_therapeutic_guidance(
            patient_profile, recent_dialogue
        )
    
    async def _generate_patient_response(self, therapist_message: str) -> str:
        """生成患者的回应"""
        # 构建情境描述
        situation = f"心理咨询师对你说: '{therapist_message}'"
        
        # 添加治疗环境的背景
        context = {
            'environment': 'therapy_session',
            'session_turn': self.current_turn,
            'therapist_message': therapist_message
        }
        
        # 生成患者回应
        response = await self.patient_agent.respond_to_situation(situation, context)
        
        # 根据治疗对话动态更新患者状态 - 使用配置参数
        self._update_patient_state_from_therapy(therapist_message, response)
        
        return response
    
    async def _analyze_dialogue_turn(self, therapist_msg: str, patient_response: str) -> Dict[str, Any]:
        """分析单轮对话的治疗效果"""
        analysis_prompt = f"""
        请分析以下心理治疗对话轮次的效果:

        治疗师: {therapist_msg}
        患者: {patient_response}

        请从以下维度评估(0-10分):
        1. 治疗技巧运用效果
        2. 患者开放程度
        3. 情感连接质量
        4. 认知洞察深度

        请严格按照以下JSON格式返回分析结果，确保JSON格式完整且有效:
        {{
            "technique_effectiveness": 6.5,
            "patient_openness": 7.0,
            "emotional_connection": 6.0,
            "cognitive_insight": 5.5,
            "overall_effectiveness": 6.25,
            "analysis_notes": "治疗师使用了恰当的共情技巧，患者表现出较好的开放性。"
        }}
        
        重要要求：
        1. 只返回JSON格式，不要包含任何其他文本、解释或markdown标记
        2. 所有分数必须是0-10之间的数字（可以是小数）
        3. analysis_notes必须是简洁的中文描述（不超过50字）
        4. 确保JSON结构完整，所有字段都必须存在
        5. 请一次性输出完整的JSON，不要分段或截断
        """
        
        try:
            # 尝试获取AI响应，设置较长的超时
            response = await self.ai_client.generate_response(analysis_prompt)
            
            if not response or len(response.strip()) < 10:
                raise ValueError("AI响应为空或过短")
            
            # 增强的JSON提取和修复逻辑
            cleaned_response = self._extract_and_fix_json(response.strip())
            
            # 尝试解析JSON
            result = json.loads(cleaned_response)
            
            # 验证和修复结果格式
            result = self._validate_and_fix_analysis_result(result)
            
            return result
            
        except json.JSONDecodeError as e:
            # JSON解析失败，尝试智能修复
            console.print(f"[yellow]⚠️ JSON解析失败，尝试修复: {str(e)}[/yellow]")
            fixed_response = self._attempt_json_repair(response if 'response' in locals() else "")
            
            if fixed_response:
                try:
                    result = json.loads(fixed_response)
                    result = self._validate_and_fix_analysis_result(result)
                    console.print(f"[green]✅ JSON修复成功[/green]")
                    return result
                except:
                    pass
            
            # 修复失败，使用默认值
            return self._get_default_analysis_result("JSON解析失败，已自动修复为默认评分")
            
        except Exception as e:
            # 其他错误
            console.print(f"[yellow]⚠️ 对话分析出错: {str(e)}[/yellow]")
            error_msg = f"分析系统异常({type(e).__name__})，使用默认评分"
            return self._get_default_analysis_result(error_msg)
    
    def _extract_and_fix_json(self, response: str) -> str:
        """从AI响应中提取并修复JSON"""
        # 移除常见的前后缀
        response = response.strip()
        
        # 方法1: 处理markdown代码块
        if "```json" in response:
            start_idx = response.find("```json") + 7
            end_idx = response.find("```", start_idx)
            if end_idx > start_idx:
                response = response[start_idx:end_idx].strip()
        elif "```" in response:
            parts = response.split("```")
            for part in parts[1::2]:  # 取奇数索引的部分（代码块内容）
                part = part.strip()
                if part.startswith('{') and (part.endswith('}') or '}' in part):
                    response = part
                    break
        
        # 方法2: 直接提取JSON对象
        start_bracket = response.find('{')
        if start_bracket != -1:
            # 寻找匹配的结束括号
            bracket_count = 0
            end_bracket = -1
            
            for i in range(start_bracket, len(response)):
                if response[i] == '{':
                    bracket_count += 1
                elif response[i] == '}':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_bracket = i
                        break
            
            if end_bracket > start_bracket:
                response = response[start_bracket:end_bracket+1]
        
        # 方法3: 清理常见问题
        response = response.replace('\n', ' ').replace('\t', ' ')
        response = ' '.join(response.split())  # 移除多余空格
        
        # 修复可能的JSON格式问题
        if not response.endswith('}') and '}' in response:
            response = response[:response.rfind('}')+1]
        
        return response
    
    def _attempt_json_repair(self, response: str) -> Optional[str]:
        """尝试修复损坏的JSON"""
        if not response:
            return None
        
        try:
            # 提取看起来像JSON的部分
            cleaned = self._extract_and_fix_json(response)
            
            # 如果JSON不完整，尝试补全
            if cleaned.startswith('{') and not cleaned.endswith('}'):
                # 找到最后一个完整的字段
                fields = []
                current_field = ""
                in_string = False
                escape_next = False
                
                for char in cleaned[1:]:  # 跳过开始的{
                    if escape_next:
                        current_field += char
                        escape_next = False
                        continue
                    
                    if char == '\\':
                        escape_next = True
                        current_field += char
                        continue
                    
                    if char == '"' and not escape_next:
                        in_string = not in_string
                    
                    if char == ',' and not in_string:
                        if current_field.strip():
                            fields.append(current_field.strip())
                        current_field = ""
                        continue
                    
                    current_field += char
                
                # 构建修复的JSON
                if fields:
                    repaired = "{" + ",".join(fields) + "}"
                    return repaired
            
            return cleaned
            
        except Exception:
            return None
    
    def _validate_and_fix_analysis_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """验证并修复分析结果"""
        required_fields = {
            "technique_effectiveness": 5.0,
            "patient_openness": 5.0,
            "emotional_connection": 5.0,
            "cognitive_insight": 5.0,
            "overall_effectiveness": 5.0,
            "analysis_notes": "分析完成"
        }
        
        # 确保所有必需字段存在
        for field, default_value in required_fields.items():
            if field not in result:
                result[field] = default_value
            elif field != "analysis_notes":
                # 验证并修复数值字段
                try:
                    value = float(result[field])
                    if value < 0 or value > 10 or not isinstance(value, (int, float)):
                        result[field] = default_value
                    else:
                        result[field] = round(value, 1)  # 保留一位小数
                except (ValueError, TypeError):
                    result[field] = default_value
            else:
                # 验证analysis_notes字段
                if not isinstance(result[field], str) or len(result[field]) > 100:
                    result[field] = "分析完成"
        
        # 计算overall_effectiveness（如果不合理的话）
        numeric_fields = ["technique_effectiveness", "patient_openness", 
                         "emotional_connection", "cognitive_insight"]
        avg_score = sum(result[field] for field in numeric_fields) / len(numeric_fields)
        
        if abs(result["overall_effectiveness"] - avg_score) > 2:  # 如果偏差太大
            result["overall_effectiveness"] = round(avg_score, 1)
        
        return result
    
    def _get_default_analysis_result(self, error_message: str = "使用默认评分") -> Dict[str, Any]:
        """获取默认的分析结果"""
        return {
            "technique_effectiveness": 5.0,
            "patient_openness": 5.0,
            "emotional_connection": 5.0,
            "cognitive_insight": 5.0,
            "overall_effectiveness": 5.0,
            "analysis_notes": error_message[:50]  # 限制长度
        }
    
    async def _evaluate_therapy_progress(self) -> TherapyProgress:
        """评估整体治疗进展"""
        if len(self.dialogue_history) < self.evaluation_interval:
            return TherapyProgress(
                turn_number=self.current_turn,
                therapy_effectiveness=5.0,
                therapeutic_alliance=5.0,
                patient_emotional_state=5.0,
                breakthrough_moment=False,
                risk_indicators=[]
            )
        
        # 分析最近几轮的对话
        recent_turns = self.dialogue_history[-self.evaluation_interval:]
        
        # 计算平均治疗效果
        avg_effectiveness = sum(
            turn.therapy_analysis.get('overall_effectiveness', 5.0)
            for turn in recent_turns
        ) / len(recent_turns)
        
        # 评估治疗联盟强度
        avg_openness = sum(
            turn.therapy_analysis.get('patient_openness', 5.0)
            for turn in recent_turns
        ) / len(recent_turns)
        
        avg_connection = sum(
            turn.therapy_analysis.get('emotional_connection', 5.0)
            for turn in recent_turns  
        ) / len(recent_turns)
        
        therapeutic_alliance = (avg_openness + avg_connection) / 2
        
        # 评估患者情绪状态变化
        emotional_state = self._calculate_emotional_state_score()
        
        # 检测突破性时刻
        breakthrough = (
            avg_effectiveness >= 8.0 and 
            therapeutic_alliance >= 7.0 and
            len(recent_turns) >= 3
        )
        
        # 识别风险指标
        risk_indicators = []
        if avg_effectiveness < 3.0:
            risk_indicators.append("治疗效果低下")
        if therapeutic_alliance < 3.0:
            risk_indicators.append("治疗联盟脆弱") 
        if emotional_state < 3.0:
            risk_indicators.append("情绪状态恶化")
        
        return TherapyProgress(
            turn_number=self.current_turn,
            therapy_effectiveness=avg_effectiveness,
            therapeutic_alliance=therapeutic_alliance,
            patient_emotional_state=emotional_state,
            breakthrough_moment=breakthrough,
            risk_indicators=risk_indicators
        )
    
    def _calculate_emotional_state_score(self) -> float:
        """计算患者当前情绪状态得分"""
        cad = self.patient_agent.cad_state
        
        # 基于CAD-MD状态计算情绪得分
        emotional_score = (
            cad.core_beliefs.self_belief * 0.3 +
            cad.core_beliefs.world_belief * 0.2 +  
            cad.affective_tone * 0.4 +
            cad.cognitive_processing.rumination * 0.1
        )
        
        return min(10.0, max(0.0, emotional_score))
    
    def _update_patient_state_from_therapy(self, therapist_msg: str, patient_response: str):
        """根据治疗对话动态更新患者状态 - 基于配置参数"""
        try:
            # 获取配置参数
            config = self.therapy_config
            cad_config = config["cad_state_changes"]
            therapy_config = config["therapy_effectiveness"]
            bounds = config["state_bounds"]
            
            # 分析治疗师技巧和患者回应质量
            positive_indicators = ['感谢', '理解', '好的', '是的', '明白', '感受到', '尝试', '愿意', '想要']
            negative_indicators = ['不知道', '算了', '没用', '不想说', '不理解', '烦', '累', '无所谓']
            
            # 治疗师技巧质量评估
            therapist_techniques = ['共情', '反映', '澄清', '总结', '支持', '鼓励', '开放式提问']
            technique_score = 0
            for technique in therapist_techniques:
                if any(word in therapist_msg for word in ['感受', '理解', '听到', '意思是', '总结', '你能']):
                    technique_score += 1
            technique_quality = min(technique_score / len(therapist_techniques), 1.0)
            
            # 患者积极性评估
            positive_count = sum(1 for indicator in positive_indicators if indicator in patient_response)
            negative_count = sum(1 for indicator in negative_indicators if indicator in patient_response)
            
            patient_openness = max(0, min(1.0, (positive_count - negative_count * 0.5) / 3))
            
            # 计算综合改善因子
            base_factor = therapy_config["base_improvement_factor"]
            technique_weight = therapy_config["technique_weight"] 
            openness_weight = therapy_config["openness_weight"]
            
            improvement_factor = base_factor * (
                technique_quality * technique_weight + 
                patient_openness * openness_weight +
                0.3  # 基础治疗环境加成
            )
            
            # 应用修正因子和同步化因子
            improvement_factor *= cad_config["correction_factor"]
            sync_factor = cad_config.get("synchronization_factor", 0.1)
            
            # 更新CAD状态 - 使用配置的变化率和同步机制
            if hasattr(self.patient_agent, 'cad_state'):
                cad_state = self.patient_agent.cad_state
                
                # 核心信念系统变化
                core_config = cad_config["core_beliefs"]
                stability = core_config["stability_factor"]
                
                # 自我信念 - 正向治疗增强自我价值感
                old_self_belief = cad_state.core_beliefs.self_belief
                change = improvement_factor * core_config["self_belief_change_rate"]
                new_self_belief = old_self_belief * stability + change
                new_self_belief = max(bounds["min_cad_value"], min(bounds["max_cad_value"], new_self_belief))
                cad_state.core_beliefs.self_belief = new_self_belief
                
                # 世界信念 - 治疗环境提供安全感
                old_world_belief = cad_state.core_beliefs.world_belief  
                change = improvement_factor * core_config["world_belief_change_rate"]
                new_world_belief = old_world_belief * stability + change
                new_world_belief = max(bounds["min_cad_value"], min(bounds["max_cad_value"], new_world_belief))
                cad_state.core_beliefs.world_belief = new_world_belief
                
                # 未来信念 - 治疗给予希望
                old_future_belief = cad_state.core_beliefs.future_belief
                change = improvement_factor * core_config["future_belief_change_rate"] 
                new_future_belief = old_future_belief * stability + change
                new_future_belief = max(bounds["min_cad_value"], min(bounds["max_cad_value"], new_future_belief))
                cad_state.core_beliefs.future_belief = new_future_belief
                
                # 认知处理改善 - 应用同步化
                cognitive_config = cad_config["cognitive_processing"]
                cognitive_stability = cognitive_config.get("stability_factor", 0.90)
                
                # 减少反刍思维
                rumination_reduction = improvement_factor * cognitive_config["rumination_reduction_rate"]
                old_rumination = cad_state.cognitive_processing.rumination
                new_rumination = old_rumination * cognitive_stability - rumination_reduction
                new_rumination = max(bounds["min_cad_value"], min(bounds["max_cad_value"], new_rumination))
                cad_state.cognitive_processing.rumination = new_rumination
                
                # 减少认知扭曲
                distortion_reduction = improvement_factor * cognitive_config["distortions_reduction_rate"]
                old_distortions = cad_state.cognitive_processing.distortions
                new_distortions = old_distortions * cognitive_stability - distortion_reduction
                new_distortions = max(bounds["min_cad_value"], min(bounds["max_cad_value"], new_distortions))
                cad_state.cognitive_processing.distortions = new_distortions
                
                # 行为模式改善 - 应用同步化
                behavioral_config = cad_config["behavioral_patterns"] 
                behavioral_stability = behavioral_config.get("stability_factor", 0.90)
                
                # 减少社交退缩
                social_improvement = improvement_factor * behavioral_config["social_withdrawal_change_rate"]
                old_withdrawal = cad_state.behavioral_inclination.social_withdrawal
                new_withdrawal = old_withdrawal * behavioral_stability - social_improvement
                new_withdrawal = max(bounds["min_cad_value"], min(bounds["max_cad_value"], new_withdrawal))
                cad_state.behavioral_inclination.social_withdrawal = new_withdrawal
                
                # 增加动机
                motivation_improvement = improvement_factor * behavioral_config["avolition_change_rate"]
                old_avolition = cad_state.behavioral_inclination.avolition
                new_avolition = old_avolition * behavioral_stability - motivation_improvement
                new_avolition = max(bounds["min_cad_value"], min(bounds["max_cad_value"], new_avolition))
                cad_state.behavioral_inclination.avolition = new_avolition
                
                # 情感基调改善
                affective_improvement = improvement_factor * cad_config["affective_tone_change_rate"]
                old_affective = cad_state.affective_tone
                new_affective = old_affective + affective_improvement
                new_affective = max(bounds["min_cad_value"], min(bounds["max_cad_value"], new_affective))
                cad_state.affective_tone = new_affective
                
                # 使用新的综合抑郁评分系统更新抑郁级别
                self._update_depression_level_comprehensive()
                
                # 记录状态变化
                self._record_state_change(improvement_factor, int(patient_openness * 10), int(technique_quality * 10))
                
        except Exception as e:
            console.print(f"[yellow]⚠️ 更新患者状态时出错: {e}[/yellow]")
    
    def _update_depression_level_comprehensive(self):
        """基于CAD状态综合更新抑郁级别"""
        try:
            if hasattr(self.patient_agent, 'cad_state'):
                cad_state = self.patient_agent.cad_state
                
                # 计算新的抑郁级别
                new_level = cad_state.get_depression_level_from_cad()
                old_level = self.patient_agent.psychological_state.depression_level
                
                # 更新抑郁级别
                self.patient_agent.psychological_state.depression_level = new_level
                
                # 如果级别发生变化，记录
                if new_level != old_level:
                    self._record_depression_level_change(old_level, new_level)
                    
        except Exception as e:
            console.print(f"[yellow]⚠️ 更新抑郁级别时出错: {e}[/yellow]")
    
    def _record_depression_level_change(self, old_level, new_level):
        """记录抑郁级别变化"""
        if not hasattr(self, 'depression_level_history'):
            self.depression_level_history = []
        
        self.depression_level_history.append({
            'turn': len(self.dialogue_history),
            'old_level': old_level.name,
            'new_level': new_level.name,
            'direction': 'improvement' if new_level.value < old_level.value else 'deterioration'
        })
        
        # 显示级别变化
        if new_level.value < old_level.value:
            console.print(f"[green]🎉 抑郁级别改善: {old_level.name} → {new_level.name}[/green]")
        elif new_level.value > old_level.value:
            console.print(f"[red]⚠️ 抑郁级别恶化: {old_level.name} → {new_level.name}[/red]")
    
    def _record_state_change(self, improvement_factor: float, response_score: int, technique_score: int):
        """记录状态变化信息"""
        if not hasattr(self, 'state_change_log'):
            self.state_change_log = []
        
        self.state_change_log.append({
            'turn': self.current_turn,
            'improvement_factor': improvement_factor,
            'response_score': response_score,
            'technique_score': technique_score,
            'timestamp': datetime.now().isoformat()
        })
    
    def _get_patient_state_snapshot(self) -> Dict[str, Any]:
        """获取患者当前状态快照"""
        return {
            'depression_level': self.patient_agent.depression_level,
            'cad_state': {
                'self_belief': self.patient_agent.cad_state.core_beliefs.self_belief,
                'world_belief': self.patient_agent.cad_state.core_beliefs.world_belief,
                'future_belief': self.patient_agent.cad_state.core_beliefs.future_belief,
                'rumination': self.patient_agent.cad_state.cognitive_processing.rumination,
                'distortions': self.patient_agent.cad_state.cognitive_processing.distortions,
                'social_withdrawal': self.patient_agent.cad_state.behavioral_inclination.social_withdrawal,
                'avolition': self.patient_agent.cad_state.behavioral_inclination.avolition,
                'affective_tone': self.patient_agent.cad_state.affective_tone
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_recent_patient_events(self) -> List[str]:
        """获取患者最近的重要事件"""
        # 从患者数据中提取关键事件
        events = []
        
        if 'daily_events' in self.patient_data:
            # 取最后几天的事件
            daily_events = self.patient_data['daily_events']
            if isinstance(daily_events, dict):
                # 取最近3天的事件
                recent_days = sorted(daily_events.keys())[-3:]
                for day in recent_days:
                    if day in daily_events:
                        day_events = daily_events[day]
                        if isinstance(day_events, list):
                            events.extend([event.get('description', str(event)) for event in day_events[-2:]])
        
        return events[:5]  # 最多5个事件
    
    def _get_recent_dialogue_context(self) -> List[Dict[str, str]]:
        """获取最近的对话上下文"""
        if not self.dialogue_history:
            return []
        
        recent_turns = self.dialogue_history[-self.max_conversation_history:]
        return [
            {
                'therapist': turn.therapist_message,
                'patient': turn.patient_response,
                'turn': turn.turn_number
            }
            for turn in recent_turns
        ]
    
    async def _generate_session_summary(self) -> Dict[str, Any]:
        """生成会话总结"""
        if not self.dialogue_history:
            return {'error': '没有对话记录'}
        
        # 计算整体统计
        total_turns = len(self.dialogue_history)
        avg_effectiveness = sum(
            turn.therapy_analysis.get('overall_effectiveness', 5.0)
            for turn in self.dialogue_history
        ) / total_turns if total_turns > 0 else 5.0
        
        # 最终进展评估
        final_progress = await self._evaluate_therapy_progress() if self.dialogue_history else None
        
        return {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'patient_name': self.patient_agent.name,
            'total_turns': total_turns,
            'average_effectiveness': avg_effectiveness,
            'final_progress': final_progress.__dict__ if final_progress else None,
            'dialogue_history': [turn.__dict__ for turn in self.dialogue_history],
            'progress_evaluations': [p.__dict__ for p in self.progress_history],
            'patient_state_evolution': {
                'initial_state': self.dialogue_history[0].patient_state_change if self.dialogue_history else {},
                'final_state': self.dialogue_history[-1].patient_state_change if self.dialogue_history else {}
            }
        }
    
    def _save_session_log(self, session_summary: Dict[str, Any]):
        """保存会话记录到日志文件"""
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        log_file = logs_dir / f"{self.session_id}_ai_therapy.json"
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(session_summary, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存会话记录失败: {e}")

    def _initialize_recovery_tracking(self):
        """初始化恢复追踪机制 - 包含CAD状态"""
        if self.patient_data:
            # 获取初始抑郁程度
            if isinstance(self.patient_data.get('depression_level'), str):
                self.initial_depression_level = self.patient_data['depression_level']
            elif hasattr(self.patient_agent, 'depression_level'):
                if hasattr(self.patient_agent.depression_level, 'name'):
                    self.initial_depression_level = self.patient_agent.depression_level.name
                else:
                    self.initial_depression_level = str(self.patient_agent.depression_level)
            else:
                self.initial_depression_level = 'MODERATE'
            
            # 保存初始抑郁级别的枚举值
            if hasattr(self.patient_agent, 'psychological_state'):
                self.initial_depression_level_enum = self.patient_agent.psychological_state.depression_level
            else:
                from models.psychology_models import DepressionLevel
                self.initial_depression_level_enum = DepressionLevel.MODERATE
            
            # 保存初始CAD状态（深拷贝）
            if hasattr(self.patient_agent, 'psychological_state'):
                import copy
                self.initial_cad_state = copy.deepcopy(self.patient_agent.psychological_state.cad_state)
            
            self.current_depression_level = self.initial_depression_level
            self.recovery_progress = [{
                "timestamp": datetime.now().isoformat(),
                "depression_level": self.initial_depression_level,
                "event": "开始AI-AI治疗",
                "therapeutic_alliance_score": 0.0
            }]
            self.therapeutic_alliance_score = 0.0
            self.session_effectiveness_scores = []
            
            console.print(f"[cyan]🎯 恢复追踪已初始化。初始抑郁程度: {self.initial_depression_level}[/cyan]")

    def _try_update_depression_level(self, improvement: bool):
        """尝试更新抑郁等级"""
        try:
            # 获取当前抑郁程度的数值
            current_level_value = DEPRESSION_LEVELS.get(self.current_depression_level, 2)
            
            if improvement and current_level_value > 0:
                # 改善：降低一级
                new_level_value = current_level_value - 1
                old_level = self.current_depression_level
                self.current_depression_level = DEPRESSION_LEVEL_NAMES.get(new_level_value, "MODERATE")
                
                # 记录变化
                self.recovery_progress.append({
                    "timestamp": datetime.now().isoformat(),
                    "depression_level": self.current_depression_level,
                    "event": f"治疗有效：从 {old_level} 改善至 {self.current_depression_level}",
                    "therapeutic_alliance_score": self.therapeutic_alliance_score,
                    "turn": self.current_turn
                })
                
                console.print(f"[green]✨ 治疗取得进展！抑郁程度从 {old_level} 改善至 {self.current_depression_level}[/green]")
                
            elif not improvement and current_level_value < 4:
                # 恶化：提高一级
                new_level_value = current_level_value + 1
                old_level = self.current_depression_level
                self.current_depression_level = DEPRESSION_LEVEL_NAMES.get(new_level_value, "MODERATE")
                
                # 记录变化
                self.recovery_progress.append({
                    "timestamp": datetime.now().isoformat(),
                    "depression_level": self.current_depression_level,
                    "event": f"需要关注：从 {old_level} 变为 {self.current_depression_level}",
                    "therapeutic_alliance_score": self.therapeutic_alliance_score,
                    "turn": self.current_turn
                })
                
                console.print(f"[yellow]⚠️ 需要调整治疗策略：抑郁程度从 {old_level} 变为 {self.current_depression_level}[/yellow]")
                
        except Exception as e:
            console.print(f"[yellow]⚠️ 更新抑郁等级时出错: {e}[/yellow]")

    async def _get_therapist_supervision(self, therapist_msg: str, patient_response: str) -> str:
        """获取专业督导建议 - 修复substitute错误"""
        try:
            # 安全处理消息内容，避免substitute错误
            safe_therapist_msg = str(therapist_msg).replace('$', '\\$') if therapist_msg else "无消息"
            safe_patient_response = str(patient_response).replace('$', '\\$') if patient_response else "无回应"
            
            # 构建督导prompt - 使用安全的字符串拼接
            recent_dialogue = self._get_recent_dialogue_context()
            dialogue_text = ""
            
            # 安全处理最近对话
            for dialogue in recent_dialogue[-3:]:  # 最近3轮
                therapist_part = str(dialogue.get('therapist', '')).replace('$', '\\$')
                patient_part = str(dialogue.get('patient', '')).replace('$', '\\$')
                dialogue_text += f"治疗师: {therapist_part}\n"
                dialogue_text += f"患者: {patient_part}\n\n"
            
            # 安全获取CAD状态
            try:
                self_belief = self.patient_agent.cad_state.core_beliefs.self_belief
                world_belief = self.patient_agent.cad_state.core_beliefs.world_belief
                future_belief = self.patient_agent.cad_state.core_beliefs.future_belief
                affective_tone = self.patient_agent.cad_state.affective_tone
                rumination = self.patient_agent.cad_state.cognitive_processing.rumination
                distortions = self.patient_agent.cad_state.cognitive_processing.distortions
            except Exception:
                # 使用默认值
                self_belief = world_belief = future_belief = affective_tone = 0.0
                rumination = distortions = 0.0
            
            # 使用f字符串而不是模板替换
            supervision_prompt = f"""作为经验丰富的心理治疗督导师，请分析以下AI-AI治疗对话，并提供专业督导建议。

【患者背景】
- 姓名: {self.patient_agent.name}
- 当前抑郁程度: {self.current_depression_level}
- 治疗进行轮次: {self.current_turn}
- 治疗联盟评分: {self.therapeutic_alliance_score:.1f}/10

【最近对话内容】
{dialogue_text}

【当前CAD状态】
- 自我信念: {self_belief:.1f}
- 世界信念: {world_belief:.1f}
- 未来信念: {future_belief:.1f}
- 情感基调: {affective_tone:.1f}
- 反刍思维: {rumination:.1f}
- 认知扭曲: {distortions:.1f}

请从以下角度提供督导建议：
1. 治疗技巧评估：AI治疗师的技巧运用是否恰当？
2. 患者反应分析：患者的参与度和开放性如何？
3. 治疗进展评价：当前治疗方向是否有效？
4. 风险评估：是否存在需要关注的风险信号？
5. 下一步建议：应该调整哪些治疗策略？

请提供简洁但专业的督导意见（300字以内）："""
            
            # 使用督导Agent生成建议
            supervision_response = await self.supervisor_agent.generate_supervision(
                supervision_prompt, {
                    'patient_profile': {
                        'name': self.patient_agent.name,
                        'depression_level': self.current_depression_level,
                        'current_turn': self.current_turn
                    },
                    'recent_dialogue': recent_dialogue
                }
            )
            
            # 确保返回安全的字符串
            if supervision_response and isinstance(supervision_response, str):
                return supervision_response.strip()
            else:
                return "督导建议：当前治疗师技巧运用得当，患者参与度良好。建议继续当前治疗方向，关注患者情绪变化。"
            
        except Exception as e:
            error_msg = str(e)
            console.print(f"[yellow]⚠️ 获取督导建议时出错: {error_msg}[/yellow]")
            
            # 返回基于错误类型的默认督导建议
            if "substitute" in error_msg.lower():
                return "督导建议：检测到技术问题，建议治疗师保持耐心，继续建立治疗关系。重点关注患者的即时情感反应。"
            else:
                return f"督导建议：系统暂时不可用，建议继续当前治疗方向，密切关注患者安全。技术问题：{error_msg}"

    def _display_recovery_progress(self):
        """显示恢复进展 - 基于CAD多维度评估"""
        if not self.recovery_progress:
            return
        
        # 使用新的10级抑郁分级系统
        initial_value = DEPRESSION_LEVELS.get(self.initial_depression_level, 6)  # 更新默认值适应10级
        current_value = DEPRESSION_LEVELS.get(self.current_depression_level, 6)
        
        # 计算基础抑郁级别改善
        depression_improvement = initial_value - current_value
        depression_improvement_pct = (depression_improvement / 9) * 100 if depression_improvement > 0 else 0
        
        # 计算CAD综合改善程度
        cad_improvement_pct = 0
        if hasattr(self.patient_agent, 'psychological_state') and hasattr(self, 'initial_cad_state'):
            try:
                cad_improvement_pct = self.patient_agent.psychological_state.calculate_improvement_percentage(
                    self.initial_cad_state, 
                    self.initial_depression_level_enum
                )
            except Exception as e:
                console.print(f"[yellow]CAD改善计算出错: {e}[/yellow]")
        
        # 综合改善程度（60%基于CAD，40%基于抑郁级别）
        improvement_percentage = cad_improvement_pct * 0.6 + depression_improvement_pct * 0.4
        
        progress_panel = Panel(
            f"""[bold cyan]📊 AI-AI治疗进展报告[/bold cyan]

💊 初始状态: {self.initial_depression_level} (级别 {initial_value}/9)
💊 当前状态: {self.current_depression_level} (级别 {current_value}/9)
📈 综合改善: {improvement_percentage:.1f}%
   └─ 抑郁级别改善: {depression_improvement_pct:.1f}%
   └─ CAD状态改善: {cad_improvement_pct:.1f}%
🤝 治疗联盟: {self.therapeutic_alliance_score:.1f}/10
🔄 对话轮次: {self.current_turn}
📝 进展记录: {len(self.recovery_progress)}条

{f'[green]✅ 治疗效果显著！[/green]' if improvement_percentage > 20 else f'[yellow]⚡ 持续治疗中...[/yellow]' if improvement_percentage >= 5 else f'[red]⚠️ 需要调整策略[/red]'}""",
            title="🎯 恢复追踪（CAD-MD多维度评估）",
            border_style="green" if improvement_percentage > 20 else "yellow" if improvement_percentage >= 5 else "red"
        )
        
        console.print(progress_panel)


# 便捷函数
async def run_ai_to_ai_therapy(ai_client, patient_log_path: str, max_turns: int = 15) -> Dict[str, Any]:
    """
    便捷函数：运行AI对AI治疗会话
    
    Args:
        ai_client: AI客户端
        patient_log_path: 患者数据路径  
        max_turns: 最大对话轮数
        
    Returns:
        会话总结
    """
    manager = AIToAITherapyManager(ai_client, patient_log_path)
    return await manager.start_therapy_session(max_turns) 