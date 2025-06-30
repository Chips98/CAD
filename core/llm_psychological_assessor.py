"""
LLM心理状态评估器 - 基于语义理解进行深度心理影响分析
结合CBT认知行为理论和贝克认知三角模型
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from models.psychology_models import LifeEvent, PsychologicalState, CognitiveAffectiveState


@dataclass
class LLMPsychologicalImpact:
    """LLM心理影响评估结果"""
    # 基础心理指标调整
    depression_adjustment: float = 0.0    # -3.0 到 +3.0
    anxiety_adjustment: float = 0.0       # -3.0 到 +3.0  
    self_esteem_adjustment: float = 0.0   # -3.0 到 +3.0
    
    # CAD认知-情感状态调整
    self_belief_adjustment: float = 0.0   # -2.0 到 +2.0
    world_belief_adjustment: float = 0.0  # -2.0 到 +2.0
    future_belief_adjustment: float = 0.0 # -2.0 到 +2.0
    
    # 认知加工和行为倾向调整
    rumination_adjustment: float = 0.0    # -2.0 到 +2.0
    distortion_adjustment: float = 0.0    # -2.0 到 +2.0
    social_withdrawal_adjustment: float = 0.0  # -2.0 到 +2.0
    avolition_adjustment: float = 0.0     # -2.0 到 +2.0
    
    # 元信息
    confidence_level: float = 0.5         # LLM对评估的信心度 0.0-1.0
    reasoning: str = ""                   # 评估理由
    risk_indicators: List[str] = None     # 识别的风险因素
    protective_factors: List[str] = None  # 保护性因素
    
    def __post_init__(self):
        if self.risk_indicators is None:
            self.risk_indicators = []
        if self.protective_factors is None:
            self.protective_factors = []
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "depression_adjustment": self.depression_adjustment,
            "anxiety_adjustment": self.anxiety_adjustment,
            "self_esteem_adjustment": self.self_esteem_adjustment,
            "self_belief_adjustment": self.self_belief_adjustment,
            "world_belief_adjustment": self.world_belief_adjustment,
            "future_belief_adjustment": self.future_belief_adjustment,
            "rumination_adjustment": self.rumination_adjustment,
            "distortion_adjustment": self.distortion_adjustment,
            "social_withdrawal_adjustment": self.social_withdrawal_adjustment,
            "avolition_adjustment": self.avolition_adjustment,
            "confidence_level": self.confidence_level,
            "reasoning": self.reasoning,
            "risk_indicators": self.risk_indicators,
            "protective_factors": self.protective_factors
        }


class LLMPsychologicalAssessor:
    """LLM心理状态评估器"""
    
    def __init__(self, ai_client):
        self.ai_client = ai_client
        self.logger = logging.getLogger(__name__)
        
        # 评估历史和质量控制
        self.assessment_history = []
        self.confidence_threshold = 0.6
        self.enable_assessment = True
        
        # 心理学理论模板
        self.cbt_framework = self._load_cbt_framework()
        self.beck_triad_rules = self._load_beck_triad_rules()
        
        self.logger.info("LLM心理状态评估器初始化完成")
    
    def _load_cbt_framework(self) -> Dict:
        """加载CBT认知行为理论框架"""
        return {
            "cognitive_distortions": [
                "全有全无思维", "过度概括", "心理过滤", "否定正面",
                "跳跃性结论", "放大和缩小", "情感推理", "应该陈述",
                "标签化", "个人化"
            ],
            "behavioral_patterns": [
                "回避行为", "社交退缩", "拖延", "强迫行为",
                "自我伤害", "物质滥用", "过度寻求保证"
            ],
            "emotional_regulation": [
                "情绪识别", "情绪表达", "情绪调节", "情绪容忍"
            ]
        }
    
    def _load_beck_triad_rules(self) -> Dict:
        """加载贝克认知三角规则"""
        return {
            "self_belief_triggers": [
                "个人能力", "自我价值", "成就表现", "他人评价",
                "外貌形象", "智力能力", "道德品质"
            ],
            "world_belief_triggers": [
                "人际关系", "社会公平", "环境安全", "他人动机",
                "社会支持", "制度信任", "世界善恶"
            ],
            "future_belief_triggers": [
                "目标实现", "希望期望", "控制感", "机会可能",
                "时间概念", "变化能力", "结果预期"
            ]
        }
    
    async def assess_event_impact(self, event: LifeEvent, 
                                current_state: PsychologicalState,
                                context: Dict = None) -> LLMPsychologicalImpact:
        """评估事件对心理状态的综合影响"""
        
        if not self.ai_client or not self.enable_assessment:
            return self._default_assessment()
        
        try:
            # 构建评估prompt
            prompt = self._build_assessment_prompt(event, current_state, context)
            
            # 调用LLM进行评估
            response = await self.ai_client.generate_response(prompt)
            
            # 解析和验证结果
            assessment = self._parse_assessment_response(response)
            
            # 记录评估历史
            self._record_assessment(event, current_state, assessment, context)
            
            self.logger.debug(f"LLM评估完成，置信度: {assessment.confidence_level:.2f}")
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"LLM心理评估失败: {e}")
            return self._default_assessment()
    
    def _build_assessment_prompt(self, event: LifeEvent, 
                               current_state: PsychologicalState,
                               context: Dict = None) -> str:
        """构建心理评估prompt"""
        
        # 当前状态信息
        depression_level = current_state.depression_level.name
        cad_state = current_state.cad_state
        
        # 最近事件历史
        recent_events = context.get("recent_events", []) if context else []
        recent_summary = self._summarize_recent_events(recent_events)
        
        # 角色信息
        character_info = context.get("character_info", {}) if context else {}
        age = character_info.get("age", 17)
        personality = character_info.get("personality", {})
        
        prompt = f"""
你是一位资深的临床心理学家，专精认知行为疗法(CBT)和贝克认知三角理论。请评估以下生活事件对患者心理状态的影响。

患者基本信息：
- 年龄：{age}岁
- 人格特质：{personality}
- 当前抑郁程度：{depression_level}
- 当前焦虑水平：{current_state.stress_level}/10
- 自尊水平：{current_state.self_esteem}/10

当前认知-情感状态(CAD)：
- 情感基调：{cad_state.affective_tone:.1f}/10 (负值=悲观)
- 自我信念：{cad_state.core_beliefs.self_belief:.1f}/10 (负值=负面自我观)
- 世界信念：{cad_state.core_beliefs.world_belief:.1f}/10 (负值=世界悲观)
- 未来信念：{cad_state.core_beliefs.future_belief:.1f}/10 (负值=未来悲观)
- 思维反刍：{cad_state.cognitive_processing.rumination:.1f}/10
- 认知扭曲：{cad_state.cognitive_processing.distortions:.1f}/10
- 社交退缩：{cad_state.behavioral_inclination.social_withdrawal:.1f}/10
- 动机缺失：{cad_state.behavioral_inclination.avolition:.1f}/10

最近发生的事件：
{recent_summary}

当前评估事件：
{event.description}
参与者：{', '.join(event.participants)}

请基于CBT理论和贝克认知三角，评估这个事件的心理影响：

评估维度（调整幅度-3.0到+3.0）：
1. 抑郁状态调整：考虑情绪反应和症状变化
2. 焦虑水平调整：考虑担忧和紧张程度
3. 自尊水平调整：考虑自我价值感变化

CAD状态调整（调整幅度-2.0到+2.0）：
4. 自我信念调整：对自我价值、能力的看法
5. 世界信念调整：对他人、环境的看法
6. 未来信念调整：对希望、可能性的看法
7. 思维反刍调整：重复负性思维的变化
8. 认知扭曲调整：思维偏差的变化
9. 社交退缩调整：回避社交的倾向
10. 动机缺失调整：兴趣和动力的变化

输出JSON格式：
{{
  "depression_adjustment": 数值,
  "anxiety_adjustment": 数值,
  "self_esteem_adjustment": 数值,
  "self_belief_adjustment": 数值,
  "world_belief_adjustment": 数值,
  "future_belief_adjustment": 数值,
  "rumination_adjustment": 数值,
  "distortion_adjustment": 数值,
  "social_withdrawal_adjustment": 数值,
  "avolition_adjustment": 数值,
  "confidence_level": 0.0-1.0,
  "reasoning": "详细的心理学分析（100-200字）",
  "risk_indicators": ["风险因素1", "风险因素2"],
  "protective_factors": ["保护因素1", "保护因素2"]
}}

注意：
- 负值表示恶化，正值表示改善
- 考虑个体差异和累积效应
- 基于循证心理学原理进行评估
"""
        
        return prompt.strip()
    
    def _summarize_recent_events(self, recent_events: List[Dict]) -> str:
        """总结最近事件"""
        if not recent_events:
            return "无特殊事件记录"
        
        summaries = []
        for event in recent_events[-5:]:  # 最近5个事件
            desc = event.get("description", "")
            impact = event.get("impact_score", 0)
            emotion = "正面" if impact > 0 else "负面" if impact < 0 else "中性"
            summaries.append(f"- {desc[:30]}... ({emotion})")
        
        return "\n".join(summaries)
    
    def _parse_assessment_response(self, response: str) -> LLMPsychologicalImpact:
        """解析LLM评估响应"""
        try:
            # 清理响应文本
            clean_response = response.strip()
            if not clean_response:
                raise ValueError("响应为空")
                
            # 处理可能的markdown格式
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            clean_response = clean_response.strip()
            
            # 尝试找到JSON部分
            if '{' in clean_response and '}' in clean_response:
                start_idx = clean_response.find('{')
                end_idx = clean_response.rfind('}') + 1
                clean_response = clean_response[start_idx:end_idx]
            
            # 解析JSON
            data = json.loads(clean_response)
            
            # 验证和规范化数值
            assessment = LLMPsychologicalImpact()
            
            # 基础心理指标 (-3.0 到 +3.0)
            assessment.depression_adjustment = self._clamp_value(
                data.get("depression_adjustment", 0.0), -3.0, 3.0)
            assessment.anxiety_adjustment = self._clamp_value(
                data.get("anxiety_adjustment", 0.0), -3.0, 3.0)
            assessment.self_esteem_adjustment = self._clamp_value(
                data.get("self_esteem_adjustment", 0.0), -3.0, 3.0)
            
            # CAD状态调整 (-2.0 到 +2.0)
            assessment.self_belief_adjustment = self._clamp_value(
                data.get("self_belief_adjustment", 0.0), -2.0, 2.0)
            assessment.world_belief_adjustment = self._clamp_value(
                data.get("world_belief_adjustment", 0.0), -2.0, 2.0)
            assessment.future_belief_adjustment = self._clamp_value(
                data.get("future_belief_adjustment", 0.0), -2.0, 2.0)
            assessment.rumination_adjustment = self._clamp_value(
                data.get("rumination_adjustment", 0.0), -2.0, 2.0)
            assessment.distortion_adjustment = self._clamp_value(
                data.get("distortion_adjustment", 0.0), -2.0, 2.0)
            assessment.social_withdrawal_adjustment = self._clamp_value(
                data.get("social_withdrawal_adjustment", 0.0), -2.0, 2.0)
            assessment.avolition_adjustment = self._clamp_value(
                data.get("avolition_adjustment", 0.0), -2.0, 2.0)
            
            # 元信息
            assessment.confidence_level = self._clamp_value(
                data.get("confidence_level", 0.5), 0.0, 1.0)
            assessment.reasoning = data.get("reasoning", "")
            assessment.risk_indicators = data.get("risk_indicators", [])
            assessment.protective_factors = data.get("protective_factors", [])
            
            # 置信度过低时降级到默认评估
            if assessment.confidence_level < self.confidence_threshold:
                self.logger.warning(f"LLM评估置信度过低: {assessment.confidence_level}")
                return self._default_assessment()
            
            self.logger.debug(f"成功解析LLM评估，置信度: {assessment.confidence_level:.2f}")
            return assessment
            
        except Exception as e:
            self.logger.error(f"解析LLM评估响应失败: {e}\n响应内容: {response[:200]}...")
            return self._default_assessment()
    
    def _clamp_value(self, value: Any, min_val: float, max_val: float) -> float:
        """限制数值在指定范围内"""
        try:
            return max(min_val, min(max_val, float(value)))
        except (ValueError, TypeError):
            return 0.0
    
    def _default_assessment(self) -> LLMPsychologicalImpact:
        """默认评估结果 - 提供更合理的默认值而不是全0"""
        return LLMPsychologicalImpact(
            # 轻微的负面影响作为默认
            depression_adjustment=-0.1,
            anxiety_adjustment=-0.1,
            self_esteem_adjustment=-0.1,
            self_belief_adjustment=-0.1,
            world_belief_adjustment=-0.05,
            future_belief_adjustment=-0.05,
            rumination_adjustment=0.1,
            distortion_adjustment=0.05,
            social_withdrawal_adjustment=0.05,
            avolition_adjustment=0.05,
            confidence_level=0.3,
            reasoning="使用默认评估，LLM不可用或评估失败，给予轻微负面影响",
            risk_indicators=["LLM评估不可用"],
            protective_factors=[]
        )
    
    def _record_assessment(self, event: LifeEvent, 
                         current_state: PsychologicalState,
                         assessment: LLMPsychologicalImpact,
                         context: Dict = None):
        """记录评估历史"""
        record = {
            "timestamp": datetime.now(),
            "event": event.to_dict(),
            "current_state": current_state.to_dict(),
            "assessment": assessment.to_dict(),
            "context": context or {}
        }
        
        self.assessment_history.append(record)
        
        # 保留最近100次评估
        if len(self.assessment_history) > 100:
            self.assessment_history = self.assessment_history[-100:]
    
    async def assess_therapy_conversation(self, conversation_data: Dict) -> Dict:
        """评估治疗对话的效果"""
        if not self.ai_client:
            return self._default_therapy_assessment()
        
        try:
            prompt = self._build_therapy_assessment_prompt(conversation_data)
            response = await self.ai_client.generate_response(prompt)
            return self._parse_therapy_assessment(response)
            
        except Exception as e:
            self.logger.error(f"评估治疗对话失败: {e}")
            return self._default_therapy_assessment()
    
    def _build_therapy_assessment_prompt(self, conversation_data: Dict) -> str:
        """构建治疗对话评估prompt"""
        dialogue_history = conversation_data.get("dialogue_history", [])
        patient_state = conversation_data.get("patient_state", {})
        
        # 最近几轮对话
        recent_dialogue = "\n".join([
            f"{item.get('speaker', '未知')}: {item.get('content', '')}"
            for item in dialogue_history[-10:]  # 最近10轮
        ])
        
        prompt = f"""
作为治疗效果评估专家，请分析以下治疗对话的质量和效果：

患者当前状态：
{patient_state}

最近对话内容：
{recent_dialogue}

请评估：
1. 对话质量 (0-10分)
2. 治疗联盟强度 (0-10分)  
3. 患者开放程度 (0-10分)
4. 治疗师干预有效性 (0-10分)
5. 预期治疗效果 (0-10分)

输出JSON格式：
{{
  "conversation_quality": 数值,
  "therapeutic_alliance": 数值,
  "patient_openness": 数值,
  "therapist_effectiveness": 数值,
  "expected_treatment_effect": 数值,
  "analysis": "详细分析",
  "recommendations": ["建议1", "建议2"]
}}
"""
        return prompt.strip()
    
    def _parse_therapy_assessment(self, response: str) -> Dict:
        """解析治疗评估响应"""
        try:
            data = json.loads(response.strip())
            
            # 规范化分数
            for key in ["conversation_quality", "therapeutic_alliance", 
                       "patient_openness", "therapist_effectiveness", 
                       "expected_treatment_effect"]:
                if key in data:
                    data[key] = self._clamp_value(data[key], 0.0, 10.0)
            
            return data
            
        except Exception as e:
            self.logger.error(f"解析治疗评估失败: {e}")
            return self._default_therapy_assessment()
    
    def _default_therapy_assessment(self) -> Dict:
        """默认治疗评估"""
        return {
            "conversation_quality": 5.0,
            "therapeutic_alliance": 5.0,
            "patient_openness": 5.0,
            "therapist_effectiveness": 5.0,
            "expected_treatment_effect": 5.0,
            "analysis": "默认评估，LLM不可用",
            "recommendations": ["建议使用LLM进行详细评估"]
        }
    
    def get_assessment_statistics(self) -> Dict:
        """获取评估统计信息"""
        if not self.assessment_history:
            return {
                "total_assessments": 0,
                "average_confidence": 0.0,
                "assessment_distribution": {},
                "common_risk_factors": [],
                "common_protective_factors": []
            }
        
        # 统计基本信息
        total_assessments = len(self.assessment_history)
        
        # 平均置信度
        confidences = [record["assessment"]["confidence_level"] 
                      for record in self.assessment_history]
        average_confidence = sum(confidences) / len(confidences)
        
        # 评估分布统计
        assessment_distribution = self._calculate_assessment_distribution()
        
        # 常见风险和保护因素
        risk_factors = self._extract_common_factors("risk_indicators")
        protective_factors = self._extract_common_factors("protective_factors")
        
        return {
            "total_assessments": total_assessments,
            "average_confidence": round(average_confidence, 3),
            "assessment_distribution": assessment_distribution,
            "common_risk_factors": risk_factors[:5],  # 前5个
            "common_protective_factors": protective_factors[:5]
        }
    
    def _calculate_assessment_distribution(self) -> Dict:
        """计算评估分布"""
        distributions = {
            "depression_adjustments": [],
            "anxiety_adjustments": [],
            "self_esteem_adjustments": []
        }
        
        for record in self.assessment_history:
            assessment = record["assessment"]
            distributions["depression_adjustments"].append(
                assessment.get("depression_adjustment", 0.0))
            distributions["anxiety_adjustments"].append(
                assessment.get("anxiety_adjustment", 0.0))
            distributions["self_esteem_adjustments"].append(
                assessment.get("self_esteem_adjustment", 0.0))
        
        # 计算平均值和范围
        result = {}
        for key, values in distributions.items():
            if values:
                result[key] = {
                    "average": round(sum(values) / len(values), 3),
                    "min": round(min(values), 3),
                    "max": round(max(values), 3)
                }
        
        return result
    
    def _extract_common_factors(self, factor_type: str) -> List[str]:
        """提取常见因素"""
        factor_counts = {}
        
        for record in self.assessment_history:
            factors = record["assessment"].get(factor_type, [])
            for factor in factors:
                factor_counts[factor] = factor_counts.get(factor, 0) + 1
        
        # 按频次排序
        sorted_factors = sorted(factor_counts.items(), 
                              key=lambda x: x[1], reverse=True)
        
        return [factor for factor, count in sorted_factors]
    
    def enable_llm_assessment(self, enable: bool = True):
        """启用/禁用LLM评估"""
        self.enable_assessment = enable
        self.logger.info(f"LLM评估已{'启用' if enable else '禁用'}")
    
    def set_confidence_threshold(self, threshold: float):
        """设置置信度阈值"""
        self.confidence_threshold = max(0.0, min(1.0, threshold))
        self.logger.info(f"置信度阈值设置为: {self.confidence_threshold}")