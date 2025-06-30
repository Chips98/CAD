from dataclasses import dataclass, field
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
    """抑郁程度枚举 - 基于PHQ-9和贝克抑郁量表扩展至10级精细分级"""
    OPTIMAL = 0          # 最佳状态 (PHQ-9: 0-1)
    HEALTHY = 1          # 健康正常 (PHQ-9: 2-4) 
    MINIMAL_SYMPTOMS = 2 # 最小症状 (PHQ-9: 5-6)
    MILD_RISK = 3        # 轻度风险 (PHQ-9: 7-9)
    MILD = 4             # 轻度抑郁 (PHQ-9: 10-12)
    MODERATE_MILD = 5    # 中轻度抑郁 (PHQ-9: 13-15)
    MODERATE = 6         # 中度抑郁 (PHQ-9: 16-18)
    MODERATE_SEVERE = 7  # 中重度抑郁 (PHQ-9: 19-21)
    SEVERE = 8           # 重度抑郁 (PHQ-9: 22-24)
    CRITICAL = 9         # 极重度抑郁 (PHQ-9: 25-27)

class EventType(Enum):
    """生活事件类型"""
    ACADEMIC_FAILURE = "学业失败"
    SOCIAL_REJECTION = "社交拒绝"
    FAMILY_CONFLICT = "家庭冲突"
    BULLYING = "霸凌"
    PEER_PRESSURE = "同辈压力"
    TEACHER_CRITICISM = "老师批评"
    EXAM_STRESS = "考试压力"

# ===== CAD-MD模型核心数据结构 =====

@dataclass
class CoreBeliefs:
    """核心信念 - 贝克认知三角"""
    self_belief: float = 0.0      # 自我信念 (-10: 极负面, 10: 极正面)
    world_belief: float = 0.0     # 世界信念 (-10 to 10)
    future_belief: float = 0.0    # 未来信念 (-10 to 10)
    
    def to_dict(self) -> Dict:
        return {
            "self_belief": self.self_belief,
            "world_belief": self.world_belief,
            "future_belief": self.future_belief
        }
    
    def get_textual_representation(self) -> Dict[str, str]:
        """转换为文本描述"""
        return {
            "self_belief": self._belief_to_text(self.self_belief, "self"),
            "world_belief": self._belief_to_text(self.world_belief, "world"), 
            "future_belief": self._belief_to_text(self.future_belief, "future")
        }
    
    def _belief_to_text(self, score: float, belief_type: str) -> str:
        """将分数转换为文本描述"""
        if belief_type == "self":
            if score >= 5: return "我是有价值的、能干的"
            elif score >= 1: return "我基本上是ok的"
            elif score >= -1: return "我对自己的看法比较中性"
            elif score >= -5: return "我经常觉得自己不够好"
            else: return "我觉得自己毫无价值、一无是处"
        elif belief_type == "world":
            if score >= 5: return "世界是友好的、充满机会的"
            elif score >= 1: return "世界总体上是公平的"
            elif score >= -1: return "世界是复杂的，有好有坏"
            elif score >= -5: return "世界充满困难和不公"
            else: return "世界是残酷的、敌对的"
        else:  # future
            if score >= 5: return "未来充满希望和可能性"
            elif score >= 1: return "未来基本上是光明的"
            elif score >= -1: return "未来不确定，但还有希望"
            elif score >= -5: return "未来可能会很困难"
            else: return "未来是绝望的、没有意义的"

@dataclass  
class CognitiveProcessing:
    """认知加工方式"""
    rumination: float = 0.0       # 负性思维反刍 (0: 无, 10: 严重)
    distortions: float = 0.0      # 认知扭曲程度 (0: 无, 10: 严重)
    
    def to_dict(self) -> Dict:
        return {
            "rumination": self.rumination,
            "distortions": self.distortions
        }

@dataclass
class BehavioralInclination:
    """行为倾向"""
    social_withdrawal: float = 0.0 # 社交退缩 (0: 无, 10: 严重)
    avolition: float = 0.0         # 动机降低/快感缺失 (0: 无, 10: 严重)
    
    def to_dict(self) -> Dict:
        return {
            "social_withdrawal": self.social_withdrawal,
            "avolition": self.avolition
        }

@dataclass
class CognitiveAffectiveState:
    """完整的认知-情感动力学状态"""
    affective_tone: float = 0.0    # 情感基调 (-10: 悲观, 10: 乐观)
    core_beliefs: CoreBeliefs = field(default_factory=CoreBeliefs)
    cognitive_processing: CognitiveProcessing = field(default_factory=CognitiveProcessing)
    behavioral_inclination: BehavioralInclination = field(default_factory=BehavioralInclination)
    
    def to_dict(self) -> Dict:
        return {
            "affective_tone": self.affective_tone,
            "core_beliefs": self.core_beliefs.to_dict(),
            "cognitive_processing": self.cognitive_processing.to_dict(),
            "behavioral_inclination": self.behavioral_inclination.to_dict()
        }
    
    def get_comprehensive_analysis(self) -> str:
        """生成用于AI prompt的综合分析"""
        beliefs_text = self.core_beliefs.get_textual_representation()
        
        analysis = f"""
=== 认知-情感动力学状态分析 ===

情感基调: {self._describe_affective_tone(self.affective_tone)}

核心信念系统 (贝克认知三角):
- 自我信念: {beliefs_text['self_belief']}
- 世界信念: {beliefs_text['world_belief']}  
- 未来信念: {beliefs_text['future_belief']}

认知加工模式:
- 思维反刍程度: {self._describe_rumination(self.cognitive_processing.rumination)}
- 认知扭曲程度: {self._describe_distortions(self.cognitive_processing.distortions)}

行为倾向:
- 社交退缩: {self._describe_social_withdrawal(self.behavioral_inclination.social_withdrawal)}
- 动机降低: {self._describe_avolition(self.behavioral_inclination.avolition)}
        """.strip()
        return analysis
    
    def _describe_affective_tone(self, score: float) -> str:
        if score >= 5: return "乐观积极"
        elif score >= 1: return "基本积极"
        elif score >= -1: return "中性"
        elif score >= -5: return "偏悲观"
        else: return "严重悲观"
    
    def _describe_rumination(self, score: float) -> str:
        if score < 2: return "很少反复思考负面想法"
        elif score < 4: return "偶尔陷入负面思维循环"
        elif score < 6: return "经常重复思考负面事件"
        elif score < 8: return "严重的负性思维反刍"
        else: return "极度严重的反刍思维，难以自控"
    
    def _describe_distortions(self, score: float) -> str:
        if score < 2: return "思维基本客观理性"
        elif score < 4: return "偶有思维偏差"
        elif score < 6: return "存在明显的认知扭曲"
        elif score < 8: return "严重的认知扭曲模式"
        else: return "极度扭曲的思维方式"
    
    def _describe_social_withdrawal(self, score: float) -> str:
        if score < 2: return "社交活跃，愿意与人交往"
        elif score < 4: return "社交略有减少"
        elif score < 6: return "明显回避社交活动"
        elif score < 8: return "严重社交退缩"
        else: return "几乎完全孤立，拒绝社交"
    
    def _describe_avolition(self, score: float) -> str:
        if score < 2: return "动机充足，对活动有兴趣"
        elif score < 4: return "动机略有下降"
        elif score < 6: return "明显缺乏动机和兴趣"
        elif score < 8: return "严重的动机缺失"
        else: return "几乎完全失去动机，快感缺失"
    
    def calculate_comprehensive_depression_score(self) -> float:
        """
        基于CAD-MD模型计算综合抑郁评分 (0-27分，类似PHQ-9扩展版)
        
        理论基础：
        - Beck认知三角：核心信念影响情绪和行为
        - Nolen-Hoeksema反刍理论：重复负性思维维持抑郁
        - 行为激活理论：社交退缩和动机缺失的恶性循环
        
        Returns:
            float: 0-27的抑郁严重程度评分
        """
        
        # 权重分配基于临床研究和CAD-MD理论
        weights = {
            'core_beliefs': 0.35,      # 核心信念是抑郁的根本（Beck, 1967）
            'affective_tone': 0.25,    # 情感基调反映整体情绪状态
            'cognitive_processing': 0.20,  # 认知加工维持抑郁循环
            'behavioral_patterns': 0.20    # 行为模式影响功能
        }
        
        # 1. 核心信念分数 (0-9分)
        # 将-10到10的信念分数转换为0-3的抑郁贡献分数
        belief_scores = []
        for belief in [self.core_beliefs.self_belief, 
                      self.core_beliefs.world_belief, 
                      self.core_beliefs.future_belief]:
            # 负性信念越强，抑郁分数越高
            depression_contribution = max(0, (-belief + 10) / 20 * 3)
            belief_scores.append(depression_contribution)
        
        core_beliefs_score = sum(belief_scores)  # 0-9分
        
        # 2. 情感基调分数 (0-6分)
        # 负性情感基调对应更高的抑郁分数
        affective_score = max(0, (-self.affective_tone + 10) / 20 * 6)
        
        # 3. 认知加工分数 (0-6分)
        cognitive_score = (
            (self.cognitive_processing.rumination / 10 * 3) +    # 反刍思维
            (self.cognitive_processing.distortions / 10 * 3)     # 认知扭曲
        )
        
        # 4. 行为模式分数 (0-6分)
        behavioral_score = (
            (self.behavioral_inclination.social_withdrawal / 10 * 3) +  # 社交退缩
            (self.behavioral_inclination.avolition / 10 * 3)            # 动机缺失
        )
        
        # 计算加权总分
        total_score = (
            core_beliefs_score * weights['core_beliefs'] +
            affective_score * weights['affective_tone'] +
            cognitive_score * weights['cognitive_processing'] +
            behavioral_score * weights['behavioral_patterns']
        ) * 27 / 9  # 归一化到0-27范围
        
        return min(27.0, max(0.0, total_score))
    
    def get_depression_level_from_cad(self) -> DepressionLevel:
        """基于CAD状态计算抑郁级别"""
        score = self.calculate_comprehensive_depression_score()
        
        # 基于PHQ-9标准的10级分类
        if score <= 1: return DepressionLevel.OPTIMAL
        elif score <= 4: return DepressionLevel.HEALTHY  
        elif score <= 6: return DepressionLevel.MINIMAL_SYMPTOMS
        elif score <= 9: return DepressionLevel.MILD_RISK
        elif score <= 12: return DepressionLevel.MILD
        elif score <= 15: return DepressionLevel.MODERATE_MILD
        elif score <= 18: return DepressionLevel.MODERATE
        elif score <= 21: return DepressionLevel.MODERATE_SEVERE
        elif score <= 24: return DepressionLevel.SEVERE
        else: return DepressionLevel.CRITICAL

@dataclass
class PsychologicalState:
    """心理状态 - 整合版（包含传统指标和CAD-MD深度建模）"""
    # 原有字段保持不变，确保向后兼容
    emotion: EmotionState
    depression_level: DepressionLevel
    stress_level: int  # 0-10
    self_esteem: int   # 0-10
    social_connection: int  # 0-10
    academic_pressure: int  # 0-10
    
    # 新增CAD-MD深度建模
    cad_state: CognitiveAffectiveState = field(default_factory=CognitiveAffectiveState)
    
    def to_dict(self) -> Dict:
        base_dict = {
            "emotion": self.emotion.value,
            "depression_level": self.depression_level.value,
            "stress_level": self.stress_level,
            "self_esteem": self.self_esteem,
            "social_connection": self.social_connection,
            "academic_pressure": self.academic_pressure
        }
        # 将CAD状态递归合并到字典中
        base_dict["cad_state"] = self.cad_state.to_dict()
        return base_dict
    
    def get_flattened_cad_state(self) -> Dict:
        """获取拍平的CAD状态，用于日志和条件事件判断"""
        cad_dict = self.cad_state.to_dict()
        flattened = {
            "affective_tone": cad_dict["affective_tone"],
            "self_belief": cad_dict["core_beliefs"]["self_belief"],
            "world_belief": cad_dict["core_beliefs"]["world_belief"],
            "future_belief": cad_dict["core_beliefs"]["future_belief"],
            "rumination": cad_dict["cognitive_processing"]["rumination"],
            "distortions": cad_dict["cognitive_processing"]["distortions"],
            "social_withdrawal": cad_dict["behavioral_inclination"]["social_withdrawal"],
            "avolition": cad_dict["behavioral_inclination"]["avolition"]
        }
        return flattened
    
    def update_depression_level_from_cad(self):
        """基于CAD状态更新抑郁级别"""
        new_level = self.cad_state.get_depression_level_from_cad()
        self.depression_level = new_level
        return new_level
    
    def calculate_improvement_percentage(self, initial_cad_state: CognitiveAffectiveState, 
                                       initial_depression_level: DepressionLevel) -> float:
        """
        计算综合改善程度（百分比）
        基于CAD多维度状态变化和抑郁级别变化的综合评估
        
        Args:
            initial_cad_state: 初始CAD状态
            initial_depression_level: 初始抑郁级别
            
        Returns:
            float: 改善程度百分比 (0-100)
        """
        
        # 1. 计算CAD各维度的改善程度
        cad_improvements = {}
        
        # 核心信念改善 (权重: 35%)
        belief_improvements = []
        belief_pairs = [
            (initial_cad_state.core_beliefs.self_belief, self.cad_state.core_beliefs.self_belief),
            (initial_cad_state.core_beliefs.world_belief, self.cad_state.core_beliefs.world_belief),
            (initial_cad_state.core_beliefs.future_belief, self.cad_state.core_beliefs.future_belief)
        ]
        
        for initial, current in belief_pairs:
            # 信念改善: 从负值向正值移动表示改善
            max_possible_improvement = 10 - initial  # 最大可能改善
            actual_improvement = current - initial    # 实际改善
            if max_possible_improvement > 0:
                improvement_pct = min(100, max(0, (actual_improvement / max_possible_improvement) * 100))
            else:
                improvement_pct = 0
            belief_improvements.append(improvement_pct)
        
        cad_improvements['core_beliefs'] = sum(belief_improvements) / len(belief_improvements)
        
        # 情感基调改善 (权重: 25%)
        max_affective_improvement = 10 - initial_cad_state.affective_tone
        actual_affective_improvement = self.cad_state.affective_tone - initial_cad_state.affective_tone
        if max_affective_improvement > 0:
            cad_improvements['affective_tone'] = min(100, max(0, 
                (actual_affective_improvement / max_affective_improvement) * 100))
        else:
            cad_improvements['affective_tone'] = 0
        
        # 认知加工改善 (权重: 20%) - 值越低越好
        rumination_improvement = max(0, initial_cad_state.cognitive_processing.rumination - 
                                   self.cad_state.cognitive_processing.rumination)
        distortion_improvement = max(0, initial_cad_state.cognitive_processing.distortions - 
                                   self.cad_state.cognitive_processing.distortions)
        
        max_rumination_improvement = initial_cad_state.cognitive_processing.rumination
        max_distortion_improvement = initial_cad_state.cognitive_processing.distortions
        
        rumination_pct = (rumination_improvement / max_rumination_improvement * 100) if max_rumination_improvement > 0 else 0
        distortion_pct = (distortion_improvement / max_distortion_improvement * 100) if max_distortion_improvement > 0 else 0
        
        cad_improvements['cognitive_processing'] = (rumination_pct + distortion_pct) / 2
        
        # 行为模式改善 (权重: 20%) - 值越低越好
        withdrawal_improvement = max(0, initial_cad_state.behavioral_inclination.social_withdrawal - 
                                   self.cad_state.behavioral_inclination.social_withdrawal)
        avolition_improvement = max(0, initial_cad_state.behavioral_inclination.avolition - 
                                  self.cad_state.behavioral_inclination.avolition)
        
        max_withdrawal_improvement = initial_cad_state.behavioral_inclination.social_withdrawal
        max_avolition_improvement = initial_cad_state.behavioral_inclination.avolition
        
        withdrawal_pct = (withdrawal_improvement / max_withdrawal_improvement * 100) if max_withdrawal_improvement > 0 else 0
        avolition_pct = (avolition_improvement / max_avolition_improvement * 100) if max_avolition_improvement > 0 else 0
        
        cad_improvements['behavioral_patterns'] = (withdrawal_pct + avolition_pct) / 2
        
        # 2. 计算抑郁级别改善 (权重: 40%)
        initial_depression_score = initial_depression_level.value
        current_depression_score = self.depression_level.value
        max_depression_improvement = initial_depression_score  # 最好能到0级
        actual_depression_improvement = max(0, initial_depression_score - current_depression_score)
        
        depression_improvement_pct = (actual_depression_improvement / max_depression_improvement * 100) if max_depression_improvement > 0 else 0
        
        # 3. 综合权重计算
        weights = {
            'core_beliefs': 0.25,
            'affective_tone': 0.15, 
            'cognitive_processing': 0.15,
            'behavioral_patterns': 0.15,
            'depression_level': 0.30  # 抑郁级别改善权重最高
        }
        
        total_improvement = (
            cad_improvements['core_beliefs'] * weights['core_beliefs'] +
            cad_improvements['affective_tone'] * weights['affective_tone'] +
            cad_improvements['cognitive_processing'] * weights['cognitive_processing'] +
            cad_improvements['behavioral_patterns'] * weights['behavioral_patterns'] +
            depression_improvement_pct * weights['depression_level']
        )
        
        return min(100.0, max(0.0, total_improvement))

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