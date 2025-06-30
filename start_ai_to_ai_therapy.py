#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 首先导入utils包以设置终端编码  
import utils

"""
AI对AI治疗启动脚本
自动运行AI心理咨询师与AI患者的对话会话
"""

import os
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm

from core.ai_client_factory import ai_client_factory
from core.ai_to_ai_therapy_manager import AIToAITherapyManager, run_ai_to_ai_therapy
from config.config_loader import load_api_config
from config.scenario_selector import select_scenario_interactive

console = Console()


def find_simulation_runs() -> List[Dict[str, Any]]:
    """查找可用的模拟运行"""
    simulation_runs = []
    logs_dir = Path("logs")
    
    if not logs_dir.exists():
        return simulation_runs
    
    for sim_dir in logs_dir.iterdir():
        if sim_dir.is_dir() and sim_dir.name.startswith("sim_"):
            final_report = sim_dir / "final_report.json"
            day_files = sorted(list(sim_dir.glob("day_*_state.json")))
            
            if final_report.exists() or day_files:
                try:
                    simulation_info = {
                        'sim_dir': sim_dir,
                        'sim_id': sim_dir.name,
                        'final_report_path': str(final_report) if final_report.exists() else None,
                        'day_files': day_files,
                        'day_count': len(day_files)
                    }
                    
                    # 如果有final_report，读取基本信息
                    if final_report.exists():
                        with open(final_report, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        patient_name = data.get('protagonist_character_profile', {}).get('name', '未知')
                        end_time = data.get('simulation_metadata', {}).get('end_time', '未知时间')
                        depression_level = data.get('final_psychological_state', {}).get('depression_level', '未知')
                        
                        # 从目录名中提取剧本类型
                        scenario_type = 'unknown'
                        if 'primary_school_bullying' in sim_dir.name:
                            scenario_type = 'primary_school_bullying'
                        elif 'university_graduation_pressure' in sim_dir.name:
                            scenario_type = 'university_graduation_pressure'
                        elif 'workplace_pua_depression' in sim_dir.name:
                            scenario_type = 'workplace_pua_depression'
                        elif 'default_adolescent' in sim_dir.name:
                            scenario_type = 'default_adolescent'
                        else:
                            # 如果目录名没有剧本信息，尝试从metadata获取
                            scenario_type = data.get('simulation_metadata', {}).get('scenario_type', 'default_adolescent')
                        
                        simulation_info.update({
                            'patient_name': patient_name,
                            'end_time': end_time,
                            'depression_level': depression_level,
                            'scenario_type': scenario_type,
                            'display_name': f"{patient_name} ({sim_dir.name})"
                        })
                    else:
                        simulation_info.update({
                            'patient_name': '未知',
                            'end_time': '未知时间',
                            'depression_level': '未知',
                            'scenario_type': 'unknown',
                            'display_name': f"未完成模拟 ({sim_dir.name})"
                        })
                    
                    simulation_runs.append(simulation_info)
                    
                except Exception as e:
                    console.print(f"[yellow]读取{sim_dir.name}失败: {e}[/yellow]")
    
    # 按时间排序，最新的在前
    simulation_runs.sort(key=lambda x: x['end_time'], reverse=True)
    return simulation_runs


def display_simulation_selection(simulation_runs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """显示模拟运行选择界面"""
    if not simulation_runs:
        console.print("[red]❌ 未找到任何模拟运行数据[/red]")
        console.print("[yellow]请先运行 'python main.py' 创建模拟数据[/yellow]")
        return None
    
    console.print(Panel.fit(
        "[bold cyan]🤖 AI对AI心理治疗系统[/bold cyan]\n"
        "[dim]选择一个模拟运行开始AI自动治疗会话[/dim]",
        border_style="cyan"
    ))
    
    # 创建模拟运行列表表格
    table = Table(title="可用模拟运行", show_header=True, header_style="bold magenta")
    table.add_column("编号", style="dim", width=4)
    table.add_column("患者姓名", min_width=10)
    table.add_column("模拟ID", style="cyan", min_width=15)
    table.add_column("天数", style="blue", min_width=6)
    table.add_column("抑郁程度", style="yellow", min_width=10)
    table.add_column("结束时间", style="green", min_width=15)
    
    for i, sim_run in enumerate(simulation_runs, 1):
        table.add_row(
            str(i),
            str(sim_run['patient_name']),
            str(sim_run['sim_id']),
            str(sim_run['day_count']),
            str(sim_run['depression_level']),
            str(sim_run['end_time'][:16] if len(sim_run['end_time']) > 16 else sim_run['end_time'])
        )
    
    console.print(table)
    
    # 用户选择
    try:
        choice = IntPrompt.ask(
            "请选择模拟运行编号",
            default=1,
            show_default=True
        )
        
        if 1 <= choice <= len(simulation_runs):
            selected_sim = simulation_runs[choice - 1]
            console.print(f"[green]✅ 已选择模拟运行: {selected_sim['display_name']}[/green]")
            return selected_sim
        else:
            console.print("[red]❌ 无效的选择[/red]")
            return None
            
    except KeyboardInterrupt:
        console.print("\n[yellow]操作已取消[/yellow]")
        return None


def display_day_selection(simulation_run: Dict[str, Any]) -> Optional[str]:
    """显示天数选择界面"""
    console.print(Panel.fit(
        f"[bold cyan]🗓️ 选择治疗起始天数[/bold cyan]\n"
        f"[dim]模拟运行: {simulation_run['display_name']}[/dim]\n"
        f"[yellow]💡 提示: 您可以选择从1-30天中的任意一天开始AI对话治疗[/yellow]",
        border_style="cyan"
    ))
    
    # 创建选项表格
    table = Table(title="🎯 可选择的治疗起始点", show_header=True, header_style="bold magenta")
    table.add_column("编号", style="dim", width=6)
    table.add_column("数据类型", min_width=12)
    table.add_column("天数", style="bold yellow", width=8)
    table.add_column("描述", style="cyan", min_width=25)
    table.add_column("推荐程度", style="green", width=10)
    
    options = []
    
    # 选项1：最终状态（第30天）- 推荐选项
    if simulation_run['final_report_path']:
        table.add_row("1", "最终状态", "第30天", "使用完整模拟后的最终抑郁状态", "⭐⭐⭐")
        options.append(('final_report', simulation_run['final_report_path']))
    
    # 选项2-N：各个天数（按天数排序）
    day_files = simulation_run['day_files']
    if day_files:
        # 按天数排序
        sorted_day_files = []
        for day_file in day_files:
            try:
                day_num = int(day_file.stem.split('_')[1])
                sorted_day_files.append((day_num, day_file))
            except (IndexError, ValueError):
                continue
        
        sorted_day_files.sort(key=lambda x: x[0])  # 按天数排序
        
        for day_num, day_file in sorted_day_files:
            option_num = len(options) + 1
            
            # 根据天数给出不同的推荐程度和描述
            if day_num <= 5:
                recommendation = "⭐"
                description = f"第{day_num}天状态 (早期阶段，可能效果有限)"
            elif day_num <= 15:
                recommendation = "⭐⭐"
                description = f"第{day_num}天状态 (中期阶段，适合观察发展)"
            elif day_num <= 25:
                recommendation = "⭐⭐⭐"
                description = f"第{day_num}天状态 (后期阶段，问题较明显)"
            else:
                recommendation = "⭐⭐"
                description = f"第{day_num}天状态 (接近最终状态)"
            
            table.add_row(
                str(option_num),
                f"每日状态",
                f"第{day_num}天",
                description,
                recommendation
            )
            options.append(('day_state', str(day_file)))
    
    if not options:
        console.print("[red]❌ 该模拟运行中没有可用的数据文件[/red]")
        return None
    
    console.print(table)
    console.print("\n[dim]💡 建议选择第20-30天的数据，此时患者的心理问题更加突出，治疗效果更明显[/dim]")
    
    # 用户选择
    try:
        choice = IntPrompt.ask(
            "请选择治疗起始点的编号",
            default=1,
            show_default=True
        )
        
        if 1 <= choice <= len(options):
            data_type, file_path = options[choice - 1]
            
            # 显示更详细的选择确认
            if data_type == 'final_report':
                console.print(f"[green]✅ 已选择: 最终状态数据 (第30天完整状态)[/green]")
                console.print(f"[dim]文件: {Path(file_path).name}[/dim]")
            else:
                day_info = Path(file_path).stem
                console.print(f"[green]✅ 已选择: {day_info} 状态数据[/green]")
                console.print(f"[dim]文件: {Path(file_path).name}[/dim]")
            
            return file_path
        else:
            console.print("[red]❌ 无效的选择[/red]")
            return None
            
    except KeyboardInterrupt:
        console.print("\n[yellow]操作已取消[/yellow]")
        return None


def select_ai_provider() -> Optional[str]:
    """选择AI提供商"""
    try:
        api_config = load_api_config()
        available_providers = []
        
        # 检查可用的提供商
        if 'providers' in api_config:
            for provider_name, provider_config in api_config['providers'].items():
                if provider_config.get('enabled', True):
                    api_key = provider_config.get('api_key')
                    if api_key and api_key.strip() and api_key != "your_api_key_here":
                        available_providers.append(provider_name)
        
        if not available_providers:
            console.print("[red]❌ 未找到可用的AI提供商配置[/red]")
            console.print("[yellow]请检查config/api_config.json中的API密钥配置[/yellow]")
            return None
        
        if len(available_providers) == 1:
            provider = available_providers[0]
            console.print(f"[green]✅ 使用AI提供商: {provider.upper()}[/green]")
            return provider
        
        # 多个提供商，让用户选择
        console.print("\n🤖 可用AI提供商:")
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("编号", style="dim", width=4)
        table.add_column("提供商", style="bold")
        table.add_column("状态", style="green")
        
        for i, provider in enumerate(available_providers, 1):
            table.add_row(str(i), provider.upper(), "可用")
        
        console.print(table)
        
        choice = IntPrompt.ask(
            "请选择AI提供商",
            choices=[str(i) for i in range(1, len(available_providers) + 1)],
            default="1"
        )
        
        provider = available_providers[choice - 1]
        console.print(f"[green]✅ 已选择: {provider.upper()}[/green]")
        return provider
        
    except Exception as e:
        console.print(f"[red]❌ 加载AI配置失败: {e}[/red]")
        return None


def get_therapy_parameters() -> Dict[str, Any]:
    """获取治疗参数"""
    console.print("\n⚙️ 治疗参数设置:")
    
    max_turns = IntPrompt.ask(
        "最大对话轮数",
        default=15,
        show_default=True
    )
    
    show_progress = Confirm.ask(
        "是否显示实时进展评估",
        default=True
    )
    
    save_log = Confirm.ask(
        "是否保存详细会话记录",
        default=True
    )
    
    return {
        'max_turns': max_turns,
        'show_progress': show_progress,
        'save_log': save_log
    }


async def main():
    """主函数 - 增强版本"""
    try:
        # 首先选择剧本类型（可选）
        console.print("\n[cyan]📖 选择治疗剧本类型（可选）[/cyan]")
        console.print("[dim]您可以选择特定剧本类型，或使用全部可用的模拟数据[/dim]")
        
        use_scenario_filter = Confirm.ask(
            "是否按剧本类型筛选模拟数据",
            default=False
        )
        
        scenario_filter = None
        if use_scenario_filter:
            scenario_filter = select_scenario_interactive("default_adolescent")
            console.print(f"[green]✅ 将筛选包含 '{scenario_filter}' 的模拟数据[/green]")
        
        # 查找模拟运行
        console.print("[cyan]🔍 正在扫描模拟运行数据...[/cyan]")
        simulation_runs = find_simulation_runs()
        
        # 如果设置了剧本筛选，进行筛选
        if scenario_filter:
            filtered_runs = [
                run for run in simulation_runs 
                if scenario_filter in run.get('scenario_type', 'unknown')
            ]
            if filtered_runs:
                simulation_runs = filtered_runs
                console.print(f"[green]✅ 筛选出 {len(simulation_runs)} 个匹配的模拟运行[/green]")
            else:
                console.print(f"[yellow]⚠️ 未找到包含 '{scenario_filter}' 的模拟数据，显示所有可用数据[/yellow]")
        
        # 显示选择界面
        selected_sim = display_simulation_selection(simulation_runs)
        if not selected_sim:
            return
        
        # 显示天数选择
        selected_data_path = display_day_selection(selected_sim)
        if not selected_data_path:
            return
        
        # 选择AI提供商
        ai_provider = select_ai_provider()
        if not ai_provider:
            return
        
        # 获取治疗参数
        therapy_params = get_therapy_parameters()
        
        console.print(f"\n[bold green]🚀 准备启动AI-AI治疗会话（增强版）[/bold green]")
        console.print(f"[cyan]📊 数据源: {selected_data_path}[/cyan]")
        console.print(f"[cyan]🤖 AI提供商: {ai_provider}[/cyan]")
        console.print(f"[cyan]🔄 对话轮数: {therapy_params['max_turns']}[/cyan]")
        console.print(f"[cyan]👨‍🎓 督导间隔: 每3轮[/cyan]")
        console.print(f"[cyan]🎯 状态追踪: 已启用[/cyan]")
        
        if not Confirm.ask("\n[bold yellow]🎯 确认开始AI-AI治疗吗？[/bold yellow]"):
            console.print("[yellow]操作已取消。[/yellow]")
            return
        
        # 创建AI客户端
        ai_client = ai_client_factory.get_client(ai_provider)
        
        console.print(f"\n[bold cyan]🤖 正在启动增强版AI-AI治疗系统...[/bold cyan]")
        
        # 运行AI对AI治疗
        result = await run_ai_to_ai_therapy(
            ai_client=ai_client,
            patient_log_path=selected_data_path,
            max_turns=therapy_params['max_turns']
        )
        
        # 显示结果总结
        console.print(f"\n[bold green]✅ AI-AI治疗会话完成！[/bold green]")
        console.print(f"[cyan]📊 总对话轮数: {result.get('total_turns', 0)}[/cyan]")
        console.print(f"[cyan]📈 平均治疗效果: {result.get('average_effectiveness', 0):.1f}/10[/cyan]")
        
        final_progress = result.get('final_progress')
        if final_progress:
            console.print(f"[cyan]🎯 最终治疗联盟: {final_progress.get('therapeutic_alliance', 0):.1f}/10[/cyan]")
            console.print(f"[cyan]💊 患者情绪状态: {final_progress.get('patient_emotional_state', 0):.1f}/10[/cyan]")
            
            if final_progress.get('breakthrough_moment'):
                console.print(f"[bold green]💫 检测到治疗突破性时刻！[/bold green]")
            
            if final_progress.get('risk_indicators'):
                console.print(f"[yellow]⚠️ 风险提示: {', '.join(final_progress['risk_indicators'])}[/yellow]")
        
        console.print(f"\n[bold blue]📁 详细会话记录已保存到 logs/ 目录[/bold blue]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⏹️ 用户中断操作。[/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ 程序执行出错: {e}[/red]")
        console.print(f"[red]💡 错误类型: {type(e).__name__}[/red]")
        
        # 特殊错误提示
        if "substitute" in str(e).lower():
            console.print(f"[yellow]🔧 检测到模板错误，这通常是由于字符串格式化问题导致的。[/yellow]")
            console.print(f"[yellow]💡 建议: 检查AI客户端配置或重新运行程序。[/yellow]")
        elif "api" in str(e).lower():
            console.print(f"[yellow]🔧 检测到API相关错误。[/yellow]")
            console.print(f"[yellow]💡 建议: 检查网络连接和API密钥配置。[/yellow]")
        
        import traceback
        console.print(f"\n[dim]详细错误信息:[/dim]")
        console.print(f"[dim]{traceback.format_exc()}[/dim]")


def run_interactive_selection():
    """运行交互式选择界面（同步版本，用于脚本调用）"""
    return asyncio.run(main())


if __name__ == "__main__":
    run_interactive_selection() 