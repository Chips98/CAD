"""
LLM驱动心理模型
完全基于大语言模型进行心理状态评估和影响计算
提供最智能的分析，但需要较长的处理时间
"""

import time
import json
import asyncio
from typing import Dict, List, Any, Optional
from models.psychological_model_base import (
    PsychologicalModelBase, ModelImpactResult, PsychologicalModelType
)
from models.psychology_models import LifeEvent, PsychologicalState, DepressionLevel, EmotionState


class LLMDrivenModel(PsychologicalModelBase):
    """LLM驱动心理模型"""
    
    REQUIRES_AI_CLIENT = True
    
    def __init__(self, model_type: PsychologicalModelType, config: Dict[str, Any] = None, ai_client = None):
        """初始化LLM驱动模型"""
        self.ai_client = ai_client
        super().__init__(model_type, config)
    
    def _initialize_model(self):
        """初始化模型特定组件"""
        if not self.ai_client:
            raise ValueError("LLM驱动模型需要AI客户端")
        
        # 设置默认配置
        default_config = {
            "max_retries": 3,              # 最大重试次数
            "timeout_seconds": 30,         # 超时时间
            "temperature": 0.3,            # LLM温度参数
            "confidence_threshold": 0.6,   # 置信度阈值
            "enable_detailed_analysis": True,  # 启用详细分析
            "enable_risk_assessment": True,    # 启用风险评估
            "context_window_size": 5,      # 上下文窗口大小
        }
        
        # 合并用户配置
        for key, value in default_config.items():
            if key not in self.config:
                self.config[key] = value
        
        # 加载心理学理论提示模板
        self.prompt_templates = self._load_prompt_templates()
        
        self.is_initialized = True
        self.logger.info("LLM驱动模型初始化完成")
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """加载LLM提示模板"""
        return {
            "system_prompt": """你是一位资深的临床心理学家，专精认知行为疗法(CBT)、贝克认知三角理论和抑郁症诊断。
你的任务是基于心理学理论，精确评估生活事件对患者心理状态的影响。

评估原则：
1. 基于循证心理学和CBT理论
2. 考虑个体差异和累积效应
3. 区分短期和长期影响
4. 评估认知、情绪、行为三个层面
5. 注意保护性因素和风险因素

输出要求：
- 所有数值必须在指定范围内
- 提供详细的心理学分析理由
- 识别关键的风险和保护因素
- 给出评估的置信度""",
            
            "assessment_prompt": """
患者基本信息：
- 年龄：{age}岁
- 人格特质：{personality}
- 当前抑郁程度：{depression_level}
- 当前焦虑水平：{anxiety_level}
- 自尊水平：{self_esteem}
- 社交连接：{social_connection}

当前认知-情感状态(CAD)：
- 情感基调：{affective_tone}/10 (负值=悲观)
- 自我信念：{self_belief}/10 (负值=负面自我观)  
- 世界信念：{world_belief}/10 (负值=世界悲观)
- 未来信念：{future_belief}/10 (负值=未来悲观)
- 思维反刍：{rumination}/10
- 认知扭曲：{distortions}/10
- 社交退缩：{social_withdrawal}/10
- 动机缺失：{avolition}/10

最近重要事件：
{recent_events}

当前评估事件：
事件描述：{event_description}
参与者：{participants}
事件影响分数：{impact_score}

请基于CBT理论和贝克认知三角，评估这个事件的心理影响：

输出JSON格式：
{{
  "basic_psychological_impact": {{
    "depression_change": 数值(-3.0到3.0),
    "anxiety_change": 数值(-3.0到3.0),
    "stress_change": 数值(-3.0到3.0),
    "self_esteem_change": 数值(-3.0到3.0),
    "social_connection_change": 数值(-3.0到3.0)
  }},
  "cad_state_impact": {{
    "affective_tone_change": 数值(-2.0到2.0),
    "self_belief_change": 数值(-2.0到2.0),
    "world_belief_change": 数值(-2.0到2.0),
    "future_belief_change": 数值(-2.0到2.0),
    "rumination_change": 数值(-2.0到2.0),
    "distortion_change": 数值(-2.0到2.0),
    "social_withdrawal_change": 数值(-2.0到2.0),
    "avolition_change": 数值(-2.0到2.0)
  }},
  "meta_analysis": {{
    "confidence_level": 数值(0.0到1.0),
    "primary_mechanisms": ["机制1", "机制2"],
    "risk_indicators": ["风险因素1", "风险因素2"],
    "protective_factors": ["保护因素1", "保护因素2"],
    "reasoning": "详细的心理学分析（150-300字）",
    "severity_assessment": "mild|moderate|severe",
    "intervention_recommendations": ["建议1", "建议2"]
  }}
}}

注意：
- 负值表示恶化，正值表示改善
- 考虑累积效应和个体韧性
- 基于循证心理学原理评估
- 重点关注认知模式变化""",
            
            "fallback_prompt": """基于以下信息，简要评估事件的心理影响：
事件：{event_description}
影响分数：{impact_score}
当前状态：{current_state}

请输出简化的JSON评估结果。"""
        }
    
    def supports_cad_state(self) -> bool:
        """LLM驱动模型支持CAD状态"""
        return True
    
    def supports_async_processing(self) -> bool:
        """LLM驱动模型需要异步处理"""
        return True
    
    async def calculate_impact(self, 
                             event: LifeEvent, 
                             current_state: PsychologicalState,
                             context: Dict[str, Any] = None) -> ModelImpactResult:
        """
        使用LLM评估事件影响
        
        Args:
            event: 生活事件
            current_state: 当前心理状态
            context: 上下文信息
            
        Returns:
            ModelImpactResult: 影响计算结果
        """
        start_time = time.time()
        
        try:
            # 构建评估提示
            prompt = self._build_assessment_prompt(event, current_state, context)
            
            # 调用LLM进行评估
            llm_response = await self._call_llm_with_retry(prompt)
            
            # 解析LLM响应
            result = self._parse_llm_response(llm_response, event)
            
            # 设置模型类型和处理时间
            result.model_type = self.model_type.value
            processing_time = (time.time() - start_time) * 1000
            result.processing_time = processing_time
            
            # 记录统计信息
            self._record_calculation(processing_time, True)
            
            return result
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self._record_calculation(processing_time, False)
            self.logger.error(f"LLM驱动模型计算失败: {e}")
            
            # 返回回退结果
            return await self._generate_fallback_result(event, current_state, processing_time, str(e))
    
    def _build_assessment_prompt(self, 
                               event: LifeEvent, 
                               current_state: PsychologicalState,
                               context: Dict[str, Any] = None) -> str:
        """构建LLM评估提示"""
        
        # 获取角色信息
        character_info = context.get("character_info", {}) if context else {}
        age = character_info.get("age", 17)
        personality = character_info.get("personality", {})
        
        # 获取最近事件
        recent_events = context.get("recent_events", []) if context else []
        recent_summary = self._summarize_recent_events(recent_events)
        
        # 获取CAD状态
        cad_state = current_state.cad_state
        
        # 构建完整提示
        prompt = self.prompt_templates["assessment_prompt"].format(
            age=age,
            personality=str(personality),
            depression_level=current_state.depression_level.name,
            anxiety_level=current_state.stress_level,  # 使用stress_level作为焦虑代理
            self_esteem=current_state.self_esteem,
            social_connection=current_state.social_connection,
            affective_tone=cad_state.affective_tone,
            self_belief=cad_state.core_beliefs.self_belief,
            world_belief=cad_state.core_beliefs.world_belief,
            future_belief=cad_state.core_beliefs.future_belief,
            rumination=cad_state.cognitive_processing.rumination,
            distortions=cad_state.cognitive_processing.distortions,
            social_withdrawal=cad_state.behavioral_inclination.social_withdrawal,
            avolition=cad_state.behavioral_inclination.avolition,
            recent_events=recent_summary,
            event_description=event.description,
            participants=", ".join(event.participants),
            impact_score=event.impact_score
        )
        
        return prompt
    
    def _summarize_recent_events(self, recent_events: List[Dict]) -> str:
        """总结最近事件"""
        if not recent_events:
            return "无特殊事件记录"
        
        summaries = []
        for event in recent_events[-self.config["context_window_size"]:]:
            desc = event.get("description", "")
            impact = event.get("impact_score", 0)
            emotion = "正面" if impact > 0 else "负面" if impact < 0 else "中性"
            summaries.append(f"- {desc[:50]}... (影响: {emotion}, 分数: {impact})")
        
        return "\n".join(summaries)
    
    async def _call_llm_with_retry(self, prompt: str) -> str:
        """带重试机制的LLM调用"""
        max_retries = self.config["max_retries"]
        
        for attempt in range(max_retries + 1):
            try:
                # 设置系统提示
                system_prompt = self.prompt_templates["system_prompt"]
                
                # 调用AI客户端
                response = await self.ai_client.generate_response(
                    prompt, 
                    system_prompt=system_prompt,
                    temperature=self.config["temperature"]
                )
                
                if response and response.strip():
                    return response
                else:
                    raise ValueError("LLM返回空响应")
                    
            except Exception as e:
                self.logger.warning(f"LLM调用尝试 {attempt + 1} 失败: {e}")
                
                if attempt < max_retries:
                    # 等待后重试
                    await asyncio.sleep(2 ** attempt)  # 指数退避
                else:
                    raise e
    
    def _parse_llm_response(self, response: str, event: LifeEvent) -> ModelImpactResult:
        """解析LLM响应"""
        try:
            # 清理响应文本
            clean_response = response.strip()
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
            
            # 创建结果对象
            result = ModelImpactResult()
            
            # 解析基础心理影响
            basic_impact = data.get("basic_psychological_impact", {})
            result.depression_change = self._clamp_value(basic_impact.get("depression_change", 0), -3.0, 3.0)
            result.anxiety_change = self._clamp_value(basic_impact.get("anxiety_change", 0), -3.0, 3.0)
            result.stress_change = self._clamp_value(basic_impact.get("stress_change", 0), -3.0, 3.0)
            result.self_esteem_change = self._clamp_value(basic_impact.get("self_esteem_change", 0), -3.0, 3.0)
            result.social_connection_change = self._clamp_value(basic_impact.get("social_connection_change", 0), -3.0, 3.0)
            
            # 解析CAD状态影响
            cad_impact = data.get("cad_state_impact", {})
            result.affective_tone_change = self._clamp_value(cad_impact.get("affective_tone_change", 0), -2.0, 2.0)
            result.self_belief_change = self._clamp_value(cad_impact.get("self_belief_change", 0), -2.0, 2.0)
            result.world_belief_change = self._clamp_value(cad_impact.get("world_belief_change", 0), -2.0, 2.0)
            result.future_belief_change = self._clamp_value(cad_impact.get("future_belief_change", 0), -2.0, 2.0)
            result.rumination_change = self._clamp_value(cad_impact.get("rumination_change", 0), -2.0, 2.0)
            result.distortion_change = self._clamp_value(cad_impact.get("distortion_change", 0), -2.0, 2.0)
            result.social_withdrawal_change = self._clamp_value(cad_impact.get("social_withdrawal_change", 0), -2.0, 2.0)
            result.avolition_change = self._clamp_value(cad_impact.get("avolition_change", 0), -2.0, 2.0)
            
            # 解析元分析
            meta_analysis = data.get("meta_analysis", {})
            result.confidence = self._clamp_value(meta_analysis.get("confidence_level", 0.5), 0.0, 1.0)
            result.reasoning = meta_analysis.get("reasoning", "LLM分析")
            
            # 检查置信度阈值
            if result.confidence < self.config["confidence_threshold"]:
                self.logger.warning(f"LLM评估置信度过低: {result.confidence}")
                # 可以选择返回降级结果或继续使用
            
            self.logger.debug(f"LLM评估成功解析，置信度: {result.confidence:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"解析LLM响应失败: {e}\n响应内容: {response[:200]}...")
            raise ValueError(f"LLM响应解析失败: {e}")
    
    def _clamp_value(self, value: Any, min_val: float, max_val: float) -> float:
        """限制数值在指定范围内"""
        try:
            return max(min_val, min(max_val, float(value)))
        except (ValueError, TypeError):
            return 0.0
    
    async def _generate_fallback_result(self, 
                                      event: LifeEvent, 
                                      current_state: PsychologicalState,
                                      processing_time: float,
                                      error_msg: str) -> ModelImpactResult:
        """生成回退结果"""
        try:
            # 尝试使用简化提示
            fallback_prompt = self.prompt_templates["fallback_prompt"].format(
                event_description=event.description,
                impact_score=event.impact_score,
                current_state=current_state.depression_level.name
            )
            
            response = await self.ai_client.generate_response(fallback_prompt)
            result = self._parse_simple_response(response)
            
        except Exception:
            # 完全回退到规则
            result = self._rule_based_fallback(event)
        
        result.model_type = self.model_type.value + "_fallback"
        result.confidence = 0.3
        result.reasoning = f"LLM主要评估失败({error_msg})，使用回退方案"
        result.processing_time = processing_time
        
        return result
    
    def _parse_simple_response(self, response: str) -> ModelImpactResult:
        """解析简化响应"""
        # 这里可以实现简化的解析逻辑
        # 暂时返回基础结果
        return ModelImpactResult()
    
    def _rule_based_fallback(self, event: LifeEvent) -> ModelImpactResult:
        """基于规则的回退方案"""
        result = ModelImpactResult()
        
        # 简单的规则映射
        impact = event.impact_score
        
        if impact < -3:
            result.depression_change = 0.8
            result.anxiety_change = 0.6
            result.stress_change = 1.0
            result.self_esteem_change = -0.7
        elif impact < 0:
            result.depression_change = 0.3
            result.anxiety_change = 0.2
            result.stress_change = 0.4
            result.self_esteem_change = -0.2
        elif impact > 3:
            result.depression_change = -0.4
            result.stress_change = -0.5
            result.self_esteem_change = 0.6
        
        return result


# 注册模型到工厂
from models.psychological_model_base import ModelFactory
ModelFactory.register_model(PsychologicalModelType.LLM_DRIVEN, LLMDrivenModel)