from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
import asyncio
import json
import logging
from datetime import datetime
import uuid

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from models.psychology_models import PsychologicalState, LifeEvent, Relationship, EmotionState, DepressionLevel, CognitiveAffectiveState

class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, name: str, age: int, personality: Dict[str, Any], 
                 ai_client: Union['GeminiClient', 'DeepSeekClient'],
                 psychological_model = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.age = age
        self.personality = personality
        self.ai_client = ai_client
        self.logger = logging.getLogger(__name__)
        
        # 心理状态初始化
        self.psychological_state = PsychologicalState(
            emotion=EmotionState.NEUTRAL,
            depression_level=DepressionLevel.HEALTHY,
            stress_level=3,
            self_esteem=7,
            social_connection=6,
            academic_pressure=4
        )
        
        # 关系网络
        self.relationships: Dict[str, Relationship] = {}
        
        # 生活事件历史
        self.life_events: List[LifeEvent] = []
        
        # 对话历史
        self.dialogue_history: List[Dict[str, str]] = []
        
        # 思考过程记录
        self.thoughts: List[str] = []
        
        # 彩色控制台
        self.console = Console()
        
        # 心理模型（新增）
        self.psychological_model = psychological_model
        
        # LLM增强组件（为了向后兼容保留）
        self.hybrid_calculator = None
        self.positive_impact_manager = None
        if not psychological_model:
            self._load_llm_enhancement_components()
    
    def _load_llm_enhancement_components(self):
        """加载LLM增强组件"""
        try:
            # 加载LLM增强配置
            config_path = "/Users/zl_24/Documents/Codes/2025/2025-07/CAD-main/config/llm_enhancement_config.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                llm_config = json.load(f)
            
            # 初始化混合影响计算器
            if (self.ai_client and 
                llm_config.get("llm_integration", {}).get("psychological_assessment", {}).get("enabled", False)):
                try:
                    from core.hybrid_impact_calculator import HybridImpactCalculator
                    self.hybrid_calculator = HybridImpactCalculator(
                        self.ai_client, 
                        llm_config.get("hybrid_calculation", {})
                    )
                    self.logger.info(f"{self.name}: 混合影响计算器已启用")
                except ImportError as e:
                    self.logger.warning(f"{self.name}: 无法加载混合影响计算器: {e}")
            
            # 初始化积极影响管理器
            if llm_config.get("bidirectional_impact", {}).get("enabled", False):
                try:
                    from core.positive_impact_manager import PositiveImpactManager
                    self.positive_impact_manager = PositiveImpactManager(
                        llm_config.get("bidirectional_impact", {})
                    )
                    self.logger.info(f"{self.name}: 积极影响管理器已启用")
                except ImportError as e:
                    self.logger.warning(f"{self.name}: 无法加载积极影响管理器: {e}")
            
        except Exception as e:
            self.logger.warning(f"{self.name}: 加载LLM增强组件失败: {e}")
        
    @abstractmethod
    def get_role_description(self) -> str:
        """获取角色描述"""
        pass
    
    @abstractmethod
    def get_current_concerns(self) -> List[str]:
        """获取当前关注的问题"""
        pass
    
    def get_profile(self) -> Dict[str, Any]:
        """获取完整的角色档案"""
        return {
            "name": self.name,
            "age": self.age,
            "role": self.get_role_description(),
            "personality": self.personality,
            "psychological_state": self.psychological_state.to_dict(),
            "current_concerns": self.get_current_concerns(),
            "relationships": {k: v.to_dict() for k, v in self.relationships.items()},
            "recent_thoughts": self.thoughts[-3:] if self.thoughts else []
        }
    
    async def respond_to_situation(self, situation: str, 
                                 other_agents: List['BaseAgent'] = None) -> str:
        """对情况做出回应"""
        # 获取角色档案
        profile = self.get_profile()
        
        # 获取对话历史
        history = [f"{item['speaker']}: {item['content']}" 
                  for item in self.dialogue_history[-5:]]
        
        # 生成回应
        response = await self.ai_client.generate_agent_response(
            profile, situation, history
        )
        
        
        # 记录对话
        self.dialogue_history.append({
            "timestamp": datetime.now().isoformat(),
            "speaker": self.name,
            "content": response,
            "situation": situation
        })
        
        return response
    
    async def internal_monologue(self, trigger: str) -> str:
        """内心独白"""
        profile = self.get_profile()
        
        prompt = f"""
        以{self.name}的身份，请写一段内心独白来回应以下触发事件：
        
        触发事件：{trigger}
        
        角色信息：
        {profile}
        
        请写出这个角色的真实内心想法，包括：
        1. 对事件的情感反应
        2. 内心的担忧或恐惧
        3. 对自己和他人的看法
        4. 未来的想法或计划
        
        用第一人称写作，长度100-300字。
        """
        
        thought = await self.ai_client.generate_response(prompt)
        self.thoughts.append(f"[{datetime.now().strftime('%H:%M')}] {thought}")
        
        return thought
    
    def add_life_event(self, event: LifeEvent):
        """添加生活事件"""
        self.life_events.append(event)
        
        # 根据事件影响调整心理状态
        asyncio.create_task(self._process_event_impact_async(event))
    
    async def _process_event_impact_async(self, event: LifeEvent):
        """异步处理事件影响（支持多种心理模型）"""
        try:
            # 保存事件前的状态用于对比
            old_state = self._capture_psychological_state_snapshot()
            
            if self.psychological_model:
                # 使用新的心理模型系统
                context = {
                    "character_info": {
                        "age": self.age,
                        "personality": self.personality
                    },
                    "recent_events": [e.to_dict() for e in self.life_events[-5:]],
                    "scenario_name": "default"
                }
                
                # 计算影响
                model_result = await self.psychological_model.calculate_impact(
                    event, self.psychological_state, context
                )
                
                # 显示模型计算结果
                self._display_model_impact_calculation(model_result)
                
                # 应用模型计算结果
                self._apply_model_impact(model_result)
                
                self.logger.debug(f"{self.name}: 使用{model_result.model_type}模型，置信度: {model_result.confidence:.2f}")
                
            elif self.hybrid_calculator:
                # 向后兼容：使用旧的LLM增强系统
                context = {
                    "character_info": {
                        "age": self.age,
                        "personality": self.personality
                    },
                    "recent_events": [e.to_dict() for e in self.life_events[-5:]],
                    "scenario_name": "default"
                }
                
                impact_result = await self.hybrid_calculator.calculate_comprehensive_impact(
                    event, self.psychological_state, context
                )
                
                # 显示LLM计算结果
                self._display_llm_impact_calculation(impact_result)
                
                # 应用混合影响结果
                self._apply_hybrid_impact(impact_result)
                
                self.logger.debug(f"{self.name}: 使用旧版LLM混合影响计算，总影响: {impact_result['total_impact']:.2f}")
                
            else:
                # 回退到传统方法
                self._process_event_impact(event)
            
            # 积极影响管理（仅在使用旧系统时）
            if self.positive_impact_manager and event.impact_score > 0 and not self.psychological_model:
                positive_events = [e for e in self.life_events[-10:] if e.impact_score > 0]
                if positive_events:
                    recovery_potential = self.positive_impact_manager.calculate_recovery_potential(
                        positive_events, self.psychological_state
                    )
                    
                    if recovery_potential > 0.3:  # 有一定恢复潜力时
                        resilience_result = self.positive_impact_manager.apply_resilience_factors(
                            self.psychological_state, recovery_potential
                        )
                        self._apply_resilience_adjustment(resilience_result)
                        
                        self.logger.debug(f"{self.name}: 积极影响管理，恢复潜力: {recovery_potential:.2f}")
            
            # 显示心理状态变化
            new_state = self._capture_psychological_state_snapshot()
            self._display_psychological_state_changes(old_state, new_state, event)
                        
        except Exception as e:
            self.logger.error(f"{self.name}: 心理影响处理失败: {e}")
            # 回退到传统方法
            self._process_event_impact(event)
    
    def _apply_hybrid_impact(self, impact_result: Dict):
        """应用混合影响计算结果"""
        
        # 应用基础心理状态变化
        depression_change = impact_result.get("depression_impact", 0)
        anxiety_change = impact_result.get("anxiety_impact", 0)
        self_esteem_change = impact_result.get("self_esteem_impact", 0)
        
        # 更新基础心理指标
        self.psychological_state.stress_level = max(0, min(10, 
            self.psychological_state.stress_level + anxiety_change))
        self.psychological_state.self_esteem = max(0, min(10,
            self.psychological_state.self_esteem + self_esteem_change))
        
        # 应用CAD状态变化
        cad_impact = impact_result.get("cad_impact", {})
        cad = self.psychological_state.cad_state
        
        # 更新核心信念
        cad.core_beliefs.self_belief = max(-10, min(10,
            cad.core_beliefs.self_belief + cad_impact.get("self_belief_impact", 0)))
        cad.core_beliefs.world_belief = max(-10, min(10,
            cad.core_beliefs.world_belief + cad_impact.get("world_belief_impact", 0)))
        cad.core_beliefs.future_belief = max(-10, min(10,
            cad.core_beliefs.future_belief + cad_impact.get("future_belief_impact", 0)))
        
        # 更新认知加工
        cad.cognitive_processing.rumination = max(0, min(10,
            cad.cognitive_processing.rumination + cad_impact.get("rumination_impact", 0)))
        cad.cognitive_processing.distortions = max(0, min(10,
            cad.cognitive_processing.distortions + cad_impact.get("distortion_impact", 0)))
        
        # 更新行为倾向
        cad.behavioral_inclination.social_withdrawal = max(0, min(10,
            cad.behavioral_inclination.social_withdrawal + cad_impact.get("withdrawal_impact", 0)))
        cad.behavioral_inclination.avolition = max(0, min(10,
            cad.behavioral_inclination.avolition + cad_impact.get("avolition_impact", 0)))
        
        # 更新抑郁级别
        self.psychological_state.update_depression_level_from_cad()
        
        # 更新情绪状态
        self._update_emotion_from_state()
    
    def _apply_resilience_adjustment(self, resilience_result: Dict):
        """应用心理弹性调整"""
        
        adjustments = resilience_result.get("adjustments", {})
        
        # 应用心理状态改善
        depression_improvement = adjustments.get("depression_improvement", 0)
        anxiety_improvement = adjustments.get("anxiety_improvement", 0)
        self_esteem_improvement = adjustments.get("self_esteem_improvement", 0)
        
        # 限制改善幅度，避免过度乐观
        max_improvement = 2.0
        
        self.psychological_state.stress_level = max(0, min(10,
            self.psychological_state.stress_level - min(anxiety_improvement, max_improvement)))
        self.psychological_state.self_esteem = max(0, min(10,
            self.psychological_state.self_esteem + min(self_esteem_improvement, max_improvement)))
        
        # 应用CAD改善
        cad_improvements = adjustments.get("cad_improvements", {})
        cad = self.psychological_state.cad_state
        
        cad.core_beliefs.self_belief = max(-10, min(10,
            cad.core_beliefs.self_belief + min(cad_improvements.get("self_belief_improvement", 0), max_improvement)))
        
        # 减少负面认知加工
        cad.cognitive_processing.rumination = max(0,
            cad.cognitive_processing.rumination - cad_improvements.get("rumination_reduction", 0))
        cad.behavioral_inclination.social_withdrawal = max(0,
            cad.behavioral_inclination.social_withdrawal - cad_improvements.get("social_withdrawal_reduction", 0))
    
    def _update_emotion_from_state(self):
        """基于当前状态更新情绪"""
        cad = self.psychological_state.cad_state
        
        if self.psychological_state.stress_level > 7:
            if self.psychological_state.depression_level.value >= 4:
                self.psychological_state.emotion = EmotionState.DEPRESSED
            else:
                self.psychological_state.emotion = EmotionState.ANXIOUS
        elif (self.psychological_state.stress_level < 3 and 
              self.psychological_state.self_esteem > 7 and
              cad.affective_tone > 2):
            self.psychological_state.emotion = EmotionState.HAPPY
        elif cad.affective_tone < -3:
            self.psychological_state.emotion = EmotionState.SAD
        else:
            self.psychological_state.emotion = EmotionState.NEUTRAL
    
    def _process_event_impact(self, event: LifeEvent):
        """处理事件对心理状态的影响（原有逻辑 + CAD-MD增强）"""
        impact = event.impact_score
        
        # === 原有的基础心理状态处理逻辑 ===
        # 调整压力水平
        if impact < 0:
            self.psychological_state.stress_level = min(10, self.psychological_state.stress_level + abs(impact) // 2)
            self.psychological_state.self_esteem = max(0, self.psychological_state.self_esteem - abs(impact) // 3)
        else:
            self.psychological_state.stress_level = max(0, self.psychological_state.stress_level - impact // 3)
            self.psychological_state.self_esteem = min(10, self.psychological_state.self_esteem + impact // 4)
        
        # 根据累积的负面事件判断抑郁倾向
        negative_events = [e for e in self.life_events[-10:] if e.impact_score < -3]
        if len(negative_events) >= 3:
            self.psychological_state.depression_level = DepressionLevel.MILD_RISK
        if len(negative_events) >= 5:
            self.psychological_state.depression_level = DepressionLevel.MODERATE
        if len(negative_events) >= 7:
            self.psychological_state.depression_level = DepressionLevel.SEVERE
            
        # 调整情绪状态
        if self.psychological_state.stress_level > 7:
            if self.psychological_state.depression_level.value >= 2:
                self.psychological_state.emotion = EmotionState.DEPRESSED
            else:
                self.psychological_state.emotion = EmotionState.ANXIOUS
        elif self.psychological_state.stress_level < 3 and self.psychological_state.self_esteem > 7:
            self.psychological_state.emotion = EmotionState.HAPPY
        else:
            self.psychological_state.emotion = EmotionState.NEUTRAL
        
        # === 新增：CAD-MD认知动力学更新 ===
        self._update_cad_state_by_rules(event)
    
    def _update_cad_state_by_rules(self, event: LifeEvent):
        """根据CAD-MD模型规则更新认知-情感状态"""
        cad = self.psychological_state.cad_state
        impact = event.impact_score
        
        # === 外部事件的直接影响 ===
        if impact < 0:
            # 情感基调受影响（缓慢变化，比其他状态更稳定）
            tone_change = impact / 15.0  # 比impact更温和的变化
            cad.affective_tone = max(-10, cad.affective_tone + tone_change)
            
            # 根据事件类型和描述精准影响核心信念
            event_desc = event.description.lower()
            
            # 自我信念相关事件：批评、失败、成绩差
            if any(keyword in event_desc for keyword in ["批评", "失败", "考试", "成绩", "不及格", "差劲"]):
                belief_change = impact * 0.4  # 中等强度影响
                cad.core_beliefs.self_belief = max(-10, cad.core_beliefs.self_belief + belief_change)
            
            # 世界信念相关事件：霸凌、孤立、拒绝、不公
            if any(keyword in event_desc for keyword in ["霸凌", "孤立", "拒绝", "嘲笑", "排斥", "冷漠"]):
                belief_change = impact * 0.5  # 较强影响
                cad.core_beliefs.world_belief = max(-10, cad.core_beliefs.world_belief + belief_change)
            
            # 未来信念相关事件：重大挫折、长期问题
            if any(keyword in event_desc for keyword in ["前途", "未来", "希望", "绝望", "放弃"]):
                belief_change = impact * 0.3
                cad.core_beliefs.future_belief = max(-10, cad.core_beliefs.future_belief + belief_change)
        
        else:  # 正面事件
            # 正面事件对改善认知的效果较弱（符合负性偏差的心理学原理）
            tone_change = impact / 20.0  # 正面事件影响更微弱
            cad.affective_tone = min(10, cad.affective_tone + tone_change)
        
        # === 情感基调的放大效应 ===
        # 当情感基调为负时，负面事件的影响会被放大
        if cad.affective_tone < -3:
            amplification_factor = 1.3  # 悲观时放大30%
            if impact < 0:
                additional_self_impact = (impact * 0.2) * amplification_factor
                cad.core_beliefs.self_belief = max(-10, cad.core_beliefs.self_belief + additional_self_impact)
        
        # === 核心信念驱动认知加工和行为 ===
        # 自我信念 -> 思维反刍：自我价值感越低，越容易反复思考自己的问题
        if cad.core_beliefs.self_belief < -2:
            rumination_increase = (-cad.core_beliefs.self_belief - 2) / 4.0  # 随自我信念降低而增加
            cad.cognitive_processing.rumination = min(10, 
                cad.cognitive_processing.rumination + rumination_increase)
        
        # 世界信念 -> 社交退缩：对世界的负面看法导致回避社交
        if cad.core_beliefs.world_belief < -2:
            withdrawal_increase = (-cad.core_beliefs.world_belief - 2) / 3.0
            cad.behavioral_inclination.social_withdrawal = min(10,
                cad.behavioral_inclination.social_withdrawal + withdrawal_increase)
        
        # 未来信念基于自我和世界信念的综合计算
        belief_average = (cad.core_beliefs.self_belief + cad.core_beliefs.world_belief) / 2.0
        cad.core_beliefs.future_belief = max(-10, min(10, 
            cad.core_beliefs.future_belief * 0.8 + belief_average * 0.2))  # 缓慢向平均值靠拢
        
        # === 认知加工影响情绪和行为 ===
        # 思维反刍 -> 加剧负面情绪
        if cad.cognitive_processing.rumination > 6:
            if self.psychological_state.emotion == EmotionState.NEUTRAL:
                self.psychological_state.emotion = EmotionState.ANXIOUS
            elif self.psychological_state.emotion == EmotionState.ANXIOUS:
                self.psychological_state.emotion = EmotionState.DEPRESSED
        
        # 思维反刍 -> 增加认知扭曲
        if cad.cognitive_processing.rumination > 5:
            distortion_increase = (cad.cognitive_processing.rumination - 5) / 10.0
            cad.cognitive_processing.distortions = min(10,
                cad.cognitive_processing.distortions + distortion_increase)
        
        # === 情绪的反馈循环 ===
        # 负面情绪 -> 加剧思维反刍（情绪惯性）
        if self.psychological_state.emotion in [EmotionState.SAD, EmotionState.DEPRESSED]:
            cad.cognitive_processing.rumination = min(10, cad.cognitive_processing.rumination + 0.3)
            
        # 抑郁情绪 -> 动机降低
        if self.psychological_state.emotion == EmotionState.DEPRESSED:
            cad.behavioral_inclination.avolition = min(10, cad.behavioral_inclination.avolition + 0.4)
        
        # === 限制所有值在合理范围内 ===
        self._clamp_cad_values()
    
    def _perform_daily_cad_evolution(self):
        """每日CAD状态的自然演化和长期影响"""
        cad = self.psychological_state.cad_state
        
        # === 行为的长期反馈循环 ===
        # 社交退缩 -> 减少积极反馈 -> 强化负面信念
        if cad.behavioral_inclination.social_withdrawal > 5:
            isolation_penalty = (cad.behavioral_inclination.social_withdrawal - 5) / 20.0
            cad.core_beliefs.self_belief = max(-10, cad.core_beliefs.self_belief - isolation_penalty)
            cad.core_beliefs.world_belief = max(-10, cad.core_beliefs.world_belief - isolation_penalty * 0.8)
        
        # 动机降低 -> 成就感减少 -> 自我价值感下降
        if cad.behavioral_inclination.avolition > 6:
            motivation_penalty = (cad.behavioral_inclination.avolition - 6) / 25.0
            cad.core_beliefs.self_belief = max(-10, cad.core_beliefs.self_belief - motivation_penalty)
        
        # === 状态的自然衰减（模拟时间的治愈效果）===
        # 思维反刍有自然衰减倾向
        cad.cognitive_processing.rumination *= 0.96  # 每日衰减4%
        cad.cognitive_processing.rumination = max(0, cad.cognitive_processing.rumination)
        
        # 认知扭曲也有轻微衰减
        cad.cognitive_processing.distortions *= 0.98  # 每日衰减2%
        cad.cognitive_processing.distortions = max(0, cad.cognitive_processing.distortions)
        
        # 情感基调有向中性回归的微弱趋势
        if abs(cad.affective_tone) > 0.1:
            cad.affective_tone *= 0.99  # 非常缓慢的回归
        
        # 行为倾向在没有强化的情况下会有轻微改善
        cad.behavioral_inclination.social_withdrawal *= 0.97
        cad.behavioral_inclination.avolition *= 0.97
        
        # === 积极事件的累积效应检查 ===
        # 如果最近几天有多个积极事件，给予小幅度的认知改善
        recent_positive_events = [e for e in self.life_events[-5:] if e.impact_score > 3]
        if len(recent_positive_events) >= 2:
            positive_boost = len(recent_positive_events) * 0.1
            cad.core_beliefs.self_belief = min(10, cad.core_beliefs.self_belief + positive_boost)
            cad.affective_tone = min(10, cad.affective_tone + positive_boost * 0.5)
        
        # === 最终值域限制 ===
        self._clamp_cad_values()
    
    def _clamp_cad_values(self):
        """限制CAD状态值在合理范围内"""
        cad = self.psychological_state.cad_state
        
        # 情感基调 [-10, 10]
        cad.affective_tone = max(-10, min(10, cad.affective_tone))
        
        # 核心信念 [-10, 10]
        cad.core_beliefs.self_belief = max(-10, min(10, cad.core_beliefs.self_belief))
        cad.core_beliefs.world_belief = max(-10, min(10, cad.core_beliefs.world_belief))
        cad.core_beliefs.future_belief = max(-10, min(10, cad.core_beliefs.future_belief))
        
        # 认知加工 [0, 10]
        cad.cognitive_processing.rumination = max(0, min(10, cad.cognitive_processing.rumination))
        cad.cognitive_processing.distortions = max(0, min(10, cad.cognitive_processing.distortions))
        
        # 行为倾向 [0, 10]
        cad.behavioral_inclination.social_withdrawal = max(0, min(10, cad.behavioral_inclination.social_withdrawal))
        cad.behavioral_inclination.avolition = max(0, min(10, cad.behavioral_inclination.avolition))
    
    def add_relationship(self, relationship: Relationship):
        """添加关系"""
        other_person = relationship.person_b if relationship.person_a == self.name else relationship.person_a
        self.relationships[other_person] = relationship
    
    def update_relationship(self, other_person: str, closeness_change: int = 0,
                          trust_change: int = 0, conflict_change: int = 0):
        """更新关系状态"""
        if other_person in self.relationships:
            rel = self.relationships[other_person]
            rel.closeness = max(0, min(10, rel.closeness + closeness_change))
            rel.trust_level = max(0, min(10, rel.trust_level + trust_change))
            rel.conflict_level = max(0, min(10, rel.conflict_level + conflict_change))
            
            # 关系变化影响社交连接度
            if closeness_change < 0 or trust_change < 0:
                self.psychological_state.social_connection = max(0,
                    self.psychological_state.social_connection - 1)
            elif closeness_change > 0 or trust_change > 0:
                self.psychological_state.social_connection = min(10,
                    self.psychological_state.social_connection + 1)
    
    def get_status_summary(self) -> str:
        """获取状态摘要"""
        return f"""
{self.name} 当前状态：
- 情绪：{self.psychological_state.emotion.value}
- 抑郁程度：{self.psychological_state.depression_level.name}
- 压力水平：{self.psychological_state.stress_level}/10
- 自尊水平：{self.psychological_state.self_esteem}/10
- 社交连接：{self.psychological_state.social_connection}/10
- 学业压力：{self.psychological_state.academic_pressure}/10
        """.strip()
    
    def _capture_psychological_state_snapshot(self) -> Dict:
        """捕获当前心理状态快照"""
        state = self.psychological_state
        cad = state.cad_state
        
        return {
            "basic": {
                "depression_level": state.depression_level.value,
                "stress_level": state.stress_level,
                "self_esteem": state.self_esteem,
                "social_connection": state.social_connection,
                "emotion": state.emotion.value
            },
            "cad": {
                "affective_tone": cad.affective_tone,
                "self_belief": cad.core_beliefs.self_belief,
                "world_belief": cad.core_beliefs.world_belief,
                "future_belief": cad.core_beliefs.future_belief,
                "rumination": cad.cognitive_processing.rumination,
                "distortions": cad.cognitive_processing.distortions,
                "social_withdrawal": cad.behavioral_inclination.social_withdrawal,
                "avolition": cad.behavioral_inclination.avolition
            }
        }
    
    def _display_llm_impact_calculation(self, impact_result: Dict):
        """显示LLM影响计算结果"""
        if not hasattr(self, 'console'):
            return
            
        # 创建LLM计算结果表格
        table = Table(title=f"🧠 LLM影响计算结果 - {self.name}", style="cyan")
        table.add_column("维度", style="white", min_width=12)
        table.add_column("影响值", style="yellow", justify="center")
        table.add_column("置信度", style="green", justify="center")
        
        # 基础心理指标
        table.add_row("抑郁程度", f"{impact_result.get('depression_impact', 0):.2f}", 
                     f"{impact_result.get('confidence', 0.5):.1f}")
        table.add_row("焦虑水平", f"{impact_result.get('anxiety_impact', 0):.2f}", "-")
        table.add_row("自尊水平", f"{impact_result.get('self_esteem_impact', 0):.2f}", "-")
        
        # CAD状态
        cad_impact = impact_result.get('cad_impact', {})
        table.add_row("[dim]--- CAD状态 ---[/dim]", "[dim]---[/dim]", "[dim]---[/dim]")
        table.add_row("自我信念", f"{cad_impact.get('self_belief_impact', 0):.2f}", "-")
        table.add_row("世界信念", f"{cad_impact.get('world_belief_impact', 0):.2f}", "-")
        table.add_row("未来信念", f"{cad_impact.get('future_belief_impact', 0):.2f}", "-")
        table.add_row("思维反刍", f"{cad_impact.get('rumination_impact', 0):.2f}", "-")
        
        self.console.print(table)
    
    def _display_psychological_state_changes(self, old_state: Dict, new_state: Dict, event: LifeEvent):
        """显示心理状态变化"""
        if not hasattr(self, 'console'):
            return
            
        # 创建状态变化表格
        table = Table(title=f"📊 心理状态变化 - {self.name}", style="magenta")
        table.add_column("指标", style="white", min_width=12)
        table.add_column("变化前", style="blue", justify="center")
        table.add_column("变化后", style="cyan", justify="center") 
        table.add_column("变化量", style="yellow", justify="center")
        table.add_column("趋势", style="green", justify="center")
        
        # 基础心理指标
        self._add_change_row(table, "抑郁程度", 
                           old_state["basic"]["depression_level"], 
                           new_state["basic"]["depression_level"])
        self._add_change_row(table, "压力水平", 
                           old_state["basic"]["stress_level"], 
                           new_state["basic"]["stress_level"])
        self._add_change_row(table, "自尊水平", 
                           old_state["basic"]["self_esteem"], 
                           new_state["basic"]["self_esteem"])
        self._add_change_row(table, "社交连接", 
                           old_state["basic"]["social_connection"], 
                           new_state["basic"]["social_connection"])
        
        # CAD状态变化
        table.add_row("[dim]--- CAD认知状态 ---[/dim]", "[dim]---[/dim]", "[dim]---[/dim]", "[dim]---[/dim]", "[dim]---[/dim]")
        self._add_change_row(table, "情感基调", 
                           old_state["cad"]["affective_tone"], 
                           new_state["cad"]["affective_tone"], precision=1)
        self._add_change_row(table, "自我信念", 
                           old_state["cad"]["self_belief"], 
                           new_state["cad"]["self_belief"], precision=1)
        self._add_change_row(table, "世界信念", 
                           old_state["cad"]["world_belief"], 
                           new_state["cad"]["world_belief"], precision=1)
        self._add_change_row(table, "未来信念", 
                           old_state["cad"]["future_belief"], 
                           new_state["cad"]["future_belief"], precision=1)
        self._add_change_row(table, "思维反刍", 
                           old_state["cad"]["rumination"], 
                           new_state["cad"]["rumination"], precision=1)
        self._add_change_row(table, "认知扭曲", 
                           old_state["cad"]["distortions"], 
                           new_state["cad"]["distortions"], precision=1)
        self._add_change_row(table, "社交退缩", 
                           old_state["cad"]["social_withdrawal"], 
                           new_state["cad"]["social_withdrawal"], precision=1)
        self._add_change_row(table, "动机缺失", 
                           old_state["cad"]["avolition"], 
                           new_state["cad"]["avolition"], precision=1)
        
        self.console.print(table)
        
        # 显示影响规则和机制
        self._display_impact_mechanisms(event, old_state, new_state)
    
    def _add_change_row(self, table: Table, name: str, old_val: float, new_val: float, precision: int = 0):
        """添加变化行到表格"""
        change = new_val - old_val
        
        if precision == 0:
            old_str = f"{old_val:.0f}"
            new_str = f"{new_val:.0f}"
            change_str = f"{change:+.0f}" if change != 0 else "0"
        else:
            old_str = f"{old_val:.1f}"
            new_str = f"{new_val:.1f}"
            change_str = f"{change:+.1f}" if change != 0 else "0.0"
        
        # 趋势指示器
        if change > 0.1:
            trend = "📈"
            trend_color = "green"
        elif change < -0.1:
            trend = "📉"
            trend_color = "red"
        else:
            trend = "➖"
            trend_color = "white"
        
        # 根据变化量调整颜色
        if abs(change) > 1:
            change_str = f"[bold]{change_str}[/bold]"
        
        table.add_row(name, old_str, new_str, change_str, f"[{trend_color}]{trend}[/{trend_color}]")
    
    def _display_impact_mechanisms(self, event: LifeEvent, old_state: Dict, new_state: Dict):
        """显示影响机制和规则"""
        if not hasattr(self, 'console'):
            return
            
        mechanisms = []
        
        # 分析影响机制
        if event.impact_score < -3:
            mechanisms.append("🔴 强负面事件 → 触发多重心理防御机制")
        elif event.impact_score < 0:
            mechanisms.append("🟡 轻度负面事件 → 激活认知偏差")
        elif event.impact_score > 3:
            mechanisms.append("🟢 积极事件 → 缓解负面认知模式")
        
        # CAD规则分析
        cad_old = old_state["cad"]
        cad_new = new_state["cad"]
        
        if cad_new["self_belief"] < cad_old["self_belief"]:
            mechanisms.append("📝 自我信念下降 → 增强思维反刍倾向")
        
        if cad_new["world_belief"] < cad_old["world_belief"]:
            mechanisms.append("🌍 世界信念悲观化 → 促进社交退缩行为")
        
        if cad_new["rumination"] > cad_old["rumination"]:
            mechanisms.append("🔄 思维反刍增强 → 放大负面情绪体验")
        
        if cad_new["social_withdrawal"] > cad_old["social_withdrawal"]:
            mechanisms.append("🚪 社交退缩增加 → 减少积极反馈机会")
        
        # 显示机制面板
        if mechanisms:
            mechanism_text = "\n".join(mechanisms)
            panel = Panel(
                mechanism_text,
                title="⚙️ 心理动力学机制",
                style="dim cyan",
                border_style="cyan"
            )
            self.console.print(panel)
    
    def _display_model_impact_calculation(self, model_result):
        """显示模型影响计算结果"""
        if not hasattr(self, 'console'):
            return
            
        from models.psychological_model_base import ModelImpactResult
        if not isinstance(model_result, ModelImpactResult):
            return
            
        # 创建模型计算结果表格
        table = Table(title=f"🧠 {model_result.model_type}模型计算结果 - {self.name}", style="cyan")
        table.add_column("维度", style="white", min_width=12)
        table.add_column("影响值", style="yellow", justify="center")
        table.add_column("置信度", style="green", justify="center")
        
        # 基础心理指标
        table.add_row("抑郁程度", f"{model_result.depression_change:.2f}", 
                     f"{model_result.confidence:.1f}")
        table.add_row("焦虑水平", f"{model_result.anxiety_change:.2f}", "-")
        table.add_row("压力水平", f"{model_result.stress_change:.2f}", "-")
        table.add_row("自尊水平", f"{model_result.self_esteem_change:.2f}", "-")
        table.add_row("社交连接", f"{model_result.social_connection_change:.2f}", "-")
        
        # CAD状态（如果支持）
        if (hasattr(self.psychological_model, 'supports_cad_state') and 
            self.psychological_model.supports_cad_state()):
            table.add_row("[dim]--- CAD状态 ---[/dim]", "[dim]---[/dim]", "[dim]---[/dim]")
            table.add_row("情感基调", f"{model_result.affective_tone_change:.2f}", "-")
            table.add_row("自我信念", f"{model_result.self_belief_change:.2f}", "-")
            table.add_row("世界信念", f"{model_result.world_belief_change:.2f}", "-")
            table.add_row("未来信念", f"{model_result.future_belief_change:.2f}", "-")
            table.add_row("思维反刍", f"{model_result.rumination_change:.2f}", "-")
            table.add_row("认知扭曲", f"{model_result.distortion_change:.2f}", "-")
            table.add_row("社交退缩", f"{model_result.social_withdrawal_change:.2f}", "-")
            table.add_row("动机缺失", f"{model_result.avolition_change:.2f}", "-")
        
        # 添加处理时间和推理
        table.add_row("[dim]--- 元信息 ---[/dim]", "[dim]---[/dim]", "[dim]---[/dim]")
        table.add_row("处理时间", f"{model_result.processing_time:.1f}ms", "-")
        
        self.console.print(table)
        
        # 显示推理说明
        if model_result.reasoning:
            reasoning_panel = Panel(
                model_result.reasoning,
                title="🤔 模型推理",
                style="dim yellow",
                border_style="yellow"
            )
            self.console.print(reasoning_panel)
    
    def _apply_model_impact(self, model_result):
        """应用模型计算结果到心理状态"""
        from models.psychological_model_base import ModelImpactResult
        if not isinstance(model_result, ModelImpactResult):
            return
        
        # 应用基础心理状态变化
        self.psychological_state.stress_level = max(0, min(10, 
            self.psychological_state.stress_level + model_result.stress_change))
        self.psychological_state.self_esteem = max(0, min(10,
            self.psychological_state.self_esteem + model_result.self_esteem_change))
        self.psychological_state.social_connection = max(0, min(10,
            self.psychological_state.social_connection + model_result.social_connection_change))
        
        # 应用CAD状态变化（如果模型支持）
        if (hasattr(self.psychological_model, 'supports_cad_state') and 
            self.psychological_model.supports_cad_state()):
            
            cad = self.psychological_state.cad_state
            
            # 更新情感基调
            cad.affective_tone = max(-10, min(10,
                cad.affective_tone + model_result.affective_tone_change))
            
            # 更新核心信念
            cad.core_beliefs.self_belief = max(-10, min(10,
                cad.core_beliefs.self_belief + model_result.self_belief_change))
            cad.core_beliefs.world_belief = max(-10, min(10,
                cad.core_beliefs.world_belief + model_result.world_belief_change))
            cad.core_beliefs.future_belief = max(-10, min(10,
                cad.core_beliefs.future_belief + model_result.future_belief_change))
            
            # 更新认知加工
            cad.cognitive_processing.rumination = max(0, min(10,
                cad.cognitive_processing.rumination + model_result.rumination_change))
            cad.cognitive_processing.distortions = max(0, min(10,
                cad.cognitive_processing.distortions + model_result.distortion_change))
            
            # 更新行为倾向
            cad.behavioral_inclination.social_withdrawal = max(0, min(10,
                cad.behavioral_inclination.social_withdrawal + model_result.social_withdrawal_change))
            cad.behavioral_inclination.avolition = max(0, min(10,
                cad.behavioral_inclination.avolition + model_result.avolition_change))
            
            # 基于CAD状态更新抑郁级别
            self.psychological_state.update_depression_level_from_cad()
        else:
            # 对于不支持CAD的模型，直接更新抑郁程度
            current_depression_value = self.psychological_state.depression_level.value
            new_depression_value = max(0, min(4, current_depression_value + model_result.depression_change))
            
            # 更新抑郁级别
            depression_levels = [DepressionLevel.HEALTHY, DepressionLevel.MILD_RISK, 
                               DepressionLevel.MODERATE, DepressionLevel.SEVERE, DepressionLevel.CRISIS]
            self.psychological_state.depression_level = depression_levels[int(new_depression_value)]
        
        # 更新情绪状态
        self._update_emotion_from_state()