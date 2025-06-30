#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一配置加载器
支持JSON格式的配置文件，替代原有的Python配置模块
"""

import json
import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from rich.console import Console

console = Console()

class ConfigLoader:
    """统一配置加载器"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        初始化配置加载器
        
        Args:
            config_dir: 配置目录路径，默认为项目根目录下的config文件夹
        """
        if config_dir is None:
            self.config_dir = Path(__file__).parent
        else:
            self.config_dir = Path(config_dir)
        
        self.scenarios_dir = self.config_dir / "scenarios"
    
    def load_api_config(self) -> Dict[str, Any]:
        """加载API配置（支持YAML和JSON）"""
        # 优先尝试YAML格式
        yaml_file = self.config_dir / "api_config.yaml"
        json_file = self.config_dir / "api_config.json"
        
        config = None
        config_file = None
        
        try:
            if yaml_file.exists():
                config_file = yaml_file
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                console.print(f"[green]使用YAML API配置: {config_file.name}[/green]")
            elif json_file.exists():
                config_file = json_file
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                console.print(f"[yellow]使用JSON API配置: {config_file.name}[/yellow]")
            else:
                console.print(f"[yellow]未找到API配置文件，使用默认配置[/yellow]")
                return self._get_default_api_config()
            
            # 优先使用环境变量
            if 'providers' in config:
                for provider_name, provider_config in config['providers'].items():
                    if provider_name == 'deepseek':
                        env_key = os.getenv('DEEPSEEK_API_KEY')
                        if env_key:
                            provider_config['api_key'] = env_key
                    elif provider_name == 'gemini':
                        env_key = os.getenv('GEMINI_API_KEY')
                        if env_key:
                            provider_config['api_key'] = env_key
            
            return config
        except FileNotFoundError:
            console.print(f"[yellow]未找到API配置文件: {config_file}[/yellow]")
            return self._get_default_api_config()
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            console.print(f"[red]API配置文件格式错误: {e}[/red]")
            return self._get_default_api_config()
    
    def load_simulation_params(self) -> Dict[str, Any]:
        """加载模拟参数配置（支持YAML和JSON）"""
        # 优先尝试YAML格式
        yaml_file = self.config_dir / "simulation_params.yaml"
        json_file = self.config_dir / "simulation_params.json"
        
        try:
            if yaml_file.exists():
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                console.print(f"[green]使用YAML模拟参数配置: {yaml_file.name}[/green]")
                return config
            elif json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                console.print(f"[yellow]使用JSON模拟参数配置: {json_file.name}[/yellow]")
                return config
            else:
                console.print(f"[yellow]未找到模拟参数配置文件，使用默认配置[/yellow]")
                return self._get_default_simulation_params()
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            console.print(f"[red]模拟参数配置文件格式错误: {e}[/red]")
            return self._get_default_simulation_params()
    
    def load_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """
        加载指定场景配置（支持YAML和JSON）
        
        Args:
            scenario_name: 场景名称（不包含扩展名）
        """
        try:
            # 优先尝试JSON格式（场景配置主要是JSON）
            json_file = self.scenarios_dir / f"{scenario_name}.json"
            yaml_file = self.scenarios_dir / f"{scenario_name}.yaml"
            
            if json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif yaml_file.exists():
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                console.print(f"[red]未找到场景配置文件: {scenario_name}[/red]")
                raise FileNotFoundError(f"Scene config not found: {scenario_name}")
                
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            console.print(f"[red]场景配置文件格式错误: {e}[/red]")
            raise
    
    def list_available_scenarios(self) -> List[str]:
        """列出所有可用的场景（支持JSON和YAML）"""
        scenarios = []
        if self.scenarios_dir.exists():
            # 收集JSON和YAML文件
            for file in self.scenarios_dir.glob("*.json"):
                scenarios.append(file.stem)
            for file in self.scenarios_dir.glob("*.yaml"):
                if file.stem not in scenarios:  # 避免重复
                    scenarios.append(file.stem)
        return sorted(scenarios)
    
    def get_scenario_info(self, scenario_name: str) -> Dict[str, str]:
        """
        获取场景基本信息
        
        Args:
            scenario_name: 场景名称
            
        Returns:
            包含场景名称和描述的字典
        """
        try:
            scenario = self.load_scenario(scenario_name)
            return {
                "name": scenario.get("scenario_name", scenario_name),
                "description": scenario.get("description", "无描述")
            }
        except:
            return {
                "name": scenario_name,
                "description": "无法读取场景信息"
            }
    
    def validate_scenario_config(self, scenario_config: Dict[str, Any]) -> bool:
        """
        验证场景配置的完整性
        
        Args:
            scenario_config: 场景配置字典
            
        Returns:
            配置是否有效
        """
        required_keys = ["characters", "relationships", "event_templates", "stage_config"]
        
        for key in required_keys:
            if key not in scenario_config:
                console.print(f"[red]场景配置缺少必需的键: {key}[/red]")
                return False
        
        # 检查是否有主角
        if "protagonist" not in scenario_config["characters"]:
            console.print("[red]场景配置缺少主角(protagonist)[/red]")
            return False
        
        return True
    
    # ===== 默认配置 =====
    
    def _get_default_api_config(self) -> Dict[str, Any]:
        """获取默认API配置"""
        return {
            "default_provider": "deepseek",
            "providers": {
                "gemini": {
                    "api_key": "your_gemini_api_key_here",
                    "model": "gemini-pro",
                    "enabled": True
                },
                "deepseek": {
                    "api_key": os.getenv('DEEPSEEK_API_KEY'),
                    "base_url": "https://api.deepseek.com",
                    "model": "deepseek-chat",
                    "enabled": True
                }
            },
            "timeout": 30,
            "max_retries": 3
        }
    
    def _get_default_simulation_params(self) -> Dict[str, Any]:
        """获取默认模拟参数"""
        return {
            "simulation": {
                "simulation_days": 30,
                "events_per_day": 5,
                "simulation_speed": 1,
                "depression_development_stages": 5,
                "interaction_frequency": 3
            },
            "logging": {
                "log_level": "INFO",
                "save_daily_states": True,
                "enable_debug_mode": False
            },
            "therapy": {
                "conversation_history_length": 20,
                "max_events_to_show": 20,
                "enable_supervision": True,
                "supervision_interval": 5,
                "supervision_analysis_depth": "COMPREHENSIVE"
            },
            "recovery": {
                "improvement_threshold": 7.0,
                "alliance_threshold": 6.0,
                "evaluation_interval": 5,
                "deterioration_threshold": 3.0
            }
        }

    def load_therapy_guidance_config(self, config_type: str = "general") -> dict:
        """
        加载治疗引导配置（支持YAML和JSON）
        
        Args:
            config_type: 配置类型 ("general", "human_therapy", "ai_to_ai_therapy")
        
        Returns:
            dict: 治疗引导配置字典
        """
        config_files = {
            "general": "therapy_guidance_config",
            "human_therapy": "human_therapy_config", 
            "ai_to_ai_therapy": "ai_to_ai_therapy_config"
        }
        
        config_basename = config_files.get(config_type, "therapy_guidance_config")
        
        try:
            # 优先尝试YAML格式
            yaml_path = self.config_dir / f"{config_basename}.yaml"
            json_path = self.config_dir / f"{config_basename}.json"
            
            config = None
            config_path = None
            
            if yaml_path.exists():
                config_path = yaml_path
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                console.print(f"[green]使用YAML治疗引导配置: {config_path.name}[/green]")
            elif json_path.exists():
                config_path = json_path
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                console.print(f"[yellow]使用JSON治疗引导配置: {config_path.name}[/yellow]")
            else:
                console.print(f"[yellow]治疗引导配置文件不存在，使用默认配置[/yellow]")
                return self._get_default_therapy_guidance_config()
            
            return config
            
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            console.print(f"[red]治疗引导配置文件格式错误: {e}[/red]")
            return self._get_default_therapy_guidance_config()
        except Exception as e:
            console.print(f"[red]加载治疗引导配置失败: {e}[/red]")
            return self._get_default_therapy_guidance_config()

    def _get_default_therapy_guidance_config(self) -> dict:
        """获取默认治疗引导配置"""
        return {
            "therapy_effectiveness": {
                "base_improvement_factor": 0.5,
                "max_improvement_per_turn": 0.8,
                "min_improvement_per_turn": 0.1,
                "technique_weight": 0.4,
                "openness_weight": 0.3,
                "connection_weight": 0.3
            },
            "cad_state_changes": {
                "core_beliefs": {
                    "self_belief_change_rate": 0.15,
                    "world_belief_change_rate": 0.12,
                    "future_belief_change_rate": 0.18,
                    "stability_factor": 0.85
                },
                "cognitive_processing": {
                    "rumination_reduction_rate": 0.20,
                    "distortions_reduction_rate": 0.16,
                    "positive_reframe_bonus": 0.1
                },
                "behavioral_patterns": {
                    "social_withdrawal_change_rate": 0.14,
                    "avolition_change_rate": 0.12,
                    "activation_bonus": 0.08
                },
                "affective_tone_change_rate": 0.22,
                "therapy_response_modifier": 1.2,
                "correction_factor": 0.95
            },
            "supervision_settings": {
                "supervision_interval": 3,
                "evaluation_interval": 1,
                "risk_threshold": 0.7,
                "progress_threshold": 0.3,
                "supervision_depth": "comprehensive"
            },
            "therapy_thresholds": {
                "breakthrough_threshold": 8.0,
                "resistance_threshold": 3.0,
                "alliance_building_threshold": 6.0,
                "crisis_intervention_threshold": 2.0
            },
            "state_bounds": {
                "min_cad_value": -10.0,
                "max_cad_value": 10.0,
                "min_depression_improvement": 0.1,
                "max_depression_change_per_session": 1.0
            }
        }

# 单例模式的配置加载器
_config_loader = None

def get_config_loader() -> ConfigLoader:
    """获取全局配置加载器实例"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader

# 便捷函数
def load_api_config() -> Dict[str, Any]:
    """加载API配置的便捷函数"""
    return get_config_loader().load_api_config()

def load_simulation_params() -> Dict[str, Any]:
    """加载模拟参数的便捷函数"""
    return get_config_loader().load_simulation_params()

def load_scenario(scenario_name: str) -> Dict[str, Any]:
    """加载场景的便捷函数"""
    return get_config_loader().load_scenario(scenario_name)

def list_scenarios() -> List[str]:
    """列出可用场景的便捷函数"""
    return get_config_loader().list_available_scenarios()

def load_complete_config(scenario_name: str = "default_adolescent") -> Dict[str, Any]:
    """
    加载完整配置，整合API、模拟参数和场景配置
    这个函数用于替代原来的config.py系统
    
    Args:
        scenario_name: 场景名称
        
    Returns:
        完整的配置字典
    """
    loader = get_config_loader()
    
    try:
        # 加载基础配置
        api_config = loader.load_api_config()
        sim_params = loader.load_simulation_params()
        scenario_config = loader.load_scenario(scenario_name)
        
        # 整合所有配置
        complete_config = {
            # API配置
            'api': api_config,
            
            # 模拟基础参数
            'simulation': sim_params.get('simulation', {}),
            'logging': sim_params.get('logging', {}),
            'therapy': sim_params.get('therapy', {}),
            'recovery': sim_params.get('recovery', {}),
            
            # 场景配置
            'scenario': {
                'name': scenario_config.get('scenario_name', scenario_name),
                'description': scenario_config.get('description', ''),
                'characters': scenario_config.get('characters', {}),
                'relationships': scenario_config.get('relationships', []),
                'event_templates': scenario_config.get('event_templates', {}),
                'stage_config': scenario_config.get('stage_config', {}),
                'conditional_events': scenario_config.get('conditional_events', {}),
                'cad_impact_rules': scenario_config.get('cad_impact_rules', {})
            },
            
            # 便捷访问的展平配置
            'default_provider': api_config.get('default_provider', 'deepseek'),
            'simulation_days': sim_params.get('simulation', {}).get('simulation_days', 30),
            'events_per_day': sim_params.get('simulation', {}).get('events_per_day', 5),
            'simulation_speed': sim_params.get('simulation', {}).get('simulation_speed', 1),
            'depression_development_stages': sim_params.get('simulation', {}).get('depression_development_stages', 5),
            'interaction_frequency': sim_params.get('simulation', {}).get('interaction_frequency', 3),
            'conversation_history_length': 20,  # 现在在专用治疗配置文件中
            'max_events_to_show': 20,  # 现在在专用治疗配置文件中
            'enable_supervision': True,  # 现在在专用治疗配置文件中
            'supervision_interval': 5,  # 现在在专用治疗配置文件中
            'log_level': sim_params.get('logging', {}).get('log_level', 'INFO'),
            'protagonist_name': scenario_config.get('characters', {}).get('protagonist', {}).get('name', '李明'),
            'protagonist_age': scenario_config.get('characters', {}).get('protagonist', {}).get('age', 17)
        }
        
        return complete_config
        
    except Exception as e:
        console.print(f"[red]加载完整配置失败: {e}[/red]")
        return {}

def save_temp_config(config_data: Dict[str, Any], temp_name: str = "web_temp") -> bool:
    """
    保存临时配置文件（用于Web界面）
    
    Args:
        config_data: 配置数据
        temp_name: 临时文件名
        
    Returns:
        是否保存成功
    """
    try:
        loader = get_config_loader()
        temp_path = loader.config_dir / f"temp_{temp_name}.json"
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        console.print(f"[red]保存临时配置失败: {e}[/red]")
        return False

def load_temp_config(temp_name: str = "web_temp") -> Dict[str, Any]:
    """
    加载临时配置文件
    
    Args:
        temp_name: 临时文件名
        
    Returns:
        配置数据
    """
    try:
        loader = get_config_loader()
        temp_path = loader.config_dir / f"temp_{temp_name}.json"
        if not temp_path.exists():
            return {}
        
        with open(temp_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[red]加载临时配置失败: {e}[/red]")
        return {}

def load_therapy_guidance_config(config_type: str = "general") -> dict:
    """便捷函数：加载治疗引导配置"""
    return get_config_loader().load_therapy_guidance_config(config_type) 