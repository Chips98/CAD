#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import os
import sys
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

from core.gemini_client import GeminiClient
from core.simulation_engine import SimulationEngine
from core.therapy_session_manager import TherapySessionManager


logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


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

def load_config():
    """加载配置"""
    try:
        import config
        history_length = getattr(config, 'CONVERSATION_HISTORY_LENGTH', 5)
        max_events = getattr(config, 'MAX_EVENTS_TO_SHOW', 5)
        return {
            'api_key': config.GEMINI_API_KEY,
            'simulation_speed': getattr(config, 'SIMULATION_SPEED', 1),
            'depression_stages': getattr(config, 'DEPRESSION_DEVELOPMENT_STAGES', 5),
            'conversation_history_length': history_length,
            'max_events_to_show': max_events
        }
    except ImportError:
        console.print("[red]错误: 请复制 config_example.py 为 config.py 并配置您的API密钥和可选设置。[/red]")
        return None
    except AttributeError as e:
        console.print(f"[red]错误: config.py 文件缺少必要的属性: {e}。请检查或使用config_example.py更新。[/red]")
        return None

def create_base_logs_directory():
    """创建基础的logs目录，如果它不存在。"""
    Path("logs").mkdir(exist_ok=True)

def display_welcome():
    """显示欢迎信息"""
    welcome_text = Text("心理健康Agent模拟框架", style="bold blue", justify="center")
    subtitle = Text("模拟学生从健康到抑郁的心理发展过程", style="italic", justify="center")
    
    panel = Panel.fit(
        f"{welcome_text}\n{subtitle}\n\n"
        "本模拟将展示一个学生角色在学校和家庭环境中，\n"
        "由于学业压力、人际关系等因素逐渐发展为抑郁症的过程。\n"
        "所有角色由Gemini AI驱动，提供真实的互动体验。",
        title="🧠 Mental Health Simulation",
        border_style="blue"
    )
    console.print(panel)

def display_simulation_info():
    """显示模拟信息"""
    info_table = Table(title="模拟角色信息")
    info_table.add_column("角色", style="cyan", no_wrap=True)
    info_table.add_column("关系", style="green")
    info_table.add_column("特点", style="yellow")
    
    info_table.add_row("李明", "主角学生", "内向、敏感、完美主义")
    info_table.add_row("李建国", "父亲", "严厉型教育，工程师")
    info_table.add_row("王秀芳", "母亲", "焦虑型，情感敏感")
    info_table.add_row("张老师", "数学老师", "严厉，期望高")
    info_table.add_row("王小明", "最好朋友", "忠诚，支持力强")
    info_table.add_row("刘强", "霸凌者", "攻击性强，缺乏共情")
    info_table.add_row("陈优秀", "竞争对手", "学业优秀，竞争激烈")
    
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
        console.print(Panel(
            f"[bold]模拟总览 (来自 {Path(report_path).name})[/bold]\n"
            f"总天数: {summary.get('total_days', 'N/A')}\n"
            f"最终阶段: {summary.get('final_stage', 'N/A')}\n"
            f"抑郁程度: {summary.get('final_depression_level', 'N/A')}\n"
            f"总事件数: {summary.get('total_events', 'N/A')}",
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
    menu_table = Table(title="🧠 心理健康Agent系统")
    menu_table.add_column("选项", style="cyan", no_wrap=True)
    menu_table.add_column("功能描述", style="green")
    
    menu_table.add_row("1", "运行30天心理健康模拟")
    menu_table.add_row("2", "与模拟后的李明进行心理咨询对话")
    menu_table.add_row("3", "查看现有模拟报告")
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
    display_welcome()
    console.print()
    
    create_base_logs_directory() # 确保 logs/ 存在
    
    config_data = load_config()
    if not config_data:
        return
    
    if not config_data['api_key'] or config_data['api_key'] == "your_gemini_api_key_here":
        console.print("[red]错误: 请在config.py中设置有效的Gemini API密钥[/red]")
        return
    
    try:
        gemini_client = GeminiClient(config_data['api_key'])
        manager_config = {
            "conversation_history_length": config_data.get('conversation_history_length'),
            "max_events_to_show": config_data.get('max_events_to_show')
        }

        while True:
            display_menu()
            
            try:
                choice = console.input("[bold cyan]请选择功能 (0-3): [/bold cyan]").strip()
                
                if choice == "0":
                    console.print("[green]感谢使用心理健康Agent系统！[/green]")
                    break
                
                elif choice == "1":
                    simulation_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    console.print(f"[cyan]准备开始新的模拟: {simulation_id}[/cyan]")
                    setup_simulation_logging(simulation_id)
                    
                    console.print("🎭 正在设置模拟环境...")
                    # 将 simulation_id (或完整路径) 传递给 SimulationEngine
                    # 假设 SimulationEngine 的 __init__ 或 setup_simulation 接受 simulation_log_dir 参数
                    engine = SimulationEngine(gemini_client, simulation_id=simulation_id) 
                    engine.setup_simulation() 
                    display_simulation_info()
                    console.print()
                    console.print("🚀 开始心理健康模拟...")
                    await run_simulation_with_progress(engine, days=30) 
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
                        f"详细日志: logs/{simulation_id}/simulation.log\n"
                        f"完整报告: {report_path}\n"
                        f"每日状态: logs/{simulation_id}/day_*_state.json\n\n"
                        "现在您可以选择功能2与李明进行心理咨询对话，或功能3查看报告。",
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
                        console.print("[yellow]请检查该模拟是否成功完成，或尝试选项 '3' 查看其他模拟。[/yellow]")
                        continue
                    
                    console.print(f"[info]使用配置: 历史长度={manager_config['conversation_history_length']}, 事件显示={manager_config['max_events_to_show']}[/info]")
                    therapy_manager = TherapySessionManager(
                        gemini_client=gemini_client,
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
                
                elif choice == "3":
                    view_existing_reports()
                
                else:
                    console.print("[red]无效选择，请输入 0-3[/red]")
                
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