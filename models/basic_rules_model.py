"""
基础规则心理模型
基于简单的规则和阈值进行心理状态更新
这是最原始的模型，不使用CAD理论或LLM
"""

import time
from typing import Dict, List, Any, Optional
from models.psychological_model_base import (
    PsychologicalModelBase, ModelImpactResult, PsychologicalModelType
)
from models.psychology_models import LifeEvent, PsychologicalState, DepressionLevel, EmotionState


class BasicRulesModel(PsychologicalModelBase):
    """基础规则心理模型"""
    
    REQUIRES_AI_CLIENT = False
    
    def __init__(self, model_type: PsychologicalModelType, config: Dict[str, Any] = None):
        """初始化基础规则模型"""
        super().__init__(model_type, config)
    
    def _initialize_model(self):
        """初始化模型特定组件"""
        # 设置默认配置
        default_config = {
            "stress_multiplier": 0.5,      # 压力影响倍数
            "self_esteem_multiplier": 0.3, # 自尊影响倍数
            "depression_threshold": 3,      # 抑郁检测阈值
            "recovery_rate": 0.1,          # 自然恢复速率
            "max_impact_per_event": 5.0,   # 单事件最大影响
            "negative_bias": 1.2           # 负面偏差倍数
        }
        
        # 合并用户配置
        for key, value in default_config.items():
            if key not in self.config:
                self.config[key] = value
        
        self.is_initialized = True
        self.logger.info("基础规则模型初始化完成")
    
    def supports_cad_state(self) -> bool:
        """基础规则模型不支持CAD状态"""
        return False
    
    def supports_async_processing(self) -> bool:
        """基础规则模型不需要异步处理"""
        return False
    
    async def calculate_impact(self, 
                             event: LifeEvent, 
                             current_state: PsychologicalState,
                             context: Dict[str, Any] = None) -> ModelImpactResult:
        """
        使用基础规则计算事件影响
        
        Args:
            event: 生活事件
            current_state: 当前心理状态
            context: 上下文信息
            
        Returns:
            ModelImpactResult: 影响计算结果
        """
        start_time = time.time()
        
        try:
            # 获取基础影响分数
            base_impact = event.impact_score
            
            # 应用配置中的倍数和限制
            impact = max(-self.config["max_impact_per_event"], 
                        min(self.config["max_impact_per_event"], base_impact))
            
            # 应用负面偏差 - 负面事件影响更大
            if impact < 0:
                impact *= self.config["negative_bias"]
            
            # 计算各维度的变化
            result = ModelImpactResult()
            result.model_type = self.model_type.value
            
            # 压力水平变化
            if impact < 0:
                result.stress_change = abs(impact) * self.config["stress_multiplier"]
            else:
                result.stress_change = -impact * self.config["stress_multiplier"] * 0.5
            
            # 自尊水平变化
            if impact < 0:
                result.self_esteem_change = impact * self.config["self_esteem_multiplier"]
            else:
                result.self_esteem_change = impact * self.config["self_esteem_multiplier"] * 0.8
            
            # 焦虑水平变化（基于压力）
            result.anxiety_change = result.stress_change * 0.8
            
            # 社交连接变化（基于事件类型）
            if self._is_social_event(event):
                if impact < 0:
                    result.social_connection_change = impact * 0.4
                else:
                    result.social_connection_change = impact * 0.6
            
            # 抑郁程度变化（基于累积负面事件）
            result.depression_change = self._calculate_depression_change(
                event, current_state, context
            )
            
            # 生成推理说明
            result.reasoning = self._generate_reasoning(event, result)
            result.confidence = 0.7  # 基础规则模型置信度中等
            
            # 记录处理时间
            processing_time = (time.time() - start_time) * 1000
            result.processing_time = processing_time
            self._record_calculation(processing_time, True)
            
            return result
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self._record_calculation(processing_time, False)
            self.logger.error(f"基础规则模型计算失败: {e}")
            
            # 返回默认结果
            return ModelImpactResult(
                model_type=self.model_type.value,
                confidence=0.1,
                reasoning=f"计算失败，使用默认影响: {e}",
                processing_time=processing_time
            )
    
    def _is_social_event(self, event: LifeEvent) -> bool:
        """判断是否为社交相关事件"""
        social_keywords = [
            "朋友", "同学", "老师", "父母", "家人", "聊天", "对话", 
            "聚会", "活动", "合作", "冲突", "争吵", "表扬", "批评"
        ]
        
        description = event.description.lower()
        return any(keyword in description for keyword in social_keywords)
    
    def _calculate_depression_change(self, 
                                   event: LifeEvent, 
                                   current_state: PsychologicalState,
                                   context: Dict[str, Any] = None) -> float:
        """计算抑郁程度变化"""
        
        # 获取最近事件历史
        recent_events = []
        if context and "recent_events" in context:
            recent_events = context["recent_events"][-10:]  # 最近10个事件
        
        # 统计负面事件
        negative_events = [e for e in recent_events if e.get("impact_score", 0) < -2]
        negative_count = len(negative_events)
        
        # 当前事件的直接影响
        depression_change = 0.0
        
        if event.impact_score < -3:  # 强负面事件
            depression_change += 0.5
        elif event.impact_score < 0:  # 轻微负面事件
            depression_change += 0.1
        elif event.impact_score > 3:  # 强正面事件
            depression_change -= 0.2
        
        # 累积效应
        if negative_count >= 3:
            depression_change += (negative_count - 2) * 0.1
        
        # 当前状态的影响（状态越差，负面事件影响越大）
        current_depression_level = current_state.depression_level.value
        if current_depression_level > 1 and event.impact_score < 0:
            depression_change *= (1 + current_depression_level * 0.1)
        
        return depression_change
    
    def _generate_reasoning(self, event: LifeEvent, result: ModelImpactResult) -> str:
        """生成推理说明"""
        reasoning_parts = []
        
        # 事件基本信息
        if event.impact_score < -3:
            reasoning_parts.append("强负面事件，显著影响心理状态")
        elif event.impact_score < 0:
            reasoning_parts.append("轻微负面事件，产生一定心理压力")
        elif event.impact_score > 3:
            reasoning_parts.append("积极事件，有助于改善心理状态")
        else:
            reasoning_parts.append("中性事件，影响较为温和")
        
        # 主要变化
        if abs(result.stress_change) > 1:
            reasoning_parts.append(f"压力水平变化显著({result.stress_change:+.1f})")
        
        if abs(result.self_esteem_change) > 0.5:
            reasoning_parts.append(f"自尊水平受到影响({result.self_esteem_change:+.1f})")
        
        if abs(result.depression_change) > 0.3:
            reasoning_parts.append(f"抑郁倾向有所变化({result.depression_change:+.1f})")
        
        # 应用的规则
        applied_rules = []
        if event.impact_score < 0:
            applied_rules.append("负面偏差放大")
        
        if self._is_social_event(event):
            applied_rules.append("社交影响计算")
        
        if applied_rules:
            reasoning_parts.append(f"应用规则: {', '.join(applied_rules)}")
        
        return "基础规则模型: " + "; ".join(reasoning_parts)
    
    def apply_daily_updates(self, current_state: PsychologicalState) -> ModelImpactResult:
        """应用每日自然变化（可选功能）"""
        result = ModelImpactResult()
        result.model_type = self.model_type.value
        
        # 轻微的自然恢复
        recovery_rate = self.config["recovery_rate"]
        
        if current_state.stress_level > 5:
            result.stress_change = -recovery_rate
        
        if current_state.depression_level.value > 1:
            result.depression_change = -recovery_rate * 0.5
        
        result.reasoning = f"每日自然恢复，恢复率: {recovery_rate}"
        result.confidence = 0.8
        
        return result


# 注册模型到工厂
from models.psychological_model_base import ModelFactory
ModelFactory.register_model(PsychologicalModelType.BASIC_RULES, BasicRulesModel)