#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统测试脚本 - 诊断潜在问题
"""

import sys
import traceback
from pathlib import Path

def test_imports():
    """测试关键模块导入"""
    print("=== 测试模块导入 ===")
    
    tests = [
        ("Rich库", "rich.console", "Console"),
        ("心理学模型", "models.psychology_models", "DepressionLevel"),
        ("配置加载器", "config.config_loader", "load_api_config"),
        ("AI客户端工厂", "core.ai_client_factory", "ai_client_factory"),
        ("模拟引擎", "core.simulation_engine", "SimulationEngine"),
        ("治疗管理器", "core.therapy_session_manager", "TherapySessionManager"),
        ("AI治疗管理器", "core.ai_to_ai_therapy_manager", "AIToAITherapyManager"),
        ("学生Agent", "agents.student_agent", "StudentAgent"),
        ("治疗师Agent", "agents.therapist_agent", "TherapistAgent"),
    ]
    
    results = []
    
    for name, module, attr in tests:
        try:
            if attr:
                exec(f"from {module} import {attr}")
            else:
                exec(f"import {module}")
            print(f"✅ {name}: 导入成功")
            results.append((name, True, None))
        except Exception as e:
            print(f"❌ {name}: 导入失败 - {e}")
            results.append((name, False, str(e)))
    
    return results

def test_depression_levels():
    """测试抑郁级别系统"""
    print("\n=== 测试抑郁级别系统 ===")
    
    try:
        from models.psychology_models import DepressionLevel
        
        print(f"✅ DepressionLevel枚举加载成功")
        print(f"   级别数量: {len(DepressionLevel)}")
        print(f"   最低级别: {min([d.value for d in DepressionLevel])}")
        print(f"   最高级别: {max([d.value for d in DepressionLevel])}")
        
        # 测试所有级别
        for level in DepressionLevel:
            print(f"   {level.value}: {level.name}")
        
        return True
    except Exception as e:
        print(f"❌ 抑郁级别测试失败: {e}")
        traceback.print_exc()
        return False

def test_config_files():
    """测试配置文件"""
    print("\n=== 测试配置文件 ===")
    
    config_files = [
        "config/api_config.json",
        "config/simulation_params.json", 
        "config/human_therapy_config.json",
        "config/ai_to_ai_therapy_config.json",
        "config/scenarios/default_adolescent.json",
    ]
    
    results = []
    
    for config_file in config_files:
        config_path = Path(config_file)
        if config_path.exists():
            try:
                import json
                with open(config_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                print(f"✅ {config_file}: JSON格式正确")
                results.append((config_file, True, None))
            except Exception as e:
                print(f"❌ {config_file}: JSON格式错误 - {e}")
                results.append((config_file, False, str(e)))
        else:
            print(f"⚠️ {config_file}: 文件不存在")
            results.append((config_file, False, "文件不存在"))
    
    return results

def test_therapy_managers():
    """测试治疗管理器的抑郁级别映射"""
    print("\n=== 测试治疗管理器抑郁级别映射 ===")
    
    try:
        # 测试 therapy_session_manager
        from core.therapy_session_manager import DEPRESSION_LEVELS as therapy_levels
        print(f"✅ TherapySessionManager 抑郁级别数量: {len(therapy_levels)}")
        print(f"   级别范围: {min(therapy_levels.values())} - {max(therapy_levels.values())}")
        
        # 测试 ai_to_ai_therapy_manager
        from core.ai_to_ai_therapy_manager import DEPRESSION_LEVELS as ai_therapy_levels
        print(f"✅ AIToAITherapyManager 抑郁级别数量: {len(ai_therapy_levels)}")
        print(f"   级别范围: {min(ai_therapy_levels.values())} - {max(ai_therapy_levels.values())}")
        
        # 检查一致性
        if therapy_levels == ai_therapy_levels:
            print("✅ 两个管理器的抑郁级别映射一致")
        else:
            print("⚠️ 两个管理器的抑郁级别映射不一致")
            print(f"   TherapySessionManager: {therapy_levels}")
            print(f"   AIToAITherapyManager: {ai_therapy_levels}")
        
        return True
    except Exception as e:
        print(f"❌ 治疗管理器测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🔍 开始系统诊断...")
    print(f"Python版本: {sys.version}")
    print(f"当前工作目录: {Path.cwd()}")
    
    # 运行所有测试
    import_results = test_imports()
    depression_test = test_depression_levels()
    config_results = test_config_files()
    therapy_test = test_therapy_managers()
    
    # 汇总结果
    print("\n" + "="*50)
    print("🎯 测试结果汇总")
    print("="*50)
    
    import_success = sum(1 for _, success, _ in import_results if success)
    total_imports = len(import_results)
    print(f"模块导入: {import_success}/{total_imports} 成功")
    
    config_success = sum(1 for _, success, _ in config_results if success)
    total_configs = len(config_results)
    print(f"配置文件: {config_success}/{total_configs} 正确")
    
    print(f"抑郁级别系统: {'✅' if depression_test else '❌'}")
    print(f"治疗管理器: {'✅' if therapy_test else '❌'}")
    
    # 显示失败的项目
    failed_items = []
    for name, success, error in import_results:
        if not success:
            failed_items.append(f"导入失败: {name} - {error}")
    
    for name, success, error in config_results:
        if not success:
            failed_items.append(f"配置错误: {name} - {error}")
    
    if failed_items:
        print("\n❌ 发现的问题:")
        for item in failed_items:
            print(f"   {item}")
    else:
        print("\n🎉 所有测试都通过了！")

if __name__ == "__main__":
    main()