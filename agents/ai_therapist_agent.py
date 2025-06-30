#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI心理咨询师Agent
实现自动化的心理引导对话功能，基于专业心理治疗技术
"""

from typing import Dict, List, Any, Optional, Union
from agents.base_agent import BaseAgent
from models.psychology_models import EmotionState, DepressionLevel, PsychologicalState
from models.cad_state_mapper import CADStateMapper
import asyncio

class AITherapistAgent(BaseAgent):
    """AI心理咨询师Agent"""
    
    def __init__(self, name: str, ai_client: Union['GeminiClient', 'DeepSeekClient']):
        """
        初始化AI心理咨询师
        
        Args:
            name: 咨询师名字
            ai_client: AI客户端
        """
        # 为BaseAgent准备personality参数
        personality = {
            "warmth": 9,
            "empathy": 10,
            "patience": 9,
            "professionalism": 10,
            "therapeutic_approach": "综合疗法"
        }
        
        # 调用BaseAgent的初始化方法
        super().__init__(name, age=45, personality=personality, ai_client=ai_client)
        
        # 咨询师特有属性
        self.therapeutic_approach = "综合疗法"  # 认知行为疗法+人本主义
        self.session_count = 0
        self.therapy_goals = []
        self.current_strategy = "建立关系"
        
    def get_role_description(self) -> str:
        """获取角色描述"""
        return f"""
        我是{self.name}，一名专业的心理咨询师。我具备以下专业能力：
        
        【专业背景】
        - 心理学博士，从业15年
        - 擅长认知行为疗法(CBT)、人本主义疗法、正念疗法
        - 专业领域：青少年抑郁症、焦虑障碍、自我认知重建
        
        【治疗风格】
        - 温暖、耐心、无条件积极关注
        - 善于倾听，不批判，创造安全空间
        - 使用苏格拉底式提问引导患者自我探索
        - 基于个体差异制定个性化治疗方案
        
        【核心技能】
        - 情感共情与反馈
        - 认知重构技术
        - 行为激活疗法
        - 正念与放松训练
        - 危机干预与自杀评估
        """
    
    def get_current_concerns(self) -> List[str]:
        """获取当前关注的问题"""
        concerns = [
            "建立稳固的治疗联盟",
            "评估患者的抑郁程度和风险",
            "识别负性认知模式",
            "制定个性化治疗计划",
            "监测治疗进展"
        ]
        
        # 根据当前策略调整关注点
        if self.current_strategy == "建立关系":
            concerns.extend(["创造安全的治疗环境", "了解患者背景和需求"])
        elif self.current_strategy == "危机干预与稳定化":
            concerns.extend(["评估自杀风险", "情绪稳定化", "安全计划制定"])
        elif self.current_strategy == "认知重构技术":
            concerns.extend(["识别认知扭曲", "挑战负性思维", "建立现实检验能力"])
        elif self.current_strategy == "行为激活疗法":
            concerns.extend(["增加愉快活动", "改善社交功能", "重建积极行为模式"])
        
        return concerns
    
    async def generate_therapeutic_guidance(self, 
                                          patient_profile: Dict[str, Any], 
                                          dialogue_history: List[Dict[str, str]],
                                          session_goals: Optional[List[str]] = None) -> str:
        """
        生成治疗引导对话
        
        Args:
            patient_profile: 患者档案信息
            dialogue_history: 对话历史
            session_goals: 本次会话目标
        
        Returns:
            AI咨询师的引导性发言
        """
        self.session_count += 1
        
        # 分析患者当前状态
        patient_analysis = self._analyze_patient_state(patient_profile)
        
        # 确定治疗策略
        current_strategy = self._determine_therapy_strategy(patient_profile, dialogue_history)
        
        # 生成治疗prompt
        prompt = await self._build_therapy_prompt(
            patient_profile=patient_profile,
            patient_analysis=patient_analysis,
            dialogue_history=dialogue_history,
            strategy=current_strategy,
            session_goals=session_goals
        )
        
        # 获取AI回应
        therapist_response = await self.ai_client.generate_response(prompt)
        
        # 更新治疗进展
        self._update_therapy_progress(patient_profile, therapist_response)
        
        return therapist_response
    
    def _analyze_patient_state(self, patient_profile: Dict[str, Any]) -> str:
        """分析患者当前心理状态"""
        analysis_parts = []
        
        # 基本信息分析
        name = patient_profile.get('name', '患者')
        age = patient_profile.get('age', '未知')
        depression_level = patient_profile.get('depression_level', 'MODERATE')
        
        analysis_parts.append(f"患者{name}（{age}岁），当前抑郁程度：{depression_level}")
        
        # CAD状态分析（如果可用）
        if 'cad_analysis' in patient_profile:
            cad_analysis = patient_profile['cad_analysis']
            analysis_parts.append(f"认知状态分析：{cad_analysis[:200]}...")
        
        # 近期事件分析
        if 'recent_events' in patient_profile:
            events = patient_profile['recent_events']
            negative_events = [e for e in events if 'negative' in str(e).lower() or 'sad' in str(e).lower()]
            if negative_events:
                analysis_parts.append(f"近期负面事件影响明显，共{len(negative_events)}次")
        
        # 关系状态分析
        if 'relationships' in patient_profile:
            relationships = patient_profile['relationships']
            analysis_parts.append(f"当前人际关系状况需要关注")
        
        return "；".join(analysis_parts)
    
    def _determine_therapy_strategy(self, 
                                  patient_profile: Dict[str, Any], 
                                  dialogue_history: List[Dict[str, str]]) -> str:
        """确定当前治疗策略"""
        
        history_length = len(dialogue_history)
        depression_level = patient_profile.get('depression_level', 'MODERATE')
        
        # 会话初期：建立治疗关系
        if history_length < 3:
            return "建立治疗关系"
        
        # 会话中期：根据问题类型选择策略
        elif history_length < 10:
            if depression_level in ['SEVERE', 'CRITICAL']:
                return "危机干预与稳定化"
            else:
                return "认知评估与探索"
        
        # 会话后期：深度干预
        else:
            if 'rumination' in str(patient_profile).lower():
                return "认知重构技术"
            elif 'withdrawal' in str(patient_profile).lower():
                return "行为激活疗法"
            else:
                return "综合心理干预"
    
    async def _build_therapy_prompt(self,
                                  patient_profile: Dict[str, Any],
                                  patient_analysis: str,
                                  dialogue_history: List[Dict[str, str]],
                                  strategy: str,
                                  session_goals: Optional[List[str]] = None) -> str:
        """构建治疗prompt"""
        
        # 格式化对话历史
        history_text = ""
        if dialogue_history:
            for i, exchange in enumerate(dialogue_history[-5:]):  # 只取最近5轮
                therapist_text = exchange.get('therapist', '')
                patient_text = exchange.get('patient', '')
                history_text += f"\n第{i+1}轮："
                if therapist_text:
                    history_text += f"\n咨询师: {therapist_text}"
                if patient_text:
                    history_text += f"\n患者: {patient_text}"
        
        # 构建session目标
        goals_text = ""
        if session_goals:
            goals_text = f"\n【本次会话目标】\n" + "\n".join([f"- {goal}" for goal in session_goals])
        
        prompt = f"""
你是一名经验丰富的专业心理咨询师，正在与一位青少年抑郁症患者进行心理治疗。

【患者状态分析】
{patient_analysis}

【治疗策略】
当前采用：{strategy}

【策略指导】
{self._get_strategy_guidelines(strategy)}

【对话历史】
{history_text if history_text else "这是治疗的开始"}

{goals_text}

【你的任务】
1. 基于患者的深层心理状态，生成下一轮的治疗引导语
2. 体现专业的心理治疗技巧：共情、反映、开放式提问、认知重构等
3. 语言温暖、耐心，营造安全的治疗环境
4. 根据当前策略，有针对性地引导患者探索和成长
5. 回应长度控制在2-4句话，避免说教
6. 如果是初次会面，要体现专业介绍和关系建立

请生成你作为心理咨询师的下一句话：
        """.strip()
        
        return prompt
    
    def _get_strategy_guidelines(self, strategy: str) -> str:
        """获取不同策略的指导原则"""
        guidelines = {
            "建立治疗关系": """
            - 展现无条件积极关注，创造安全接纳的环境
            - 介绍治疗框架，说明保密性和治疗目标
            - 使用开放式提问了解患者的主要困扰
            - 避免过早进行深度解释或建议
            """,
            
            "危机干预与稳定化": """
            - 评估自伤自杀风险，确保患者安全
            - 提供即时的情感支持和安抚
            - 引导患者使用应对技巧（如深呼吸、接地技术）
            - 建立短期支持计划和安全承诺
            """,
            
            "认知评估与探索": """
            - 使用苏格拉底式提问探索负性思维模式
            - 帮助患者识别自动化思维和认知扭曲
            - 探索核心信念的形成和影响
            - 引导患者觉察思维-情绪-行为的循环
            """,
            
            "认知重构技术": """
            - 挑战非理性信念，探索证据和反证
            - 引导患者生成更平衡、现实的思维方式
            - 使用"如果朋友遇到同样问题你会怎么说"的技巧
            - 练习替代性思维和应对陈述
            """,
            
            "行为激活疗法": """
            - 探索患者过去享受的活动和兴趣
            - 制定小步骤的行为计划，增加正性强化
            - 分析回避行为的维持因素
            - 鼓励患者尝试新的社交和活动体验
            """,
            
            "综合心理干预": """
            - 整合多种治疗技巧，根据当下需要灵活运用
            - 巩固治疗收获，探索长期应对策略
            - 准备治疗结束和独立应对的过渡
            - 关注预防复发和持续成长
            """
        }
        
        return guidelines.get(strategy, "使用基本的倾听、共情和支持技巧")
    
    def _update_therapy_progress(self, patient_profile: Dict[str, Any], therapist_response: str):
        """更新治疗进展记录"""
        # 这里可以记录治疗进展、调整策略等
        if not hasattr(self, 'therapy_notes'):
            self.therapy_notes = []
        
        self.therapy_notes.append({
            'session': self.session_count,
            'strategy': self.current_strategy,
            'response_theme': self._extract_response_theme(therapist_response),
            'timestamp': None  # 可以添加时间戳
        })
        
        # 如果治疗笔记过多，保留最近的20条
        if len(self.therapy_notes) > 20:
            self.therapy_notes = self.therapy_notes[-20:]
    
    def _extract_response_theme(self, response: str) -> str:
        """提取回应的主题"""
        if '感受' in response or '情绪' in response:
            return '情感探索'
        elif '想法' in response or '认为' in response:
            return '认知探索'
        elif '做' in response or '行动' in response:
            return '行为引导'
        elif '关系' in response or '朋友' in response:
            return '人际探索'
        else:
            return '一般支持'
    
    def get_therapy_summary(self) -> Dict[str, Any]:
        """获取治疗总结"""
        return {
            'therapist_name': self.name,
            'session_count': self.session_count,
            'current_strategy': self.current_strategy,
            'therapy_approach': self.therapeutic_approach,
            'recent_themes': [note['response_theme'] for note in self.therapy_notes[-5:]] if hasattr(self, 'therapy_notes') else []
        }

    async def respond_to_situation(self, situation: str, context: Dict) -> str:
        """基类方法实现 - 专业的治疗回应"""
        return await self.generate_therapeutic_guidance(
            patient_profile=context,
            dialogue_history=[]
        ) 