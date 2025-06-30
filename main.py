#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 首先导入utils包以设置终端编码
import utils

import asyncio
import logging
import os
import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import json
from datetime import datetime

console = Console()


sys.path.append(str(Path(__file__).resolve().parent))

from core.ai_client_factory import ai_client_factory
from core.simulation_engine import SimulationEngine
from core.therapy_session_manager import TherapySessionManager
from config.scenario_selector import select_scenario_interactive


logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 设置第三方库的日志级别，隐藏HTTP请求信息
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('openai').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)

if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)


current_simulation_file_handler = None

def setup_simulation_logging(simulation_id: str):
    """为特定的模拟运行设置文件日志记录。"""
    global current_simulation_file_handler, logger, formatter
    

    if current_simulation_file_handler:
        logger.removeHandler(current_simulation_file_handler)
        current_simulation_file_handler.close()
        current_simulation_file_handler = None
        
    simulation_log_dir = Path("logs") / simulation_id
    simulation_log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = simulation_log_dir / "simulation.log"
    
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    current_simulation_file_handler = file_handler
    logger.info(f"日志将记录到: {log_file_path}")

def cleanup_simulation_logging():
    """清理特定模拟运行的文件日志记录器。"""
    global current_simulation_file_handler, logger
    if current_simulation_file_handler:
        logger.info(f"停止向 {current_simulation_file_handler.baseFilename} 记录日志。")
        logger.removeHandler(current_simulation_file_handler)
        current_simulation_file_handler.close()
        current_simulation_file_handler = None

def load_config(scenario_name: str = "default_adolescent", use_temp_config: bool = False, temp_name: str = "web_temp"):
    """
    加载配置
    
    Args:
        scenario_name: 场景名称
        use_temp_config: 是否使用临时配置（Web界面使用）
        temp_name: 临时配置名称
    """
    try:
        # 使用新的JSON配置系统
        from config.config_loader import load_complete_config, load_temp_config
        
        # 加载完整配置
        if use_temp_config:
            # 尝试加载临时配置
            temp_config = load_temp_config(temp_name)
            if temp_config:
                console.print(f"[cyan]使用临时配置: {temp_name}[/cyan]")
                config_data = temp_config
            else:
                console.print("[yellow]未找到临时配置，使用默认配置[/yellow]")
                config_data = load_complete_config(scenario_name)
        else:
            config_data = load_complete_config(scenario_name)
        
        if not config_data:
            console.print("[red]错误: 配置加载失败[/red]")
            return None
        
        # 检查可用的AI提供商
        available_providers = ai_client_factory.get_available_providers()
        default_provider = config_data.get('default_provider', 'deepseek')
        
        if not available_providers:
            console.print("[red]错误: 未配置任何AI提供商的API密钥[/red]")
            console.print("[yellow]请在config/api_config.json中配置API密钥[/yellow]")
            return None
        
        # 返回格式化的配置，保持向后兼容
        formatted_config = {
            'available_providers': available_providers,
            'default_provider': default_provider,
            'simulation_speed': config_data.get('simulation_speed', 1),
            'depression_stages': config_data.get('depression_development_stages', 5),
            'interaction_frequency': config_data.get('interaction_frequency', 3),
            'conversation_history_length': config_data.get('conversation_history_length', 20),
            'max_events_to_show': config_data.get('max_events_to_show', 20),
            'simulation_days': config_data.get('simulation_days', 30),
            'events_per_day': config_data.get('events_per_day', 5),
            'enable_supervision': config_data.get('enable_supervision', True),
            'supervision_interval': config_data.get('supervision_interval', 5),
            'log_level': config_data.get('log_level', 'INFO'),
            'protagonist_name': config_data.get('protagonist_name', '李明'),
            'protagonist_age': config_data.get('protagonist_age', 17),
            'scenario_name': scenario_name,
            # 从load_complete_config返回的数据中获取scenario字段
            'scenario': config_data.get('scenario', {
                'name': scenario_name,
                'description': ''
            }),
            # 保存完整配置用于引擎初始化
            'complete_config': config_data
        }
        
        return formatted_config
        
    except Exception as e:
        console.print(f"[red]错误: 配置加载失败: {e}[/red]")
        console.print("[yellow]请检查config/目录下的配置文件[/yellow]")
        return None

def select_ai_provider(available_providers: list, default_provider: str) -> str:
    """选择AI提供商"""
    if len(available_providers) == 1:
        console.print(f"[info]使用唯一可用的AI提供商: {available_providers[0]}[/info]")
        return available_providers[0]
    
    console.print(Panel("[bold blue]选择AI模型提供商[/bold blue]"))
    provider_table = Table()
    provider_table.add_column("编号", style="cyan", no_wrap=True)
    provider_table.add_column("提供商", style="green")
    provider_table.add_column("状态", style="yellow")
    
    for i, provider in enumerate(available_providers, 1):
        status = "默认" if provider == default_provider else "可用"
        provider_table.add_row(str(i), provider.upper(), status)
    
    console.print(provider_table)
    
    while True:
        try:
            choice = console.input(f"[cyan]请选择AI提供商 (1-{len(available_providers)}) 或回车使用默认: [/cyan]").strip()
            
            if not choice:  # 使用默认
                return default_provider
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(available_providers):
                selected_provider = available_providers[choice_idx]
                console.print(f"[green]已选择: {selected_provider.upper()}[/green]")
                return selected_provider
            else:
                console.print("[red]无效选择，请重新输入[/red]")
        except ValueError:
            console.print("[red]请输入有效的数字[/red]")
        except KeyboardInterrupt:
            console.print("\n[yellow]使用默认提供商[/yellow]")
            return default_provider

def create_base_logs_directory():
    """创建基础的logs目录，如果它不存在。"""
    Path("logs").mkdir(exist_ok=True)

def display_welcome(): 
    """显示欢迎信息"""
    welcome_text = Text("心理健康Agent模拟框架", style="bold blue", justify="center")
    subtitle     = Text("模拟心理健康发展过程的AI系统", style="italic", justify="center")
    
    panel = Panel.fit(
        f"{welcome_text}\n{subtitle}\n\n"
        "本系统通过多个AI智能体模拟真实的人际互动环境，\n"
        "展示心理健康状况在各种压力因素影响下的变化过程。\n"
        "支持自定义场景配置，可模拟不同的心理健康情境。",
        title        = "🧠 Mental Health Simulation",
        border_style = "blue"
    )
    console.print(panel)

def get_scenario_description(engine=None): 
    """根据配置生成场景描述"""
    if engine and hasattr(engine, 'config'):
        # 获取主角信息
        protagonist_config = engine.config.CHARACTERS.get('protagonist', {})
        protagonist_name = protagonist_config.get('name', '主角')
        protagonist_age = protagonist_config.get('age', '')
        
        # 获取阶段信息
        stages = list(engine.config.STAGE_CONFIG.keys())
        stages_str = " → ".join(stages[:3]) + "..."
        
        return f"即将开始模拟 {protagonist_name}（{protagonist_age}岁）的心理发展过程\n发展阶段：{stages_str}"
    else:
        return "即将开始心理健康模拟"

def display_simulation_info(engine=None): 
    """显示模拟信息"""
    info_table = Table(title="模拟角色信息")
    info_table.add_column("角色", style="cyan", no_wrap=True)
    info_table.add_column("类型", style="green")
    info_table.add_column("特点", style="yellow")
    
    if engine and hasattr(engine, 'config'): 
        # 从配置中动态读取角色信息
        for char_id, char_config in engine.config.CHARACTERS.items():
            name = char_config.get('name', '未知')
            char_type = char_config.get('type', '').replace('Agent', '')
            
            # 提取关键特征
            personality = char_config.get('personality', {})
            traits = []
            
            if 'traits' in personality:
                traits.extend(personality['traits'][:2])  # 取前两个特征
            elif 'occupation' in personality:
                traits.append(personality['occupation'])
            elif 'teaching_style' in personality:
                traits.append(personality['teaching_style'])
            
            if char_id == 'protagonist':
                char_type = "主角"
            
            traits_str = "、".join(traits) if traits else "多样化性格"
            info_table.add_row(name, char_type, traits_str)
    else: 
        # 如果没有engine，尝试加载默认配置来显示
        try: 
            import sim_config.simulation_config as default_config
            for char_id, char_config in default_config.CHARACTERS.items(): 
                name = char_config.get('name', '未知')
                char_type = char_config.get('type', '').replace('Agent', '')
                
                # 提取关键特征
                personality = char_config.get('personality', {})
                traits = []
                
                if 'traits' in personality:
                    traits.extend(personality['traits'][:2])
                elif 'occupation' in personality:
                    traits.append(personality['occupation'])
                elif 'teaching_style' in personality:
                    traits.append(personality['teaching_style'])
                
                if char_id == 'protagonist':
                    char_type = "主角"
                
                traits_str = "、".join(traits) if traits else "多样化性格"
                info_table.add_row(name, char_type, traits_str)
        except ImportError:
            # 如果连默认配置都没有，显示占位信息
            info_table.add_row("待定", "主角", "将根据配置确定")
            info_table.add_row("待定", "支持角色", "家人、朋友、老师等")
            info_table.add_row("待定", "环境角色", "影响主角发展的人物")
    
    console.print(info_table)

async def run_simulation_with_progress(engine: SimulationEngine, days: int = 30): 
    """带进度条的模拟执行"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("正在运行心理健康模拟...", total=None)
        
        try:
            await engine.run_simulation(days)
            progress.update(task, description="✅ 模拟完成")
        except Exception as e:
            progress.update(task, description=f"❌ 模拟出错: {e}")
            raise

def display_results_summary(report_path: str):
    """显示结果摘要，现在report_path是完整路径"""
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        summary = report.get("simulation_summary", {})
        journey = report.get("protagonist_journey", {})
        
        # 获取主角名称
        protagonist_name = "主角"
        if journey and 'final_state' in journey: 
            # 尝试从最终状态中提取名称
            final_state = journey['final_state']
            if isinstance(final_state, str) and '：' in final_state:
                protagonist_name = final_state.split('：')[0]
        
        console.print(Panel(
            f"[bold]模拟总览 (来自 {Path(report_path).name})[/bold]\n"
            f"主角: {protagonist_name}\n"
            f"总天数: {summary.get('total_days', 'N/A')}\n"
            f"最终阶段: {summary.get('final_stage', 'N/A')}\n"
            f"心理状态: {summary.get('final_depression_level', 'N/A')}\n"
            f"总事件数: {summary.get('total_events', 'N/A')}\n"
            f"事件多样性: {summary.get('event_variety_score', 0):.2%}",
            title="📊 模拟结果",
            border_style="green"
        ))
        journey = report.get("protagonist_journey", {})
        symptoms = journey.get("key_symptoms", [])
        risk_factors = journey.get("risk_factors", [])
        if symptoms:
            console.print(Panel("\n".join(f"• {symptom}" for symptom in symptoms), title="🔍 观察到的抑郁症状", border_style="yellow"))
        if risk_factors:
            console.print(Panel("\n".join(f"• {factor}" for factor in risk_factors), title="⚠️ 识别的风险因素", border_style="red"))
        ai_analysis = report.get("ai_analysis", "")
        if ai_analysis:
            console.print(Panel(ai_analysis, title="🤖 AI专业分析", border_style="blue"))
            
    except FileNotFoundError:
        console.print(f"[red]错误: 找不到报告文件 {report_path}[/red]")
    except json.JSONDecodeError:
        console.print(f"[red]错误: 报告文件 {report_path} 格式错误[/red]")

def display_menu():
    """显示主菜单"""
    config_data = load_config()
    menu_table = Table(title="🧠 心理健康Agent系统")
    menu_table.add_column("选项", style="cyan", no_wrap=True)
    menu_table.add_column("功能描述", style="green")
    
    menu_table.add_row("1", f"运行心理健康模拟（{config_data['simulation_days']}天）")
    menu_table.add_row("2", "与模拟主角进行人工治疗师对话")
    menu_table.add_row("3", "启动AI治疗师与模拟主角对话")
    menu_table.add_row("4", "查看现有模拟报告")
    menu_table.add_row("5", "心理模型配置")
    menu_table.add_row("0", "退出系统")
    
    console.print(menu_table)
    console.print()

def view_existing_reports():
    """查看现有的模拟报告和咨询记录(需要更新以支持子目录)"""
    console.print("[blue]正在查找现有报告和咨询记录...[/blue]")
    logs_dir = Path("logs")
    if not logs_dir.exists() or not any(logs_dir.iterdir()):
        console.print("[yellow]'logs' 目录不存在或为空。[/yellow]")
        return

    simulation_runs = [d for d in logs_dir.iterdir() if d.is_dir() and d.name.startswith("sim_")]
    
    if not simulation_runs:
        console.print("[yellow]未找到任何已记录的模拟运行。[/yellow]")

        old_final_report = logs_dir / "final_report.json"
        if old_final_report.exists():
            console.print(f"[cyan]发现旧格式的最终报告: {old_final_report}[/cyan]")
            display_results_summary(str(old_final_report))
        return

    console.print(Panel("[bold green]发现以下模拟运行记录：[/bold green]"))
    for i, run_dir in enumerate(simulation_runs):
        console.print(f"  [cyan]{i+1}. {run_dir.name}[/cyan]")
        report_path = run_dir / "final_report.json"
        if report_path.exists():
            console.print(f"     [green]包含最终报告 (final_report.json)[/green]")
        else:
            console.print(f"     [yellow]缺少最终报告[/yellow]")
        therapy_logs_path = run_dir 
        therapy_files = list(therapy_logs_path.glob("therapy_session_*.json"))
        therapy_files.extend(list(therapy_logs_path.glob("therapy_from_logs_*.json")))
        if therapy_files:
            console.print(f"     [magenta]包含 {len(therapy_files)} 个咨询记录[/magenta]")

    try:
        choice = console.input("\n[cyan]输入编号查看模拟运行的最终报告 (或 '0' 返回): [/cyan]").strip()
        if choice == '0': return
        selected_index = int(choice) - 1
        if 0 <= selected_index < len(simulation_runs):
            selected_run_dir = simulation_runs[selected_index]
            report_to_display = selected_run_dir / "final_report.json"
            if report_to_display.exists():
                display_results_summary(str(report_to_display))
            else:
                console.print(f"[red]选定的模拟运行 {selected_run_dir.name} 没有找到 final_report.json。[/red]")
        else:
            console.print("[red]无效选择。[/red]")
    except ValueError:
        console.print("[red]请输入有效的数字。[/red]")
    console.print("-"*50)

async def main(): 
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='心理健康Agent模拟框架')
    parser.add_argument('-c', '--config', type=str, default='sim_config.simulation_config',
                        help='配置模块路径 (默认: sim_config.simulation_config)')
    parser.add_argument('--model', type=str, help='指定心理模型类型')
    parser.add_argument('--interactive-model', action='store_true', 
                        help='交互式选择心理模型')
    args = parser.parse_args()
    
    # 存储配置模块路径
    config_module = args.config
    
    display_welcome()
    console.print()
    
    create_base_logs_directory() # 确保 logs/ 存在
    
    config_data = load_config()
    if not config_data:
        return
    
    # 选择AI提供商
    selected_provider = select_ai_provider(
        config_data['available_providers'], 
        config_data['default_provider']
    )
    
    # 初始化心理模型选择器
    from models.model_selector import ModelSelector
    model_selector = ModelSelector(console)
    
    # 心理模型选择
    psychological_model = None
    if args.interactive_model:
        # 交互式选择
        ai_client = ai_client_factory.get_client(selected_provider)
        model_type, model_config = model_selector.select_model_interactive(ai_client)
        psychological_model = model_selector.create_model_instance(model_type, model_config, ai_client)
        console.print(f"[green]已配置心理模型: {psychological_model.get_display_name()}[/green]")
    elif args.model:
        # 命令行指定模型
        ai_client = ai_client_factory.get_client(selected_provider)
        model_type, model_config = model_selector.quick_select(args.model, ai_client)
        psychological_model = model_selector.create_model_instance(model_type, model_config, ai_client)
        console.print(f"[green]使用指定心理模型: {psychological_model.get_display_name()}[/green]")
    
    try:
        # 获取AI客户端
        ai_client = ai_client_factory.get_client(selected_provider)
        manager_config = {
            "conversation_history_length": config_data.get('conversation_history_length'),
            "max_events_to_show": config_data.get('max_events_to_show')
        }

        while True:
            display_menu()
            
            try:
                choice = console.input("[bold cyan]请选择功能 (0-5): [/bold cyan]").strip()
                
                if choice == "0":
                    console.print("[green]感谢使用心理健康Agent系统！[/green]")
                    break
                
                elif choice == "1":
                    # 添加剧本选择功能
                    console.print("\n[cyan]📖 选择模拟剧本[/cyan]")
                    selected_scenario = select_scenario_interactive("default_adolescent")
                    
                    # 重新加载选定剧本的配置
                    config_data = load_config(selected_scenario)
                    if not config_data:
                        console.print("[red]错误: 剧本配置加载失败[/red]")
                        continue
                    
                    # 如果还没有选择心理模型，提供快速选择
                    if not psychological_model:
                        console.print("\n[yellow]当前未配置心理模型，使用默认模型[/yellow]")
                        try:
                            ai_client = ai_client_factory.get_client(selected_provider)
                            model_type, model_config = model_selector.quick_select(None, ai_client)
                            psychological_model = model_selector.create_model_instance(model_type, model_config, ai_client)
                        except Exception as e:
                            console.print(f"[yellow]心理模型加载失败，将使用传统方法: {e}[/yellow]")
                            psychological_model = None
                    
                    simulation_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{selected_scenario}"
                    console.print(f"[cyan]准备开始新的模拟: {simulation_id}[/cyan]")
                    
                    # 显示使用的心理模型
                    if psychological_model:
                        console.print(f"[green]心理模型: {psychological_model.get_display_name()}[/green]")
                    else:
                        console.print("[yellow]心理模型: 传统规则系统[/yellow]")
                    
                    setup_simulation_logging(simulation_id)
                    
                    console.print("🎭 正在设置模拟环境...")
                    console.print(f"[cyan]使用剧本: {config_data['scenario']['name']}[/cyan]")
                    # 使用选定的AI提供商和新的JSON配置创建模拟引擎
                    engine = SimulationEngine(
                        simulation_id  = simulation_id,
                        config_module  = config_module,  # 保持向后兼容
                        model_provider = selected_provider,
                        config_data    = config_data['complete_config'],  # 传递完整配置数据
                        psychological_model = psychological_model  # 传递心理模型
                    )
                    
                    engine.setup_simulation() 
                    display_simulation_info(engine)
                    console.print()
                    
                    # 显示场景描述
                    scenario_desc = get_scenario_description(engine)
                    console.print(Panel(scenario_desc, title="📖 模拟场景", border_style="cyan"))
                    console.print()
                    
                    console.print("🚀 开始心理健康模拟...")
                    await run_simulation_with_progress(engine, days=config_data['simulation_days']) 
                    console.print()
                    console.print("📋 正在生成结果报告...")
                    
                    # SimulationEngine 现在应将报告保存到其自己的子目录中
                    # report_path 将是 logs/{simulation_id}/final_report.json
                    report_path = Path("logs") / simulation_id / "final_report.json"
                    if report_path.exists():
                        display_results_summary(str(report_path))
                    else:
                        console.print(f"[yellow]模拟 {simulation_id} 未找到最终报告。[/yellow]")
                    
                    console.print()
                    console.print(Panel(
                        f"[bold green]模拟 {simulation_id} 完成！[/bold green]\n\n"
                        f"使用AI模型: {selected_provider.upper()}\n"
                        f"详细日志: logs/{simulation_id}/simulation.log\n"
                        f"完整报告: {report_path}\n"
                        f"每日状态: logs/{simulation_id}/day_*_state.json\n\n"
                        "现在您可以选择功能2与模拟主角进行心理咨询对话，或功能3查看报告。",
                        title="✅ 任务完成",
                        border_style="green"
                    ))
                    cleanup_simulation_logging() # 清理当前模拟的日志处理器
                
                elif choice == "2": # 与模拟后的李明进行咨询
                    console.print("💬 准备开始心理咨询对话模式...")
                    # 需要让用户选择从哪个模拟运行加载数据
                    # 这部分可以调用 start_therapy_from_logs.py 的逻辑，或者在这里简化实现
                    
                    logs_dir = Path("logs")
                    simulation_runs = sorted([d for d in logs_dir.iterdir() if d.is_dir() and d.name.startswith("sim_")], reverse=True)

                    if not simulation_runs:
                        console.print("[red]错误: 未找到任何模拟运行记录。[/red]")
                        console.print("[yellow]请先运行选项 '1' 完成一次心理健康模拟。[/yellow]")
                        continue
                    
                    # 默认加载最新的模拟报告
                    latest_run_dir = simulation_runs[0]
                    final_report_path = latest_run_dir / "final_report.json"
                    
                    console.print(f"[info]将尝试从最新的模拟运行加载数据: {latest_run_dir.name}[/info]")
                    
                    if not final_report_path.exists():
                        console.print(f"[red]错误: 最新的模拟运行 {latest_run_dir.name} 中未找到 final_report.json。[/red]")
                        console.print("[yellow]请检查该模拟是否成功完成，或尝试选项 '4' 查看其他模拟。[/yellow]")
                        continue
                    
                    console.print(f"[info]使用配置: 历史长度={manager_config['conversation_history_length']}, 事件显示={manager_config['max_events_to_show']}[/info]")
                    therapy_manager = TherapySessionManager(
                        ai_client=ai_client,
                        conversation_history_length=manager_config['conversation_history_length'],
                        max_events_to_show=manager_config['max_events_to_show']
                    )
                    
                    # TherapySessionManager需要知道报告的原始路径，以便保存咨询记录到同一子目录
                    # 我们可以在 patient_data 中存储来源路径，或者 TherapySessionManager.load_patient_data_from_file
                    # 内部记录这个路径。 TherapySessionManager.load_patient_data_from_file 已经这样做了。
                    if therapy_manager.load_patient_data_from_file(str(final_report_path)):
                        console.print(f"[green]已成功从 {final_report_path.name} 加载患者最终状态。[/green]")
                        # TherapySessionManager.save_session_log 现在需要知道原始报告的目录
                        # 它可以通过 self.patient_data 中存储的 file_path 的 parent 推断出来
                        await therapy_manager.start_interactive_session(provide_supervision=True, supervision_interval=3)
                    else:
                        console.print(f"[red]加载患者最终状态失败: {final_report_path}[/red]")
                
                elif choice == "3": # AI治疗师与模拟主角对话
                    console.print("🤖 准备启动AI治疗师对话模式...")
                    
                    # 检查是否有可用的模拟数据
                    logs_dir = Path("logs")
                    simulation_runs = sorted([d for d in logs_dir.iterdir() if d.is_dir() and d.name.startswith("sim_")], reverse=True)

                    if not simulation_runs:
                        console.print("[red]错误: 未找到任何模拟运行记录。[/red]")
                        console.print("[yellow]请先运行选项 '1' 完成一次心理健康模拟。[/yellow]")
                        continue
                    
                    # 使用最新的模拟数据启动AI-AI对话
                    latest_run_dir = simulation_runs[0]
                    console.print(f"[info]将使用最新的模拟数据: {latest_run_dir.name}[/info]")
                    
                    # 导入并启动AI-AI治疗模块
                    try:
                        from start_ai_to_ai_therapy import main as ai_therapy_main
                        console.print("[green]正在启动AI治疗师对话系统...[/green]")
                        await ai_therapy_main()
                    except ImportError as e:
                        console.print(f"[red]错误: 无法导入AI治疗模块: {e}[/red]")
                        console.print("[yellow]请确保start_ai_to_ai_therapy.py文件存在且可用[/yellow]")
                    except Exception as e:
                        console.print(f"[red]AI治疗模式运行时发生错误: {e}[/red]")
                        logging.exception("AI治疗模式运行错误")
                
                elif choice == "4":
                    view_existing_reports()
                
                elif choice == "5":
                    # 心理模型配置
                    console.print("\n[cyan]🧠 心理模型配置[/cyan]")
                    
                    try:
                        # 获取AI客户端
                        ai_client = ai_client_factory.get_client(selected_provider)
                        
                        # 交互式选择心理模型
                        model_type, model_config = model_selector.select_model_interactive(ai_client)
                        psychological_model = model_selector.create_model_instance(model_type, model_config, ai_client)
                        
                        console.print(Panel(
                            f"[bold green]心理模型配置完成！[/bold green]\n\n"
                            f"模型类型: {psychological_model.get_display_name()}\n"
                            f"模型描述: {psychological_model.get_description()}\n"
                            f"CAD支持: {'✓' if psychological_model.supports_cad_state() else '✗'}\n"
                            f"异步处理: {'✓' if psychological_model.supports_async_processing() else '✗'}\n\n"
                            "配置已保存，下次运行模拟时将使用此模型。\n"
                            "您也可以使用命令行参数 --model 指定特定模型。",
                            title="✅ 配置完成",
                            border_style="green"
                        ))
                        
                        # 显示模型统计信息（如果有）
                        if hasattr(psychological_model, 'get_model_info'):
                            model_selector.display_model_statistics(psychological_model)
                            
                    except Exception as e:
                        console.print(f"[red]心理模型配置失败: {e}[/red]")
                        logging.exception("心理模型配置错误")
                
                else:
                    console.print("[red]无效选择，请输入 0-5[/red]")
                
                console.print("\n" + "="*50 + "\n")
                
            except KeyboardInterrupt:
                console.print("\n[yellow]操作被用户中断[/yellow]")
                cleanup_simulation_logging() # 确保即使中断也清理日志处理器
                continue
            except Exception as e:
                console.print(f"[red]处理选项时发生错误: {e}[/red]")
                logging.exception("处理菜单选项时发生错误")
                cleanup_simulation_logging()
                continue 
        
    except KeyboardInterrupt:
        console.print("\n[yellow]程序被用户中断[/yellow]")
    except Exception as e:
        console.print(f"[red]主程序运行时发生严重错误: {e}[/red]")
        logging.exception("主程序运行时发生错误")
    finally:
        cleanup_simulation_logging() # 程序退出前确保清理

if __name__ == "__main__":
    try:
        if sys.version_info < (3, 8):
            console.print("[red]错误: 需要Python 3.8或更高版本运行此程序。[/red]")
            sys.exit(1)
        
        asyncio.run(main())
        
    except KeyboardInterrupt:
        console.print("\n[yellow]程序已通过Ctrl+C退出[/yellow]")
    except Exception as e:
        console.print(f"[bold red]💥 程序意外终止: {e}[/bold red]")
        logging.critical(f"程序因未捕获的异常而终止: {e}", exc_info=True)
        sys.exit(1) 