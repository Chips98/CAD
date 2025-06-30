"""
CAD增强心理模型
基于认知-情感-抑郁(Cognitive-Affective-Depression)理论的增强模型
结合Beck认知三角和CBT理论进行心理状态更新
"""

import time
from typing import Dict, List, Any, Optional
from models.psychological_model_base import (
    PsychologicalModelBase, ModelImpactResult, PsychologicalModelType
)
from models.psychology_models import LifeEvent, PsychologicalState, DepressionLevel, EmotionState


class CADEnhancedModel(PsychologicalModelBase):
    """CAD增强心理模型"""
    
    REQUIRES_AI_CLIENT = False
    
    def __init__(self, model_type: PsychologicalModelType, config: Dict[str, Any] = None):
        """初始化CAD增强模型"""
        super().__init__(model_type, config)
    
    def _initialize_model(self):
        """初始化模型特定组件"""
        # 设置默认配置
        default_config = {
            # CAD理论参数
            "belief_impact_strength": 0.4,      # 核心信念影响强度
            "affective_amplification": 1.3,     # 情感放大系数
            "rumination_threshold": 6.0,        # 思维反刍阈值
            "cognitive_distortion_rate": 0.1,   # 认知扭曲增长率
            "social_withdrawal_trigger": -2.0,  # 社交退缩触发阈值
            "behavioral_feedback_rate": 0.15,   # 行为反馈系数
            
            # 动力学参数
            "belief_interaction_rate": 0.2,     # 信念间相互影响率
            "emotion_cognition_coupling": 0.25, # 情绪认知耦合强度
            "daily_decay_rate": 0.04,          # 每日自然衰减率
            "positive_bias_reduction": 0.8,     # 积极事件偏差削减
            
            # 阈值参数
            "severe_event_threshold": -5,       # 严重事件阈值
            "mild_event_threshold": -2,         # 轻微事件阈值
            "recovery_event_threshold": 3,      # 恢复事件阈值
        }
        
        # 合并用户配置
        for key, value in default_config.items():
            if key not in self.config:
                self.config[key] = value
        
        # 加载CBT理论框架
        self.cbt_framework = self._load_cbt_framework()
        
        self.is_initialized = True
        self.logger.info("CAD增强模型初始化完成")
    
    def _load_cbt_framework(self) -> Dict[str, List[str]]:
        """加载CBT认知行为理论框架"""
        return {
            "self_belief_triggers": [
                "批评", "失败", "考试", "成绩", "不及格", "差劲", "能力", "表现", "竞争"
            ],
            "world_belief_triggers": [
                "霸凌", "孤立", "拒绝", "嘲笑", "排斥", "冷漠", "不公", "欺骗", "背叛"
            ],
            "future_belief_triggers": [
                "前途", "未来", "希望", "绝望", "放弃", "机会", "目标", "梦想", "计划"
            ],
            "social_triggers": [
                "朋友", "同学", "聚会", "活动", "合作", "团队", "交往", "关系", "沟通"
            ],
            "academic_triggers": [
                "学习", "作业", "考试", "成绩", "老师", "课程", "知识", "理解", "记忆"
            ]
        }
    
    def supports_cad_state(self) -> bool:
        """CAD增强模型支持CAD状态"""
        return True
    
    def supports_async_processing(self) -> bool:
        """CAD增强模型不需要异步处理"""
        return False
    
    async def calculate_impact(self, 
                             event: LifeEvent, 
                             current_state: PsychologicalState,
                             context: Dict[str, Any] = None) -> ModelImpactResult:
        """
        使用CAD理论计算事件影响
        
        Args:
            event: 生活事件
            current_state: 当前心理状态
            context: 上下文信息
            
        Returns:
            ModelImpactResult: 影响计算结果
        """
        start_time = time.time()
        
        try:
            result = ModelImpactResult()
            result.model_type = self.model_type.value
            
            # 分析事件类型和触发器
            event_analysis = self._analyze_event_triggers(event)
            
            # 计算情感基调影响
            affective_impact = self._calculate_affective_tone_impact(event, current_state)
            result.affective_tone_change = affective_impact
            
            # 计算核心信念影响
            belief_impacts = self._calculate_core_belief_impacts(
                event, current_state, event_analysis
            )
            result.self_belief_change = belief_impacts["self_belief"]
            result.world_belief_change = belief_impacts["world_belief"]
            result.future_belief_change = belief_impacts["future_belief"]
            
            # 计算认知加工影响
            cognitive_impacts = self._calculate_cognitive_processing_impacts(
                event, current_state, belief_impacts
            )
            result.rumination_change = cognitive_impacts["rumination"]
            result.distortion_change = cognitive_impacts["distortion"]
            
            # 计算行为倾向影响
            behavioral_impacts = self._calculate_behavioral_impacts(
                event, current_state, belief_impacts
            )
            result.social_withdrawal_change = behavioral_impacts["social_withdrawal"]
            result.avolition_change = behavioral_impacts["avolition"]
            
            # 基于CAD状态计算基础心理指标
            basic_impacts = self._calculate_basic_psychological_impacts(
                result, current_state
            )
            result.depression_change = basic_impacts["depression"]
            result.anxiety_change = basic_impacts["anxiety"]
            result.stress_change = basic_impacts["stress"]
            result.self_esteem_change = basic_impacts["self_esteem"]
            result.social_connection_change = basic_impacts["social_connection"]
            
            # 应用情感放大效应
            result = self._apply_affective_amplification(result, current_state)
            
            # 生成推理说明
            result.reasoning = self._generate_cad_reasoning(event, result, event_analysis)
            result.confidence = 0.85  # CAD模型置信度较高
            
            # 记录处理时间
            processing_time = (time.time() - start_time) * 1000
            result.processing_time = processing_time
            self._record_calculation(processing_time, True)
            
            return result
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self._record_calculation(processing_time, False)
            self.logger.error(f"CAD增强模型计算失败: {e}")
            
            return ModelImpactResult(
                model_type=self.model_type.value,
                confidence=0.1,
                reasoning=f"CAD计算失败，使用默认影响: {e}",
                processing_time=processing_time
            )
    
    def _analyze_event_triggers(self, event: LifeEvent) -> Dict[str, bool]:
        """分析事件触发的心理机制"""
        description = event.description.lower()
        
        return {
            "self_belief_triggered": any(
                trigger in description 
                for trigger in self.cbt_framework["self_belief_triggers"]
            ),
            "world_belief_triggered": any(
                trigger in description 
                for trigger in self.cbt_framework["world_belief_triggers"]
            ),
            "future_belief_triggered": any(
                trigger in description 
                for trigger in self.cbt_framework["future_belief_triggers"]
            ),
            "social_triggered": any(
                trigger in description 
                for trigger in self.cbt_framework["social_triggers"]
            ),
            "academic_triggered": any(
                trigger in description 
                for trigger in self.cbt_framework["academic_triggers"]
            )
        }
    
    def _calculate_affective_tone_impact(self, 
                                       event: LifeEvent, 
                                       current_state: PsychologicalState) -> float:
        """计算情感基调影响"""
        base_impact = event.impact_score
        
        # 情感基调变化比其他维度更缓慢更稳定
        tone_change = base_impact / 15.0
        
        # 当前情感基调的调节作用
        current_tone = current_state.cad_state.affective_tone
        if current_tone < -3 and base_impact < 0:
            # 已经悲观时，负面事件影响减弱（饱和效应）
            tone_change *= 0.7
        elif current_tone > 3 and base_impact > 0:
            # 已经乐观时，正面事件影响减弱
            tone_change *= 0.8
        
        return max(-2.0, min(2.0, tone_change))
    
    def _calculate_core_belief_impacts(self, 
                                     event: LifeEvent, 
                                     current_state: PsychologicalState,
                                     event_analysis: Dict[str, bool]) -> Dict[str, float]:
        """计算核心信念影响"""
        base_impact = event.impact_score
        belief_strength = self.config["belief_impact_strength"]
        
        impacts = {
            "self_belief": 0.0,
            "world_belief": 0.0, 
            "future_belief": 0.0
        }
        
        # 自我信念影响
        if event_analysis["self_belief_triggered"]:
            impacts["self_belief"] = base_impact * belief_strength
            if event_analysis["academic_triggered"]:
                impacts["self_belief"] *= 1.2  # 学业相关事件对自我信念影响更大
        
        # 世界信念影响  
        if event_analysis["world_belief_triggered"]:
            impacts["world_belief"] = base_impact * belief_strength * 1.1
            if event_analysis["social_triggered"]:
                impacts["world_belief"] *= 1.3  # 社交事件对世界观影响更大
        
        # 未来信念影响
        if event_analysis["future_belief_triggered"]:
            impacts["future_belief"] = base_impact * belief_strength * 0.8
        
        # 信念间的相互影响
        interaction_rate = self.config["belief_interaction_rate"]
        current_beliefs = current_state.cad_state.core_beliefs
        
        # 未来信念受自我和世界信念平均影响
        belief_average = (current_beliefs.self_belief + current_beliefs.world_belief) / 2.0
        impacts["future_belief"] += (belief_average * interaction_rate * 0.1)
        
        # 应用积极事件偏差削减
        if base_impact > 0:
            for key in impacts:
                impacts[key] *= self.config["positive_bias_reduction"]
        
        # 限制影响范围
        for key in impacts:
            impacts[key] = max(-2.0, min(2.0, impacts[key]))
        
        return impacts
    
    def _calculate_cognitive_processing_impacts(self, 
                                              event: LifeEvent,
                                              current_state: PsychologicalState,
                                              belief_impacts: Dict[str, float]) -> Dict[str, float]:
        """计算认知加工影响"""
        impacts = {
            "rumination": 0.0,
            "distortion": 0.0
        }
        
        current_cad = current_state.cad_state
        
        # 思维反刍：自我信念越负面，越容易反刍
        if current_cad.core_beliefs.self_belief < -2:
            rumination_increase = (-current_cad.core_beliefs.self_belief - 2) / 4.0
            impacts["rumination"] = rumination_increase
        
        # 负面事件直接增加思维反刍
        if event.impact_score < self.config["mild_event_threshold"]:
            impacts["rumination"] += abs(event.impact_score) * 0.2
        
        # 认知扭曲：思维反刍会增加认知扭曲
        current_rumination = current_cad.cognitive_processing.rumination
        if current_rumination > self.config["rumination_threshold"]:
            distortion_increase = (current_rumination - self.config["rumination_threshold"]) / 10.0
            impacts["distortion"] = distortion_increase * self.config["cognitive_distortion_rate"]
        
        # 负面信念变化也会增加认知扭曲
        total_belief_decline = sum(min(0, impact) for impact in belief_impacts.values())
        if total_belief_decline < -1:
            impacts["distortion"] += abs(total_belief_decline) * 0.1
        
        # 限制影响范围
        for key in impacts:
            impacts[key] = max(0, min(2.0, impacts[key]))
        
        return impacts
    
    def _calculate_behavioral_impacts(self, 
                                    event: LifeEvent,
                                    current_state: PsychologicalState,
                                    belief_impacts: Dict[str, float]) -> Dict[str, float]:
        """计算行为倾向影响"""
        impacts = {
            "social_withdrawal": 0.0,
            "avolition": 0.0
        }
        
        current_cad = current_state.cad_state
        
        # 社交退缩：世界信念负面时增加
        if current_cad.core_beliefs.world_belief < self.config["social_withdrawal_trigger"]:
            withdrawal_increase = (-current_cad.core_beliefs.world_belief - 2) / 3.0
            impacts["social_withdrawal"] = withdrawal_increase * self.config["behavioral_feedback_rate"]
        
        # 社交相关负面事件直接影响社交退缩
        if event.impact_score < 0 and "社交" in event.description:
            impacts["social_withdrawal"] += abs(event.impact_score) * 0.3
        
        # 动机缺失：多重负面信念时增加
        negative_beliefs = sum(1 for impact in belief_impacts.values() if impact < -0.5)
        if negative_beliefs >= 2:
            impacts["avolition"] += negative_beliefs * 0.2
        
        # 未来信念负面时增加动机缺失
        if current_cad.core_beliefs.future_belief < -3:
            impacts["avolition"] += abs(current_cad.core_beliefs.future_belief + 3) / 5.0
        
        # 限制影响范围
        for key in impacts:
            impacts[key] = max(0, min(2.0, impacts[key]))
        
        return impacts
    
    def _calculate_basic_psychological_impacts(self, 
                                             cad_result: ModelImpactResult,
                                             current_state: PsychologicalState) -> Dict[str, float]:
        """基于CAD状态变化计算基础心理指标影响"""
        impacts = {
            "depression": 0.0,
            "anxiety": 0.0,
            "stress": 0.0,
            "self_esteem": 0.0,
            "social_connection": 0.0
        }
        
        # 抑郁程度：基于多个CAD维度
        depression_factors = [
            cad_result.affective_tone_change * -0.4,  # 情感基调负面增加抑郁
            cad_result.self_belief_change * -0.3,     # 自我信念负面增加抑郁
            cad_result.rumination_change * 0.3,       # 思维反刍增加抑郁
            cad_result.avolition_change * 0.4         # 动机缺失增加抑郁
        ]
        impacts["depression"] = sum(depression_factors)
        
        # 焦虑水平：基于思维反刍和认知扭曲
        impacts["anxiety"] = (cad_result.rumination_change * 0.4 + 
                            cad_result.distortion_change * 0.3)
        
        # 压力水平：基于负面信念变化
        stress_factors = [
            max(0, -cad_result.self_belief_change) * 0.4,
            max(0, -cad_result.world_belief_change) * 0.3,
            cad_result.rumination_change * 0.3
        ]
        impacts["stress"] = sum(stress_factors)
        
        # 自尊水平：主要基于自我信念
        impacts["self_esteem"] = cad_result.self_belief_change * 0.5
        
        # 社交连接：基于社交退缩
        impacts["social_connection"] = -cad_result.social_withdrawal_change * 0.6
        
        return impacts
    
    def _apply_affective_amplification(self, 
                                     result: ModelImpactResult,
                                     current_state: PsychologicalState) -> ModelImpactResult:
        """应用情感放大效应"""
        current_tone = current_state.cad_state.affective_tone
        amplification = self.config["affective_amplification"]
        
        # 当情感基调为负时，负面变化被放大
        if current_tone < -3:
            if result.depression_change > 0:
                result.depression_change *= amplification
            if result.anxiety_change > 0:
                result.anxiety_change *= amplification
            if result.stress_change > 0:
                result.stress_change *= amplification
        
        return result
    
    def _generate_cad_reasoning(self, 
                              event: LifeEvent, 
                              result: ModelImpactResult,
                              event_analysis: Dict[str, bool]) -> str:
        """生成CAD理论推理说明"""
        reasoning_parts = ["CAD增强模型分析:"]
        
        # 事件分类
        triggered_mechanisms = [k.replace("_triggered", "") for k, v in event_analysis.items() if v]
        if triggered_mechanisms:
            reasoning_parts.append(f"触发机制: {', '.join(triggered_mechanisms)}")
        
        # 主要变化
        significant_changes = []
        if abs(result.self_belief_change) > 0.3:
            significant_changes.append(f"自我信念{result.self_belief_change:+.1f}")
        if abs(result.world_belief_change) > 0.3:
            significant_changes.append(f"世界信念{result.world_belief_change:+.1f}")
        if abs(result.rumination_change) > 0.3:
            significant_changes.append(f"思维反刍{result.rumination_change:+.1f}")
        if abs(result.social_withdrawal_change) > 0.3:
            significant_changes.append(f"社交退缩{result.social_withdrawal_change:+.1f}")
        
        if significant_changes:
            reasoning_parts.append(f"显著变化: {', '.join(significant_changes)}")
        
        # 应用的CAD理论
        applied_theories = []
        if abs(result.self_belief_change) > 0.1:
            applied_theories.append("Beck认知三角")
        if result.rumination_change > 0.1:
            applied_theories.append("认知加工理论")
        if result.social_withdrawal_change > 0.1:
            applied_theories.append("行为动力学")
        
        if applied_theories:
            reasoning_parts.append(f"应用理论: {', '.join(applied_theories)}")
        
        return "; ".join(reasoning_parts)
    
    def apply_daily_cad_evolution(self, current_state: PsychologicalState) -> ModelImpactResult:
        """应用每日CAD状态自然演化"""
        result = ModelImpactResult()
        result.model_type = self.model_type.value
        
        decay_rate = self.config["daily_decay_rate"]
        cad = current_state.cad_state
        
        # 自然衰减效应
        result.rumination_change = -cad.cognitive_processing.rumination * decay_rate
        result.distortion_change = -cad.cognitive_processing.distortions * decay_rate * 0.5
        result.social_withdrawal_change = -cad.behavioral_inclination.social_withdrawal * decay_rate * 0.8
        result.avolition_change = -cad.behavioral_inclination.avolition * decay_rate * 0.8
        
        # 情感基调的微弱回归
        if abs(cad.affective_tone) > 0.1:
            result.affective_tone_change = -cad.affective_tone * decay_rate * 0.3
        
        result.reasoning = f"CAD日常演化: 自然衰减率{decay_rate}, 向健康状态微调"
        result.confidence = 0.9
        
        return result


# 注册模型到工厂
from models.psychological_model_base import ModelFactory
ModelFactory.register_model(PsychologicalModelType.CAD_ENHANCED, CADEnhancedModel)