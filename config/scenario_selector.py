#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
剧本选择器
提供交互式剧本选择功能
"""

from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

from .config_loader import get_config_loader

console = Console()

class ScenarioSelector:
    """剧本选择器"""
    
    def __init__(self):
        self.loader = get_config_loader()
    
    def display_available_scenarios(self) -> None:
        """显示所有可用的剧本"""
        scenarios = self.loader.list_available_scenarios()
        
        if not scenarios:
            console.print("[red]错误：未找到任何剧本配置文件[/red]")
            return
        
        console.print(Panel("[bold blue]可用剧本列表[/bold blue]"))
        
        scenario_table = Table()
        scenario_table.add_column("编号", style="cyan", no_wrap=True)
        scenario_table.add_column("剧本名称", style="green")
        scenario_table.add_column("主角", style="yellow")
        scenario_table.add_column("年龄", style="magenta")
        scenario_table.add_column("描述", style="white")
        
        for i, scenario in enumerate(scenarios, 1):
            try:
                info = self.loader.get_scenario_info(scenario)
                config = self.loader.load_scenario(scenario)
                
                protagonist = config.get('characters', {}).get('protagonist', {})
                protagonist_name = protagonist.get('name', '未知')
                protagonist_age = str(protagonist.get('age', '未知'))
                
                description = info.get('description', '无描述')
                # 截断描述，避免表格过宽
                if len(description) > 50:
                    description = description[:47] + "..."
                
                scenario_table.add_row(
                    str(i), 
                    info.get('name', scenario),
                    protagonist_name,
                    protagonist_age,
                    description
                )
            except Exception as e:
                scenario_table.add_row(
                    str(i),
                    scenario,
                    "错误",
                    "错误", 
                    f"配置加载失败: {str(e)[:30]}..."
                )
        
        console.print(scenario_table)
    
    def select_scenario_interactive(self, default_scenario: str = "default_adolescent") -> str:
        """
        交互式选择剧本
        
        Args:
            default_scenario: 默认剧本
            
        Returns:
            选择的剧本名称
        """
        scenarios = self.loader.list_available_scenarios()
        
        if not scenarios:
            console.print("[red]错误：未找到任何剧本配置文件，使用默认剧本[/red]")
            return default_scenario
        
        # 显示可用剧本
        self.display_available_scenarios()
        console.print()
        
        # 获取默认剧本在列表中的位置
        default_index = 0
        try:
            if default_scenario in scenarios:
                default_index = scenarios.index(default_scenario) + 1
        except ValueError:
            default_index = 1
        
        while True:
            try:
                choice = Prompt.ask(
                    f"[cyan]请选择剧本 (1-{len(scenarios)}) 或回车使用默认[/cyan]",
                    default=str(default_index)
                )
                
                if not choice.strip():
                    choice = str(default_index)
                
                choice_idx = int(choice) - 1
                
                if 0 <= choice_idx < len(scenarios):
                    selected_scenario = scenarios[choice_idx]
                    
                    # 显示选择的剧本信息
                    try:
                        info = self.loader.get_scenario_info(selected_scenario)
                        config = self.loader.load_scenario(selected_scenario)
                        protagonist = config.get('characters', {}).get('protagonist', {})
                        
                        console.print(Panel(
                            f"[bold green]已选择剧本：{info.get('name', selected_scenario)}[/bold green]\n\n"
                            f"主角：{protagonist.get('name', '未知')}，{protagonist.get('age', '未知')}岁\n"
                            f"描述：{info.get('description', '无描述')}",
                            title="✅ 剧本选择确认",
                            border_style="green"
                        ))
                        
                        return selected_scenario
                    except Exception as e:
                        console.print(f"[red]获取剧本信息失败: {e}[/red]")
                        return selected_scenario
                else:
                    console.print(f"[red]无效选择，请输入 1-{len(scenarios)} 之间的数字[/red]")
                    
            except ValueError:
                console.print("[red]请输入有效的数字[/red]")
            except KeyboardInterrupt:
                console.print(f"\n[yellow]使用默认剧本: {default_scenario}[/yellow]")
                return default_scenario
    
    def get_scenario_by_name(self, scenario_name: str) -> Optional[str]:
        """
        根据名称获取剧本（支持模糊匹配）
        
        Args:
            scenario_name: 剧本名称或关键词
            
        Returns:
            匹配的剧本名称，如果没有匹配则返回None
        """
        scenarios = self.loader.list_available_scenarios()
        
        # 精确匹配
        if scenario_name in scenarios:
            return scenario_name
        
        # 模糊匹配
        matches = [s for s in scenarios if scenario_name.lower() in s.lower()]
        
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            console.print(f"[yellow]找到多个匹配的剧本: {matches}[/yellow]")
            return None
        else:
            console.print(f"[red]未找到匹配的剧本: {scenario_name}[/red]")
            return None
    
    def validate_scenario(self, scenario_name: str) -> bool:
        """
        验证剧本是否存在且有效
        
        Args:
            scenario_name: 剧本名称
            
        Returns:
            是否有效
        """
        try:
            config = self.loader.load_scenario(scenario_name)
            return self.loader.validate_scenario_config(config)
        except Exception as e:
            console.print(f"[red]剧本验证失败: {e}[/red]")
            return False

# 全局剧本选择器实例
_scenario_selector = None

def get_scenario_selector() -> ScenarioSelector:
    """获取全局剧本选择器实例"""
    global _scenario_selector
    if _scenario_selector is None:
        _scenario_selector = ScenarioSelector()
    return _scenario_selector

def select_scenario_interactive(default_scenario: str = "default_adolescent") -> str:
    """便捷函数：交互式选择剧本"""
    return get_scenario_selector().select_scenario_interactive(default_scenario)

def display_scenarios() -> None:
    """便捷函数：显示所有可用剧本"""
    get_scenario_selector().display_available_scenarios()

def validate_scenario(scenario_name: str) -> bool:
    """便捷函数：验证剧本"""
    return get_scenario_selector().validate_scenario(scenario_name) 