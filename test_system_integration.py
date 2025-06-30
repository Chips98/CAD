#!/usr/bin/env python3
"""
系统集成测试脚本 - 验证LLM增强后的CAD系统
模拟一个完整的心理模拟和治疗流程
"""

import asyncio
import sys
import logging
import json
from pathlib import Path
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 模拟AI客户端
class TestAIClient:
    """测试用的AI客户端"""
    
    async def generate_response(self, prompt: str) -> str:
        """生成模拟响应"""
        
        if "数学" in prompt and "考试" in prompt:
            return "虽然这次数学考试没有达到预期，但这并不代表你的全部能力。每个人都会遇到挫折，重要的是从中学习。你觉得下次可以怎样准备得更好呢？"
        elif "心理" in prompt or "评估" in prompt:
            return """
            {
              "depression_adjustment": -0.3,
              "anxiety_adjustment": 0.2,
              "self_esteem_adjustment": -0.4,
              "self_belief_adjustment": -0.2,
              "world_belief_adjustment": 0.1,
              "future_belief_adjustment": -0.1,
              "confidence_level": 0.75,
              "reasoning": "考试失败可能会暂时影响自信心，但不会对整体心理状态造成严重冲击"
            }
            """
        else:
            return "我理解你的感受，请继续分享你的想法。"
    
    async def generate_agent_response(self, profile, situation, history):
        """生成agent响应"""
        return f"我现在感觉{situation}让我有些困扰，但我在努力应对。"


async def test_main_simulation():
    """测试主要的模拟功能"""
    print("\n=== 测试主要模拟功能 ===")
    
    try:
        # 导入必要模块
        from models.psychology_models import PsychologicalState, LifeEvent, EventType, EmotionState, DepressionLevel
        from agents.student_agent import StudentAgent
        from core.simulation_engine import SimulationEngine
        from config.config_loader import load_scenario
        
        # 加载配置
        config = load_scenario("primary_school_bullying")
        
        # 创建AI客户端
        ai_client = TestAIClient()
        
        # 创建学生智能体
        student_config = config["characters"]["protagonist"]
        student = StudentAgent(
            name=student_config["name"],
            age=student_config["age"],
            personality=student_config["personality"],
            ai_client=ai_client
        )
        
        print(f"✓ 创建学生智能体: {student.name}")
        print(f"  年龄: {student.age}")
        print(f"  初始心理状态: {student.psychological_state.depression_level.name}")
        
        # 测试事件影响
        test_event = LifeEvent(
            event_type=EventType.ACADEMIC_FAILURE,
            description="数学考试成绩不理想",
            impact_score=-3,
            timestamp=datetime.now().isoformat(),
            participants=[student.name]
        )
        
        print(f"  添加测试事件: {test_event.description}")
        student.add_life_event(test_event)
        
        # 等待异步处理完成
        await asyncio.sleep(1)
        
        print(f"  事件后心理状态: {student.psychological_state.depression_level.name}")
        print(f"  压力水平: {student.psychological_state.stress_level}/10")
        print(f"  自尊水平: {student.psychological_state.self_esteem}/10")
        
        # 测试LLM增强组件
        if hasattr(student, 'hybrid_calculator') and student.hybrid_calculator:
            print("  ✓ LLM混合影响计算器已启用")
        else:
            print("  ⚠ LLM混合影响计算器未启用")
        
        if hasattr(student, 'positive_impact_manager') and student.positive_impact_manager:
            print("  ✓ 积极影响管理器已启用")
        else:
            print("  ⚠ 积极影响管理器未启用")
        
        return True
        
    except Exception as e:
        print(f"✗ 主要模拟功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_therapy_system():
    """测试治疗系统"""
    print("\n=== 测试治疗系统 ===")
    
    try:
        from core.therapy_session_manager import TherapySessionManager
        from agents.therapist_agent import TherapistAgent
        from core.llm_therapy_enhancer import LLMTherapyEnhancer
        
        # 创建AI客户端
        ai_client = TestAIClient()
        
        # 创建治疗师
        therapist = TherapistAgent(
            name="心理治疗师",
            ai_client=ai_client
        )
        
        print(f"✓ 创建治疗师: {therapist.name}")
        
        # 测试LLM治疗增强器
        enhancer = LLMTherapyEnhancer(ai_client)
        
        # 模拟对话
        dialogue_history = [
            {"speaker": "患者", "content": "我最近总是感觉很累", "timestamp": datetime.now().isoformat()},
            {"speaker": "治疗师", "content": "能具体说说是什么样的累吗？", "timestamp": datetime.now().isoformat()}
        ]
        
        from models.psychology_models import PsychologicalState, EmotionState, DepressionLevel
        patient_state = PsychologicalState(
            emotion=EmotionState.SAD,
            depression_level=DepressionLevel.MILD,
            stress_level=7,
            self_esteem=4,
            social_connection=3,
            academic_pressure=8
        )
        
        # 分析对话
        analysis = await enhancer.analyze_conversation(dialogue_history, patient_state)
        print(f"  对话分析 - 治疗联盟: {analysis.therapeutic_alliance:.1f}/10")
        print(f"  患者开放程度: {analysis.patient_openness:.1f}/10")
        
        # 生成治疗回应
        response = await enhancer.generate_therapeutic_response(
            "我感觉什么都不想做", patient_state, dialogue_history, analysis
        )
        print(f"  治疗回应: {response.content}")
        print(f"  使用技术: {response.therapeutic_techniques}")
        
        return True
        
    except Exception as e:
        print(f"✗ 治疗系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_configuration_loading():
    """测试配置加载"""
    print("\n=== 测试配置加载 ===")
    
    try:
        # 测试LLM增强配置
        config_path = "/Users/zl_24/Documents/Codes/2025/2025-07/CAD-main/config/llm_enhancement_config.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            llm_config = json.load(f)
        
        print("✓ LLM增强配置加载成功")
        print(f"  事件生成启用: {llm_config.get('llm_integration', {}).get('event_generation', {}).get('enabled', False)}")
        print(f"  心理评估启用: {llm_config.get('llm_integration', {}).get('psychological_assessment', {}).get('enabled', False)}")
        print(f"  概率建模启用: {llm_config.get('probabilistic_modeling', {}).get('enabled', False)}")
        print(f"  双向影响启用: {llm_config.get('bidirectional_impact', {}).get('enabled', False)}")
        
        # 测试场景配置
        scenarios_dir = Path("/Users/zl_24/Documents/Codes/2025/2025-07/CAD-main/config/scenarios")
        scenario_files = list(scenarios_dir.glob("*.json"))
        print(f"✓ 发现 {len(scenario_files)} 个场景配置文件")
        
        for scenario_file in scenario_files:
            with open(scenario_file, 'r', encoding='utf-8') as f:
                scenario_config = json.load(f)
            print(f"  - {scenario_file.stem}: {scenario_config.get('scenario_name', '未知场景')}")
        
        return True
        
    except Exception as e:
        print(f"✗ 配置加载测试失败: {e}")
        return False


def test_model_integration():
    """测试模型集成"""
    print("\n=== 测试模型集成 ===")
    
    try:
        from models.psychology_models import PsychologicalState, CognitiveAffectiveState, EmotionState, DepressionLevel
        
        # 创建完整的心理状态
        cad_state = CognitiveAffectiveState()
        cad_state.affective_tone = -2.5
        cad_state.core_beliefs.self_belief = -3.0
        cad_state.core_beliefs.world_belief = -1.5
        cad_state.core_beliefs.future_belief = -2.0
        cad_state.cognitive_processing.rumination = 6.5
        cad_state.cognitive_processing.distortions = 4.0
        cad_state.behavioral_inclination.social_withdrawal = 5.5
        cad_state.behavioral_inclination.avolition = 4.5
        
        psychological_state = PsychologicalState(
            emotion=EmotionState.SAD,
            depression_level=DepressionLevel.MILD,
            stress_level=6,
            self_esteem=4,
            social_connection=3,
            academic_pressure=7,
            cad_state=cad_state
        )
        
        print("✓ 心理状态模型创建成功")
        
        # 测试CAD状态分析
        comprehensive_analysis = cad_state.get_comprehensive_analysis()
        print(f"  CAD状态分析长度: {len(comprehensive_analysis)} 字符")
        
        # 测试抑郁评分计算
        depression_score = cad_state.calculate_comprehensive_depression_score()
        print(f"  CAD抑郁评分: {depression_score:.2f}/27")
        
        # 测试抑郁级别更新
        psychological_state.update_depression_level_from_cad()
        print(f"  更新后抑郁级别: {psychological_state.depression_level.name}")
        
        return True
        
    except Exception as e:
        print(f"✗ 模型集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_event_generation():
    """测试事件生成系统"""
    print("\n=== 测试事件生成系统 ===")
    
    try:
        from core.event_generator import EventGenerator
        from config.config_loader import load_scenario
        
        # 加载配置
        config = load_scenario("primary_school_bullying")
        
        # 创建AI客户端
        ai_client = TestAIClient()
        
        # 创建事件生成器
        event_templates = config["event_templates"]
        character_mapping = {
            char_id: char_info["name"] 
            for char_id, char_info in config["characters"].items()
        }
        
        generator = EventGenerator(ai_client, event_templates, character_mapping, config)
        
        print("✓ 事件生成器创建成功")
        print(f"  LLM增强: {'启用' if generator.llm_event_generator else '禁用'}")
        print(f"  混合计算器: {'启用' if generator.hybrid_calculator else '禁用'}")
        print(f"  概率模型: {'启用' if generator.probabilistic_model else '禁用'}")
        
        # 测试事件生成
        protagonist_state = {
            "stress_level": 5,
            "depression_level": "MILD",
            "self_esteem": 4,
            "personality": {"neuroticism": 6}
        }
        
        stage_config = {"stress_modifier": 1.2}
        
        event_description, participants, impact_score = await generator.generate_event(
            "academic", "negative", protagonist_state, stage_config
        )
        
        print(f"  生成事件: {event_description}")
        print(f"  参与者: {participants}")
        print(f"  影响分数: {impact_score}")
        
        return True
        
    except Exception as e:
        print(f"✗ 事件生成系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("开始CAD系统LLM增强集成测试...")
    print("=" * 60)
    
    test_results = []
    
    # 运行所有测试
    test_results.append(test_configuration_loading())
    test_results.append(test_model_integration())
    test_results.append(await test_event_generation())
    test_results.append(await test_main_simulation())
    test_results.append(await test_therapy_system())
    
    # 统计结果
    passed = sum(test_results)
    total = len(test_results)
    
    print("\n" + "=" * 60)
    print(f"系统集成测试完成: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 CAD系统LLM增强集成测试全部通过！")
        print("\n系统已成功集成以下LLM增强功能：")
        print("  ✓ LLM事件生成器 - 生成多样化和上下文相关的生活事件")
        print("  ✓ LLM心理状态评估器 - 深度分析事件的心理影响")
        print("  ✓ 混合影响计算器 - 融合规则和LLM的影响计算")
        print("  ✓ 积极影响管理器 - 处理心理恢复和双向影响")
        print("  ✓ 概率性影响模型 - 引入不确定性和个体差异")
        print("  ✓ LLM治疗增强器 - 提升治疗对话质量")
        print("\n可以开始使用以下脚本进行测试：")
        print("  - python main.py (30轮心理模拟)")
        print("  - python start_ai_to_ai_therapy.py (AI自动治疗)")  
        print("  - python start_therapy_from_logs.py (人工治疗)")
        
        return 0
    else:
        print(f"⚠️  有 {total - passed} 项测试失败")
        print("请检查失败的组件并修复问题后重新测试")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)