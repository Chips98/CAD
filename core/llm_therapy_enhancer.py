"""
LLM治疗增强器 - 增强治疗对话系统的AI能力
包括对话质量评估、治疗效果分析、个性化回应生成等
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from models.psychology_models import PsychologicalState
from core.llm_psychological_assessor import LLMPsychologicalAssessor


@dataclass
class TherapeuticResponse:
    """治疗回应数据结构"""
    content: str
    response_type: str  # "supportive", "challenging", "educational", "exploratory"
    therapeutic_techniques: List[str]
    expected_impact: Dict[str, float]
    confidence: float
    reasoning: str


@dataclass
class ConversationAnalysis:
    """对话分析结果"""
    therapeutic_alliance: float  # 治疗联盟强度 0-10
    patient_openness: float      # 患者开放程度 0-10
    engagement_level: float      # 参与度 0-10
    emotional_tone: str          # 情感基调
    progress_indicators: List[str]
    risk_indicators: List[str]
    recommendations: List[str]


class LLMTherapyEnhancer:
    """LLM治疗增强器"""
    
    def __init__(self, ai_client):
        self.ai_client = ai_client
        self.logger = logging.getLogger(__name__)
        
        # 治疗技术库
        self.therapeutic_techniques = self._load_therapeutic_techniques()
        
        # 对话分析历史
        self.conversation_analyses = []
        self.therapy_responses = []
        
        # LLM心理评估器
        self.psychological_assessor = LLMPsychologicalAssessor(ai_client)
        
        self.logger.info("LLM治疗增强器初始化完成")
    
    def _load_therapeutic_techniques(self) -> Dict[str, Dict]:
        """加载治疗技术库"""
        return {
            "cognitive_restructuring": {
                "description": "认知重构 - 识别和改变负面思维模式",
                "keywords": ["想法", "思维", "信念", "看法", "认为"],
                "prompts": [
                    "你觉得这种想法对你有帮助吗？",
                    "有没有其他角度可以看待这个情况？",
                    "这个想法是基于事实还是感觉？"
                ]
            },
            "behavioral_activation": {
                "description": "行为激活 - 鼓励参与积极活动",
                "keywords": ["活动", "做事", "参与", "行动", "尝试"],
                "prompts": [
                    "有什么活动能让你感觉好一些？",
                    "我们可以一起制定一个小目标吗？",
                    "你愿意尝试一些新的活动吗？"
                ]
            },
            "emotion_regulation": {
                "description": "情绪调节 - 学习管理和表达情感",
                "keywords": ["感受", "情绪", "心情", "感觉", "情感"],
                "prompts": [
                    "你现在的感受是什么？",
                    "这种情绪对你意味着什么？",
                    "有什么方法能帮你处理这种感受？"
                ]
            },
            "mindfulness": {
                "description": "正念技术 - 专注当下",
                "keywords": ["现在", "当下", "注意", "专注", "觉察"],
                "prompts": [
                    "让我们专注于当下这一刻",
                    "你现在注意到了什么？",
                    "试着深呼吸，感受现在的自己"
                ]
            },
            "social_skills": {
                "description": "社交技能训练",
                "keywords": ["朋友", "人际", "社交", "交流", "关系"],
                "prompts": [
                    "你希望在人际关系中看到什么变化？",
                    "和别人交流时你通常感觉如何？",
                    "有什么社交技巧你想要学习？"
                ]
            }
        }
    
    async def analyze_conversation(self, dialogue_history: List[Dict], 
                                 patient_state: PsychologicalState) -> ConversationAnalysis:
        """分析对话质量和治疗效果"""
        
        if not self.ai_client:
            return self._default_conversation_analysis()
        
        try:
            # 构建分析prompt
            prompt = self._build_conversation_analysis_prompt(dialogue_history, patient_state)
            
            # 调用LLM进行分析
            response = await self.ai_client.generate_response(prompt)
            
            # 解析分析结果
            analysis = self._parse_conversation_analysis(response)
            
            # 记录分析历史
            self.conversation_analyses.append({
                "timestamp": datetime.now(),
                "analysis": analysis,
                "dialogue_length": len(dialogue_history),
                "patient_state": patient_state.to_dict()
            })
            
            self.logger.debug(f"对话分析完成: 联盟强度={analysis.therapeutic_alliance:.1f}, "
                             f"开放程度={analysis.patient_openness:.1f}")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"对话分析失败: {e}")
            return self._default_conversation_analysis()
    
    def _build_conversation_analysis_prompt(self, dialogue_history: List[Dict], 
                                          patient_state: PsychologicalState) -> str:
        """构建对话分析prompt"""
        
        # 最近对话内容
        recent_dialogue = "\n".join([
            f"{item.get('speaker', '未知')}: {item.get('content', '')}"
            for item in dialogue_history[-10:]  # 最近10轮对话
        ])
        
        # 患者状态摘要
        state_summary = f"""
        抑郁程度: {patient_state.depression_level.name}
        压力水平: {patient_state.stress_level}/10
        自尊水平: {patient_state.self_esteem}/10
        社交连接: {patient_state.social_connection}/10
        """
        
        prompt = f"""
你是一位经验丰富的心理治疗督导，请分析以下治疗对话的质量和效果。

患者当前状态：
{state_summary}

最近对话内容：
{recent_dialogue}

请从以下维度进行专业分析：

1. 治疗联盟强度 (0-10分): 治疗师与患者的信任和合作关系
2. 患者开放程度 (0-10分): 患者分享内心想法和感受的程度
3. 参与度 (0-10分): 患者在对话中的主动参与程度
4. 情感基调: 对话的整体情感氛围
5. 进展指标: 积极的治疗进展表现
6. 风险指标: 需要关注的风险信号
7. 改进建议: 对下一步治疗的建议

输出JSON格式：
{{
  "therapeutic_alliance": 数值,
  "patient_openness": 数值,
  "engagement_level": 数值,
  "emotional_tone": "积极/中性/消极",
  "progress_indicators": ["指标1", "指标2"],
  "risk_indicators": ["风险1", "风险2"],
  "recommendations": ["建议1", "建议2"]
}}
"""
        
        return prompt.strip()
    
    def _parse_conversation_analysis(self, response: str) -> ConversationAnalysis:
        """解析对话分析响应"""
        try:
            data = json.loads(response.strip())
            
            return ConversationAnalysis(
                therapeutic_alliance=self._clamp_value(data.get("therapeutic_alliance", 5.0), 0.0, 10.0),
                patient_openness=self._clamp_value(data.get("patient_openness", 5.0), 0.0, 10.0),
                engagement_level=self._clamp_value(data.get("engagement_level", 5.0), 0.0, 10.0),
                emotional_tone=data.get("emotional_tone", "中性"),
                progress_indicators=data.get("progress_indicators", []),
                risk_indicators=data.get("risk_indicators", []),
                recommendations=data.get("recommendations", [])
            )
            
        except Exception as e:
            self.logger.error(f"解析对话分析失败: {e}")
            return self._default_conversation_analysis()
    
    def _default_conversation_analysis(self) -> ConversationAnalysis:
        """默认对话分析"""
        return ConversationAnalysis(
            therapeutic_alliance=5.0,
            patient_openness=5.0,
            engagement_level=5.0,
            emotional_tone="中性",
            progress_indicators=[],
            risk_indicators=[],
            recommendations=["建议启用LLM分析获取详细评估"]
        )
    
    async def generate_therapeutic_response(self, patient_message: str,
                                          patient_state: PsychologicalState,
                                          dialogue_history: List[Dict],
                                          conversation_analysis: ConversationAnalysis = None) -> TherapeuticResponse:
        """生成治疗性回应"""
        
        if not self.ai_client:
            return self._default_therapeutic_response()
        
        try:
            # 分析患者消息中的关键信息
            message_analysis = await self._analyze_patient_message(patient_message, patient_state)
            
            # 选择合适的治疗技术
            recommended_techniques = self._select_therapeutic_techniques(
                message_analysis, patient_state, conversation_analysis)
            
            # 构建回应生成prompt
            prompt = self._build_response_generation_prompt(
                patient_message, patient_state, dialogue_history, 
                message_analysis, recommended_techniques)
            
            # 生成回应
            response = await self.ai_client.generate_response(prompt)
            
            # 解析回应
            therapeutic_response = self._parse_therapeutic_response(
                response, recommended_techniques)
            
            # 记录回应历史
            self.therapy_responses.append({
                "timestamp": datetime.now(),
                "patient_message": patient_message,
                "response": therapeutic_response,
                "techniques_used": recommended_techniques
            })
            
            return therapeutic_response
            
        except Exception as e:
            self.logger.error(f"生成治疗回应失败: {e}")
            return self._default_therapeutic_response()
    
    async def _analyze_patient_message(self, message: str, 
                                     patient_state: PsychologicalState) -> Dict:
        """分析患者消息"""
        
        prompt = f"""
分析患者的以下消息，识别关键信息：

患者消息："{message}"

患者状态：抑郁程度{patient_state.depression_level.name}，压力{patient_state.stress_level}/10

请识别：
1. 主要情感（0-10）
2. 关键主题
3. 认知模式
4. 行为提及
5. 风险信号

输出JSON：
{{
  "emotional_intensity": 数值,
  "primary_emotion": "情感类型",
  "key_themes": ["主题1", "主题2"],
  "cognitive_patterns": ["模式1", "模式2"],
  "behavioral_mentions": ["行为1", "行为2"],
  "risk_signals": ["风险1", "风险2"]
}}
"""
        
        try:
            response = await self.ai_client.generate_response(prompt)
            return json.loads(response.strip())
        except:
            return {
                "emotional_intensity": 5.0,
                "primary_emotion": "未知",
                "key_themes": [],
                "cognitive_patterns": [],
                "behavioral_mentions": [],
                "risk_signals": []
            }
    
    def _select_therapeutic_techniques(self, message_analysis: Dict,
                                     patient_state: PsychologicalState,
                                     conversation_analysis: ConversationAnalysis = None) -> List[str]:
        """选择合适的治疗技术"""
        
        selected_techniques = []
        
        # 基于消息分析选择技术
        key_themes = message_analysis.get("key_themes", [])
        cognitive_patterns = message_analysis.get("cognitive_patterns", [])
        behavioral_mentions = message_analysis.get("behavioral_mentions", [])
        
        # 认知重构 - 如果有负面思维模式
        if any("负面" in pattern or "消极" in pattern for pattern in cognitive_patterns):
            selected_techniques.append("cognitive_restructuring")
        
        # 行为激活 - 如果提及缺乏活动或动机
        if any("不想" in mention or "懒得" in mention for mention in behavioral_mentions):
            selected_techniques.append("behavioral_activation")
        
        # 情绪调节 - 如果情感强度高
        if message_analysis.get("emotional_intensity", 0) > 7:
            selected_techniques.append("emotion_regulation")
        
        # 社交技能 - 如果提及人际问题
        if patient_state.social_connection < 4:
            selected_techniques.append("social_skills")
        
        # 正念 - 如果焦虑或反刍严重
        if patient_state.stress_level > 7:
            selected_techniques.append("mindfulness")
        
        # 确保至少有一个技术
        if not selected_techniques:
            selected_techniques.append("emotion_regulation")
        
        return selected_techniques[:2]  # 最多选择2个技术
    
    def _build_response_generation_prompt(self, patient_message: str,
                                        patient_state: PsychologicalState,
                                        dialogue_history: List[Dict],
                                        message_analysis: Dict,
                                        techniques: List[str]) -> str:
        """构建回应生成prompt"""
        
        # 治疗技术描述
        technique_descriptions = []
        for tech in techniques:
            if tech in self.therapeutic_techniques:
                desc = self.therapeutic_techniques[tech]["description"]
                technique_descriptions.append(f"- {tech}: {desc}")
        
        # 对话上下文
        context = "\n".join([
            f"{item.get('speaker', '未知')}: {item.get('content', '')}"
            for item in dialogue_history[-5:]  # 最近5轮对话
        ])
        
        prompt = f"""
你是一位专业的心理治疗师，请为患者提供治疗性回应。

患者消息："{patient_message}"

患者状态：
- 抑郁程度：{patient_state.depression_level.name}
- 压力水平：{patient_state.stress_level}/10
- 自尊水平：{patient_state.self_esteem}/10

对话上下文：
{context}

消息分析：
- 主要情感：{message_analysis.get('primary_emotion', '未知')}
- 情感强度：{message_analysis.get('emotional_intensity', 5)}/10
- 关键主题：{', '.join(message_analysis.get('key_themes', []))}

建议使用的治疗技术：
{chr(10).join(technique_descriptions)}

请生成一个治疗性回应，要求：
1. 体现共情和理解
2. 运用建议的治疗技术
3. 避免给出直接建议，而是引导思考
4. 长度适中（50-100字）
5. 语调温和、专业

输出JSON格式：
{{
  "content": "回应内容",
  "response_type": "supportive/challenging/educational/exploratory",
  "therapeutic_techniques": ["使用的技术1", "技术2"],
  "expected_impact": {{
    "emotional_support": 0.0-1.0,
    "insight_promotion": 0.0-1.0,
    "behavioral_change": 0.0-1.0
  }},
  "confidence": 0.0-1.0,
  "reasoning": "选择这种回应的理由"
}}
"""
        
        return prompt.strip()
    
    def _parse_therapeutic_response(self, response: str, 
                                  techniques: List[str]) -> TherapeuticResponse:
        """解析治疗回应"""
        try:
            data = json.loads(response.strip())
            
            return TherapeuticResponse(
                content=data.get("content", "我理解你的感受。"),
                response_type=data.get("response_type", "supportive"),
                therapeutic_techniques=data.get("therapeutic_techniques", techniques),
                expected_impact=data.get("expected_impact", {}),
                confidence=self._clamp_value(data.get("confidence", 0.5), 0.0, 1.0),
                reasoning=data.get("reasoning", "")
            )
            
        except Exception as e:
            self.logger.error(f"解析治疗回应失败: {e}")
            return self._default_therapeutic_response()
    
    def _default_therapeutic_response(self) -> TherapeuticResponse:
        """默认治疗回应"""
        return TherapeuticResponse(
            content="我听到了你的话，感谢你的分享。你现在的感受如何？",
            response_type="supportive",
            therapeutic_techniques=["emotion_regulation"],
            expected_impact={"emotional_support": 0.5},
            confidence=0.3,
            reasoning="默认回应，LLM不可用"
        )
    
    async def evaluate_session_effectiveness(self, session_data: Dict) -> Dict:
        """评估会话有效性"""
        
        if not self.ai_client:
            return self._default_session_evaluation()
        
        try:
            prompt = self._build_session_evaluation_prompt(session_data)
            response = await self.ai_client.generate_response(prompt)
            return self._parse_session_evaluation(response)
            
        except Exception as e:
            self.logger.error(f"会话评估失败: {e}")
            return self._default_session_evaluation()
    
    def _build_session_evaluation_prompt(self, session_data: Dict) -> str:
        """构建会话评估prompt"""
        
        dialogue_count = len(session_data.get("dialogue_history", []))
        initial_state = session_data.get("initial_patient_state", {})
        final_state = session_data.get("final_patient_state", {})
        session_duration = session_data.get("duration_minutes", 0)
        
        prompt = f"""
评估心理治疗会话的有效性：

会话信息：
- 对话轮数：{dialogue_count}
- 持续时间：{session_duration}分钟
- 初始状态：{initial_state}
- 结束状态：{final_state}

请评估：
1. 整体会话质量 (0-10)
2. 治疗目标达成度 (0-10)
3. 患者参与度 (0-10)
4. 治疗师专业水平 (0-10)
5. 预期长期效果 (0-10)

输出JSON：
{{
  "overall_quality": 数值,
  "goal_achievement": 数值,
  "patient_engagement": 数值,
  "therapist_competence": 数值,
  "expected_long_term_effect": 数值,
  "strengths": ["优点1", "优点2"],
  "areas_for_improvement": ["改进点1", "改进点2"],
  "recommendations": ["建议1", "建议2"]
}}
"""
        
        return prompt.strip()
    
    def _parse_session_evaluation(self, response: str) -> Dict:
        """解析会话评估"""
        try:
            data = json.loads(response.strip())
            
            # 确保数值在合理范围内
            for key in ["overall_quality", "goal_achievement", "patient_engagement", 
                       "therapist_competence", "expected_long_term_effect"]:
                if key in data:
                    data[key] = self._clamp_value(data[key], 0.0, 10.0)
            
            return data
            
        except Exception as e:
            self.logger.error(f"解析会话评估失败: {e}")
            return self._default_session_evaluation()
    
    def _default_session_evaluation(self) -> Dict:
        """默认会话评估"""
        return {
            "overall_quality": 5.0,
            "goal_achievement": 5.0,
            "patient_engagement": 5.0,
            "therapist_competence": 5.0,
            "expected_long_term_effect": 5.0,
            "strengths": ["基础对话功能正常"],
            "areas_for_improvement": ["启用LLM增强获取详细评估"],
            "recommendations": ["建议使用LLM增强功能"]
        }
    
    def _clamp_value(self, value: Any, min_val: float, max_val: float) -> float:
        """限制数值范围"""
        try:
            return max(min_val, min(max_val, float(value)))
        except (ValueError, TypeError):
            return (min_val + max_val) / 2
    
    def get_therapy_statistics(self) -> Dict:
        """获取治疗统计信息"""
        
        total_analyses = len(self.conversation_analyses)
        total_responses = len(self.therapy_responses)
        
        if total_analyses == 0:
            return {
                "total_conversation_analyses": 0,
                "total_therapeutic_responses": total_responses,
                "average_therapeutic_alliance": 0.0,
                "most_used_techniques": []
            }
        
        # 计算平均治疗联盟强度
        avg_alliance = sum(analysis["analysis"].therapeutic_alliance 
                          for analysis in self.conversation_analyses) / total_analyses
        
        # 统计最常用的治疗技术
        technique_counts = {}
        for response_record in self.therapy_responses:
            techniques = response_record.get("techniques_used", [])
            for technique in techniques:
                technique_counts[technique] = technique_counts.get(technique, 0) + 1
        
        most_used = sorted(technique_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "total_conversation_analyses": total_analyses,
            "total_therapeutic_responses": total_responses,
            "average_therapeutic_alliance": round(avg_alliance, 2),
            "most_used_techniques": [technique for technique, count in most_used],
            "technique_usage": technique_counts
        }