"""
混合影响计算器 - 融合规则系统与LLM语义理解
实现双向心理状态影响机制和概率性调整
"""

import numpy as np
import random
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from models.psychology_models import LifeEvent, PsychologicalState, CognitiveAffectiveState
from core.llm_psychological_assessor import LLMPsychologicalAssessor, LLMPsychologicalImpact


class HybridImpactCalculator:
    """混合影响计算器 - 规则+LLM+概率性+非线性"""
    
    def __init__(self, ai_client, config: Dict = None):
        self.ai_client = ai_client
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 初始化LLM评估器
        self.llm_assessor = LLMPsychologicalAssessor(ai_client)
        
        # 影响计算配置
        self.rule_weight = self.config.get("rule_weight", 0.6)  # 规则权重
        self.llm_weight = self.config.get("llm_weight", 0.4)    # LLM权重
        self.probability_variance = self.config.get("probability_variance", 0.3)
        self.enable_nonlinear = self.config.get("enable_nonlinear", True)
        self.enable_bidirectional = self.config.get("enable_bidirectional", True)
        
        # 双向影响配置
        self.negativity_bias = 1.3      # 负性偏差：负面事件权重更高
        self.positivity_reduction = 0.8  # 正面事件权重较低
        self.resilience_factor = 0.3    # 心理弹性影响恢复能力
        
        # 非线性函数参数
        self.threshold_value = 3.0      # 阈值效应参数
        self.saturation_steepness = 5.0 # 饱和效应参数
        self.cumulative_decay = 0.9     # 累积效应衰减
        
        # 计算历史
        self.calculation_history = []
        
        self.logger.info("混合影响计算器初始化完成")
    
    async def calculate_comprehensive_impact(self, 
                                           event: LifeEvent,
                                           current_state: PsychologicalState,
                                           context: Dict = None) -> Dict:
        """计算事件的综合心理影响"""
        
        try:
            # 1. 规则基础计算
            rule_impact = self._calculate_rule_based_impact(event, current_state)
            
            # 2. LLM语义评估
            llm_assessment = await self.llm_assessor.assess_event_impact(
                event, current_state, context)
            
            # 3. 混合权重融合
            hybrid_impact = self._calculate_hybrid_fusion(rule_impact, llm_assessment)
            
            # 4. 双向影响调整
            if self.enable_bidirectional:
                hybrid_impact = self._apply_bidirectional_adjustment(
                    hybrid_impact, current_state, event)
            
            # 5. 概率性调整
            probabilistic_impact = self._apply_probabilistic_adjustment(hybrid_impact)
            
            # 6. 非线性变换
            if self.enable_nonlinear:
                final_impact = self._apply_nonlinear_transformation(
                    probabilistic_impact, current_state)
            else:
                final_impact = probabilistic_impact
            
            # 7. 记录计算过程
            calculation_record = {
                "timestamp": datetime.now(),
                "event": event.to_dict(),
                "rule_impact": rule_impact,
                "llm_assessment": llm_assessment.to_dict(),
                "hybrid_impact": hybrid_impact,
                "probabilistic_impact": probabilistic_impact,
                "final_impact": final_impact,
                "context": context or {}
            }
            
            self.calculation_history.append(calculation_record)
            self._maintain_history_size()
            
            self.logger.debug(f"综合影响计算完成: {final_impact['total_impact']:.2f}")
            
            return final_impact
            
        except Exception as e:
            self.logger.error(f"综合影响计算失败: {e}")
            return self._fallback_impact_calculation(event, current_state)
    
    def _calculate_rule_based_impact(self, event: LifeEvent, 
                                   current_state: PsychologicalState) -> Dict:
        """基于规则的影响计算（原有逻辑的增强版）"""
        
        base_impact = event.impact_score
        
        # 基础心理状态影响
        depression_impact = base_impact * 0.5  # 对抑郁的影响
        anxiety_impact = base_impact * 0.4     # 对焦虑的影响
        self_esteem_impact = base_impact * 0.6 # 对自尊的影响
        
        # 根据当前状态调整影响强度
        stress_modifier = 1.0
        if current_state.stress_level > 7:
            stress_modifier = 1.5 if base_impact < 0 else 0.7
        elif current_state.stress_level < 3:
            stress_modifier = 0.7 if base_impact < 0 else 1.2
        
        # CAD状态影响（基于事件描述关键词）
        cad_impact = self._calculate_rule_based_cad_impact(event, current_state)
        
        return {
            "total_impact": base_impact * stress_modifier,
            "depression_impact": depression_impact * stress_modifier,
            "anxiety_impact": anxiety_impact * stress_modifier,
            "self_esteem_impact": self_esteem_impact * stress_modifier,
            "cad_impact": cad_impact,
            "stress_modifier": stress_modifier,
            "calculation_method": "rule_based"
        }
    
    def _calculate_rule_based_cad_impact(self, event: LifeEvent, 
                                       current_state: PsychologicalState) -> Dict:
        """基于规则的CAD状态影响计算"""
        
        event_desc = event.description.lower()
        impact = event.impact_score
        
        # 自我信念影响关键词
        self_keywords = ["批评", "失败", "成绩", "表现", "能力", "聪明", "笨", "优秀"]
        self_belief_impact = 0.0
        if any(keyword in event_desc for keyword in self_keywords):
            self_belief_impact = impact * 0.4
        
        # 世界信念影响关键词
        world_keywords = ["霸凌", "孤立", "拒绝", "友善", "帮助", "支持", "关心"]
        world_belief_impact = 0.0
        if any(keyword in event_desc for keyword in world_keywords):
            world_belief_impact = impact * 0.3
        
        # 未来信念影响关键词
        future_keywords = ["希望", "绝望", "未来", "梦想", "目标", "机会", "可能"]
        future_belief_impact = 0.0
        if any(keyword in event_desc for keyword in future_keywords):
            future_belief_impact = impact * 0.2
        
        # 认知加工影响
        rumination_impact = max(0, -impact * 0.3) if impact < 0 else 0
        distortion_impact = max(0, -impact * 0.2) if impact < 0 else 0
        
        # 行为倾向影响
        withdrawal_impact = max(0, -impact * 0.25) if impact < 0 else 0
        avolition_impact = max(0, -impact * 0.3) if impact < 0 else 0
        
        return {
            "self_belief_impact": self_belief_impact,
            "world_belief_impact": world_belief_impact,
            "future_belief_impact": future_belief_impact,
            "rumination_impact": rumination_impact,
            "distortion_impact": distortion_impact,
            "withdrawal_impact": withdrawal_impact,
            "avolition_impact": avolition_impact
        }
    
    def _calculate_hybrid_fusion(self, rule_impact: Dict, 
                               llm_assessment: LLMPsychologicalImpact) -> Dict:
        """混合融合规则和LLM评估结果"""
        
        # 权重融合基础影响
        total_impact = (rule_impact["total_impact"] * self.rule_weight + 
                       llm_assessment.depression_adjustment * self.llm_weight)
        
        # 融合各维度影响
        depression_impact = (rule_impact["depression_impact"] * self.rule_weight +
                           llm_assessment.depression_adjustment * self.llm_weight)
        
        anxiety_impact = (rule_impact["anxiety_impact"] * self.rule_weight +
                        llm_assessment.anxiety_adjustment * self.llm_weight)
        
        self_esteem_impact = (rule_impact["self_esteem_impact"] * self.rule_weight +
                            llm_assessment.self_esteem_adjustment * self.llm_weight)
        
        # CAD状态融合
        rule_cad = rule_impact["cad_impact"]
        hybrid_cad = {
            "self_belief_impact": (rule_cad["self_belief_impact"] * self.rule_weight +
                                 llm_assessment.self_belief_adjustment * self.llm_weight),
            "world_belief_impact": (rule_cad["world_belief_impact"] * self.rule_weight +
                                  llm_assessment.world_belief_adjustment * self.llm_weight),
            "future_belief_impact": (rule_cad["future_belief_impact"] * self.rule_weight +
                                   llm_assessment.future_belief_adjustment * self.llm_weight),
            "rumination_impact": (rule_cad["rumination_impact"] * self.rule_weight +
                                llm_assessment.rumination_adjustment * self.llm_weight),
            "distortion_impact": (rule_cad["distortion_impact"] * self.rule_weight +
                                llm_assessment.distortion_adjustment * self.llm_weight),
            "withdrawal_impact": (rule_cad["withdrawal_impact"] * self.rule_weight +
                                llm_assessment.social_withdrawal_adjustment * self.llm_weight),
            "avolition_impact": (rule_cad["avolition_impact"] * self.rule_weight +
                               llm_assessment.avolition_adjustment * self.llm_weight)
        }
        
        return {
            "total_impact": total_impact,
            "depression_impact": depression_impact,
            "anxiety_impact": anxiety_impact,
            "self_esteem_impact": self_esteem_impact,
            "cad_impact": hybrid_cad,
            "llm_confidence": llm_assessment.confidence_level,
            "calculation_method": "hybrid_fusion",
            "fusion_weights": {"rule": self.rule_weight, "llm": self.llm_weight}
        }
    
    def _apply_bidirectional_adjustment(self, impact: Dict, 
                                      current_state: PsychologicalState,
                                      event: LifeEvent) -> Dict:
        """应用双向影响调整"""
        
        total_impact = impact["total_impact"]
        
        # 负性偏差：负面事件影响更强
        if total_impact < 0:
            adjusted_impact = total_impact * self.negativity_bias
        else:
            adjusted_impact = total_impact * self.positivity_reduction
        
        # 心理弹性调整
        resilience = self._calculate_resilience(current_state)
        if total_impact < 0:  # 负面事件：弹性降低影响
            resilience_adjustment = 1.0 - (resilience * self.resilience_factor)
        else:  # 正面事件：弹性增强影响
            resilience_adjustment = 1.0 + (resilience * self.resilience_factor * 0.5)
        
        final_impact = adjusted_impact * resilience_adjustment
        
        # 更新其他维度的影响
        impact_ratio = final_impact / total_impact if total_impact != 0 else 1.0
        
        return {
            "total_impact": final_impact,
            "depression_impact": impact["depression_impact"] * impact_ratio,
            "anxiety_impact": impact["anxiety_impact"] * impact_ratio,
            "self_esteem_impact": impact["self_esteem_impact"] * impact_ratio,
            "cad_impact": {k: v * impact_ratio for k, v in impact["cad_impact"].items()},
            "llm_confidence": impact.get("llm_confidence", 0.5),
            "bidirectional_adjustment": {
                "negativity_bias": self.negativity_bias if total_impact < 0 else 1.0,
                "positivity_reduction": self.positivity_reduction if total_impact > 0 else 1.0,
                "resilience": resilience,
                "resilience_adjustment": resilience_adjustment
            },
            "calculation_method": "bidirectional_adjusted"
        }
    
    def _calculate_resilience(self, current_state: PsychologicalState) -> float:
        """计算心理弹性"""
        # 基于多个因素计算弹性
        self_esteem_factor = current_state.self_esteem / 10.0
        social_factor = current_state.social_connection / 10.0
        stress_factor = (10 - current_state.stress_level) / 10.0
        
        # CAD状态因素
        cad = current_state.cad_state
        belief_factor = (cad.core_beliefs.self_belief + 10) / 20.0  # 转换为0-1
        
        # 综合弹性分数
        resilience = (self_esteem_factor * 0.3 + 
                     social_factor * 0.3 + 
                     stress_factor * 0.2 + 
                     belief_factor * 0.2)
        
        return max(0.0, min(1.0, resilience))
    
    def _apply_probabilistic_adjustment(self, impact: Dict) -> Dict:
        """应用概率性调整"""
        
        # 为每个影响维度添加随机变异
        variance = self.probability_variance
        
        adjusted_impact = {}
        for key, value in impact.items():
            if isinstance(value, (int, float)):
                # 正态分布变异
                random_factor = np.random.normal(1.0, variance)
                adjusted_value = value * random_factor
                adjusted_impact[key] = adjusted_value
            elif isinstance(value, dict):
                # 递归处理嵌套字典
                adjusted_impact[key] = {
                    k: v * np.random.normal(1.0, variance) if isinstance(v, (int, float)) else v
                    for k, v in value.items()
                }
            else:
                adjusted_impact[key] = value
        
        # 记录概率调整信息
        adjusted_impact["probabilistic_adjustment"] = {
            "variance_applied": variance,
            "method": "normal_distribution"
        }
        adjusted_impact["calculation_method"] = "probabilistic_adjusted"
        
        return adjusted_impact
    
    def _apply_nonlinear_transformation(self, impact: Dict, 
                                      current_state: PsychologicalState) -> Dict:
        """应用非线性变换"""
        
        total_impact = impact["total_impact"]
        
        # 1. 阈值效应
        threshold_impact = self._apply_threshold_effect(total_impact)
        
        # 2. 饱和效应
        saturation_impact = self._apply_saturation_effect(
            threshold_impact, current_state)
        
        # 3. 累积效应
        cumulative_impact = self._apply_cumulative_effect(saturation_impact)
        
        # 计算变换比例
        impact_ratio = cumulative_impact / total_impact if total_impact != 0 else 1.0
        
        # 应用到所有维度
        transformed_impact = {}
        for key, value in impact.items():
            if key == "total_impact":
                transformed_impact[key] = cumulative_impact
            elif isinstance(value, (int, float)):
                transformed_impact[key] = value * impact_ratio
            elif isinstance(value, dict):
                transformed_impact[key] = {
                    k: v * impact_ratio if isinstance(v, (int, float)) else v
                    for k, v in value.items()
                }
            else:
                transformed_impact[key] = value
        
        # 记录非线性变换信息
        transformed_impact["nonlinear_transformation"] = {
            "threshold_effect": threshold_impact / total_impact if total_impact != 0 else 1.0,
            "saturation_effect": saturation_impact / threshold_impact if threshold_impact != 0 else 1.0,
            "cumulative_effect": cumulative_impact / saturation_impact if saturation_impact != 0 else 1.0,
            "final_ratio": impact_ratio
        }
        transformed_impact["calculation_method"] = "nonlinear_transformed"
        
        return transformed_impact
    
    def _apply_threshold_effect(self, impact: float) -> float:
        """应用阈值效应"""
        if abs(impact) < self.threshold_value:
            return impact * 0.3  # 低于阈值时影响减弱
        else:
            return impact * 1.5  # 超过阈值时影响放大
    
    def _apply_saturation_effect(self, impact: float, 
                               current_state: PsychologicalState) -> float:
        """应用饱和效应"""
        # 基于当前状态计算饱和程度
        depression_score = current_state.cad_state.calculate_comprehensive_depression_score()
        saturation_factor = 1 / (1 + np.exp(-self.saturation_steepness * 
                                           (0.5 - depression_score / 27)))
        
        return impact * saturation_factor
    
    def _apply_cumulative_effect(self, impact: float) -> float:
        """应用累积效应"""
        # 基于最近事件的累积影响
        if len(self.calculation_history) < 2:
            return impact
        
        recent_impacts = [record["final_impact"]["total_impact"] 
                         for record in self.calculation_history[-5:]]
        
        # 计算累积动量
        cumulative_momentum = sum(recent_impacts) * self.cumulative_decay
        
        # 同向累积增强，异向累积减弱
        if (impact > 0 and cumulative_momentum > 0) or (impact < 0 and cumulative_momentum < 0):
            return impact * (1 + abs(cumulative_momentum) * 0.1)
        else:
            return impact * (1 - abs(cumulative_momentum) * 0.05)
    
    def _fallback_impact_calculation(self, event: LifeEvent, 
                                   current_state: PsychologicalState) -> Dict:
        """后备影响计算"""
        base_impact = event.impact_score
        
        return {
            "total_impact": base_impact,
            "depression_impact": base_impact * 0.5,
            "anxiety_impact": base_impact * 0.4,
            "self_esteem_impact": base_impact * 0.6,
            "cad_impact": {
                "self_belief_impact": base_impact * 0.3,
                "world_belief_impact": base_impact * 0.2,
                "future_belief_impact": base_impact * 0.1,
                "rumination_impact": max(0, -base_impact * 0.2),
                "distortion_impact": max(0, -base_impact * 0.1),
                "withdrawal_impact": max(0, -base_impact * 0.2),
                "avolition_impact": max(0, -base_impact * 0.3)
            },
            "calculation_method": "fallback",
            "llm_confidence": 0.0
        }
    
    def _maintain_history_size(self, max_size: int = 100):
        """维护历史记录大小"""
        if len(self.calculation_history) > max_size:
            self.calculation_history = self.calculation_history[-max_size:]
    
    def get_calculation_statistics(self) -> Dict:
        """获取计算统计信息"""
        if not self.calculation_history:
            return {"total_calculations": 0}
        
        total_calculations = len(self.calculation_history)
        
        # 计算方法分布
        methods = [record.get("final_impact", {}).get("calculation_method", "unknown")
                  for record in self.calculation_history]
        method_distribution = {method: methods.count(method) for method in set(methods)}
        
        # 平均LLM置信度
        confidences = [record.get("final_impact", {}).get("llm_confidence", 0.0)
                      for record in self.calculation_history]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # 影响强度分布
        impacts = [record.get("final_impact", {}).get("total_impact", 0.0)
                  for record in self.calculation_history]
        
        return {
            "total_calculations": total_calculations,
            "method_distribution": method_distribution,
            "average_llm_confidence": round(avg_confidence, 3),
            "impact_statistics": {
                "average": round(sum(impacts) / len(impacts), 3) if impacts else 0.0,
                "min": round(min(impacts), 3) if impacts else 0.0,
                "max": round(max(impacts), 3) if impacts else 0.0
            },
            "configuration": {
                "rule_weight": self.rule_weight,
                "llm_weight": self.llm_weight,
                "probability_variance": self.probability_variance,
                "enable_nonlinear": self.enable_nonlinear,
                "enable_bidirectional": self.enable_bidirectional
            }
        }
    
    def update_configuration(self, new_config: Dict):
        """更新配置"""
        self.rule_weight = new_config.get("rule_weight", self.rule_weight)
        self.llm_weight = new_config.get("llm_weight", self.llm_weight)
        self.probability_variance = new_config.get("probability_variance", self.probability_variance)
        self.enable_nonlinear = new_config.get("enable_nonlinear", self.enable_nonlinear)
        self.enable_bidirectional = new_config.get("enable_bidirectional", self.enable_bidirectional)
        
        # 确保权重归一化
        total_weight = self.rule_weight + self.llm_weight
        if total_weight > 0:
            self.rule_weight = self.rule_weight / total_weight
            self.llm_weight = self.llm_weight / total_weight
        
        self.logger.info(f"混合影响计算器配置已更新: rule_weight={self.rule_weight:.2f}, llm_weight={self.llm_weight:.2f}")