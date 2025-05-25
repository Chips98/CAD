#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
从现有log直接开始心理咨询 (已重构以支持模拟子文件夹)
读取特定模拟运行的数据，立即开始与李明的心理咨询对话
使用 TherapySessionManager 进行核心会话管理。
支持 Gemini 和 DeepSeek API。
"""

import asyncio
import sys
from pathlib import Path
import json
from typing import List, Dict, Any, Optional, Tuple, Union # 添加 Union

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).resolve().parent.parent)) # 更可靠的路径添加

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# 核心管理器
from core.therapy_session_manager import TherapySessionManager
from core.gemini_client import GeminiClient
from core.deepseek_client import DeepSeekClient  # 添加 DeepSeek 客户端
from agents.therapist_agent import TherapistAgent # 需要初始化Manager

# 假设config.py在项目根目录下
try:
    import config
except ImportError:
    print("错误: config.py 未找到或无法导入。请确保它在项目根目录中。")
    sys.exit(1)

console = Console()

def get_api_client() -> Union[GeminiClient, DeepSeekClient]:
    """
    根据配置获取 API 客户端。
    如果两个 API 密钥都配置了，让用户选择使用哪个。
    """
    has_gemini = config.GEMINI_API_KEY and config.GEMINI_API_KEY != "your_gemini_api_key_here"
    has_deepseek = config.DEEPSEEK_API_KEY and config.DEEPSEEK_API_KEY != ""
    
    if not has_gemini and not has_deepseek:
        console.print("[red]错误: 请在 config.py 中至少设置一个有效的 API 密钥 (GEMINI_API_KEY 或 DEEPSEEK_API_KEY)。[/red]")
        sys.exit(1)
    
    # 如果只有一个 API 可用，直接使用
    if has_gemini and not has_deepseek:
        console.print("[cyan]使用 Gemini API...[/cyan]")
        return GeminiClient(api_key=config.GEMINI_API_KEY)
    elif has_deepseek and not has_gemini:
        console.print("[cyan]使用 DeepSeek API...[/cyan]")
        return DeepSeekClient(
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_BASE_URL,
            model=config.DEEPSEEK_MODEL
        )
    
    # 如果两个都可用，检查默认设置
    default_provider = getattr(config, 'DEFAULT_MODEL_PROVIDER', 'gemini').lower()
    
    # 如果有默认设置且有效，直接使用
    if default_provider == 'gemini' and has_gemini:
        console.print(f"[cyan]使用默认配置的 Gemini API...[/cyan]")
        return GeminiClient(api_key=config.GEMINI_API_KEY)
    elif default_provider == 'deepseek' and has_deepseek:
        console.print(f"[cyan]使用默认配置的 DeepSeek API...[/cyan]")
        return DeepSeekClient(
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_BASE_URL,
            model=config.DEEPSEEK_MODEL
        )
    
    # 让用户选择
    console.print(Panel(
        "[bold blue]选择 API 提供商[/bold blue]\n\n"
        "检测到多个可用的 API 配置：",
        title="🤖 API 选择",
        border_style="blue"
    ))
    
    table = Table(title="可用的 API 提供商")
    table.add_column("选项", style="cyan", no_wrap=True)
    table.add_column("提供商", style="green")
    table.add_column("模型", style="yellow")
    table.add_column("状态", style="magenta")
    
    table.add_row("1", "Gemini", "gemini-2.0-flash", "✅ 已配置")
    table.add_row("2", "DeepSeek", config.DEEPSEEK_MODEL, "✅ 已配置")
    
    console.print(table)
    
    while True:
        choice = console.input("\n[bold cyan]请选择 API 提供商 (1 或 2): [/bold cyan]").strip()
        
        if choice == "1":
            console.print("[green]已选择 Gemini API[/green]")
            return GeminiClient(api_key=config.GEMINI_API_KEY)
        elif choice == "2":
            console.print("[green]已选择 DeepSeek API[/green]")
            return DeepSeekClient(
                api_key=config.DEEPSEEK_API_KEY,
                base_url=config.DEEPSEEK_BASE_URL,
                model=config.DEEPSEEK_MODEL
            )
        else:
            console.print("[red]无效选择，请输入 1 或 2。[/red]")

def scan_simulation_runs() -> List[Dict[str, Any]]:
    """
    扫描 logs/ 目录，查找所有模拟运行 (sim_*) 子文件夹。
    返回一个包含每个模拟运行信息的列表。
    """
    logs_dir = Path("logs")
    if not logs_dir.exists() or not logs_dir.is_dir():
        console.print("[yellow] 'logs' 目录不存在。将尝试创建。[/yellow]")
        try:
            logs_dir.mkdir(parents=True, exist_ok=True)
            return [] # 新创建的目录是空的
        except Exception as e:
            console.print(f"[red]创建 'logs' 目录失败: {e}[/red]")
            return []

    simulation_runs = []
    # 按名称（通常是时间戳）降序排序，最新的在前面
    for sim_dir in sorted(logs_dir.iterdir(), key=lambda p: p.name, reverse=True):
        if sim_dir.is_dir() and sim_dir.name.startswith("sim_"):
            report_path = sim_dir / "final_report.json"
            day_state_files = sorted(list(sim_dir.glob("day_*_state.json")), reverse=True)
            therapy_log_files = list(sim_dir.glob("therapy_session_*.json"))
            therapy_log_files.extend(list(sim_dir.glob("therapy_from_logs_*.json")))
            
            run_info = {
                "id": sim_dir.name,
                "path": sim_dir,
                "has_final_report": report_path.exists(),
                "latest_day_state_file": day_state_files[0] if day_state_files else None,
                "day_state_count": len(day_state_files),
                "therapy_log_count": len(therapy_log_files)
            }
            simulation_runs.append(run_info)
            
    return simulation_runs

def display_simulation_run_menu(simulation_runs: List[Dict[str, Any]]) -> Dict[str, Tuple[str, Path]]:
    """
    显示可用的模拟运行列表作为菜单，让用户选择。
    返回一个选项字典，键是选择编号，值是 ("simulation_run_id", sim_dir_path)。
    """
    console.print(Panel(
        "[bold blue]选择一个模拟运行开始咨询[/bold blue]\n\n"
        "检测到以下模拟运行记录：",
        title="📁 模拟运行选择",
        border_style="blue"
    ))
    
    table = Table(title="可用的模拟运行")
    table.add_column("选项", style="cyan", no_wrap=True)
    table.add_column("模拟ID (文件夹)", style="green")
    table.add_column("状态", style="yellow")
    table.add_column("咨询记录数", style="magenta")
    
    options: Dict[str, Tuple[str, Path]] = {}
    if not simulation_runs:
        console.print("[yellow]在 'logs/' 目录下没有找到 'sim_*' 开头的模拟运行文件夹。[/yellow]")
        console.print("[cyan]请先通过 main.py 运行一次完整的模拟。[/cyan]")
    else:
        for i, run_info in enumerate(simulation_runs):
            option_num = str(i + 1)
            status_parts = []
            if run_info["has_final_report"]:
                status_parts.append("[green]有最终报告[/green]")
            else:
                status_parts.append("[yellow]无最终报告[/yellow]")
            if run_info["latest_day_state_file"]:
                status_parts.append(f"{run_info['day_state_count']}天记录 (最新: {run_info['latest_day_state_file'].name})")
            else:
                status_parts.append("无每日记录")
            
            table.add_row(
                option_num,
                run_info["id"],
                ", ".join(status_parts),
                str(run_info["therapy_log_count"])
            )
            options[option_num] = ("selected_simulation_run", run_info["path"]) # 存储模拟运行的路径
    
    table.add_row("s", "对话设置", "查看配置信息和使用说明")
    table.add_row("0", "退出", "退出系统")
    
    console.print(table)
    return options

def display_data_source_menu(simulation_run_path: Path) -> Dict[str, Tuple[str, Optional[Path]]]:
    """
    在选定的模拟运行中，让用户选择数据源。
    返回一个选项字典，键是选择编号，值是 ("data_file_type", file_path_or_run_path).
    data_file_type 可以是 "final_report", "day_state", "all_history"
    对于 "all_history", file_path_or_run_path 将是 simulation_run_path 本身。
    """
    console.print(Panel(
        f"[bold blue]从模拟运行 {simulation_run_path.name} 中选择数据源[/bold blue]",
        title="💾 数据源选择",
        border_style="blue"
    ))
    table = Table(title=f"模拟 {simulation_run_path.name} 内可用的数据")
    table.add_column("选项", style="cyan", no_wrap=True)
    table.add_column("数据类型", style="green")
    table.add_column("描述/文件名", style="yellow")

    options: Dict[str, Tuple[str, Optional[Path]]] = {}
    option_num = 1

    # 1. "全部历史数据" 选项 (如果final_report存在，以此为基础整合所有每日事件)
    final_report_file = simulation_run_path / "final_report.json"
    if final_report_file.exists():
        table.add_row(str(option_num), "全部历史数据", f"整合 {final_report_file.name} 及所有每日事件")
        # options的第二个元素存储了用于加载的路径或标记
        # 对于"all_history", 我们传递 simulation_run_path, Manager会处理它
        options[str(option_num)] = ("all_history", simulation_run_path) 
        option_num += 1
    else:
        # 如果没有final_report，也允许选择"全部每日数据"（如果存在）
        day_state_files_for_all = sorted(list(simulation_run_path.glob("day_*_state.json")))
        if day_state_files_for_all:
            table.add_row(str(option_num), "全部每日事件", f"整合该模拟的所有 {len(day_state_files_for_all)} 天的事件")
            options[str(option_num)] = ("all_daily_events_only", simulation_run_path)
            option_num += 1

    # 2. 单独的 "最终报告" 选项
    if final_report_file.exists(): # 再次检查，即使在"全部历史"中用过，单独加载也是一个选项
        table.add_row(str(option_num), "最终报告 (单独)", final_report_file.name)
        options[str(option_num)] = ("final_report", final_report_file)
        option_num += 1
    
    # 3. 列出所有可用的每日状态文件，供单独选择
    def extract_day_number(day_file_path):
        """从文件名中提取天数，用于正确排序"""
        try:
            # 支持格式: day_X_state.json 或 day_state_X.json
            stem = day_file_path.stem  # 不带扩展名的文件名
            parts = stem.split('_')
            
            # 尝试 day_X_state 格式
            if len(parts) >= 3 and parts[0] == 'day' and parts[2] == 'state':
                if parts[1].isdigit():
                    return int(parts[1])
            
            # 尝试 day_state_X 格式
            if len(parts) >= 3 and parts[0] == 'day' and parts[1] == 'state':
                if parts[2].isdigit():
                    return int(parts[2])
                    
            # 兜底：尝试找到任何数字部分
            for part in parts:
                if part.isdigit():
                    return int(part)
                    
            return -1  # 如果找不到数字，排在最前面
        except (IndexError, ValueError):
            return -1

    day_state_files = sorted(
        list(simulation_run_path.glob("day_*_state.json")),
        key=extract_day_number,  # 使用新的提取函数
        reverse=False  # 改为升序排列：第1天、第2天...第30天
    )
    
    if day_state_files:
        # 可以考虑只显示最新的几个，或者分页，如果数量很多的话
        # limit_display = 5 
        # console.print(f"[dim]显示最近 {limit_display if len(day_state_files) > limit_display else len(day_state_files)} 个可用的每日状态文件...[/dim]")
        table.add_row(f"[white on blue]--- 单独选择特定某一天的数据 (共 {len(day_state_files)} 天) ---[/white on blue]", "", "")
        for day_file in day_state_files: #[:limit_display]:
            try:
                # 尝试从文件名提取天数，例如 day_15_state.json -> 15
                day_num_str = day_file.stem.split('_')[-2] # 假设格式是 day_X_state
                if day_num_str.isdigit():
                    day_num = int(day_num_str)
                    table.add_row(str(option_num), f"第 {day_num} 天状态", day_file.name)
                    options[str(option_num)] = ("day_state", day_file)
                    option_num += 1
                else: # 兼容 day_state_X.json 格式
                    day_num_str_alt = day_file.stem.split('_')[-1]
                    if day_num_str_alt.isdigit():
                        day_num = int(day_num_str_alt)
                        table.add_row(str(option_num), f"第 {day_num} 天状态", day_file.name)
                        options[str(option_num)] = ("day_state", day_file)
                        option_num += 1
                    else:
                        console.print(f"[yellow]无法解析天数: {day_file.name}[/yellow]")
            except (IndexError, ValueError):
                console.print(f"[yellow]无法从文件名解析天数: {day_file.name}[/yellow]")

    if not options: # 如果该模拟运行下没有找到任何可加载的文件
        console.print(f"[yellow]在模拟运行 {simulation_run_path.name} 中未找到可加载的数据文件。[/yellow]")

    table.add_row("0", "返回上一级", "重新选择模拟运行")
    console.print(table)
    return options

def configure_settings():
    """显示当前配置信息和使用说明"""
    console.print(Panel(
        "[bold blue]咨询系统配置信息[/bold blue]\n\n"
        "以下是从 config.py 读取的默认设置，您可以在咨询过程中动态调整：",
        title="⚙️ 设置信息",
        border_style="blue"
    ))
    
    table = Table(title="当前配置 (来自 config.py)")
    table.add_column("设置项", style="cyan")
    table.add_column("当前值", style="green")
    table.add_column("说明", style="yellow")
    
    # 显示 API 配置
    has_gemini = config.GEMINI_API_KEY and config.GEMINI_API_KEY != "your_gemini_api_key_here"
    has_deepseek = config.DEEPSEEK_API_KEY and config.DEEPSEEK_API_KEY != ""
    
    table.add_row("Gemini API", "✅ 已配置" if has_gemini else "❌ 未配置", "Google Gemini API")
    table.add_row("DeepSeek API", "✅ 已配置" if has_deepseek else "❌ 未配置", "DeepSeek Chat API")
    table.add_row("默认 API", getattr(config, 'DEFAULT_MODEL_PROVIDER', 'gemini'), "默认使用的 API 提供商")
    
    # 显示咨询相关设置
    table.add_row("对话历史长度", str(getattr(config, 'CONVERSATION_HISTORY_LENGTH', 20)), "AI在生成回应时参考的最近对话轮数")
    table.add_row("显示事件数量", str(getattr(config, 'MAX_EVENTS_TO_SHOW', 20)), "在患者状态面板中显示的最近重要事件数量")
    
    # 显示督导相关设置
    table.add_row("启用督导", "✅ 是" if getattr(config, 'ENABLE_SUPERVISION', True) else "❌ 否", "是否启用AI督导功能")
    table.add_row("督导间隔", str(getattr(config, 'SUPERVISION_INTERVAL', 3)), "每N轮对话触发一次督导分析")
    table.add_row("督导分析深度", str(getattr(config, 'SUPERVISION_ANALYSIS_DEPTH', 'COMPREHENSIVE')), "督导分析的详细程度")
    
    console.print(table)
    
    console.print(Panel(
        "[bold cyan]💡 动态调整说明：[/bold cyan]\n\n"
        "• 在咨询过程中，输入 [bold]'s'[/bold] 或 [bold]'settings'[/bold] 可打开设置菜单\n"
        "• 可以实时调整对话历史长度、事件显示数量、督导设置等\n"
        "• 设置更改会立即生效，无需重启程序\n"
        "• 如需修改默认值，请编辑 config.py 文件",
        title="🔧 使用提示",
        border_style="green"
    ))
    
    console.input("\n[cyan]按回车键返回主菜单...[/cyan]")

def view_all_therapy_sessions_globally():
    """全局扫描并查看所有logs/sim_*/therapy_*.json文件。"""
    console.print(Panel("[bold blue]全局历史咨询记录查看[/bold blue]", border_style="blue"))
    logs_dir = Path("logs")
    all_session_files = list(logs_dir.glob("sim_*/therapy_session_*.json"))
    all_session_files.extend(list(logs_dir.glob("sim_*/therapy_from_logs_*.json")))
    # 也包括可能在logs根目录下的旧格式文件
    all_session_files.extend(list(logs_dir.glob("therapy_session_*.json")))
    all_session_files.extend(list(logs_dir.glob("therapy_from_logs_*.json")))
    
    if not all_session_files:
        console.print("[yellow]在 'logs' 及其子目录中没有找到任何咨询记录文件。[/yellow]")
        return

    console.print(f"[green]共找到 {len(all_session_files)} 个历史咨询记录文件：[/green]")
    for i, session_file in enumerate(sorted(list(set(all_session_files)))):
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            session_info = session_data.get("session_info", {})
            display_path = session_file.relative_to(logs_dir.parent) # 显示相对路径
            console.print(f"  [cyan]{i+1}. {display_path}[/cyan]")
            console.print(f"     [dim]ID:[/dim] {session_info.get('session_id', 'N/A')}")
            console.print(f"     [dim]来源:[/dim] {session_info.get('data_source_file', session_info.get('data_source', 'N/A'))}")
            console.print(f"     [dim]时间:[/dim] {session_info.get('start_time', 'N/A')}")
        except Exception as e:
            console.print(f"  [red]读取文件 {session_file.name} 摘要失败: {e}[/red]")
    console.print("-" * 70 + "\n")

async def main_loop(api_client: Union[GeminiClient, DeepSeekClient]):
    """主循环，处理用户选择。"""

    while True:
        simulation_runs = scan_simulation_runs()
        run_options = display_simulation_run_menu(simulation_runs)
        
        choice = console.input("\n[bold cyan]请选择一个模拟运行或操作 (输入编号): [/bold cyan]").strip().lower()

        if choice == "0":
            console.print("[green]感谢使用，系统退出。[/green]")
            break
        elif choice == "s":
            configure_settings()
            continue
        elif choice in run_options:
            _, selected_sim_path = run_options[choice] # selected_sim_path 是模拟运行的目录Path
            
            # 第二层菜单：选择数据源
            while True: 
                data_source_options = display_data_source_menu(selected_sim_path)
                if not data_source_options:
                    console.print(f"[yellow]模拟运行 {selected_sim_path.name} 中没有可供咨询的数据文件。正在返回上一级...[/yellow]")
                    await asyncio.sleep(1)
                    break 

                ds_choice = console.input("\n[bold cyan]请选择数据文件或选项开始咨询 (输入编号, 0 返回): [/bold cyan]").strip().lower()

                if ds_choice == "0":
                    break # 返回到模拟运行选择菜单
                
                if ds_choice in data_source_options:
                    load_type_selected, path_for_loading = data_source_options[ds_choice]
                    
                    console.print(f"[cyan]准备加载数据: 类型='{load_type_selected}', 路径='{path_for_loading}'...[/cyan]")
                    
                    # 使用config中的设置创建TherapySessionManager
                    manager = TherapySessionManager(
                        ai_client=api_client  # 使用传入的 API 客户端
                        # 不再传递参数，让它使用config中的默认值
                    )
                    
                    # 调用 load_patient_data_from_file，传递正确的 load_type 和路径字符串
                    load_successful = manager.load_patient_data_from_file(
                        str(path_for_loading), 
                        load_type=load_type_selected
                    )
                    
                    if load_successful:
                        console.print(f"[green]数据加载成功 (类型: {manager.loaded_data_type})。患者: {manager.patient_data.get('name', '未知')}[/green]")
                        await manager.start_interactive_session()
                        console.print(f"[info]与来自 {path_for_loading.name} 的数据的咨询已结束。[/info]")
                        break # 结束当前模拟的数据源选择，返回到模拟运行选择
                    else:
                        console.print(f"[red]无法从 {path_for_loading.name} (类型: {load_type_selected}) 加载数据。请重试。[/red]")
                else:
                    console.print("[red]无效的数据文件选择。[/red]")
                console.print("---") 
        else:
            console.print("[red]无效的模拟运行选择。[/red]")
        console.print("\n" + "="*70 + "\n")

async def main():
    console.print("[bold blue]🧠 从现有模拟日志开始心理咨询 (v4 - 支持多种 API)[/bold blue]\n")
    
    try:
        # 获取 API 客户端（可能是 Gemini 或 DeepSeek）
        api_client = get_api_client()
        await main_loop(api_client)
    except Exception as e:
        console.print(f"[red]主程序发生严重错误: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]程序被用户中断。[/yellow]")
    except Exception as e:
        console.print(f"[red]脚本执行出错: {e}[/red]")
        import traceback
        traceback.print_exc() 