"""
心理模型选择器
提供交互式的模型选择界面和配置管理
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from models.psychological_model_base import (
    PsychologicalModelType, ModelFactory, PsychologicalModelBase
)


class ModelSelector:
    """心理模型选择器"""
    
    def __init__(self, console: Console = None):
        """初始化模型选择器"""
        self.console = console or Console()
        self.config_file = Path("config/psychological_model_config.json")
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载默认配置
        self.default_config = self._load_default_config()
        
        # 当前选择
        self.selected_model_type = None
        self.selected_config = {}
    
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            "default_model": PsychologicalModelType.CAD_ENHANCED.value,
            "model_configs": {
                PsychologicalModelType.BASIC_RULES.value: {
                    "stress_multiplier": 0.5,
                    "self_esteem_multiplier": 0.3,
                    "depression_threshold": 3,
                    "recovery_rate": 0.1,
                    "negative_bias": 1.2
                },
                PsychologicalModelType.CAD_ENHANCED.value: {
                    "belief_impact_strength": 0.4,
                    "affective_amplification": 1.3,
                    "rumination_threshold": 6.0,
                    "cognitive_distortion_rate": 0.1,
                    "daily_decay_rate": 0.04
                },
                PsychologicalModelType.LLM_DRIVEN.value: {
                    "max_retries": 3,
                    "timeout_seconds": 30,
                    "temperature": 0.3,
                    "confidence_threshold": 0.6,
                    "enable_detailed_analysis": True
                },
                PsychologicalModelType.HYBRID.value: {
                    "basic_rules_weight": 0.3,
                    "cad_weight": 0.4,
                    "llm_weight": 0.3,
                    "llm_trigger_threshold": 3,
                    "llm_frequency": 0.5,
                    "enable_adaptive_weights": True
                }
            },
            "performance_settings": {
                "enable_parallel_processing": True,
                "cache_results": True,
                "log_detailed_metrics": False
            }
        }
    
    def load_saved_config(self) -> Dict[str, Any]:
        """加载保存的配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                # 合并默认配置
                config = self.default_config.copy()
                config.update(saved_config)
                return config
            else:
                return self.default_config
        except Exception as e:
            self.console.print(f"[yellow]加载配置失败，使用默认配置: {e}[/yellow]")
            return self.default_config
    
    def save_config(self, config: Dict[str, Any]):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.console.print(f"[green]配置已保存到: {self.config_file}[/green]")
        except Exception as e:
            self.console.print(f"[red]保存配置失败: {e}[/red]")
    
    def select_model_interactive(self, ai_client = None) -> Tuple[PsychologicalModelType, Dict[str, Any]]:
        """交互式选择心理模型"""
        
        # 显示欢迎信息
        self.console.print(Panel(
            "[bold blue]心理模型选择器[/bold blue]\n\n"
            "请选择适合您需求的心理状态评估模型。\n"
            "不同模型在准确性、速度和功能上各有特色。",
            title="🧠 模型选择",
            border_style="blue"
        ))
        
        # 获取可用模型信息
        model_info = ModelFactory.get_model_info_all()
        
        # 显示模型对比表
        self._display_model_comparison(model_info, ai_client)
        
        # 选择模型
        selected_type = self._prompt_model_selection(model_info, ai_client)
        
        # 配置模型参数
        config = self._configure_model_parameters(selected_type)
        
        # 确认选择
        if self._confirm_selection(selected_type, config):
            # 保存配置
            full_config = self.load_saved_config()
            full_config["default_model"] = selected_type.value
            full_config["model_configs"][selected_type.value] = config
            self.save_config(full_config)
            
            self.selected_model_type = selected_type
            self.selected_config = config
            
            return selected_type, config
        else:
            # 重新选择
            return self.select_model_interactive(ai_client)
    
    def _display_model_comparison(self, model_info: Dict, ai_client = None):
        """显示模型对比表"""
        table = Table(title="🔍 心理模型对比")
        table.add_column("模型", style="cyan", no_wrap=True)
        table.add_column("描述", style="white", width=35)
        table.add_column("CAD支持", justify="center", style="green")
        table.add_column("异步处理", justify="center", style="yellow")
        table.add_column("AI需求", justify="center", style="red")
        table.add_column("推荐场景", style="blue", width=25)
        
        # 推荐场景映射
        recommendations = {
            PsychologicalModelType.BASIC_RULES: "快速测试、教学演示",
            PsychologicalModelType.CAD_ENHANCED: "科研分析、准确模拟",
            PsychologicalModelType.LLM_DRIVEN: "深度分析、复杂案例",
            PsychologicalModelType.HYBRID: "生产环境、综合评估"
        }
        
        for model_type, info in model_info.items():
            # 检查AI可用性
            ai_available = "✓" if not info["requires_ai_client"] or ai_client else "✗"
            ai_style = "green" if ai_available == "✓" else "red"
            
            table.add_row(
                info["display_name"],
                info["description"],
                "✓" if info["supports_cad"] else "✗",
                "✓" if info["supports_async"] else "✗",
                f"[{ai_style}]{ai_available}[/{ai_style}]",
                recommendations.get(model_type, "通用场景")
            )
        
        self.console.print(table)
    
    def _prompt_model_selection(self, model_info: Dict, ai_client = None) -> PsychologicalModelType:
        """提示用户选择模型"""
        
        # 过滤可用模型
        available_models = []
        for model_type, info in model_info.items():
            if not info["requires_ai_client"] or ai_client:
                available_models.append(model_type)
        
        if not available_models:
            raise ValueError("没有可用的心理模型")
        
        # 显示选择菜单
        self.console.print("\n[cyan]可用模型：[/cyan]")
        for i, model_type in enumerate(available_models, 1):
            info = model_info[model_type]
            self.console.print(f"  {i}. {info['display_name']}")
        
        # 获取用户选择
        while True:
            try:
                choice = Prompt.ask(
                    "\n请选择模型",
                    choices=[str(i) for i in range(1, len(available_models) + 1)],
                    default="2"  # 默认选择CAD增强模型
                )
                
                selected_index = int(choice) - 1
                selected_type = available_models[selected_index]
                
                # 显示选择的模型信息
                info = model_info[selected_type]
                self.console.print(f"\n[green]已选择: {info['display_name']}[/green]")
                self.console.print(f"[dim]{info['description']}[/dim]")
                
                return selected_type
                
            except (ValueError, IndexError):
                self.console.print("[red]无效选择，请重新输入[/red]")
    
    def _configure_model_parameters(self, model_type: PsychologicalModelType) -> Dict[str, Any]:
        """配置模型参数"""
        
        # 获取默认配置
        default_config = self.default_config["model_configs"].get(model_type.value, {})
        
        # 询问是否自定义配置
        if not Confirm.ask("\n是否自定义模型参数", default=False):
            return default_config
        
        self.console.print(f"\n[cyan]配置 {model_type.value} 模型参数：[/cyan]")
        
        config = {}
        parameter_descriptions = self._get_parameter_descriptions(model_type)
        
        for param_name, default_value in default_config.items():
            description = parameter_descriptions.get(param_name, "")
            
            # 显示参数信息
            self.console.print(f"\n[white]{param_name}[/white]: {description}")
            self.console.print(f"[dim]默认值: {default_value}[/dim]")
            
            # 获取用户输入
            if isinstance(default_value, bool):
                config[param_name] = Confirm.ask("是否启用", default=default_value)
            elif isinstance(default_value, (int, float)):
                while True:
                    try:
                        user_input = Prompt.ask(
                            "请输入数值",
                            default=str(default_value)
                        )
                        config[param_name] = type(default_value)(user_input)
                        break
                    except ValueError:
                        self.console.print("[red]请输入有效数值[/red]")
            else:
                config[param_name] = Prompt.ask(
                    "请输入值",
                    default=str(default_value)
                )
        
        return config
    
    def _get_parameter_descriptions(self, model_type: PsychologicalModelType) -> Dict[str, str]:
        """获取参数描述"""
        descriptions = {
            PsychologicalModelType.BASIC_RULES: {
                "stress_multiplier": "压力影响倍数 (0.1-1.0)",
                "self_esteem_multiplier": "自尊影响倍数 (0.1-1.0)",
                "depression_threshold": "抑郁检测阈值 (1-10)",
                "recovery_rate": "自然恢复速率 (0.01-0.5)",
                "negative_bias": "负面偏差倍数 (1.0-2.0)"
            },
            PsychologicalModelType.CAD_ENHANCED: {
                "belief_impact_strength": "信念影响强度 (0.1-1.0)",
                "affective_amplification": "情感放大系数 (1.0-2.0)",
                "rumination_threshold": "思维反刍阈值 (3.0-10.0)",
                "cognitive_distortion_rate": "认知扭曲增长率 (0.01-0.5)",
                "daily_decay_rate": "每日衰减率 (0.01-0.1)"
            },
            PsychologicalModelType.LLM_DRIVEN: {
                "max_retries": "最大重试次数 (1-10)",
                "timeout_seconds": "超时时间秒数 (10-60)",
                "temperature": "LLM温度参数 (0.0-1.0)",
                "confidence_threshold": "置信度阈值 (0.1-1.0)",
                "enable_detailed_analysis": "启用详细分析"
            },
            PsychologicalModelType.HYBRID: {
                "basic_rules_weight": "基础规则权重 (0.0-1.0)",
                "cad_weight": "CAD模型权重 (0.0-1.0)", 
                "llm_weight": "LLM模型权重 (0.0-1.0)",
                "llm_trigger_threshold": "LLM触发阈值 (1-10)",
                "llm_frequency": "LLM使用频率 (0.0-1.0)",
                "enable_adaptive_weights": "启用自适应权重"
            }
        }
        
        return descriptions.get(model_type, {})
    
    def _confirm_selection(self, model_type: PsychologicalModelType, config: Dict[str, Any]) -> bool:
        """确认选择"""
        
        # 显示最终配置
        self.console.print(Panel(
            f"[bold]模型类型:[/bold] {model_type.value}\n"
            f"[bold]配置参数:[/bold]\n" +
            "\n".join([f"  {k}: {v}" for k, v in config.items()]),
            title="📋 配置确认",
            border_style="green"
        ))
        
        return Confirm.ask("\n确认使用此配置", default=True)
    
    def quick_select(self, model_name: str = None, ai_client = None) -> Tuple[PsychologicalModelType, Dict[str, Any]]:
        """快速选择模型（用于脚本调用）"""
        
        # 加载配置
        config = self.load_saved_config()
        
        # 确定模型类型
        if model_name:
            try:
                model_type = PsychologicalModelType(model_name)
            except ValueError:
                self.console.print(f"[red]无效的模型名称: {model_name}[/red]")
                model_type = PsychologicalModelType(config["default_model"])
        else:
            model_type = PsychologicalModelType(config["default_model"])
        
        # 检查AI客户端需求
        model_info = ModelFactory.get_model_info_all()
        if model_info[model_type]["requires_ai_client"] and not ai_client:
            self.console.print(f"[yellow]模型 {model_type.value} 需要AI客户端，回退到CAD模型[/yellow]")
            model_type = PsychologicalModelType.CAD_ENHANCED
        
        # 获取模型配置
        model_config = config["model_configs"].get(model_type.value, {})
        
        self.console.print(f"[green]使用心理模型: {model_type.value}[/green]")
        
        return model_type, model_config
    
    def create_model_instance(self, 
                            model_type: PsychologicalModelType, 
                            config: Dict[str, Any],
                            ai_client = None) -> PsychologicalModelBase:
        """创建模型实例"""
        try:
            return ModelFactory.create_model(model_type, config, ai_client)
        except Exception as e:
            self.console.print(f"[red]创建模型实例失败: {e}[/red]")
            # 回退到基础规则模型
            self.console.print("[yellow]回退到基础规则模型[/yellow]")
            return ModelFactory.create_model(PsychologicalModelType.BASIC_RULES, {})
    
    def display_model_statistics(self, model: PsychologicalModelBase):
        """显示模型统计信息"""
        info = model.get_model_info()
        stats = info["statistics"]
        
        table = Table(title=f"📊 {info['type']} 模型统计")
        table.add_column("指标", style="cyan")
        table.add_column("数值", style="yellow", justify="right")
        
        table.add_row("总计算次数", str(stats["total_calculations"]))
        table.add_row("平均处理时间", f"{stats['average_processing_time']:.2f}ms")
        table.add_row("错误率", f"{stats['error_rate']:.1%}")
        table.add_row("CAD支持", "✓" if info["supports_cad"] else "✗")
        table.add_row("异步支持", "✓" if info["supports_async"] else "✗")
        
        self.console.print(table)