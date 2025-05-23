from typing import Dict, List, Any, Optional, Union
import asyncio
from datetime import datetime

from agents.base_agent import BaseAgent
from models.psychology_models import PsychologicalState, EmotionState, DepressionLevel

class TherapistAgent(BaseAgent):
    """心理医生Agent - 专业心理咨询师"""
    
    def __init__(self, name: str, ai_client: Union['GeminiClient', 'DeepSeekClient']):
        super().__init__(
            name=name,
            age=35,
            personality={
                "profession": "临床心理学家",
                "specialization": "青少年心理健康",
                "experience_years": 10,
                "therapeutic_approach": ["认知行为疗法", "人本主义疗法", "系统家庭治疗"],
                "empathy": 9,
                "patience": 9,
                "active_listening": 9,
                "professional_boundaries": 8
            },
            ai_client=ai_client
        )
        
        # 治疗记录
        self.therapy_sessions: List[Dict[str, Any]] = []
        self.treatment_plan: Dict[str, Any] = {}
        self.patient_insights: List[str] = []
        
    def get_role_description(self) -> str:
        return "专业心理医生，擅长青少年心理健康治疗"
    
    def get_current_concerns(self) -> List[str]:
        return [
            "建立治疗关系",
            "评估患者心理状态", 
            "制定个性化治疗方案",
            "提供专业心理支持"
        ]
    
    async def conduct_therapy_session(self, patient_agent: BaseAgent, 
                                    user_input: str = None) -> str:
        """进行心理治疗会话"""
        
        # 获取患者当前状态
        patient_state = patient_agent.get_profile()
        
        # 构建治疗师的专业回应
        if user_input:
            # 用户作为治疗师发言
            therapist_response = await self._generate_professional_response(
                user_input, patient_state
            )
        else:
            # AI治疗师主动开始会话
            therapist_response = await self._initiate_session(patient_state)
        
        # 记录会话
        session_record = {
            "timestamp": datetime.now().isoformat(),
            "therapist_input": user_input or "会话开始",
            "therapist_response": therapist_response,
            "patient_state_before": patient_state,
            "session_type": "个体心理治疗"
        }
        
        self.therapy_sessions.append(session_record)
        
        return therapist_response
    
    async def _generate_professional_response(self, user_input: str, 
                                            patient_state: Dict) -> str:
        """生成专业的治疗师回应"""
        
        prompt = f"""
        你是一位经验丰富的临床心理学家，正在为一位17岁的青少年患者进行心理治疗。

        患者当前状态：
        {patient_state}

        用户（作为治疗师）刚才说："{user_input}"

        请作为专业心理医生，对用户的话进行专业点评和建议，包括：

        1. **技术分析**：
           - 评估用户使用的治疗技术是否恰当
           - 指出可能的改进空间
           - 建议更有效的干预方法

        2. **患者反应预测**：
           - 患者可能如何回应这样的干预
           - 这种方法的潜在效果
           - 需要注意的风险点

        3. **专业建议**：
           - 下一步治疗方向建议
           - 可以尝试的其他技术
           - 治疗目标调整建议

        4. **示范回应**：
           - 提供一个更专业的回应示例
           - 解释为什么这样回应更有效

        请用专业但易懂的语言回应，帮助用户提高心理咨询技能。
        """
        
        return await self.ai_client.generate_response(prompt)
    
    async def _initiate_session(self, patient_state: Dict) -> str:
        """主动开始治疗会话"""
        
        prompt = f"""
        你是一位专业的青少年心理医生，正准备开始与17岁患者李明的治疗会话。

        患者当前状态：
        {patient_state}

        请提供治疗会话的开场指导，包括：

        1. **会话开场建议**：
           - 如何建立初始的治疗关系
           - 适合的开场话语示例
           - 需要观察的患者行为

        2. **评估重点**：
           - 本次会话应该重点评估的内容
           - 需要探索的核心问题
           - 风险评估要点

        3. **治疗目标**：
           - 短期目标（本次会话）
           - 中期目标（近几次会话）
           - 长期治疗目标

        4. **技术建议**：
           - 推荐使用的治疗技术
           - 需要避免的做法
           - 预期的治疗挑战

        请为初学者心理咨询师提供清晰的指导。
        """
        
        return await self.ai_client.generate_response(prompt)
    
    async def analyze_treatment_progress(self, patient_agent: BaseAgent) -> Dict[str, Any]:
        """分析治疗进展"""
        
        current_state = patient_agent.get_profile()
        session_history = self.therapy_sessions[-5:] if self.therapy_sessions else []
        
        prompt = f"""
        作为临床心理学家，请分析患者的治疗进展：

        患者当前状态：
        {current_state}

        最近5次会话记录：
        {session_history}

        请提供详细的治疗进展分析，包括：

        1. **症状变化**：
           - 抑郁症状的改善情况
           - 焦虑水平的变化
           - 社交功能的恢复

        2. **治疗效果评估**：
           - 有效的干预技术
           - 治疗阻抗分析
           - 突破性进展识别

        3. **风险评估**：
           - 自伤风险评估
           - 病情恶化迹象
           - 需要紧急干预的信号

        4. **治疗方案调整**：
           - 是否需要调整治疗目标
           - 建议的新干预技术
           - 治疗频率建议

        请返回JSON格式的专业分析报告。
        """
        
        try:
            response = await self.ai_client.generate_response(prompt)
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            import json
            return json.loads(json_str)
        except Exception as e:
            return {
                "analysis_error": str(e),
                "basic_assessment": "需要继续观察患者状态变化"
            }
    
    async def provide_supervision(self, user_intervention: str, 
                                patient_response: str) -> str:
        """提供督导建议"""
        
        prompt = f"""
        作为资深督导师，请对以下心理治疗互动进行专业督导：

        治疗师干预："{user_intervention}"
        患者回应："{patient_response}"

        请提供督导反馈：

        1. **干预技术评估**：
           - 使用的技术是否恰当
           - 时机把握是否合适
           - 表达方式的专业性

        2. **患者反应分析**：
           - 患者回应反映的心理状态
           - 治疗关系的变化
           - 阻抗或配合的表现

        3. **改进建议**：
           - 可以改进的地方
           - 更有效的干预方式
           - 避免的沟通陷阱

        4. **下步方向**：
           - 后续会话的重点
           - 可以探索的新话题
           - 维护治疗关系的方法

        请用鼓励但专业的语言提供建设性反馈。
        """
        
        return await self.ai_client.generate_response(prompt)

    async def provide_supervision_with_context(self, user_intervention: str, 
                                             patient_response: str,
                                             conversation_context: str,
                                             patient_data: Dict[str, Any],
                                             supervision_interval: int = 3) -> str:
        """提供基于完整上下文的督导建议"""
        
        # 构建患者背景信息
        patient_background = ""
        if patient_data:
            patient_background = f"""
        患者背景信息：
        - 姓名：{patient_data.get('name', '李明')}，年龄：{patient_data.get('age', 17)}岁
        - 抑郁程度：{patient_data.get('depression_level', 'N/A')}
        - 当前状态：{patient_data.get('final_state_description', 'N/A')}
        - 主要症状：{', '.join(patient_data.get('symptoms', [])[:5])}
        - 风险因素：{', '.join(patient_data.get('risk_factors', [])[:3])}
        - 数据来源：{patient_data.get('data_source', 'N/A')}
            """
        
        # 构建对话历史上下文
        context_section = ""
        if conversation_context:
            context_section = f"""
        最近{supervision_interval}轮对话历史：
        {conversation_context}
        """
        
        prompt = f"""
        作为资深督导师，请对以下心理治疗互动进行专业督导分析：

        {patient_background}

        {context_section}

        当前这轮对话：
        治疗师干预："{user_intervention}"
        患者回应："{patient_response}"

        请基于完整的背景信息和最近{supervision_interval}轮对话历史，提供综合性督导反馈：

        1. **当前干预评估**：
           - 这次干预在整个治疗进程中的恰当性
           - 是否符合患者当前的心理状态和需求
           - 时机选择和表达方式的专业性评价

        2. **患者反应深层分析**：
           - 结合患者历史创伤和症状，分析当前回应的意义
           - 从最近{supervision_interval}轮对话看，治疗关系的发展趋势
           - 患者可能的内在心理动力和防御机制

        3. **治疗进程评估**：
           - 从最近{supervision_interval}轮对话看，治疗的整体进展如何
           - 是否正在有效建立治疗联盟
           - 患者的开放度和信任度变化

        4. **专业改进建议**：
           - 基于患者完整背景，建议更有效的干预策略
           - 考虑到对话历史，提出后续探索方向
           - 针对这类青少年抑郁患者的特殊技术建议

        5. **风险评估和注意事项**：
           - 基于患者背景评估当前风险水平
           - 需要特别关注的症状或行为表现
           - 治疗中需要避免的触发因素

        请提供具体、实用且鼓励性的专业督导建议。
        """
        
        return await self.ai_client.generate_response(prompt) 