#!/usr/bin/env python3
"""
LLM增强功能测试脚本
测试所有新增的LLM组件是否正常工作
"""

import asyncio
import sys
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入所需模块
from models.psychology_models import PsychologicalState, LifeEvent, EventType, EmotionState, DepressionLevel
from core.llm_event_generator import LLMEventGenerator
from core.llm_psychological_assessor import LLMPsychologicalAssessor
from core.hybrid_impact_calculator import HybridImpactCalculator
from core.positive_impact_manager import PositiveImpactManager
from core.probabilistic_impact import ProbabilisticImpactModel
from core.llm_therapy_enhancer import LLMTherapyEnhancer


class MockAIClient:
    """模拟AI客户端，用于测试"""
    
    async def generate_response(self, prompt: str) -> str:
        """模拟LLM响应"""
        
        if "事件生成" in prompt or "generate_contextual_event" in prompt:
            return """
            {
              "description": "李明在数学课上回答问题得到老师表扬",
              "participants": ["李明", "王老师"],
              "impact_score": 3,
              "emotional_intensity": 0.6,
              "category": "academic"
            }
            """
        
        elif "心理影响评估" in prompt or "depression_adjustment" in prompt:
            return """
            {
              "depression_adjustment": -0.5,
              "anxiety_adjustment": -0.3,
              "self_esteem_adjustment": 0.8,
              "self_belief_adjustment": 0.6,
              "world_belief_adjustment": 0.2,
              "future_belief_adjustment": 0.4,
              "rumination_adjustment": -0.2,
              "distortion_adjustment": -0.1,
              "social_withdrawal_adjustment": -0.3,
              "avolition_adjustment": -0.4,
              "confidence_level": 0.8,
              "reasoning": "这是一个积极的学术认可事件，有助于提升自尊和自我信念",
              "risk_indicators": [],
              "protective_factors": ["老师认可", "学术成就"]
            }
            """
        
        elif "对话分析" in prompt or "therapeutic_alliance" in prompt:
            return """
            {
              "therapeutic_alliance": 7.5,
              "patient_openness": 6.8,
              "engagement_level": 7.2,
              "emotional_tone": "积极",
              "progress_indicators": ["主动分享", "情绪稳定"],
              "risk_indicators": [],
              "recommendations": ["继续当前治疗方向", "增加行为激活"]
            }
            """
        
        elif "治疗回应" in prompt or "therapeutic_response" in prompt:
            return """
            {
              "content": "我能感受到你在这件事上的进步，这种被认可的感觉对你来说意味着什么？",
              "response_type": "exploratory",
              "therapeutic_techniques": ["cognitive_restructuring", "emotion_regulation"],
              "expected_impact": {
                "emotional_support": 0.7,
                "insight_promotion": 0.8,
                "behavioral_change": 0.5
              },
              "confidence": 0.85,
              "reasoning": "通过探索意义来强化积极体验"
            }
            """
        
        else:
            return "这是一个模拟的AI响应用于测试。"


async def test_llm_event_generator():
    """测试LLM事件生成器"""
    print("\n=== 测试 LLM事件生成器 ===")
    
    try:
        ai_client = MockAIClient()
        generator = LLMEventGenerator(ai_client)
        
        # 测试上下文事件生成
        context = {
            "protagonist_state": {
                "stress_level": 6,
                "depression_level": "MILD"
            },
            "recent_events": [],
            "scenario_name": "primary_school_bullying"
        }
        
        event_data = await generator.generate_contextual_event(context, "positive")
        print(f"✓ 生成事件: {event_data['description']}")
        print(f"  参与者: {event_data['participants']}")
        print(f"  影响分数: {event_data['impact_score']}")
        
        return True
        
    except Exception as e:
        print(f"✗ LLM事件生成器测试失败: {e}")
        return False


async def test_llm_psychological_assessor():
    """测试LLM心理状态评估器"""
    print("\n=== 测试 LLM心理状态评估器 ===")
    
    try:
        ai_client = MockAIClient()
        assessor = LLMPsychologicalAssessor(ai_client)
        
        # 创建测试事件和状态
        event = LifeEvent(
            event_type=EventType.ACADEMIC_FAILURE,
            description="数学考试成绩不理想",
            impact_score=-3,
            timestamp=datetime.now().isoformat(),
            participants=["李明"]
        )
        
        state = PsychologicalState(
            emotion=EmotionState.NEUTRAL,
            depression_level=DepressionLevel.MILD,
            stress_level=6,
            self_esteem=4,
            social_connection=5,
            academic_pressure=7
        )
        
        assessment = await assessor.assess_event_impact(event, state)
        print(f"✓ 评估完成")
        print(f"  抑郁调整: {assessment.depression_adjustment}")
        print(f"  自尊调整: {assessment.self_esteem_adjustment}")
        print(f"  置信度: {assessment.confidence_level}")
        print(f"  推理: {assessment.reasoning[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ LLM心理状态评估器测试失败: {e}")
        return False


async def test_hybrid_impact_calculator():
    """测试混合影响计算器"""
    print("\n=== 测试 混合影响计算器 ===")
    
    try:
        ai_client = MockAIClient()
        calculator = HybridImpactCalculator(ai_client)
        
        # 创建测试数据
        event = LifeEvent(
            event_type=EventType.ACADEMIC_FAILURE,
            description="获得老师表扬",
            impact_score=4,
            timestamp=datetime.now().isoformat(),
            participants=["李明", "老师"]
        )
        
        state = PsychologicalState(
            emotion=EmotionState.NEUTRAL,
            depression_level=DepressionLevel.MILD,
            stress_level=5,
            self_esteem=6,
            social_connection=5,
            academic_pressure=6
        )
        
        impact_result = await calculator.calculate_comprehensive_impact(event, state)
        print(f"✓ 混合影响计算完成")
        print(f"  总影响: {impact_result['total_impact']:.2f}")
        print(f"  计算方法: {impact_result['calculation_method']}")
        
        if 'llm_confidence' in impact_result:
            print(f"  LLM置信度: {impact_result['llm_confidence']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"✗ 混合影响计算器测试失败: {e}")
        return False


def test_positive_impact_manager():
    """测试积极影响管理器"""
    print("\n=== 测试 积极影响管理器 ===")
    
    try:
        manager = PositiveImpactManager()
        
        # 创建积极事件列表
        positive_events = [
            LifeEvent(
                event_type=EventType.ACADEMIC_FAILURE,
                description="获得老师表扬",
                impact_score=3,
                timestamp=datetime.now().isoformat(),
                participants=["李明", "老师"]
            ),
            LifeEvent(
                event_type=EventType.SOCIAL_REJECTION,
                description="和朋友一起玩游戏",
                impact_score=2,
                timestamp=datetime.now().isoformat(),
                participants=["李明", "小明"]
            )
        ]
        
        state = PsychologicalState(
            emotion=EmotionState.SAD,
            depression_level=DepressionLevel.MILD,
            stress_level=6,
            self_esteem=4,
            social_connection=5,
            academic_pressure=7
        )
        
        # 计算恢复潜力
        recovery_potential = manager.calculate_recovery_potential(positive_events, state)
        print(f"✓ 恢复潜力计算完成: {recovery_potential:.2f}")
        
        # 应用心理弹性因子
        resilience_result = manager.apply_resilience_factors(state, recovery_potential)
        print(f"  当前弹性: {resilience_result['current_resilience']:.2f}")
        print(f"  新弹性: {resilience_result['new_resilience']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"✗ 积极影响管理器测试失败: {e}")
        return False


def test_probabilistic_impact():
    """测试概率性影响模型"""
    print("\n=== 测试 概率性影响模型 ===")
    
    try:
        model = ProbabilisticImpactModel()
        
        base_impact = 3.0
        
        # 测试正态变异
        varied_impact = model.apply_normal_variation(base_impact)
        print(f"✓ 正态变异: {base_impact} -> {varied_impact:.2f}")
        
        # 测试极端事件分布
        extreme_impact = model.apply_extreme_event_distribution(base_impact)
        print(f"  极端事件分布: {base_impact} -> {extreme_impact:.2f}")
        
        # 测试个体差异
        personality = {"neuroticism": 7, "extraversion": 4}
        individual_impact = model.apply_individual_variance(base_impact, personality)
        print(f"  个体差异调整: {base_impact} -> {individual_impact:.2f}")
        
        return True
        
    except Exception as e:
        print(f"✗ 概率性影响模型测试失败: {e}")
        return False


async def test_llm_therapy_enhancer():
    """测试LLM治疗增强器"""
    print("\n=== 测试 LLM治疗增强器 ===")
    
    try:
        ai_client = MockAIClient()
        enhancer = LLMTherapyEnhancer(ai_client)
        
        # 创建测试数据
        dialogue_history = [
            {"speaker": "患者", "content": "我最近心情不太好"},
            {"speaker": "治疗师", "content": "能告诉我具体发生了什么吗？"},
            {"speaker": "患者", "content": "考试没考好，觉得自己很笨"}
        ]
        
        state = PsychologicalState(
            emotion=EmotionState.SAD,
            depression_level=DepressionLevel.MILD,
            stress_level=7,
            self_esteem=3,
            social_connection=4,
            academic_pressure=8
        )
        
        # 测试对话分析
        analysis = await enhancer.analyze_conversation(dialogue_history, state)
        print(f"✓ 对话分析完成")
        print(f"  治疗联盟: {analysis.therapeutic_alliance:.1f}/10")
        print(f"  患者开放程度: {analysis.patient_openness:.1f}/10")
        print(f"  情感基调: {analysis.emotional_tone}")
        
        # 测试治疗回应生成
        response = await enhancer.generate_therapeutic_response(
            "我觉得自己很失败", state, dialogue_history, analysis
        )
        print(f"  治疗回应: {response.content}")
        print(f"  回应类型: {response.response_type}")
        print(f"  使用技术: {response.therapeutic_techniques}")
        
        return True
        
    except Exception as e:
        print(f"✗ LLM治疗增强器测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("开始LLM增强功能集成测试...")
    print("=" * 50)
    
    test_results = []
    
    # 运行所有测试
    test_results.append(await test_llm_event_generator())
    test_results.append(await test_llm_psychological_assessor())
    test_results.append(await test_hybrid_impact_calculator())
    test_results.append(test_positive_impact_manager())
    test_results.append(test_probabilistic_impact())
    test_results.append(await test_llm_therapy_enhancer())
    
    # 统计结果
    passed = sum(test_results)
    total = len(test_results)
    
    print("\n" + "=" * 50)
    print(f"测试完成: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有LLM增强功能测试通过！")
        return 0
    else:
        print(f"⚠️  有 {total - passed} 项测试失败")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)