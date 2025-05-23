from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
import asyncio
from datetime import datetime
import uuid

from models.psychology_models import PsychologicalState, LifeEvent, Relationship, EmotionState, DepressionLevel

class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, name: str, age: int, personality: Dict[str, Any], 
                 ai_client: Union['GeminiClient', 'DeepSeekClient']):
        self.id = str(uuid.uuid4())
        self.name = name
        self.age = age
        self.personality = personality
        self.ai_client = ai_client
        
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
        self._process_event_impact(event)
    
    def _process_event_impact(self, event: LifeEvent):
        """处理事件对心理状态的影响"""
        impact = event.impact_score
        
        # 调整压力水平
        if impact < 0:
            self.psychological_state.stress_level = min(10, 
                self.psychological_state.stress_level + abs(impact) // 2)
            self.psychological_state.self_esteem = max(0,
                self.psychological_state.self_esteem - abs(impact) // 3)
        else:
            self.psychological_state.stress_level = max(0,
                self.psychological_state.stress_level - impact // 3)
            self.psychological_state.self_esteem = min(10,
                self.psychological_state.self_esteem + impact // 4)
        
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