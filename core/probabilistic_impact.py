"""
概率性影响模块 - 实现不确定性和随机性的心理影响建模
包含正态分布变异、极端事件分布、个体差异建模等
"""

import numpy as np
import random
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from scipy import stats
from dataclasses import dataclass

from models.psychology_models import PsychologicalState


@dataclass
class ProbabilityDistribution:
    """概率分布配置"""
    distribution_type: str  # "normal", "gamma", "beta", "uniform"
    parameters: Dict[str, float]
    bounds: Tuple[float, float] = (-10.0, 10.0)


class ProbabilisticImpactModel:
    """概率性影响模型"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 概率分布配置
        self.normal_variance_sigma = self.config.get("normal_variance_sigma", 0.3)
        self.extreme_event_probability = self.config.get("extreme_event_probability", 0.05)
        self.individual_variance_factor = self.config.get("individual_variance_factor", 0.2)
        
        # 分布参数
        self.impact_distributions = self._initialize_impact_distributions()
        self.personality_variance_map = self._initialize_personality_variance()
        
        # 随机种子控制
        self.random_seed = self.config.get("random_seed", None)
        if self.random_seed:
            np.random.seed(self.random_seed)
            random.seed(self.random_seed)
        
        # 概率性调整历史
        self.adjustment_history = []
        
        self.logger.info("概率性影响模型初始化完成")
    
    def _initialize_impact_distributions(self) -> Dict[str, ProbabilityDistribution]:
        """初始化影响分布"""
        
        return {
            "normal_impact": ProbabilityDistribution(
                distribution_type="normal",
                parameters={"mean": 1.0, "std": self.normal_variance_sigma},
                bounds=(0.1, 2.0)
            ),
            "extreme_negative": ProbabilityDistribution(
                distribution_type="gamma",
                parameters={"shape": 2.0, "scale": 1.5},
                bounds=(1.0, 5.0)
            ),
            "extreme_positive": ProbabilityDistribution(
                distribution_type="beta",
                parameters={"alpha": 2.0, "beta": 5.0},
                bounds=(0.5, 2.0)
            ),
            "stress_amplification": ProbabilityDistribution(
                distribution_type="normal",
                parameters={"mean": 1.0, "std": 0.4},
                bounds=(0.3, 2.5)
            )
        }
    
    def _initialize_personality_variance(self) -> Dict[str, float]:
        """初始化人格差异方差映射"""
        
        return {
            "openness": 0.15,      # 开放性影响对新体验的反应变异
            "conscientiousness": 0.10,  # 尽责性影响对成就事件的反应
            "extraversion": 0.20,  # 外向性影响对社交事件的反应
            "agreeableness": 0.12, # 宜人性影响对人际冲突的反应
            "neuroticism": 0.25    # 神经质影响对压力事件的反应
        }
    
    def apply_normal_variation(self, base_impact: float, 
                             variation_sigma: float = None) -> float:
        """应用正态分布变异"""
        
        if variation_sigma is None:
            variation_sigma = self.normal_variance_sigma
        
        # 生成正态分布的变异因子
        variation_factor = np.random.normal(1.0, variation_sigma)
        
        # 限制在合理范围内
        variation_factor = max(0.1, min(3.0, variation_factor))
        
        adjusted_impact = base_impact * variation_factor
        
        self.logger.debug(f"正态变异: {base_impact:.2f} -> {adjusted_impact:.2f} (因子: {variation_factor:.2f})")
        
        return adjusted_impact
    
    def apply_extreme_event_distribution(self, base_impact: float, 
                                       event_type: str = "normal") -> float:
        """应用极端事件分布"""
        
        # 判断是否触发极端事件
        if random.random() > self.extreme_event_probability:
            return base_impact  # 大部分情况下不触发极端事件
        
        # 根据事件类型选择分布
        if base_impact < 0:  # 负面事件
            distribution = self.impact_distributions["extreme_negative"]
            multiplier = self._sample_from_distribution(distribution)
            adjusted_impact = base_impact * multiplier  # 放大负面影响
        else:  # 正面事件
            distribution = self.impact_distributions["extreme_positive"]
            multiplier = self._sample_from_distribution(distribution)
            adjusted_impact = base_impact * multiplier
        
        self.logger.info(f"极端事件触发: {base_impact:.2f} -> {adjusted_impact:.2f}")
        
        return adjusted_impact
    
    def apply_individual_variance(self, base_impact: float, 
                                agent_personality: Dict) -> float:
        """基于个体人格差异应用变异"""
        
        if not agent_personality:
            return base_impact
        
        # 计算个体变异因子
        total_variance = 0.0
        variance_count = 0
        
        for trait, variance in self.personality_variance_map.items():
            if trait in agent_personality:
                trait_score = agent_personality[trait]
                # 将人格特质分数(通常0-10)转换为变异强度
                trait_variance = variance * (trait_score / 10.0)
                total_variance += trait_variance
                variance_count += 1
        
        if variance_count == 0:
            return base_impact
        
        # 平均个体变异
        avg_variance = total_variance / variance_count
        
        # 生成个体化的变异因子
        individual_factor = np.random.normal(1.0, avg_variance * self.individual_variance_factor)
        individual_factor = max(0.2, min(2.5, individual_factor))
        
        adjusted_impact = base_impact * individual_factor
        
        self.logger.debug(f"个体差异调整: {base_impact:.2f} -> {adjusted_impact:.2f}")
        
        return adjusted_impact
    
    def _sample_from_distribution(self, distribution: ProbabilityDistribution) -> float:
        """从指定分布中采样"""
        
        dist_type = distribution.distribution_type
        params = distribution.parameters
        bounds = distribution.bounds
        
        try:
            if dist_type == "normal":
                sample = np.random.normal(params["mean"], params["std"])
            elif dist_type == "gamma":
                sample = np.random.gamma(params["shape"], params["scale"])
            elif dist_type == "beta":
                sample = np.random.beta(params["alpha"], params["beta"])
                # Beta分布结果需要缩放到合适范围
                sample = sample * (bounds[1] - bounds[0]) + bounds[0]
            elif dist_type == "uniform":
                sample = np.random.uniform(bounds[0], bounds[1])
            else:
                self.logger.warning(f"未知分布类型: {dist_type}")
                sample = 1.0
            
            # 应用边界限制
            sample = max(bounds[0], min(bounds[1], sample))
            
            return sample
            
        except Exception as e:
            self.logger.error(f"分布采样失败: {e}")
            return 1.0
    
    def apply_stress_dependent_variance(self, base_impact: float, 
                                      current_state: PsychologicalState) -> float:
        """应用依赖于压力状态的变异"""
        
        stress_level = current_state.stress_level
        depression_score = current_state.cad_state.calculate_comprehensive_depression_score()
        
        # 高压力和抑郁状态下，反应变异性增加
        stress_factor = stress_level / 10.0
        depression_factor = depression_score / 27.0
        
        # 综合脆弱性因子
        vulnerability = (stress_factor * 0.6 + depression_factor * 0.4)
        
        # 脆弱性越高，变异性越大
        stress_variance = 0.1 + vulnerability * 0.4
        
        # 生成压力相关的变异
        stress_variation = np.random.normal(1.0, stress_variance)
        stress_variation = max(0.3, min(2.0, stress_variation))
        
        # 对负面事件的变异放大更明显
        if base_impact < 0:
            stress_variation = stress_variation ** (1 + vulnerability * 0.5)
        
        adjusted_impact = base_impact * stress_variation
        
        self.logger.debug(f"压力相关变异: {base_impact:.2f} -> {adjusted_impact:.2f} "
                         f"(脆弱性: {vulnerability:.2f})")
        
        return adjusted_impact
    
    def apply_temporal_uncertainty(self, base_impact: float, 
                                 time_context: Dict = None) -> float:
        """应用时间相关的不确定性"""
        
        if not time_context:
            return base_impact
        
        # 时间因素：早晨vs晚上，工作日vs周末等
        hour = time_context.get("hour", 12)
        is_weekend = time_context.get("is_weekend", False)
        season = time_context.get("season", "spring")
        
        # 昼夜节律影响
        circadian_factor = 1.0
        if 6 <= hour <= 10:  # 早晨
            circadian_factor = 1.1  # 轻微放大
        elif 14 <= hour <= 16:  # 下午低潮
            circadian_factor = 0.9
        elif 20 <= hour <= 23:  # 晚上
            circadian_factor = 1.2  # 情绪影响放大
        
        # 周末效应
        weekend_factor = 0.8 if is_weekend else 1.0
        
        # 季节效应
        seasonal_factors = {
            "spring": 1.0,
            "summer": 0.9,
            "autumn": 1.1,
            "winter": 1.2  # 冬季抑郁风险
        }
        seasonal_factor = seasonal_factors.get(season, 1.0)
        
        # 综合时间因子
        temporal_factor = circadian_factor * weekend_factor * seasonal_factor
        
        # 添加时间相关的随机性
        temporal_noise = np.random.normal(1.0, 0.1)
        final_factor = temporal_factor * temporal_noise
        
        adjusted_impact = base_impact * final_factor
        
        self.logger.debug(f"时间不确定性: {base_impact:.2f} -> {adjusted_impact:.2f}")
        
        return adjusted_impact
    
    def apply_social_context_variance(self, base_impact: float, 
                                    social_context: Dict = None) -> float:
        """应用社会情境变异"""
        
        if not social_context:
            return base_impact
        
        # 社会情境因素
        group_size = social_context.get("group_size", 1)
        authority_present = social_context.get("authority_present", False)
        peer_pressure = social_context.get("peer_pressure", 0.0)
        social_support = social_context.get("social_support", 0.5)
        
        # 群体规模效应
        if group_size > 1:
            group_factor = 1.0 + min(0.3, (group_size - 1) * 0.1)
        else:
            group_factor = 1.0
        
        # 权威在场效应
        authority_factor = 1.2 if authority_present else 1.0
        
        # 同伴压力效应
        pressure_factor = 1.0 + peer_pressure * 0.3
        
        # 社会支持缓冲效应
        support_buffer = 1.0 - social_support * 0.2
        
        # 综合社会因子
        social_factor = group_factor * authority_factor * pressure_factor * support_buffer
        
        # 社会情境随机性
        social_noise = np.random.normal(1.0, 0.15)
        final_factor = social_factor * social_noise
        
        adjusted_impact = base_impact * final_factor
        
        return adjusted_impact
    
    def generate_stochastic_trajectory(self, base_impacts: List[float], 
                                     time_steps: int = 30) -> List[float]:
        """生成随机轨迹"""
        
        trajectory = []
        
        for i in range(time_steps):
            if i < len(base_impacts):
                base_impact = base_impacts[i]
            else:
                # 使用最后一个值或生成新的基础影响
                base_impact = base_impacts[-1] if base_impacts else 0.0
            
            # 应用多层随机性
            stochastic_impact = base_impact
            
            # 正态变异
            stochastic_impact = self.apply_normal_variation(stochastic_impact)
            
            # 极端事件
            stochastic_impact = self.apply_extreme_event_distribution(stochastic_impact)
            
            # 时间相关随机行走
            if i > 0:
                momentum = trajectory[i-1] * 0.1  # 10%动量
                random_walk = np.random.normal(0, 0.2)
                stochastic_impact += momentum + random_walk
            
            trajectory.append(stochastic_impact)
        
        return trajectory
    
    def calculate_uncertainty_bounds(self, base_impact: float, 
                                   confidence_level: float = 0.95) -> Tuple[float, float]:
        """计算不确定性边界"""
        
        # 基于配置的总体不确定性
        total_variance = (self.normal_variance_sigma ** 2 + 
                         self.individual_variance_factor ** 2)
        
        # 计算置信区间
        z_score = stats.norm.ppf((1 + confidence_level) / 2)
        margin = z_score * np.sqrt(total_variance) * abs(base_impact)
        
        lower_bound = base_impact - margin
        upper_bound = base_impact + margin
        
        return (lower_bound, upper_bound)
    
    def simulate_monte_carlo(self, base_impact: float, 
                           context: Dict = None,
                           num_simulations: int = 1000) -> Dict:
        """蒙特卡洛模拟"""
        
        simulated_impacts = []
        
        for _ in range(num_simulations):
            impact = base_impact
            
            # 应用各种概率性调整
            impact = self.apply_normal_variation(impact)
            impact = self.apply_extreme_event_distribution(impact)
            
            if context:
                if "personality" in context:
                    impact = self.apply_individual_variance(impact, context["personality"])
                if "psychological_state" in context:
                    impact = self.apply_stress_dependent_variance(impact, context["psychological_state"])
                if "time_context" in context:
                    impact = self.apply_temporal_uncertainty(impact, context["time_context"])
                if "social_context" in context:
                    impact = self.apply_social_context_variance(impact, context["social_context"])
            
            simulated_impacts.append(impact)
        
        # 统计分析
        simulated_impacts = np.array(simulated_impacts)
        
        return {
            "mean": float(np.mean(simulated_impacts)),
            "std": float(np.std(simulated_impacts)),
            "median": float(np.median(simulated_impacts)),
            "percentile_5": float(np.percentile(simulated_impacts, 5)),
            "percentile_25": float(np.percentile(simulated_impacts, 25)),
            "percentile_75": float(np.percentile(simulated_impacts, 75)),
            "percentile_95": float(np.percentile(simulated_impacts, 95)),
            "min": float(np.min(simulated_impacts)),
            "max": float(np.max(simulated_impacts)),
            "simulations": simulated_impacts.tolist()
        }
    
    def record_adjustment(self, original_impact: float, 
                         adjusted_impact: float,
                         adjustment_type: str,
                         context: Dict = None):
        """记录概率性调整"""
        
        record = {
            "timestamp": datetime.now(),
            "original_impact": original_impact,
            "adjusted_impact": adjusted_impact,
            "adjustment_ratio": adjusted_impact / original_impact if original_impact != 0 else 1.0,
            "adjustment_type": adjustment_type,
            "context": context or {}
        }
        
        self.adjustment_history.append(record)
        
        # 保持历史记录在合理大小
        if len(self.adjustment_history) > 1000:
            self.adjustment_history = self.adjustment_history[-1000:]
    
    def get_probabilistic_statistics(self) -> Dict:
        """获取概率性统计信息"""
        
        if not self.adjustment_history:
            return {"total_adjustments": 0}
        
        adjustments = [record["adjustment_ratio"] for record in self.adjustment_history]
        
        return {
            "total_adjustments": len(self.adjustment_history),
            "adjustment_statistics": {
                "mean_ratio": float(np.mean(adjustments)),
                "std_ratio": float(np.std(adjustments)),
                "median_ratio": float(np.median(adjustments)),
                "min_ratio": float(np.min(adjustments)),
                "max_ratio": float(np.max(adjustments))
            },
            "extreme_events_triggered": len([r for r in self.adjustment_history 
                                           if abs(r["adjustment_ratio"] - 1.0) > 0.5]),
            "configuration": {
                "normal_variance_sigma": self.normal_variance_sigma,
                "extreme_event_probability": self.extreme_event_probability,
                "individual_variance_factor": self.individual_variance_factor
            }
        }
    
    def update_configuration(self, new_config: Dict):
        """更新配置"""
        
        self.normal_variance_sigma = new_config.get("normal_variance_sigma", self.normal_variance_sigma)
        self.extreme_event_probability = new_config.get("extreme_event_probability", self.extreme_event_probability)
        self.individual_variance_factor = new_config.get("individual_variance_factor", self.individual_variance_factor)
        
        # 重新初始化分布
        self.impact_distributions = self._initialize_impact_distributions()
        
        self.logger.info("概率性影响模型配置已更新")