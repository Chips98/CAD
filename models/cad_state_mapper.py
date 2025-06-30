#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CAD-MD状态映射工具
为认知-情感动力学模型提供分数到文本的映射和综合分析功能
"""

from typing import Dict, List, Any, Union
from models.psychology_models import CognitiveAffectiveState, CoreBeliefs, CognitiveProcessing, BehavioralInclination

class CADStateMapper:
    """CAD状态映射器"""
    
    @staticmethod
    def map_cad_scores_to_labels(cad_state: CognitiveAffectiveState) -> Dict[str, str]:
        """将CAD状态的所有分数转换为可读标签"""
        return {
            "affective_tone_label": CADStateMapper._map_affective_tone(cad_state.affective_tone),
            "self_belief_label": CADStateMapper._map_belief_score(cad_state.core_beliefs.self_belief, "self"),
            "world_belief_label": CADStateMapper._map_belief_score(cad_state.core_beliefs.world_belief, "world"),
            "future_belief_label": CADStateMapper._map_belief_score(cad_state.core_beliefs.future_belief, "future"),
            "rumination_label": CADStateMapper._map_rumination(cad_state.cognitive_processing.rumination),
            "distortions_label": CADStateMapper._map_distortions(cad_state.cognitive_processing.distortions),
            "social_withdrawal_label": CADStateMapper._map_social_withdrawal(cad_state.behavioral_inclination.social_withdrawal),
            "avolition_label": CADStateMapper._map_avolition(cad_state.behavioral_inclination.avolition)
        }
    
    @staticmethod
    def generate_therapist_analysis(cad_state: CognitiveAffectiveState, patient_name: str = "患者") -> str:
        """为治疗师生成专业的CAD状态分析"""
        labels = CADStateMapper.map_cad_scores_to_labels(cad_state)
        
        analysis = f"""
=== {patient_name}的认知-情感动力学状态分析 ===

【情感基调】
{labels['affective_tone_label']}
(数值: {cad_state.affective_tone:.1f}/10，{CADStateMapper._get_severity_level(cad_state.affective_tone, is_bipolar=True)})

【核心信念系统 - 贝克认知三角】
🧠 自我信念: {labels['self_belief_label']}
   (数值: {cad_state.core_beliefs.self_belief:.1f}/10，{CADStateMapper._get_severity_level(cad_state.core_beliefs.self_belief, is_bipolar=True)})

🌍 世界信念: {labels['world_belief_label']} 
   (数值: {cad_state.core_beliefs.world_belief:.1f}/10，{CADStateMapper._get_severity_level(cad_state.core_beliefs.world_belief, is_bipolar=True)})

🔮 未来信念: {labels['future_belief_label']}
   (数值: {cad_state.core_beliefs.future_belief:.1f}/10，{CADStateMapper._get_severity_level(cad_state.core_beliefs.future_belief, is_bipolar=True)})

【认知加工模式】
🔄 思维反刍: {labels['rumination_label']}
   (数值: {cad_state.cognitive_processing.rumination:.1f}/10，{CADStateMapper._get_severity_level(cad_state.cognitive_processing.rumination)})

❌ 认知扭曲: {labels['distortions_label']}
   (数值: {cad_state.cognitive_processing.distortions:.1f}/10，{CADStateMapper._get_severity_level(cad_state.cognitive_processing.distortions)})

【行为倾向】
🏠 社交退缩: {labels['social_withdrawal_label']}
   (数值: {cad_state.behavioral_inclination.social_withdrawal:.1f}/10，{CADStateMapper._get_severity_level(cad_state.behavioral_inclination.social_withdrawal)})

😶 动机降低: {labels['avolition_label']}
   (数值: {cad_state.behavioral_inclination.avolition:.1f}/10，{CADStateMapper._get_severity_level(cad_state.behavioral_inclination.avolition)})

【治疗建议】
{CADStateMapper._generate_treatment_recommendations(cad_state)}
        """.strip()
        return analysis
    
    @staticmethod
    def generate_patient_prompt_analysis(cad_data: Union[CognitiveAffectiveState, Dict]) -> str:
        """为AI患者生成内在心理状态描述
        
        Args:
            cad_data: 可以是CognitiveAffectiveState对象或字典格式的CAD数据
        """
        # 如果是字典格式，先安全提取数据
        if isinstance(cad_data, dict):
            # 安全提取各个维度的数据，避免KeyError
            affective_tone = cad_data.get('affective_tone', 0.0)
            
            core_beliefs_dict = cad_data.get('core_beliefs', {})
            self_belief = core_beliefs_dict.get('self_belief', 0.0)
            world_belief = core_beliefs_dict.get('world_belief', 0.0)
            future_belief = core_beliefs_dict.get('future_belief', 0.0)
            
            cognitive_processing_dict = cad_data.get('cognitive_processing', {})
            rumination = cognitive_processing_dict.get('rumination', 0.0)
            distortions = cognitive_processing_dict.get('distortions', 0.0)
            
            behavioral_inclination_dict = cad_data.get('behavioral_inclination', {})
            social_withdrawal = behavioral_inclination_dict.get('social_withdrawal', 0.0)
            avolition = behavioral_inclination_dict.get('avolition', 0.0)
            
        else:
            # 如果是CognitiveAffectiveState对象，直接访问属性
            affective_tone = cad_data.affective_tone
            self_belief = cad_data.core_beliefs.self_belief
            world_belief = cad_data.core_beliefs.world_belief
            future_belief = cad_data.core_beliefs.future_belief
            rumination = cad_data.cognitive_processing.rumination
            distortions = cad_data.cognitive_processing.distortions
            social_withdrawal = cad_data.behavioral_inclination.social_withdrawal
            avolition = cad_data.behavioral_inclination.avolition
        
        # 使用提取的数据生成分析
        return f"""
=== 你的内在认知世界深度分析 ===

你必须基于以下深层心理状态进行角色扮演：

【情感底色】你的整体情感基调是 {CADStateMapper._map_affective_tone(affective_tone)}

【核心信念】这些是你最深层的、自动化的想法：
- 关于自己: {CADStateMapper._map_belief_score(self_belief, "self")}
- 关于世界: {CADStateMapper._map_belief_score(world_belief, "world")}  
- 关于未来: {CADStateMapper._map_belief_score(future_belief, "future")}

【思维模式】
- 你{CADStateMapper._map_rumination(rumination)}
- 你{CADStateMapper._map_distortions(distortions)}

【行为特征】
- 社交方面: 你{CADStateMapper._map_social_withdrawal(social_withdrawal)}
- 动机方面: 你{CADStateMapper._map_avolition(avolition)}

请严格按照这些深层认知状态来回应治疗师，让你的回答体现出这些内在的信念和思维模式。
        """.strip()
    
    @staticmethod
    def identify_treatment_priorities(cad_state: CognitiveAffectiveState) -> List[str]:
        """识别治疗优先级"""
        priorities = []
        
        # 基于分数识别最需要干预的领域
        if cad_state.core_beliefs.self_belief < -5:
            priorities.append("自我信念重构（CBT核心信念干预）")
        
        if cad_state.cognitive_processing.rumination > 7:
            priorities.append("思维反刍控制（正念疗法/反刍中断技术）")
        
        if cad_state.behavioral_inclination.social_withdrawal > 7:
            priorities.append("社交行为激活（行为激活疗法）")
        
        if cad_state.behavioral_inclination.avolition > 7:
            priorities.append("动机激活（快乐活动安排）")
        
        if cad_state.core_beliefs.world_belief < -6:
            priorities.append("世界观重建（认知重构）")
        
        if cad_state.core_beliefs.future_belief < -7:
            priorities.append("希望重建（未来导向治疗）")
        
        return priorities[:3]  # 返回前3个最重要的
    
    # ===== 私有映射方法 =====
    
    @staticmethod
    def _map_affective_tone(score: float) -> str:
        if score >= 6: return "整体心境非常积极乐观"
        elif score >= 3: return "心境总体积极"
        elif score >= 1: return "心境偏向积极"
        elif score >= -1: return "心境基本中性"
        elif score >= -3: return "心境偏向悲观"
        elif score >= -6: return "心境总体悲观"
        else: return "心境极度悲观消极"
    
    @staticmethod
    def _map_belief_score(score: float, belief_type: str) -> str:
        if belief_type == "self":
            if score >= 6: return "我非常有价值，有能力应对挑战"
            elif score >= 3: return "我总体上是ok的，有一些优点"
            elif score >= 1: return "我基本可以接受自己"
            elif score >= -1: return "我对自己的看法比较中性"
            elif score >= -3: return "我经常觉得自己不够好"
            elif score >= -6: return "我觉得自己很多方面都有问题"
            else: return "我觉得自己毫无价值，完全没用"
        elif belief_type == "world":
            if score >= 6: return "世界充满机会，人们总体是善良的"
            elif score >= 3: return "世界虽有问题但总体是公平的"
            elif score >= 1: return "世界是复杂的，但还是有希望的"
            elif score >= -1: return "世界有好有坏，比较复杂"
            elif score >= -3: return "世界经常让人失望"
            elif score >= -6: return "世界充满困难和不公"
            else: return "世界是残酷的，到处都是危险和敌意"
        else:  # future
            if score >= 6: return "未来肯定会很美好，充满可能性"
            elif score >= 3: return "未来基本上是光明的"
            elif score >= 1: return "未来还是有希望的"
            elif score >= -1: return "未来不确定，但不算太坏"
            elif score >= -3: return "未来可能会有困难"
            elif score >= -6: return "未来很可能会很糟糕"
            else: return "未来是绝望的，没有任何意义"
    
    @staticmethod
    def _map_rumination(score: float) -> str:
        if score < 2: return "很少陷入负面思维循环"
        elif score < 4: return "偶尔会反复思考负面的事情"
        elif score < 6: return "经常重复思考负面事件和情绪"
        elif score < 8: return "严重的负性思维反刍，很难停下来"
        else: return "极度严重的反刍思维，几乎无法自控"
    
    @staticmethod
    def _map_distortions(score: float) -> str:
        if score < 2: return "思维基本客观理性"
        elif score < 4: return "偶尔会有思维偏差"
        elif score < 6: return "存在明显的认知扭曲模式"
        elif score < 8: return "严重的认知扭曲，很难看到客观事实"
        else: return "极度扭曲的思维方式，完全偏离现实"
    
    @staticmethod
    def _map_social_withdrawal(score: float) -> str:
        if score < 2: return "积极参与社交活动，享受与人交往"
        elif score < 4: return "社交活动略有减少，但还是愿意参与"
        elif score < 6: return "明显回避社交活动，与人保持距离"
        elif score < 8: return "严重社交退缩，很少与人接触"
        else: return "几乎完全孤立自己，拒绝所有社交"
    
    @staticmethod
    def _map_avolition(score: float) -> str:
        if score < 2: return "对生活充满动力和兴趣"
        elif score < 4: return "动机和兴趣有所下降，但还可以"
        elif score < 6: return "明显缺乏动机，对很多事情失去兴趣"
        elif score < 8: return "严重的动机缺失，几乎不想做任何事"
        else: return "完全失去动机，快感缺失，对一切都提不起兴趣"
    
    @staticmethod
    def _get_severity_level(score: float, is_bipolar: bool = False) -> str:
        """获取严重程度标签"""
        if is_bipolar:  # 双极性评分 (-10 to 10)
            abs_score = abs(score)
            if abs_score < 2: return "正常范围"
            elif abs_score < 4: return "轻度"
            elif abs_score < 6: return "中度"
            elif abs_score < 8: return "重度"
            else: return "极重度"
        else:  # 单极性评分 (0 to 10)
            if score < 2: return "正常"
            elif score < 4: return "轻度"
            elif score < 6: return "中度"
            elif score < 8: return "重度"
            else: return "极重度"
    
    @staticmethod
    def _generate_treatment_recommendations(cad_state: CognitiveAffectiveState) -> str:
        """生成治疗建议"""
        recommendations = []
        
        # 基于具体状态给出针对性建议
        if cad_state.core_beliefs.self_belief < -4:
            recommendations.append("🎯 优先进行自我信念重构，使用CBT认知三角技术")
        
        if cad_state.cognitive_processing.rumination > 6:
            recommendations.append("🧘 引入正念技术，打破思维反刍循环")
        
        if cad_state.behavioral_inclination.social_withdrawal > 6:
            recommendations.append("👥 实施行为激活疗法，逐步增加社交活动")
        
        if cad_state.behavioral_inclination.avolition > 6:
            recommendations.append("⚡ 设置小目标，重建快乐体验和成就感")
        
        if cad_state.affective_tone < -5:
            recommendations.append("🌅 考虑情绪调节技术，改善整体情感基调")
        
        if not recommendations:
            recommendations.append("✅ 当前状态相对稳定，专注于维持和巩固治疗成果")
        
        return "\n".join(recommendations) 