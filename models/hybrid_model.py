"""
混合心理模型
结合基础规则、CAD理论和LLM评估的混合方案
平衡准确性与效率，提供最佳的综合评估
"""

import time
import asyncio
from typing import Dict, List, Any, Optional
from models.psychological_model_base import (
    PsychologicalModelBase, ModelImpactResult, PsychologicalModelType, ModelFactory
)
from models.psychology_models import LifeEvent, PsychologicalState, DepressionLevel, EmotionState


class HybridModel(PsychologicalModelBase):
    """混合心理模型"""
    
    REQUIRES_AI_CLIENT = True
    
    def __init__(self, model_type: PsychologicalModelType, config: Dict[str, Any] = None, ai_client = None):
        """初始化混合模型"""
        self.ai_client = ai_client
        super().__init__(model_type, config)
    
    def _initialize_model(self):
        """初始化模型特定组件"""
        # 设置默认配置
        default_config = {
            # 模型权重配置
            "basic_rules_weight": 0.3,      # 基础规则权重
            "cad_weight": 0.4,              # CAD理论权重
            "llm_weight": 0.3,              # LLM评估权重
            
            # LLM使用策略
            "llm_trigger_threshold": 3,     # 触发LLM的事件重要性阈值
            "llm_frequency": 0.5,           # LLM使用频率 (0-1)
            "llm_timeout": 15,              # LLM超时时间（秒）
            
            # 一致性检查
            "consistency_threshold": 2.0,   # 模型间一致性阈值
            "enable_cross_validation": True, # 启用交叉验证
            
            # 自适应权重
            "enable_adaptive_weights": True, # 启用自适应权重调整
            "weight_adjustment_rate": 0.05,  # 权重调整速率
            
            # 性能优化
            "enable_parallel_processing": True, # 启用并行处理
            "cache_llm_results": True,      # 缓存LLM结果
        }
        
        # 合并用户配置
        for key, value in default_config.items():
            if key not in self.config:
                self.config[key] = value
        
        # 初始化子模型
        self._initialize_sub_models()
        
        # 权重历史记录（用于自适应调整）
        self.weight_history = []
        self.performance_metrics = {
            "basic_rules_accuracy": 0.7,
            "cad_accuracy": 0.85,
            "llm_accuracy": 0.9
        }
        
        self.is_initialized = True
        self.logger.info("混合心理模型初始化完成")
    
    def _initialize_sub_models(self):
        """初始化子模型"""
        try:
            # 初始化基础规则模型
            self.basic_rules_model = ModelFactory.create_model(
                PsychologicalModelType.BASIC_RULES, 
                self.config
            )
            
            # 初始化CAD增强模型
            self.cad_model = ModelFactory.create_model(
                PsychologicalModelType.CAD_ENHANCED, 
                self.config
            )
            
            # 初始化LLM驱动模型
            if self.ai_client:
                self.llm_model = ModelFactory.create_model(
                    PsychologicalModelType.LLM_DRIVEN, 
                    self.config, 
                    self.ai_client
                )
            else:
                self.llm_model = None
                self.logger.warning("未提供AI客户端，LLM模型不可用")
            
        except Exception as e:
            self.logger.error(f"初始化子模型失败: {e}")
            raise e
    
    def supports_cad_state(self) -> bool:
        """混合模型支持CAD状态"""
        return True
    
    def supports_async_processing(self) -> bool:
        """混合模型支持异步处理"""
        return True
    
    async def calculate_impact(self, 
                             event: LifeEvent, 
                             current_state: PsychologicalState,
                             context: Dict[str, Any] = None) -> ModelImpactResult:
        """
        使用混合方法计算事件影响
        
        Args:
            event: 生活事件
            current_state: 当前心理状态
            context: 上下文信息
            
        Returns:
            ModelImpactResult: 混合影响计算结果
        """
        start_time = time.time()
        
        try:
            # 决定是否使用LLM
            use_llm = self._should_use_llm(event, current_state)
            
            # 并行或串行计算各模型结果
            if self.config["enable_parallel_processing"] and use_llm:
                results = await self._calculate_parallel(event, current_state, context, use_llm)
            else:
                results = await self._calculate_sequential(event, current_state, context, use_llm)
            
            # 融合结果
            hybrid_result = self._fusion_results(results, event)
            
            # 一致性检查
            if self.config["enable_cross_validation"]:
                self._validate_consistency(results)
            
            # 自适应权重调整
            if self.config["enable_adaptive_weights"]:
                self._adaptive_weight_adjustment(results, hybrid_result)
            
            # 设置元信息
            hybrid_result.model_type = self.model_type.value
            processing_time = (time.time() - start_time) * 1000
            hybrid_result.processing_time = processing_time
            
            # 生成混合推理
            hybrid_result.reasoning = self._generate_hybrid_reasoning(results, use_llm)
            
            # 记录统计信息
            self._record_calculation(processing_time, True)
            
            return hybrid_result
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self._record_calculation(processing_time, False)
            self.logger.error(f"混合模型计算失败: {e}")
            
            # 回退到CAD模型
            return await self._fallback_to_cad(event, current_state, context, processing_time, str(e))
    
    def _should_use_llm(self, event: LifeEvent, current_state: PsychologicalState) -> bool:
        """决定是否使用LLM"""
        if not self.llm_model:
            return False
        
        # 基于事件重要性
        if abs(event.impact_score) >= self.config["llm_trigger_threshold"]:
            return True
        
        # 基于当前状态严重程度
        if current_state.depression_level.value >= 3:
            return True
        
        # 基于随机频率
        import random
        if random.random() < self.config["llm_frequency"]:
            return True
        
        return False
    
    async def _calculate_parallel(self, 
                                event: LifeEvent, 
                                current_state: PsychologicalState,
                                context: Dict[str, Any],
                                use_llm: bool) -> Dict[str, ModelImpactResult]:
        """并行计算各模型结果"""
        tasks = []
        
        # 基础规则模型（同步）
        tasks.append(asyncio.create_task(
            self.basic_rules_model.calculate_impact(event, current_state, context)
        ))
        
        # CAD增强模型（同步）
        tasks.append(asyncio.create_task(
            self.cad_model.calculate_impact(event, current_state, context)
        ))
        
        # LLM模型（异步）
        if use_llm:
            tasks.append(asyncio.create_task(
                asyncio.wait_for(
                    self.llm_model.calculate_impact(event, current_state, context),
                    timeout=self.config["llm_timeout"]
                )
            ))
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        result_dict = {
            "basic_rules": results[0] if not isinstance(results[0], Exception) else None,
            "cad": results[1] if not isinstance(results[1], Exception) else None,
            "llm": results[2] if use_llm and len(results) > 2 and not isinstance(results[2], Exception) else None
        }
        
        # 记录失败的模型
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                model_name = ["basic_rules", "cad", "llm"][i] if i < 3 else "unknown"
                self.logger.warning(f"{model_name}模型计算失败: {result}")
        
        return result_dict
    
    async def _calculate_sequential(self, 
                                  event: LifeEvent, 
                                  current_state: PsychologicalState,
                                  context: Dict[str, Any],
                                  use_llm: bool) -> Dict[str, ModelImpactResult]:
        """串行计算各模型结果"""
        results = {}
        
        # 基础规则模型
        try:
            results["basic_rules"] = await self.basic_rules_model.calculate_impact(
                event, current_state, context
            )
        except Exception as e:
            self.logger.warning(f"基础规则模型失败: {e}")
            results["basic_rules"] = None
        
        # CAD增强模型
        try:
            results["cad"] = await self.cad_model.calculate_impact(
                event, current_state, context
            )
        except Exception as e:
            self.logger.warning(f"CAD模型失败: {e}")
            results["cad"] = None
        
        # LLM模型
        if use_llm:
            try:
                results["llm"] = await asyncio.wait_for(
                    self.llm_model.calculate_impact(event, current_state, context),
                    timeout=self.config["llm_timeout"]
                )
            except Exception as e:
                self.logger.warning(f"LLM模型失败: {e}")
                results["llm"] = None
        else:
            results["llm"] = None
        
        return results
    
    def _fusion_results(self, 
                       results: Dict[str, ModelImpactResult], 
                       event: LifeEvent) -> ModelImpactResult:
        """融合各模型结果"""
        
        # 获取当前权重
        weights = self._get_current_weights(results)
        
        # 初始化融合结果
        fusion_result = ModelImpactResult()
        
        # 可用结果列表
        available_results = {k: v for k, v in results.items() if v is not None}
        
        if not available_results:
            raise ValueError("所有子模型都失败了")
        
        # 重新归一化权重
        total_weight = sum(weights[k] for k in available_results.keys())
        normalized_weights = {k: weights[k] / total_weight for k in available_results.keys()}
        
        # 融合基础心理指标
        fusion_result.depression_change = sum(
            result.depression_change * normalized_weights[model_name]
            for model_name, result in available_results.items()
        )
        fusion_result.anxiety_change = sum(
            result.anxiety_change * normalized_weights[model_name]
            for model_name, result in available_results.items()
        )
        fusion_result.stress_change = sum(
            result.stress_change * normalized_weights[model_name]
            for model_name, result in available_results.items()
        )
        fusion_result.self_esteem_change = sum(
            result.self_esteem_change * normalized_weights[model_name]
            for model_name, result in available_results.items()
        )
        fusion_result.social_connection_change = sum(
            result.social_connection_change * normalized_weights[model_name]
            for model_name, result in available_results.items()
        )
        
        # 融合CAD状态（优先使用支持CAD的模型）
        cad_supporting_models = {
            k: v for k, v in available_results.items() 
            if k in ["cad", "llm"]  # 只有CAD和LLM模型支持CAD状态
        }
        
        if cad_supporting_models:
            cad_total_weight = sum(normalized_weights[k] for k in cad_supporting_models.keys())
            cad_weights = {k: normalized_weights[k] / cad_total_weight for k in cad_supporting_models.keys()}
            
            fusion_result.affective_tone_change = sum(
                result.affective_tone_change * cad_weights[model_name]
                for model_name, result in cad_supporting_models.items()
            )
            fusion_result.self_belief_change = sum(
                result.self_belief_change * cad_weights[model_name]
                for model_name, result in cad_supporting_models.items()
            )
            fusion_result.world_belief_change = sum(
                result.world_belief_change * cad_weights[model_name]
                for model_name, result in cad_supporting_models.items()
            )
            fusion_result.future_belief_change = sum(
                result.future_belief_change * cad_weights[model_name]
                for model_name, result in cad_supporting_models.items()
            )
            fusion_result.rumination_change = sum(
                result.rumination_change * cad_weights[model_name]
                for model_name, result in cad_supporting_models.items()
            )
            fusion_result.distortion_change = sum(
                result.distortion_change * cad_weights[model_name]
                for model_name, result in cad_supporting_models.items()
            )
            fusion_result.social_withdrawal_change = sum(
                result.social_withdrawal_change * cad_weights[model_name]
                for model_name, result in cad_supporting_models.items()
            )
            fusion_result.avolition_change = sum(
                result.avolition_change * cad_weights[model_name]
                for model_name, result in cad_supporting_models.items()
            )
        
        # 计算融合置信度
        fusion_result.confidence = sum(
            result.confidence * normalized_weights[model_name]
            for model_name, result in available_results.items()
        )
        
        return fusion_result
    
    def _get_current_weights(self, results: Dict[str, ModelImpactResult]) -> Dict[str, float]:
        """获取当前权重"""
        base_weights = {
            "basic_rules": self.config["basic_rules_weight"],
            "cad": self.config["cad_weight"],
            "llm": self.config["llm_weight"]
        }
        
        # 如果启用自适应权重，基于性能调整
        if self.config["enable_adaptive_weights"]:
            base_weights["basic_rules"] *= self.performance_metrics["basic_rules_accuracy"]
            base_weights["cad"] *= self.performance_metrics["cad_accuracy"]
            base_weights["llm"] *= self.performance_metrics["llm_accuracy"]
        
        return base_weights
    
    def _validate_consistency(self, results: Dict[str, ModelImpactResult]):
        """验证模型间一致性"""
        available_results = [v for v in results.values() if v is not None]
        
        if len(available_results) < 2:
            return  # 无法进行一致性检查
        
        # 检查抑郁程度变化的一致性
        depression_changes = [r.depression_change for r in available_results]
        max_diff = max(depression_changes) - min(depression_changes)
        
        if max_diff > self.config["consistency_threshold"]:
            self.logger.warning(f"模型间抑郁变化差异较大: {max_diff:.2f}")
    
    def _adaptive_weight_adjustment(self, 
                                  results: Dict[str, ModelImpactResult],
                                  fusion_result: ModelImpactResult):
        """自适应权重调整"""
        # 这里可以实现基于结果质量的权重调整逻辑
        # 暂时保持简单实现
        pass
    
    def _generate_hybrid_reasoning(self, 
                                 results: Dict[str, ModelImpactResult],
                                 used_llm: bool) -> str:
        """生成混合推理说明"""
        reasoning_parts = ["混合模型分析:"]
        
        # 统计可用模型
        available_models = [k for k, v in results.items() if v is not None]
        reasoning_parts.append(f"使用模型: {', '.join(available_models)}")
        
        # 权重信息
        weights = self._get_current_weights(results)
        weight_info = ", ".join([f"{k}:{v:.1f}" for k, v in weights.items() if k in available_models])
        reasoning_parts.append(f"融合权重: {weight_info}")
        
        # LLM使用状态
        if used_llm and results.get("llm"):
            reasoning_parts.append("包含LLM深度分析")
        elif used_llm:
            reasoning_parts.append("LLM分析失败，使用规则+CAD")
        else:
            reasoning_parts.append("基于规则+CAD快速分析")
        
        # 一致性信息
        if len(available_models) > 1:
            reasoning_parts.append("已进行模型间一致性验证")
        
        return "; ".join(reasoning_parts)
    
    async def _fallback_to_cad(self, 
                             event: LifeEvent, 
                             current_state: PsychologicalState,
                             context: Dict[str, Any],
                             processing_time: float,
                             error_msg: str) -> ModelImpactResult:
        """回退到CAD模型"""
        try:
            result = await self.cad_model.calculate_impact(event, current_state, context)
            result.model_type = self.model_type.value + "_cad_fallback"
            result.confidence *= 0.8  # 降低置信度
            result.reasoning = f"混合模型失败({error_msg})，回退到CAD模型: " + result.reasoning
            result.processing_time = processing_time
            return result
        except Exception as e:
            # 最后回退到基础规则
            self.logger.error(f"CAD回退也失败: {e}")
            result = await self.basic_rules_model.calculate_impact(event, current_state, context)
            result.model_type = self.model_type.value + "_basic_fallback"
            result.confidence = 0.3
            result.reasoning = f"混合模型和CAD都失败，使用基础规则"
            result.processing_time = processing_time
            return result


# 注册模型到工厂
ModelFactory.register_model(PsychologicalModelType.HYBRID, HybridModel)