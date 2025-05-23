from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
import json

class EmotionState(Enum):
    """情绪状态枚举"""
    HAPPY = "开心"
    NEUTRAL = "中性"
    ANXIOUS = "焦虑"
    SAD = "悲伤"
    DEPRESSED = "抑郁"
    ANGRY = "愤怒"
    CONFUSED = "困惑"

class DepressionLevel(Enum):
    """抑郁程度枚举"""
    HEALTHY = 0      # 健康
    MILD_RISK = 1    # 轻度风险
    MODERATE = 2     # 中度抑郁
    SEVERE = 3       # 重度抑郁
    CRITICAL = 4     # 严重抑郁

class EventType(Enum):
    """生活事件类型"""
    ACADEMIC_FAILURE = "学业失败"
    SOCIAL_REJECTION = "社交拒绝"
    FAMILY_CONFLICT = "家庭冲突"
    BULLYING = "霸凌"
    PEER_PRESSURE = "同辈压力"
    TEACHER_CRITICISM = "老师批评"
    EXAM_STRESS = "考试压力"

@dataclass
class PsychologicalState:
    """心理状态"""
    emotion: EmotionState
    depression_level: DepressionLevel
    stress_level: int  # 0-10
    self_esteem: int   # 0-10
    social_connection: int  # 0-10
    academic_pressure: int  # 0-10
    
    def to_dict(self) -> Dict:
        return {
            "emotion": self.emotion.value,
            "depression_level": self.depression_level.value,
            "stress_level": self.stress_level,
            "self_esteem": self.self_esteem,
            "social_connection": self.social_connection,
            "academic_pressure": self.academic_pressure
        }

@dataclass
class LifeEvent:
    """生活事件"""
    event_type: EventType
    description: str
    impact_score: int  # -10 到 10，负数表示负面影响
    timestamp: str
    participants: List[str]  # 参与者名称
    
    def to_dict(self) -> Dict:
        return {
            "event_type": self.event_type.value,
            "description": self.description,
            "impact_score": self.impact_score,
            "timestamp": self.timestamp,
            "participants": self.participants
        }

@dataclass
class Relationship:
    """关系模型"""
    person_a: str
    person_b: str
    relationship_type: str  # "父子", "母子", "同学", "师生"
    closeness: int  # 0-10
    trust_level: int  # 0-10
    conflict_level: int  # 0-10
    
    def to_dict(self) -> Dict:
        return {
            "person_a": self.person_a,
            "person_b": self.person_b,
            "relationship_type": self.relationship_type,
            "closeness": self.closeness,
            "trust_level": self.trust_level,
            "conflict_level": self.conflict_level
        } 