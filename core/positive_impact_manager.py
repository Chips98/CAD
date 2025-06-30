"""
积极影响管理器 - 处理心理修复和改善机制
实现积极事件的心理修复效果、社会支持、成就感和自我认知改善
"""

import logging
import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

from models.psychology_models import LifeEvent, PsychologicalState, CognitiveAffectiveState


class PositiveImpactManager:
    """积极影响管理器 - 处理心理状态的积极变化和恢复机制"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 积极影响配置
        self.recovery_amplification = self.config.get("recovery_amplification", 1.2)
        self.momentum_threshold = self.config.get("momentum_threshold", 3)  # 连续积极事件阈值
        self.social_support_weight = self.config.get("social_support_weight", 0.4)
        self.achievement_weight = self.config.get("achievement_weight", 0.3)
        self.self_efficacy_weight = self.config.get("self_efficacy_weight", 0.3)
        
        # 恢复轨迹跟踪
        self.recovery_history = []
        self.positive_momentum_counter = 0
        self.last_positive_event_time = None
        
        # 心理弹性因子
        self.base_resilience = 0.5
        self.resilience_growth_rate = 0.1
        self.resilience_decay_rate = 0.02
        
        self.logger.info("积极影响管理器初始化完成")
    
    def calculate_recovery_potential(self, positive_events: List[LifeEvent], 
                                   current_state: PsychologicalState) -> float:
        """计算恢复潜力"""
        
        if not positive_events:
            return 0.0
        
        # 1. 基于积极事件的数量和质量
        event_recovery_score = self._calculate_event_recovery_score(positive_events)
        
        # 2. 基于当前心理状态的恢复能力
        state_recovery_capacity = self._calculate_state_recovery_capacity(current_state)
        
        # 3. 基于时间分布的恢复效果
        temporal_recovery_effect = self._calculate_temporal_recovery_effect(positive_events)
        
        # 4. 综合恢复潜力
        total_recovery_potential = (
            event_recovery_score * 0.4 +
            state_recovery_capacity * 0.3 +
            temporal_recovery_effect * 0.3
        )
        
        self.logger.debug(f"恢复潜力计算: 事件={event_recovery_score:.2f}, "
                         f"状态={state_recovery_capacity:.2f}, 时间={temporal_recovery_effect:.2f}")
        
        return max(0.0, min(1.0, total_recovery_potential))
    
    def _calculate_event_recovery_score(self, positive_events: List[LifeEvent]) -> float:
        """计算积极事件的恢复分数"""
        
        if not positive_events:
            return 0.0
        
        total_score = 0.0
        
        for event in positive_events:
            # 基础积极影响
            base_score = max(0, event.impact_score) / 10.0  # 归一化到0-1
            
            # 事件类型加权
            type_multiplier = self._get_event_type_multiplier(event)
            
            # 参与者影响（社会支持）
            social_multiplier = self._get_social_support_multiplier(event)
            
            # 单个事件恢复分数
            event_recovery = base_score * type_multiplier * social_multiplier
            total_score += event_recovery
        
        # 平均分数并应用事件数量奖励
        average_score = total_score / len(positive_events)
        quantity_bonus = min(0.3, len(positive_events) * 0.05)  # 最多30%奖励
        
        return min(1.0, average_score + quantity_bonus)
    
    def _get_event_type_multiplier(self, event: LifeEvent) -> float:
        """根据事件类型获取恢复倍数"""
        
        event_desc = event.description.lower()
        
        # 成就相关事件
        achievement_keywords = ["成功", "完成", "获得", "表扬", "认可", "优秀", "第一"]
        if any(keyword in event_desc for keyword in achievement_keywords):
            return self.achievement_weight + 1.0
        
        # 社会支持相关事件
        social_keywords = ["朋友", "家人", "帮助", "支持", "关心", "陪伴", "理解"]
        if any(keyword in event_desc for keyword in social_keywords):
            return self.social_support_weight + 1.0
        
        # 自我效能相关事件
        efficacy_keywords = ["自己", "独立", "解决", "克服", "努力", "坚持", "进步"]
        if any(keyword in event_desc for keyword in efficacy_keywords):
            return self.self_efficacy_weight + 1.0
        
        return 1.0  # 默认倍数
    
    def _get_social_support_multiplier(self, event: LifeEvent) -> float:
        """基于参与者计算社会支持倍数"""
        
        # 计算社会支持强度
        support_strength = 1.0
        
        # 家人参与提供更强支持
        family_keywords = ["妈妈", "爸爸", "父母", "家人", "母亲", "父亲"]
        if any(keyword in " ".join(event.participants) for keyword in family_keywords):
            support_strength += 0.3
        
        # 朋友参与提供中等支持
        friend_keywords = ["朋友", "同学", "同伴", "伙伴"]
        if any(keyword in " ".join(event.participants) for keyword in friend_keywords):
            support_strength += 0.2
        
        # 权威人物参与提供认可支持
        authority_keywords = ["老师", "导师", "教练", "领导"]
        if any(keyword in " ".join(event.participants) for keyword in authority_keywords):
            support_strength += 0.25
        
        return min(1.5, support_strength)  # 最大1.5倍
    
    def _calculate_state_recovery_capacity(self, current_state: PsychologicalState) -> float:
        """计算当前状态的恢复能力"""
        
        cad = current_state.cad_state
        
        # 1. 基础心理资源
        self_esteem_capacity = current_state.self_esteem / 10.0
        social_capacity = current_state.social_connection / 10.0
        stress_capacity = (10 - current_state.stress_level) / 10.0
        
        # 2. 认知资源
        # 积极的核心信念有助于恢复
        belief_capacity = max(0, (cad.core_beliefs.self_belief + 10) / 20.0)
        hope_capacity = max(0, (cad.core_beliefs.future_belief + 10) / 20.0)
        
        # 3. 认知负担（负面认知加工降低恢复能力）
        rumination_burden = 1.0 - (cad.cognitive_processing.rumination / 10.0)
        distortion_burden = 1.0 - (cad.cognitive_processing.distortions / 10.0)
        
        # 4. 行为激活能力（低退缩和高动机有助恢复）
        activation_capacity = (
            (1.0 - cad.behavioral_inclination.social_withdrawal / 10.0) * 0.5 +
            (1.0 - cad.behavioral_inclination.avolition / 10.0) * 0.5
        )
        
        # 综合恢复能力
        total_capacity = (
            self_esteem_capacity * 0.2 +
            social_capacity * 0.2 +
            stress_capacity * 0.15 +
            belief_capacity * 0.15 +
            hope_capacity * 0.1 +
            rumination_burden * 0.1 +
            distortion_burden * 0.05 +
            activation_capacity * 0.05
        )
        
        return max(0.0, min(1.0, total_capacity))
    
    def _calculate_temporal_recovery_effect(self, positive_events: List[LifeEvent]) -> float:
        """计算时间分布的恢复效果"""
        
        if len(positive_events) < 2:
            return 0.5  # 单个事件默认中等时间效果
        
        # 分析事件时间分布
        event_times = []
        for event in positive_events:
            try:
                # 假设timestamp格式为datetime字符串
                event_time = datetime.fromisoformat(event.timestamp.replace('Z', '+00:00'))
                event_times.append(event_time)
            except:
                # 时间解析失败，使用当前时间
                event_times.append(datetime.now())
        
        event_times.sort()
        
        # 计算事件间隔
        intervals = []
        for i in range(1, len(event_times)):
            interval = (event_times[i] - event_times[i-1]).total_seconds() / 3600  # 小时
            intervals.append(interval)
        
        # 理想间隔：不太密集也不太稀疏
        ideal_interval = 24.0  # 24小时
        
        # 计算间隔质量分数
        interval_scores = []
        for interval in intervals:
            if interval <= 1:  # 太密集
                score = 0.3
            elif interval <= 12:  # 较好
                score = 0.8
            elif interval <= 48:  # 理想
                score = 1.0
            elif interval <= 168:  # 可接受（一周内）
                score = 0.6
            else:  # 太稀疏
                score = 0.2
            interval_scores.append(score)
        
        # 平均间隔质量
        avg_interval_quality = sum(interval_scores) / len(interval_scores) if interval_scores else 0.5
        
        # 连续性奖励：连续的积极事件有累积效果
        continuity_bonus = min(0.3, (len(positive_events) - 1) * 0.1)
        
        return min(1.0, avg_interval_quality + continuity_bonus)
    
    def apply_resilience_factors(self, current_state: PsychologicalState, 
                               recovery_potential: float) -> Dict:
        """应用心理弹性因子"""
        
        # 计算当前弹性水平
        current_resilience = self._calculate_current_resilience(current_state)
        
        # 弹性增长（通过积极经历）
        if recovery_potential > 0.6:
            resilience_growth = recovery_potential * self.resilience_growth_rate
            new_resilience = min(1.0, current_resilience + resilience_growth)
        else:
            # 弹性自然衰减
            new_resilience = max(0.1, current_resilience - self.resilience_decay_rate)
        
        # 弹性对恢复的放大效果
        resilience_amplification = 1.0 + (new_resilience * 0.5)
        
        # 计算弹性调整后的各项改善
        resilience_adjustments = {
            "depression_improvement": recovery_potential * 0.4 * resilience_amplification,
            "anxiety_improvement": recovery_potential * 0.3 * resilience_amplification,
            "self_esteem_improvement": recovery_potential * 0.5 * resilience_amplification,
            "social_connection_improvement": recovery_potential * 0.3 * resilience_amplification,
            "cad_improvements": self._calculate_cad_resilience_improvements(
                recovery_potential, resilience_amplification)
        }
        
        return {
            "current_resilience": current_resilience,
            "new_resilience": new_resilience,
            "resilience_amplification": resilience_amplification,
            "adjustments": resilience_adjustments
        }
    
    def _calculate_current_resilience(self, current_state: PsychologicalState) -> float:
        """计算当前心理弹性"""
        
        # 基于多个维度计算弹性
        cad = current_state.cad_state
        
        # 认知弹性
        cognitive_resilience = max(0, (cad.core_beliefs.self_belief + 10) / 20.0)
        
        # 情感弹性
        emotional_resilience = max(0, (cad.affective_tone + 10) / 20.0)
        
        # 行为弹性
        behavioral_resilience = 1.0 - ((cad.behavioral_inclination.social_withdrawal + 
                                       cad.behavioral_inclination.avolition) / 20.0)
        
        # 社会弹性
        social_resilience = current_state.social_connection / 10.0
        
        # 综合弹性
        total_resilience = (
            cognitive_resilience * 0.3 +
            emotional_resilience * 0.25 +
            behavioral_resilience * 0.25 +
            social_resilience * 0.2
        )
        
        return max(0.1, min(1.0, total_resilience))
    
    def _calculate_cad_resilience_improvements(self, recovery_potential: float, 
                                             resilience_amplification: float) -> Dict:
        """计算CAD状态的弹性改善"""
        
        base_improvement = recovery_potential * resilience_amplification
        
        return {
            "self_belief_improvement": base_improvement * 0.4,
            "world_belief_improvement": base_improvement * 0.3,
            "future_belief_improvement": base_improvement * 0.5,
            "affective_tone_improvement": base_improvement * 0.3,
            "rumination_reduction": base_improvement * 0.3,
            "distortion_reduction": base_improvement * 0.2,
            "social_withdrawal_reduction": base_improvement * 0.4,
            "avolition_reduction": base_improvement * 0.5
        }
    
    def track_improvement_momentum(self, state_history: List[Dict]) -> float:
        """跟踪改善动量"""
        
        if len(state_history) < 2:
            return 0.0
        
        # 分析最近的状态变化趋势
        recent_states = state_history[-5:]  # 最近5个状态
        
        momentum_indicators = []
        
        for i in range(1, len(recent_states)):
            prev_state = recent_states[i-1]
            curr_state = recent_states[i]
            
            # 计算各维度的改善情况
            depression_change = self._get_depression_change(prev_state, curr_state)
            stress_change = prev_state.get("stress_level", 5) - curr_state.get("stress_level", 5)
            self_esteem_change = curr_state.get("self_esteem", 5) - prev_state.get("self_esteem", 5)
            
            # CAD状态改善
            cad_improvement = self._calculate_cad_momentum(prev_state, curr_state)
            
            # 综合改善指标
            total_improvement = (
                depression_change * 0.3 +
                stress_change * 0.2 +
                self_esteem_change * 0.2 +
                cad_improvement * 0.3
            )
            
            momentum_indicators.append(total_improvement)
        
        # 计算改善动量（考虑趋势和一致性）
        if not momentum_indicators:
            return 0.0
        
        # 平均改善程度
        avg_improvement = sum(momentum_indicators) / len(momentum_indicators)
        
        # 一致性奖励（连续改善）
        consistency_bonus = 0.0
        positive_changes = sum(1 for change in momentum_indicators if change > 0)
        if positive_changes == len(momentum_indicators):
            consistency_bonus = 0.3
        elif positive_changes >= len(momentum_indicators) * 0.7:
            consistency_bonus = 0.1
        
        final_momentum = avg_improvement + consistency_bonus
        
        return max(0.0, min(1.0, final_momentum))
    
    def _get_depression_change(self, prev_state: Dict, curr_state: Dict) -> float:
        """计算抑郁程度变化"""
        
        # 获取抑郁级别数值
        prev_depression = self._depression_level_to_value(
            prev_state.get("depression_level", "HEALTHY"))
        curr_depression = self._depression_level_to_value(
            curr_state.get("depression_level", "HEALTHY"))
        
        # 抑郁减轻为正值
        return (prev_depression - curr_depression) / 9.0  # 归一化
    
    def _depression_level_to_value(self, level_name: str) -> int:
        """将抑郁级别名称转换为数值"""
        level_mapping = {
            "OPTIMAL": 0,
            "HEALTHY": 1,
            "MINIMAL_SYMPTOMS": 2,
            "MILD_RISK": 3,
            "MILD": 4,
            "MODERATE_MILD": 5,
            "MODERATE": 6,
            "MODERATE_SEVERE": 7,
            "SEVERE": 8,
            "CRITICAL": 9
        }
        return level_mapping.get(level_name, 4)  # 默认MILD
    
    def _calculate_cad_momentum(self, prev_state: Dict, curr_state: Dict) -> float:
        """计算CAD状态改善动量"""
        
        def get_cad_value(state_dict: Dict, path: str, default: float = 0.0) -> float:
            try:
                parts = path.split('.')
                value = state_dict
                for part in parts:
                    value = value[part]
                return float(value)
            except:
                return default
        
        # 核心信念改善
        prev_self = get_cad_value(prev_state, "cad_state.core_beliefs.self_belief")
        curr_self = get_cad_value(curr_state, "cad_state.core_beliefs.self_belief")
        self_improvement = (curr_self - prev_self) / 20.0  # 归一化
        
        prev_world = get_cad_value(prev_state, "cad_state.core_beliefs.world_belief")
        curr_world = get_cad_value(curr_state, "cad_state.core_beliefs.world_belief")
        world_improvement = (curr_world - prev_world) / 20.0
        
        prev_future = get_cad_value(prev_state, "cad_state.core_beliefs.future_belief")
        curr_future = get_cad_value(curr_state, "cad_state.core_beliefs.future_belief")
        future_improvement = (curr_future - prev_future) / 20.0
        
        # 情感基调改善
        prev_tone = get_cad_value(prev_state, "cad_state.affective_tone")
        curr_tone = get_cad_value(curr_state, "cad_state.affective_tone")
        tone_improvement = (curr_tone - prev_tone) / 20.0
        
        # 负面认知加工减少
        prev_rum = get_cad_value(prev_state, "cad_state.cognitive_processing.rumination")
        curr_rum = get_cad_value(curr_state, "cad_state.cognitive_processing.rumination")
        rumination_reduction = (prev_rum - curr_rum) / 10.0
        
        # 综合CAD改善
        cad_improvement = (
            self_improvement * 0.3 +
            world_improvement * 0.2 +
            future_improvement * 0.2 +
            tone_improvement * 0.2 +
            rumination_reduction * 0.1
        )
        
        return max(0.0, cad_improvement)
    
    def generate_recovery_plan(self, current_state: PsychologicalState, 
                             recovery_potential: float) -> Dict:
        """生成个性化恢复计划"""
        
        # 分析当前状态的主要问题
        problem_areas = self._identify_problem_areas(current_state)
        
        # 基于恢复潜力制定计划
        plan_intensity = "轻度" if recovery_potential < 0.3 else "中度" if recovery_potential < 0.7 else "强化"
        
        # 生成具体恢复建议
        recovery_strategies = self._generate_recovery_strategies(problem_areas, plan_intensity)
        
        # 预期恢复时间
        estimated_recovery_time = self._estimate_recovery_time(current_state, recovery_potential)
        
        return {
            "current_state_analysis": problem_areas,
            "recovery_potential": recovery_potential,
            "plan_intensity": plan_intensity,
            "recovery_strategies": recovery_strategies,
            "estimated_recovery_time": estimated_recovery_time,
            "monitoring_indicators": self._get_monitoring_indicators(),
            "risk_factors": self._identify_risk_factors(current_state)
        }
    
    def _identify_problem_areas(self, current_state: PsychologicalState) -> Dict:
        """识别主要问题领域"""
        
        cad = current_state.cad_state
        problems = {}
        
        # 抑郁症状
        if current_state.depression_level.value >= 4:
            problems["depression"] = {
                "severity": "严重" if current_state.depression_level.value >= 7 else "中等",
                "priority": "high"
            }
        
        # 核心信念问题
        if cad.core_beliefs.self_belief < -3:
            problems["self_belief"] = {
                "severity": "负面自我观念",
                "priority": "high"
            }
        
        # 认知加工问题
        if cad.cognitive_processing.rumination > 6:
            problems["rumination"] = {
                "severity": "过度反刍思维",
                "priority": "medium"
            }
        
        # 行为问题
        if cad.behavioral_inclination.social_withdrawal > 6:
            problems["social_isolation"] = {
                "severity": "社交退缩",
                "priority": "medium"
            }
        
        if cad.behavioral_inclination.avolition > 6:
            problems["motivation"] = {
                "severity": "动机缺失",
                "priority": "high"
            }
        
        return problems
    
    def _generate_recovery_strategies(self, problem_areas: Dict, intensity: str) -> List[Dict]:
        """生成恢复策略"""
        
        strategies = []
        
        # 基于问题区域生成策略
        if "depression" in problem_areas:
            strategies.append({
                "type": "behavioral_activation",
                "description": "逐步增加愉快活动",
                "frequency": "每日" if intensity == "强化" else "每周3次",
                "duration": "30-60分钟"
            })
        
        if "self_belief" in problem_areas:
            strategies.append({
                "type": "cognitive_restructuring",
                "description": "挑战负面自我观念",
                "frequency": "每日记录积极体验",
                "duration": "15-30分钟"
            })
        
        if "rumination" in problem_areas:
            strategies.append({
                "type": "mindfulness",
                "description": "正念练习减少反刍",
                "frequency": "每日",
                "duration": "10-20分钟"
            })
        
        if "social_isolation" in problem_areas:
            strategies.append({
                "type": "social_activation",
                "description": "逐步增加社交接触",
                "frequency": "每周2-3次",
                "duration": "30分钟以上"
            })
        
        if "motivation" in problem_areas:
            strategies.append({
                "type": "goal_setting",
                "description": "设定小而具体的目标",
                "frequency": "每周制定新目标",
                "duration": "持续跟踪"
            })
        
        return strategies
    
    def _estimate_recovery_time(self, current_state: PsychologicalState, 
                              recovery_potential: float) -> Dict:
        """估计恢复时间"""
        
        # 基于抑郁严重程度和恢复潜力
        severity = current_state.depression_level.value
        
        base_weeks = severity * 2  # 基础恢复周数
        
        # 恢复潜力调整
        potential_adjustment = (1.0 - recovery_potential) * 0.5
        adjusted_weeks = base_weeks * (1 + potential_adjustment)
        
        return {
            "estimated_weeks": int(adjusted_weeks),
            "confidence": "高" if recovery_potential > 0.7 else "中" if recovery_potential > 0.4 else "低",
            "factors": f"基于当前严重程度({severity})和恢复潜力({recovery_potential:.2f})"
        }
    
    def _get_monitoring_indicators(self) -> List[str]:
        """获取监控指标"""
        return [
            "日常活动参与度",
            "社交互动频率",
            "睡眠质量",
            "食欲变化",
            "情绪波动",
            "负面思维频率",
            "自我效能感",
            "希望感水平"
        ]
    
    def _identify_risk_factors(self, current_state: PsychologicalState) -> List[str]:
        """识别风险因素"""
        
        risk_factors = []
        cad = current_state.cad_state
        
        if current_state.stress_level > 8:
            risk_factors.append("高压力水平")
        
        if current_state.social_connection < 3:
            risk_factors.append("社会支持不足")
        
        if cad.core_beliefs.future_belief < -5:
            risk_factors.append("极度悲观的未来观")
        
        if cad.cognitive_processing.rumination > 8:
            risk_factors.append("严重反刍思维")
        
        if cad.behavioral_inclination.avolition > 8:
            risk_factors.append("严重动机缺失")
        
        return risk_factors
    
    def get_positive_impact_statistics(self) -> Dict:
        """获取积极影响统计"""
        
        return {
            "recovery_history_count": len(self.recovery_history),
            "current_momentum_counter": self.positive_momentum_counter,
            "last_positive_event": self.last_positive_event_time.isoformat() if self.last_positive_event_time else None,
            "configuration": {
                "recovery_amplification": self.recovery_amplification,
                "momentum_threshold": self.momentum_threshold,
                "social_support_weight": self.social_support_weight,
                "achievement_weight": self.achievement_weight,
                "self_efficacy_weight": self.self_efficacy_weight
            }
        }