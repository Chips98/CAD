#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
import asyncio 
from datetime import datetime 
from typing import Optional, Union, Dict, List, Any
from agents.therapist_agent import TherapistAgent 
import config

# 可配置的常量，可以从config.py导入或在这里定义
CONVERSATION_HISTORY_LENGTH = 20
MAX_EVENTS_TO_SHOW = 5

console = Console()

# 抑郁程度映射（用于恢复机制）
DEPRESSION_LEVELS = {
    "HEALTHY": 0,      # 健康
    "MILD_RISK": 1,    # 轻度风险  
    "MODERATE": 2,     # 中度抑郁
    "SEVERE": 3,       # 重度抑郁
    "CRITICAL": 4      # 严重抑郁
}

# 反向映射
DEPRESSION_LEVEL_NAMES = {v: k for k, v in DEPRESSION_LEVELS.items()}

class TherapySessionManager:
    """
    管理心理咨询对话的核心类。
    负责加载患者数据、生成回应、管理对话历史等。
    """
    def __init__(self, 
                 ai_client                  : Union['GeminiClient', 'DeepSeekClient'],
                 therapist_agent            : TherapistAgent = None,
                 conversation_history_length: int = None,                              # 默认从config读取
                 max_events_to_show         : int = None)                            : # 默认从config读取
        self.ai_client            = ai_client
        self.therapist_agent      = therapist_agent if therapist_agent else TherapistAgent("专业心理督导", ai_client)
        self.patient_data         = None
        self.conversation_history = []
        
        # 使用传入的配置或config中的默认值
        self.conversation_history_length = conversation_history_length or getattr(config, 'CONVERSATION_HISTORY_LENGTH', 20)
        self.max_events_to_show = max_events_to_show or getattr(config, 'MAX_EVENTS_TO_SHOW', 20)
        
        # 督导相关的运行时设置（可在程序中动态调整）
        self.enable_supervision = getattr(config, 'ENABLE_SUPERVISION', True)
        self.supervision_interval = getattr(config, 'SUPERVISION_INTERVAL', 3)
        self.supervision_analysis_depth = getattr(config, 'SUPERVISION_ANALYSIS_DEPTH', 'COMPREHENSIVE')
        
        self.current_patient_file_path: Optional[Path] = None # 新增，用于存储加载文件的原始路径
        self.current_simulation_id: Optional[str] = None # 新增，用于存储当前模拟的ID
        self.loaded_data_type: Optional[str] = None # 新增，记录加载的数据类型
        
        # 恢复机制相关属性
        self.initial_depression_level: Optional[str] = None  # 记录初始抑郁程度
        self.current_depression_level: Optional[str] = None  # 当前抑郁程度
        self.recovery_progress: List[Dict] = []  # 记录恢复进展
        self.therapeutic_alliance_score: float = 0.0  # 治疗联盟分数 (0-10)
        self.session_effectiveness_scores: List[float] = []  # 每轮对话的效果分数
        
        console.print(f"[debug]TherapySessionManager initialized with history_length={self.conversation_history_length}, max_events={self.max_events_to_show}, supervision_interval={self.supervision_interval}[/debug]")

    def _format_final_report_data(self, report_data: dict, file_path: Path, is_part_of_all_history: bool = False) -> dict:
        """格式化从final_report.json加载的数据"""
        journey = report_data.get("protagonist_journey", {})
        events = report_data.get("significant_events", []) # 这是报告中定义的"重要"事件
        simulation_summary = report_data.get("simulation_summary", {})
        character_profile = report_data.get("protagonist_character_profile", {})
        
        source_desc = f"最终报告 ({file_path.name})" 
        if is_part_of_all_history:
            source_desc = f"完整历史数据 (基于 {file_path.name})"
        
        # 从character_profile获取角色信息，如果没有则使用默认值
        protagonist_name = character_profile.get("name", "李明")
        protagonist_age = character_profile.get("age", 17)
        
        formatted_data = {
            "data_source_file": str(file_path), 
            "data_source": source_desc,
            "simulation_id": simulation_summary.get("simulation_id", file_path.parent.name if file_path.parent.name.startswith("sim_") else None),
            "name": protagonist_name,
            "age": protagonist_age,
            "depression_level": simulation_summary.get("final_depression_level", "SEVERE"),
            "final_state_description": journey.get("final_state", ""), # Renamed from final_state to avoid confusion
            "symptoms": journey.get("key_symptoms", []),
            "risk_factors": journey.get("risk_factors", []),
            "significant_events": events[-self.max_events_to_show:] if events else [], # 显示在面板上的重要事件
            "report_defined_significant_events": events, # 存储报告中定义的所有重要事件
            "full_event_log": [], # 用于存储所有每日事件（如果加载全部历史）
            "total_days": simulation_summary.get("total_days", 30),
            "total_events_in_report": simulation_summary.get("total_events", 0),
            "ai_analysis": report_data.get("ai_analysis", ""), # 添加AI分析
            "protagonist_character_profile": character_profile  # 添加角色配置信息
        }
        return formatted_data

    def _format_day_state_data(self, day_data: dict, day_number: int, file_path: Path, is_part_of_all_history: bool = False) -> dict:
        """格式化从day_X_state.json加载的数据"""
        protagonist_state = day_data.get("protagonist", {}).get("current_mental_state", {})
        protagonist_info = day_data.get("protagonist", {})
        source_desc = f"第{day_number}天状态 ({file_path.name})"
        if is_part_of_all_history:
             source_desc = f"第{day_number}天状态 (作为完整历史的一部分)"
        
        formatted_data = {
            "data_source_file": str(file_path),
            "data_source": source_desc,
            "simulation_id": file_path.parent.name if file_path.parent.name.startswith("sim_") else None,
            "name": protagonist_info.get("name", "李明"),
            "age": protagonist_info.get("age", 17),
            "depression_level": protagonist_state.get("depression_level", "MODERATE"),
            "final_state_description": f"情绪: {protagonist_state.get('emotion', 'N/A')}, 压力: {protagonist_state.get('stress_level', 'N/A')}/10, 自尊: {protagonist_state.get('self_esteem', 'N/A')}/10",
            "symptoms": protagonist_state.get("symptoms", []),
            "risk_factors": protagonist_state.get("risk_factors", []),
            "significant_events": day_data.get("events", [])[-self.max_events_to_show:], # 当天面板上显示的事件
            "daily_events": day_data.get("events", []), # 当天所有事件，用于合并
            "current_day": day_number,
            "stress_level": protagonist_state.get("stress_level", 0),
            "self_esteem": protagonist_state.get("self_esteem", 0),
            "social_connection": protagonist_state.get("social_connection", 0)
        }
        return formatted_data

    def load_patient_data_from_file(self, file_or_dir_path_str: str, load_type: str = "auto") -> bool:
        """
        从指定的JSON文件或目录加载患者数据。
        根据文件名或目录名自动判断是final_report还是每日状态，或加载全部历史数据。
        """
        self.reset_session() # 每次加载新文件时重置会话
        input_path = Path(file_or_dir_path_str).resolve() # 使用绝对路径
        if not input_path.exists():
            console.print(f"[red]错误: 路径不存在 {input_path}[/red]")
            return False
        
        self.current_patient_file_path = input_path # 存储文件路径
        # 推断 simulation_id 和设置 current_patient_file_path
        if input_path.is_dir() and input_path.name.startswith("sim_") and input_path.parent.name == "logs":
            self.current_simulation_id = input_path.name
            self.current_patient_file_path = input_path # 对于目录加载，指向目录
            console.print(f"[debug]从目录路径推断出 Simulation ID: {self.current_simulation_id}[/debug]")
        elif input_path.is_file():
            self.current_patient_file_path = input_path
            if input_path.parent.name.startswith("sim_") and input_path.parent.parent.name == "logs":
                self.current_simulation_id = input_path.parent.name
                console.print(f"[debug]从文件路径推断出 Simulation ID: {self.current_simulation_id}[/debug]")
            else:
                self.current_simulation_id = None
                console.print(f"[debug]无法从文件路径 {input_path} 的父目录推断 Simulation ID。[/debug]")
        else:
            self.current_simulation_id = None
            self.current_patient_file_path = input_path # 即使不是标准结构，也记录一下
            console.print(f"[debug]提供的路径 {input_path} 不是标准的模拟子目录或文件结构。[/debug]")

        self.loaded_data_type = load_type
        try:
            if load_type == "all_history" or load_type == "all_daily_events_only":
                if not input_path.is_dir():
                    console.print(f"[red]错误: 加载 '{load_type}' 需要一个模拟运行的目录路径，而不是文件。[/red]")
                    return False
                sim_run_path = input_path
                self.patient_data = {}
                all_daily_events_combined = []
                
                if load_type == "all_history":
                    final_report_file = sim_run_path / "final_report.json"
                    if final_report_file.exists():
                        with open(final_report_file, 'r', encoding='utf-8') as f:
                            report_content = json.load(f)
                        self.patient_data = self._format_final_report_data(report_content, final_report_file, is_part_of_all_history=True)
                        console.print(f"[green]已加载基础最终报告: {final_report_file.name}[/green]")
                    else:
                        console.print(f"[yellow]警告: 在 {sim_run_path.name} 中未找到 final_report.json。'all_history' 将只包含每日事件。[/yellow]")
                        self.patient_data = {}  # 初始化空字典
                        self.patient_data["data_source"] = f"完整历史数据 (无最终报告，来自 {sim_run_path.name})"
                        self.patient_data["simulation_id"] = self.current_simulation_id
                        self.patient_data["name"] = "主角 (历史数据)"
                        self.patient_data["age"] = 17
                        # ...可以尝试从最新的每日数据补充一些基础信息
                
                if load_type == "all_daily_events_only" and not self.patient_data:
                     self.patient_data = {}  # 初始化空字典
                     self.patient_data["data_source"] = f"所有每日事件 (来自 {sim_run_path.name})"
                     self.patient_data["simulation_id"] = self.current_simulation_id
                     self.patient_data["name"] = "主角 (每日历史)"
                     # ... (可能需要从最新一天获取一些基础信息)

                def extract_day_number_from_file(day_file_path):
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
                                
                        return float('inf')  # 如果找不到数字，排在最后面
                    except (IndexError, ValueError):
                        return float('inf')

                day_state_files = sorted(list(sim_run_path.glob("day_*_state.json")), key=extract_day_number_from_file)
                for day_file in day_state_files:
                    with open(day_file, 'r', encoding='utf-8') as f:
                        day_content = json.load(f)
                    # 每日事件列表中的每个事件都是一个字典
                    daily_events_for_this_day = day_content.get("events", []) 
                    all_daily_events_combined.extend(daily_events_for_this_day)
                
                self.patient_data["all_daily_events_combined"] = all_daily_events_combined
                # significant_events 字段现在可以从 all_daily_events_combined 的尾部获取，如果最终报告没有提供的话
                if not self.patient_data.get("significant_events") and all_daily_events_combined:
                     self.patient_data["significant_events"] = all_daily_events_combined[-self.max_events_to_show:]
                console.print(f"[green]已整合来自 {sim_run_path.name} 的 {len(all_daily_events_combined)} 条每日事件。[/green]")
                return True

            elif input_path.is_file(): # 处理单个文件加载
                with open(input_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if load_type == "auto": # 自动判断文件类型
                    if "final_report.json" in input_path.name:
                        self.loaded_data_type = "final_report"
                        self.patient_data = self._format_final_report_data(data, input_path)
                    elif "day_" in input_path.name and "_state.json" in input_path.name:
                        self.loaded_data_type = "day_state"
                        day_number_str = input_path.stem.split('_')[1]
                        if day_number_str.isdigit():
                            self.patient_data = self._format_day_state_data(data, int(day_number_str), input_path)
                        else: raise ValueError("无法从文件名解析日期")
                    else: raise ValueError("未知文件类型")
                elif load_type == "final_report":
                    self.patient_data = self._format_final_report_data(data, input_path)
                elif load_type == "day_state":
                    day_number_str = input_path.stem.split('_')[1]
                    if day_number_str.isdigit():
                        self.patient_data = self._format_day_state_data(data, int(day_number_str), input_path)
                    else: raise ValueError(f"无法从文件名 {input_path.name} 解析日期以加载day_state")
                else:
                    console.print(f"[red]错误: 不支持的 load_type '{load_type}' 用于文件路径。[/red]")
                    return False
                console.print(f"[green]成功从 {input_path.name} (类型: {self.loaded_data_type}) 加载数据。[/green]")
                # 确保simulation_id被正确设置
                if not self.patient_data.get("simulation_id") and self.current_simulation_id:
                    self.patient_data["simulation_id"] = self.current_simulation_id
                return True
            else:
                console.print(f"[red]错误: 路径 {input_path} 不是一个文件，且 load_type 不是目录加载类型。[/red]")
                return False

        except json.JSONDecodeError:
            console.print(f"[red]错误: JSON文件格式错误 {input_path}[/red]")
        except ValueError as ve:
            console.print(f"[red]错误: {ve}[/red]")
        except Exception as e:
            console.print(f"[red]加载患者数据时发生未知错误 {input_path}: {e}[/red]")
        
        # 如果任何步骤失败，重置状态
        self.reset_session() #确保清理不完整状态
        return False

    def get_patient_summary(self) -> str:
        """获取当前加载的患者数据的简要总结"""
        if not self.patient_data:
            return "没有加载患者数据。"
        
        summary = (
            f"数据来源: {self.patient_data.get('data_source', 'N/A')}\n"
            f"姓名: {self.patient_data.get('name', 'N/A')}, 年龄: {self.patient_data.get('age', 'N/A')}\n"
            f"抑郁程度: {self.patient_data.get('depression_level', 'N/A')}\n"
            f"当前状态: {self.patient_data.get('final_state_description', 'N/A')}"
        )
        return summary

    def display_patient_status_panel(self):
        """以Rich Panel形式显示患者状态（包含恢复进展）"""
        if not self.patient_data:
            console.print("[yellow]没有患者数据可显示。[/yellow]")
            return

        has_full_history = 'all_daily_events_combined' in self.patient_data

        # 添加恢复进展信息
        recovery_info = ""
        if self.current_depression_level and self.initial_depression_level:
            initial_value = DEPRESSION_LEVELS.get(self.initial_depression_level, 2)
            current_value = DEPRESSION_LEVELS.get(self.current_depression_level, 2)
            if current_value < initial_value:
                recovery_info = f"  [green]恢复进展：从 {self.initial_depression_level} → {self.current_depression_level}[/green]\n"
            elif current_value > initial_value:
                recovery_info = f"  [red]状态变化：从 {self.initial_depression_level} → {self.current_depression_level}[/red]\n"

        panel_content = (
            f"[bold]数据来源：[/bold]{self.patient_data.get('data_source', '未知')}\n\n"
            f"[bold]患者信息：[/bold]\n"
            f"  姓名：{self.patient_data.get('name', '李明')}\n"
            f"  年龄：{self.patient_data.get('age', 17)}岁\n"
            f"  抑郁程度：{self.current_depression_level or self.patient_data.get('depression_level', 'N/A')}\n"
            f"{recovery_info}"
            f"  治疗联盟：{self.therapeutic_alliance_score:.1f}/10\n\n"
            f"[bold]当前状态描述：[/bold]\n{self.patient_data.get('final_state_description', '状态未知')}\n\n"
        )

        # 如果有完整历史数据，显示统计信息
        if has_full_history:
            all_events = self.patient_data.get('all_daily_events_combined', [])
            total_events = len(all_events)
            negative_events = len([e for e in all_events if e.get('impact_score', 0) < 0])
            positive_events = len([e for e in all_events if e.get('impact_score', 0) > 0])
            
            panel_content += f"[bold cyan]完整历史数据统计：[/bold cyan]\n"
            panel_content += f"  总事件数：{total_events}个\n"
            panel_content += f"  负面事件：{negative_events}个 ({negative_events/total_events*100:.1f}%)\n" if total_events > 0 else ""
            panel_content += f"  正面事件：{positive_events}个 ({positive_events/total_events*100:.1f}%)\n" if total_events > 0 else ""
            panel_content += f"  中性事件：{total_events - negative_events - positive_events}个\n\n"

        symptoms = self.patient_data.get('symptoms', [])
        if symptoms:
            panel_content += "[bold red]主要症状：[/bold red]\n" + "\n".join(f"• {symptom}" for symptom in symptoms[:6]) + "\n\n"
        
        risk_factors = self.patient_data.get('risk_factors', [])
        if risk_factors:
            panel_content += "[bold yellow]风险因素：[/bold yellow]\n" + "\n".join(f"• {factor}" for factor in risk_factors[:4]) + "\n\n"

        if has_full_history:
            # 显示发展阶段的关键事件
            all_events = self.patient_data.get('all_daily_events_combined', [])
            if all_events:
                total_events = len(all_events)
                early_critical = [e for e in all_events[:total_events//3] if e.get('impact_score', 0) < -3][:2]
                recent_critical = [e for e in all_events[-10:] if e.get('impact_score', 0) < -2][:3]
                
                panel_content += "[bold magenta]关键发展节点：[/bold magenta]\n"
                if early_critical:
                    panel_content += "[dim]早期创伤：[/dim]\n"
                    for event in early_critical:
                        panel_content += f"• {event.get('description', '未知事件')[:50]}... (影响: {event.get('impact_score', 'N/A')})\n"
                
                if recent_critical:
                    panel_content += "[dim]近期恶化：[/dim]\n"
                    for event in recent_critical:
                        panel_content += f"• {event.get('description', '未知事件')[:50]}... (影响: {event.get('impact_score', 'N/A')})\n"
        else:
            # 原有逻辑：显示significant_events
            significant_events = self.patient_data.get('significant_events', [])
            if significant_events:
                panel_content += "[bold magenta]最近重要事件：[/bold magenta]\n"
                for event in significant_events:
                     panel_content += f"• {event.get('description', '未知事件')} (影响: {event.get('impact_score', 'N/A')})\n"
        
        console.print(Panel(
            panel_content.strip(),
            title="🩺 患者状态" + (" (完整历史)" if has_full_history else ""),
            border_style="red",
            expand=False
        ))
        
        # 如果是final_report，显示AI分析摘要
        if "final_report.json" in self.patient_data.get('data_source', '') and self.patient_data.get('ai_analysis'):
            ai_analysis_summary = self.patient_data['ai_analysis'][:500] + "..." # 显示部分摘要
            console.print(Panel(
                ai_analysis_summary,
                title="🤖 AI专业分析 (摘要)",
                border_style="blue",
                expand=False
            ))

        # 如果有完整历史，显示发展趋势
        if has_full_history:
            all_events = self.patient_data.get('all_daily_events_combined', [])
            if len(all_events) >= 10:
                # 简单的趋势分析
                early_avg = sum([e.get('impact_score', 0) for e in all_events[:len(all_events)//3]]) / (len(all_events)//3) if len(all_events) >= 3 else 0
                recent_avg = sum([e.get('impact_score', 0) for e in all_events[-len(all_events)//3:]]) / (len(all_events)//3) if len(all_events) >= 3 else 0
                
                trend_text = ""
                if recent_avg < early_avg - 1:
                    trend_text = f"📉 心理状态呈明显恶化趋势 (早期平均: {early_avg:.1f} → 近期平均: {recent_avg:.1f})"
                elif recent_avg > early_avg + 1:
                    trend_text = f"📈 心理状态有所改善 (早期平均: {early_avg:.1f} → 近期平均: {recent_avg:.1f})"
                else:
                    trend_text = f"📊 心理状态相对稳定 (早期平均: {early_avg:.1f} → 近期平均: {recent_avg:.1f})"
                
                console.print(Panel(
                    trend_text,
                    title="📊 发展趋势分析",
                    border_style="yellow",
                    expand=False
                ))

    def reset_session(self):
        """重置会话状态，清空患者数据、对话历史和文件路径信息。"""
        self.patient_data = None
        self.conversation_history = []
        self.current_patient_file_path = None
        self.current_simulation_id = None
        self.loaded_data_type = None
        # console.print("[yellow]会话已重置。[/yellow]") # 可以在调用处打印，或保留

    def show_settings_menu(self):
        """显示并处理设置菜单"""
        while True:
            settings_content = f"""
[bold cyan]当前设置：[/bold cyan]

[bold]咨询设置：[/bold]
  1️⃣  对话历史长度: {self.conversation_history_length} 轮
  2️⃣  事件显示数量: {self.max_events_to_show} 个

[bold]督导设置：[/bold]
  3️⃣  启用督导: {'✅ 是' if self.enable_supervision else '❌ 否'}
  4️⃣  督导间隔: {self.supervision_interval} 轮对话
  5️⃣  分析深度: {self.supervision_analysis_depth}

[bold]操作：[/bold]
  [cyan]输入数字选择要修改的设置[/cyan]
  [cyan]输入 'q' 或 'quit' 返回咨询界面[/cyan]
            """
            
            console.print(Panel(
                settings_content.strip(),
                title="⚙️  设置菜单",
                border_style="cyan",
                expand=False
            ))
            
            choice = console.input("\n[bold cyan]请选择 (1-5, q退出)：[/bold cyan] ").strip().lower()
            
            if choice in ['q', 'quit', '退出']:
                console.print("[green]设置已保存，返回咨询界面。[/green]\n")
                break
            elif choice == '1':
                self._modify_conversation_history_length()
            elif choice == '2':
                self._modify_max_events_to_show()
            elif choice == '3':
                self._toggle_supervision()
            elif choice == '4':
                self._modify_supervision_interval()
            elif choice == '5':
                self._modify_supervision_depth()
            else:
                console.print("[red]无效选择，请输入 1-5 或 q。[/red]\n")
    
    def _modify_conversation_history_length(self):
        """修改对话历史长度"""
        try:
            new_length = console.input(f"[cyan]当前对话历史长度: {self.conversation_history_length} 轮，请输入新值 (5-50): [/cyan]")
            new_length = int(new_length)
            if 5 <= new_length <= 50:
                self.conversation_history_length = new_length
                console.print(f"[green]✅ 对话历史长度已设置为 {new_length} 轮[/green]\n")
            else:
                console.print("[red]❌ 值必须在 5-50 之间[/red]\n")
        except ValueError:
            console.print("[red]❌ 请输入有效数字[/red]\n")
    
    def _modify_max_events_to_show(self):
        """修改事件显示数量"""
        try:
            new_count = console.input(f"[cyan]当前事件显示数量: {self.max_events_to_show} 个，请输入新值 (3-30): [/cyan]")
            new_count = int(new_count)
            if 3 <= new_count <= 30:
                self.max_events_to_show = new_count
                console.print(f"[green]✅ 事件显示数量已设置为 {new_count} 个[/green]\n")
            else:
                console.print("[red]❌ 值必须在 3-30 之间[/red]\n")
        except ValueError:
            console.print("[red]❌ 请输入有效数字[/red]\n")
    
    def _toggle_supervision(self):
        """切换督导开关"""
        self.enable_supervision = not self.enable_supervision
        status = "启用" if self.enable_supervision else "禁用"
        console.print(f"[green]✅ 督导功能已{status}[/green]\n")
    
    def _modify_supervision_interval(self):
        """修改督导间隔"""
        try:
            new_interval = console.input(f"[cyan]当前督导间隔: {self.supervision_interval} 轮，请输入新值 (1-10): [/cyan]")
            new_interval = int(new_interval)
            if 1 <= new_interval <= 10:
                self.supervision_interval = new_interval
                console.print(f"[green]✅ 督导间隔已设置为 {new_interval} 轮[/green]\n")
            else:
                console.print("[red]❌ 值必须在 1-10 之间[/red]\n")
        except ValueError:
            console.print("[red]❌ 请输入有效数字[/red]\n")
    
    def _modify_supervision_depth(self):
        """修改督导分析深度"""
        depths = ["BASIC", "STANDARD", "COMPREHENSIVE"]
        console.print("[cyan]分析深度选项：[/cyan]")
        console.print("  1. BASIC - 基础分析")
        console.print("  2. STANDARD - 标准分析")
        console.print("  3. COMPREHENSIVE - 全面分析")
        
        try:
            choice = console.input(f"[cyan]当前: {self.supervision_analysis_depth}，请选择 (1-3): [/cyan]")
            choice_num = int(choice)
            if 1 <= choice_num <= 3:
                self.supervision_analysis_depth = depths[choice_num - 1]
                console.print(f"[green]✅ 督导分析深度已设置为 {self.supervision_analysis_depth}[/green]\n")
            else:
                console.print("[red]❌ 请选择 1-3[/red]\n")
        except ValueError:
            console.print("[red]❌ 请输入有效数字[/red]\n")

    async def _generate_prompt_for_patient(self, therapist_input: str) -> str:
        """为患者回应构建详细的prompt。"""
        if not self.patient_data:
            return "错误：患者数据未加载。"

        # 构建最近对话历史
        recent_conversation = ""
        if self.conversation_history:
            history_to_use = self.conversation_history[-self.conversation_history_length:]
            patient_name = self.patient_data.get('name', '李明')
            recent_conversation = "\n".join([
                f"咨询师: {conv.get('therapist', '')}\n{patient_name}: {conv.get('patient', '')}"
                for conv in history_to_use
            ])
            if len(self.conversation_history) > self.conversation_history_length:
                omitted_count = len(self.conversation_history) - self.conversation_history_length
                recent_conversation = f"[之前省略了{omitted_count}轮对话...]\n\n" + recent_conversation

        symptoms_text = ', '.join(self.patient_data.get('symptoms', [])[:6])
        risk_factors_text = ', '.join(self.patient_data.get('risk_factors', [])[:4])
        
        # 检查是否有完整历史数据
        has_full_history = 'all_daily_events_combined' in self.patient_data
        events_text = ""
        psychological_development_text = ""
        
        if has_full_history:
            # 利用完整历史数据构建更丰富的背景
            all_events = self.patient_data.get('all_daily_events_combined', [])
            total_events = len(all_events)
            
            # 初始化变量，确保在所有情况下都有定义
            recent_events = []
            
            # 构建心理发展轨迹
            if total_events > 0:
                # 分阶段展示发展过程
                early_events = all_events[:total_events//3] if total_events >= 9 else all_events[:3]
                middle_events = all_events[total_events//3:2*total_events//3] if total_events >= 9 else all_events[3:6] if total_events > 6 else []
                recent_events = all_events[-self.max_events_to_show:] if total_events > self.max_events_to_show else all_events
                
                psychological_development_text = f"""
        
        你的心理发展历程（基于{total_events}个完整历史事件）：
        
        早期阶段：
        {chr(10).join([f"- {event.get('description', '')} (影响: {event.get('impact_score', 'N/A')})" for event in early_events[:3]])}
        
        中期发展：
        {chr(10).join([f"- {event.get('description', '')} (影响: {event.get('impact_score', 'N/A')})" for event in middle_events[:3]]) if middle_events else "（中期数据较少）"}
        
        最近重要事件：
        {chr(10).join([f"- {event.get('description', '')} (影响: {event.get('impact_score', 'N/A')})" for event in recent_events])}
        
        累积心理影响分析：
        - 你经历了从相对正常到逐渐恶化的心理状态变化
        - 早期的负面事件为后续问题埋下了伏笔
        - 中期压力事件的累积加重了你的心理负担  
        - 最近的事件可能是导致当前严重状态的直接原因
                """
                
                # 简化的最近事件（避免重复）
                events_text = f"（详见上方完整发展历程，这里显示最关键的几个事件）\n" + "\n".join([f"- {event.get('description', '')}" for event in recent_events[-3:]]) if recent_events else ""
            else:
                # 没有事件数据的情况
                psychological_development_text = "\n你目前没有具体的历史事件记录，但你的心理状态说明你经历了一些困难。"
                events_text = "（暂无具体事件记录）"
        
        else:
            # 原有逻辑：使用significant_events
            significant_events = self.patient_data.get('significant_events', [])
            if significant_events:
                events_text = "\n".join([f"- {event.get('description', '')}" for event in significant_events])
            else:
                events_text = "（暂无重要事件记录）"

        conversation_count = len(self.conversation_history)
        context_note = ""
        if conversation_count == 0:
            context_note = "这是第一次见面，你可能会有些紧张和防备。"
        elif conversation_count < 3:
            context_note = "你们刚开始对话不久，你还在观察和适应这个咨询师。"
        elif conversation_count < 10:
            context_note = "你们已经对话一段时间了，你可能开始有些信任但仍保持谨慎。"
        else:
            context_note = "你们已经进行了较长时间的对话，治疗关系正在建立中。"

        # 构建基础背景信息
        data_richness_note = ""
        if has_full_history:
            data_richness_note = f"注意：你拥有完整的30天发展历程记忆，包括{len(self.patient_data.get('all_daily_events_combined', []))}个具体事件的详细记忆。这些经历深深影响了你的当前状态和对世界的看法。"
        else:
            data_richness_note = f"注意：你只记得一些重要的经历片段，但这些已经深深影响了你的心理状态。"

        # 使用当前的抑郁程度（如果有恢复追踪）
        current_depression = self.current_depression_level or self.patient_data.get('depression_level', 'MODERATE')
        
        # 如果抑郁程度有改善，添加相关背景
        recovery_context = ""
        if self.current_depression_level and self.initial_depression_level:
            initial_value = DEPRESSION_LEVELS.get(self.initial_depression_level, 2)
            current_value = DEPRESSION_LEVELS.get(self.current_depression_level, 2)
            if current_value < initial_value:
                recovery_context = f"\n        - 治疗进展：你的状态从 {self.initial_depression_level} 改善到了 {self.current_depression_level}，你能感受到一些积极的变化"
                recovery_context += f"\n        - 治疗联盟：你与咨询师的关系评分为 {self.therapeutic_alliance_score:.1f}/10"
            elif current_value > initial_value:
                recovery_context = f"\n        - 治疗挑战：你的状态从 {self.initial_depression_level} 变为 {self.current_depression_level}，你可能感到更加困难"

        prompt = f"""
        你是{self.patient_data.get('name', '李明')}，一个{self.patient_data.get('age', 17)}岁的高中生，正在接受心理咨询。

        你的完整背景：
        - 数据来源：{self.patient_data.get('data_source', '模拟记录')}
        - 当前状态描述：{self.patient_data.get('final_state_description', '心理健康状况不佳')}
        - 抑郁程度：{current_depression}
        - 主要症状：{symptoms_text}
        - 风险因素：{risk_factors_text}{recovery_context}
        
        {data_richness_note}
        {psychological_development_text if has_full_history else ""}
        
        你最近经历的事件{f"（最多显示{self.max_events_to_show}条）" if not has_full_history else ""}：
        {events_text}

        你的性格特点：
        {chr(10).join([f"- {trait}" for trait in self._get_personality_traits_description()])}

        对话背景：
        {context_note} (对话历史长度配置为 {self.conversation_history_length} 轮)

        最近的咨询对话：
        {recent_conversation}

        现在你的心理咨询师对你说："{therapist_input}"

        请以{self.patient_data.get('name', '李明')}的身份回应，请确保你的回应：
        1. 真实反映基于你独特背景、经历和当前心理状态的情绪和想法。
        2. 符合你当前被评估的抑郁程度（{current_depression}）。
        3. 使用符合你年龄和性格的语言风格。
        4. 体现出对咨询师可能的防备心理，但也可能流露出求助的渴望或对被理解的期待。
        5. 自然地展现情绪波动，这可能包括沉默、犹豫、悲伤、愤怒、麻木或困惑等。
        6. 考虑到当前对话所处的阶段和与咨询师之间正在建立的关系。
        {"7. 在合适的时候，可以引用你发展历程中的具体事件或感受，展现出深层的心理创伤和复杂情感。" if has_full_history else ""}
        {"8. 如果状态有所改善，可以适当表现出一些积极的变化，但要符合青少年的表达方式。" if recovery_context and "改善" in recovery_context else ""}

        你的回应应当自然且符合情境，避免过于冗长或戏剧化，一般不超过100字。
        """
        return prompt

    async def get_patient_response(self, therapist_input: str) -> str:
        """获取AI生成的患者对治疗师输入的回应。"""
        if not self.patient_data:
            return "（系统提示：无法生成回应，患者数据未加载。）"
        
        prompt = await self._generate_prompt_for_patient(therapist_input)
        if "错误：" in prompt:
            return f"（系统提示：{prompt}）"
            
        try:
            response = await self.ai_client.generate_response(prompt)
            return response.strip()
        except Exception as e:
            console.print(f"[red]生成患者回应时出错: {e}[/red]")
            return "（患者沉默不语，看起来很难受...也许是网络或API出错了。）"

    async def get_therapist_supervision(self, therapist_input: str, patient_response: str, supervision_interval: int = 3) -> str:
        """获取对当前对话交互的专业督导建议。"""
        try:
            # 构建最近的对话历史给督导参考，使用督导间隔作为分析轮数
            conversation_context = ""
            if self.conversation_history:
                # 获取最近n轮对话作为上下文，n等于督导间隔
                recent_conversations = self.conversation_history[-min(supervision_interval, len(self.conversation_history)):]
                patient_name = self.patient_data.get('name', '李明') if self.patient_data else '患者'
                conversation_context = "\n".join([
                    f"咨询师: {conv.get('therapist', '')}\n{patient_name}: {conv.get('patient', '')}"
                    for conv in recent_conversations
                ])
                if len(self.conversation_history) > supervision_interval:
                    omitted_count = len(self.conversation_history) - supervision_interval
                    conversation_context = f"[之前省略了{omitted_count}轮对话...]\n\n" + conversation_context
            
            # 传递完整上下文给督导，包含分析轮数信息
            suggestion = await self.therapist_agent.provide_supervision_with_context(
                therapist_input, 
                patient_response, 
                conversation_context,
                self.patient_data,  # 也传递患者背景信息
                supervision_interval  # 传递督导间隔，让督导知道分析了多少轮
            )
            return suggestion
        except Exception as e:
            console.print(f"[red]获取督导建议时出错: {e}[/red]")
            return "（督导建议获取失败。）"

    async def save_session_log(self, session_id_prefix: str = "session") -> Optional[Path]:
        """保存当前咨询对话记录到JSON文件。"""
        if not self.conversation_history: 
            console.print("[yellow]没有对话记录可保存。[/yellow]")
            return None

        # 决定保存路径
        if self.current_simulation_id and self.current_patient_file_path:
            # 保存到原始报告所在的模拟子目录中
            target_dir = self.current_patient_file_path.parent 
        else:
            # 回退到主 logs 目录
            target_dir = Path("logs")
        
        target_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # 为避免与TherapySessionManager自己的日志和从start_therapy_from_logs.py启动的日志混淆，可以加个前缀
        patient_name_for_file = self.patient_data.get('name', 'patient').replace(" ", "_").replace("(", "").replace(")","")
        session_file_name = f"{session_id_prefix}_{patient_name_for_file}_{timestamp}.json"
        session_file_path = target_dir / session_file_name
        
        session_data = {
            "session_info": {
                "session_id": f"{session_id_prefix}_{patient_name_for_file}_{timestamp}",
                "data_source_file": str(self.current_patient_file_path) if self.current_patient_file_path else '未知',
                "simulation_id": self.current_simulation_id if self.current_simulation_id else self.patient_data.get('simulation_id', '未知'),
                "patient_name": self.patient_data.get('name', '李明') if self.patient_data else '李明',
                "start_time": self.conversation_history[0]["timestamp"] if self.conversation_history else None,
                "end_time": self.conversation_history[-1]["timestamp"] if self.conversation_history else None,
                "total_exchanges": len(self.conversation_history),
                "session_saved_to": str(session_file_path), # 记录保存路径本身
                # 恢复进展信息
                "initial_depression_level": self.initial_depression_level,
                "final_depression_level": self.current_depression_level,
                "therapeutic_alliance_score": self.therapeutic_alliance_score,
                "avg_effectiveness_score": sum(self.session_effectiveness_scores) / len(self.session_effectiveness_scores) if self.session_effectiveness_scores else 0
            },
            "patient_background_at_start": self.patient_data,
            "conversation": self.conversation_history,
            "recovery_progress": self.recovery_progress,
            "session_effectiveness_scores": self.session_effectiveness_scores
        }
        
        try:
            with open(session_file_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            console.print(f"[green]咨询记录已保存到: {session_file_path}[/green]")
            return session_file_path
        except Exception as e:
            console.print(f"[red]保存咨询记录失败到 {session_file_path}: {e}[/red]")
            return None

    async def start_interactive_session(self, provide_supervision: bool = None, supervision_interval: int = None):
        """开始一个交互式的心理咨询会话。"""
        if not self.patient_data:
            console.print("[red]错误: 患者数据未加载。请先调用 load_patient_data_from_file() 方法。[/red]")
            return

        # 使用传入的参数或实例的设置
        provide_supervision  = provide_supervision if provide_supervision is not None else self.enable_supervision
        supervision_interval = supervision_interval if supervision_interval is not None else self.supervision_interval

        self.conversation_history = [] # 开始新会话前清空历史
        
        # 初始化恢复追踪
        self._initialize_recovery_tracking()
        
        console.print(Panel(
            f"[bold blue]与 {self.patient_data.get('name', '李明')} 的心理咨询已开始[/bold blue]\n\n"
            f"患者数据来源: {self.patient_data.get('data_source', '未知')}\n"
            f"督导设置: {'✅启用' if provide_supervision else '❌禁用'} (间隔: {supervision_interval}轮)\n"
            f"恢复机制: ✅已启用\n\n"
            "💬 开始对话\n"
            "⚙️  输入 's' 或 'settings' 进入设置菜单\n"
            "📊 输入 'progress' 或 'p' 查看恢复进展\n"
            "🚪 输入 'quit', 'exit', '退出', 或 'q' 来结束对话",
            title="💬 咨询会话进行中",
            border_style="blue"
        ))
        
        self.display_patient_status_panel()
        
        console.print(f"\n[green]{self.patient_data.get('name', '李明')}正在等待您的问候...[/green]\n")
        
        try:
            while True:
                therapist_input = console.input("[bold cyan]咨询师：[/bold cyan] ").strip()
                
                if therapist_input.lower() in ['quit', 'exit', '退出', 'q']:
                    console.print("[yellow]咨询对话已结束。[/yellow]")
                    break
                
                if therapist_input.lower() in ['s', 'settings', '设置']:
                    self.show_settings_menu()
                    # 更新会话中的督导设置
                    provide_supervision = self.enable_supervision
                    supervision_interval = self.supervision_interval
                    console.print(f"[cyan]当前督导设置: {'✅启用' if provide_supervision else '❌禁用'} (间隔: {supervision_interval}轮)[/cyan]\n")
                    continue
                
                if therapist_input.lower() in ['progress', 'p', '进展']:
                    self._display_recovery_progress()
                    continue
                
                if not therapist_input:
                    continue
                
                # 生成患者回应
                console.print(f"[grey50]{self.patient_data.get('name', '李明')}正在思考...[/grey50]")
                patient_response = await self.get_patient_response(therapist_input)
                
                console.print(f"[bold yellow]{self.patient_data.get('name', '李明')}：[/bold yellow] {patient_response}\n")
                
                self.conversation_history.append({
                    "therapist": therapist_input,
                    "patient": patient_response,
                    "timestamp": datetime.now().isoformat()
                })
                
                # 每supervision_interval轮对话进行一次评估和督导
                if len(self.conversation_history) % supervision_interval == 0:
                    # 评估对话效果
                    console.print("[grey50]评估治疗效果...[/grey50]")
                    
                    # 获取最近supervision_interval轮的对话进行整体评估
                    recent_conversations = self.conversation_history[-supervision_interval:]
                    effectiveness = await self._evaluate_conversation_effectiveness_batch(recent_conversations, supervision_interval)
                    
                    # 更新治疗联盟分数
                    self.therapeutic_alliance_score = max(0, min(10, 
                        self.therapeutic_alliance_score + effectiveness.get('therapeutic_alliance_change', 0)))
                    
                    # 记录效果分数
                    self.session_effectiveness_scores.append(effectiveness.get('effectiveness_score', 5))
                    
                    # 显示简短的效果反馈
                    if effectiveness.get('breakthrough_moment', False):
                        console.print("[bold green]💫 突破性时刻！患者有重要的情感表达或认知转变。[/bold green]")
                    
                    if effectiveness.get('risk_indicators', []):
                        console.print(f"[bold red]⚠️ 风险提示: {', '.join(effectiveness['risk_indicators'])}[/bold red]")
                    
                    # 提供督导建议
                    if provide_supervision:
                        console.print("[grey50]督导正在分析...[/grey50]")
                        supervision_suggestion = await self.get_therapist_supervision(therapist_input, patient_response, supervision_interval)
                        console.print(Panel(
                            supervision_suggestion,
                            title=f"💡 专业督导建议 (基于最近{supervision_interval}轮对话)",
                            border_style="green",
                            expand=False
                        ))
                        console.print()
                
                # 每5轮对话检查是否可以更新抑郁程度
                if len(self.conversation_history) % 5 == 0:
                    self._update_depression_level()

        except KeyboardInterrupt:
            console.print("\n[yellow]咨询被用户中断。[/yellow]")
        except Exception as e:
            console.print(f"[red]咨询过程中发生意外错误: {e}[/red]")
        finally:
            if self.conversation_history:
                await self.save_session_log(session_id_prefix=f"therapy_session_{self.patient_data.get('name', 'patient')}")
            console.print("感谢使用本咨询模块。")

    def _initialize_recovery_tracking(self):
        """初始化恢复追踪机制"""
        if self.patient_data:
            self.initial_depression_level = self.patient_data.get('depression_level', 'MODERATE')
            self.current_depression_level = self.initial_depression_level
            self.recovery_progress = [{
                "timestamp": datetime.now().isoformat(),
                "depression_level": self.initial_depression_level,
                "event": "开始咨询",
                "therapeutic_alliance_score": 0.0
            }]
            self.therapeutic_alliance_score = 0.0
            self.session_effectiveness_scores = []
            console.print(f"[cyan]恢复追踪已初始化。初始抑郁程度: {self.initial_depression_level}[/cyan]")

    async def _evaluate_conversation_effectiveness(self, therapist_input: str, patient_response: str) -> Dict[str, any]:
        """评估单轮对话的治疗效果"""
        prompt = f"""
        请评估这轮心理咨询对话的治疗效果。
        
        咨询师说: "{therapist_input}"
        患者回应: "{patient_response}"
        
        患者背景:
        - 当前抑郁程度: {self.current_depression_level}
        - 治疗联盟分数: {self.therapeutic_alliance_score:.1f}/10
        - 已进行对话轮数: {len(self.conversation_history)}
        
        请返回JSON格式的评估结果:
        {{
            "effectiveness_score": 0-10的分数（10表示非常有效）,
            "therapeutic_alliance_change": -2到2的变化值,
            "key_therapeutic_factors": ["识别的治疗因素列表"],
            "patient_engagement": "高/中/低",
            "emotional_expression": "开放/谨慎/封闭",
            "resistance_level": "无/轻微/中等/严重",
            "breakthrough_moment": true/false,
            "risk_indicators": ["风险指标列表，如有"],
            "recommendation": "简短的建议"
        }}
        
        只返回JSON，不要其他内容。
        """
        
        try:
            response = await self.ai_client.generate_response(prompt)
            # 解析JSON
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].strip()
            else:
                json_str = response.strip()
            
            return json.loads(json_str)
        except Exception as e:
            console.print(f"[yellow]评估对话效果时出错: {e}[/yellow]")
            # 返回默认评估
            return {
                "effectiveness_score": 5,
                "therapeutic_alliance_change": 0,
                "key_therapeutic_factors": [],
                "patient_engagement": "中",
                "emotional_expression": "谨慎",
                "resistance_level": "轻微",
                "breakthrough_moment": False,
                "risk_indicators": [],
                "recommendation": "继续当前方法"
            }

    async def _evaluate_conversation_effectiveness_batch(self, recent_conversations: List[Dict], interval: int) -> Dict[str, any]:
        """批量评估最近几轮对话的整体治疗效果"""
        # 构建对话历史文本
        conversation_text = ""
        for i, conv in enumerate(recent_conversations, 1):
            conversation_text += f"第{i}轮:\n"
            conversation_text += f"咨询师: {conv.get('therapist', '')}\n"
            conversation_text += f"患者: {conv.get('patient', '')}\n\n"
        
        prompt = f"""
        请评估最近{interval}轮心理咨询对话的整体治疗效果。
        
        对话记录:
        {conversation_text}
        
        患者背景:
        - 当前抑郁程度: {self.current_depression_level}
        - 治疗联盟分数: {self.therapeutic_alliance_score:.1f}/10
        - 总对话轮数: {len(self.conversation_history)}
        
        请返回JSON格式的整体评估结果:
        {{
            "effectiveness_score": 0-10的平均分数（10表示非常有效）,
            "therapeutic_alliance_change": -2到2的总变化值,
            "key_therapeutic_factors": ["这{interval}轮中识别的主要治疗因素"],
            "patient_engagement": "高/中/低（整体评估）",
            "emotional_expression": "开放/谨慎/封闭（整体趋势）",
            "resistance_level": "无/轻微/中等/严重（整体水平）",
            "breakthrough_moment": true/false（是否有突破性进展）,
            "risk_indicators": ["这{interval}轮中发现的风险指标"],
            "recommendation": "基于这{interval}轮对话的建议",
            "progress_summary": "简要总结这{interval}轮的治疗进展"
        }}
        
        只返回JSON，不要其他内容。
        """
        
        try:
            response = await self.ai_client.generate_response(prompt)
            # 解析JSON
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].strip()
            else:
                json_str = response.strip()
            
            result = json.loads(json_str)
            
            # 显示进展总结
            if result.get('progress_summary'):
                console.print(f"[cyan]📝 {interval}轮对话总结: {result['progress_summary']}[/cyan]")
            
            return result
        except Exception as e:
            console.print(f"[yellow]批量评估对话效果时出错: {e}[/yellow]")
            # 返回默认评估
            return {
                "effectiveness_score": 5,
                "therapeutic_alliance_change": 0,
                "key_therapeutic_factors": [],
                "patient_engagement": "中",
                "emotional_expression": "谨慎",
                "resistance_level": "轻微",
                "breakthrough_moment": False,
                "risk_indicators": [],
                "recommendation": "继续当前方法",
                "progress_summary": f"最近{interval}轮对话的评估出现错误，使用默认值"
            }

    def _update_depression_level(self):
        """根据治疗进展更新抑郁程度"""
        if not self.session_effectiveness_scores:
            return
        
        # 计算最近几轮的平均效果
        recent_scores = self.session_effectiveness_scores[-5:]  # 最近5轮
        avg_effectiveness = sum(recent_scores) / len(recent_scores)
        
        # 获取当前抑郁程度的数值
        current_level_value = DEPRESSION_LEVELS.get(self.current_depression_level, 2)
        
        # 根据效果和治疗联盟决定是否改善
        improvement_threshold = 7.0  # 效果分数阈值
        alliance_threshold = 6.0     # 治疗联盟阈值
        
        new_level_value = current_level_value
        
        # 判断是否可以改善
        if avg_effectiveness >= improvement_threshold and self.therapeutic_alliance_score >= alliance_threshold:
            # 检查是否有足够的积极对话
            if len(self.session_effectiveness_scores) >= 5:
                # 可以改善一级
                if current_level_value > 0:
                    new_level_value = current_level_value - 1
                    console.print(f"[green]✨ 治疗取得显著进展！[/green]")
        
        # 判断是否恶化（如果效果很差）
        elif avg_effectiveness < 3.0 and self.therapeutic_alliance_score < 3.0:
            if current_level_value < 4:
                new_level_value = current_level_value + 1
                console.print(f"[red]⚠️ 治疗效果不佳，需要调整方法。[/red]")
        
        # 更新抑郁程度
        if new_level_value != current_level_value:
            old_level = self.current_depression_level
            self.current_depression_level = DEPRESSION_LEVEL_NAMES.get(new_level_value, "MODERATE")
            
            # 记录变化
            self.recovery_progress.append({
                "timestamp": datetime.now().isoformat(),
                "depression_level": self.current_depression_level,
                "event": f"抑郁程度从 {old_level} 变为 {self.current_depression_level}",
                "therapeutic_alliance_score": self.therapeutic_alliance_score,
                "avg_effectiveness": avg_effectiveness
            })
            
            # 更新患者数据
            if self.patient_data:
                self.patient_data['depression_level'] = self.current_depression_level
            
            # 显示进展
            self._display_recovery_progress()

    def _display_recovery_progress(self):
        """显示恢复进展"""
        if not self.recovery_progress:
            return
        
        initial_value = DEPRESSION_LEVELS.get(self.initial_depression_level, 2)
        current_value = DEPRESSION_LEVELS.get(self.current_depression_level, 2)
        
        progress_text = f"""
[bold cyan]📊 治疗进展报告[/bold cyan]

初始状态: {self.initial_depression_level} (级别 {initial_value})
当前状态: {self.current_depression_level} (级别 {current_value})
治疗联盟: {self.therapeutic_alliance_score:.1f}/10
对话轮数: {len(self.conversation_history)}

进展轨迹:
"""
        
        for i, progress in enumerate(self.recovery_progress[-5:]):  # 显示最近5条
            progress_text += f"  {i+1}. {progress['event']} (联盟分数: {progress['therapeutic_alliance_score']:.1f})\n"
        
        # 计算整体改善
        improvement = initial_value - current_value
        if improvement > 0:
            progress_text += f"\n[green]✅ 总体改善: 降低了 {improvement} 个级别[/green]"
        elif improvement < 0:
            progress_text += f"\n[red]⚠️ 状态恶化: 上升了 {-improvement} 个级别[/red]"
        else: 
            progress_text += f"\n[yellow]📍 状态维持在初始水平[/yellow]"
        
        console.print(Panel(
            progress_text.strip(),
            title        = "🌟 恢复进展",
            border_style = "cyan",
            expand       = False
        ))

    def _get_personality_traits_description(self) -> List[str]:
        """从患者数据中获取角色性格特点描述"""
        personality_traits = []
        
        # 先尝试从patient_data中的protagonist_character_profile获取
        character_profile = self.patient_data.get('protagonist_character_profile', {}) if self.patient_data else {}
        
        if character_profile and character_profile.get('personality'):
            personality_config = character_profile['personality']
            name = character_profile.get('name', '主角')
            age = character_profile.get('age', 17)
            
            # 从配置中构建性格描述
            traits = personality_config.get('traits', [])
            if traits:
                traits_text = '、'.join(traits[:4])  # 取前4个特征
                personality_traits.append(f"{age}岁的{name}，性格特点：{traits_text}。")
            
            # 添加五大人格特征描述（如果有的话）
            big_five_traits = []
            if 'openness' in personality_config:
                openness = personality_config['openness']
                if openness >= 7:
                    big_five_traits.append("对新体验较为开放")
                elif openness <= 3:
                    big_five_traits.append("偏好熟悉的环境和经历")
            
            if 'conscientiousness' in personality_config:
                conscientiousness = personality_config['conscientiousness']
                if conscientiousness >= 7:
                    big_five_traits.append("有很强的自制力和责任感")
                elif conscientiousness <= 3:
                    big_five_traits.append("在规划和执行方面较为随意")
            
            if 'extraversion' in personality_config:
                extraversion = personality_config['extraversion']
                if extraversion >= 7:
                    big_five_traits.append("性格外向、善于社交")
                elif extraversion <= 3:
                    big_five_traits.append("性格内向、喜欢独处")
            
            if 'agreeableness' in personality_config:
                agreeableness = personality_config['agreeableness']
                if agreeableness >= 7:
                    big_five_traits.append("待人友善、富有同情心")
                elif agreeableness <= 3:
                    big_five_traits.append("在人际关系中较为直接，不太妥协")
            
            if 'neuroticism' in personality_config:
                neuroticism = personality_config['neuroticism']
                if neuroticism >= 7:
                    big_five_traits.append("情绪敏感、容易焦虑")
                elif neuroticism <= 3:
                    big_five_traits.append("情绪稳定、抗压能力强")
            
            if big_five_traits:
                personality_traits.append("从人格特质来看：" + "，".join(big_five_traits) + "。")
            
            # 添加背景信息
            background = character_profile.get('background', {})
            if 'family_situation' in background:
                personality_traits.append(f"家庭背景：{background['family_situation']}。")
            
            if 'academic_performance' in background:
                personality_traits.append(f"学业表现：{background['academic_performance']}。")
            
            # 根据当前状态添加心理状态相关的描述
            personality_traits.append("因为近期的经历，变得更加消极和自我保护。")
            personality_traits.append("对他人有防备心理，但内心深处渴望被理解和帮助。")
            personality_traits.append("容易自我责备，认为问题都是自己造成的。")
            personality_traits.append("表达方式符合青少年特点，有时可能不直接或带有情绪。")
            
            return personality_traits
        
        # 如果没有配置信息，返回默认性格特点
        age = self.patient_data.get('age', 17) if self.patient_data else 17
        personality_traits = [
            f"{age}岁高中生，通常被描述为内向、敏感。",
            "因为经历的创伤而变得更加消极和自我保护。",
            "对他人有防备心理，但内心深处可能渴望被理解和帮助。",
            "容易自我责备，认为问题都是自己造成的。",
            "表达方式符合青少年特点，有时可能不直接或带有情绪。"
        ]
        return personality_traits

# 示例用法 (后续会移除或放到测试/demo中)
if __name__ == '__main__':
    async def test_interactive_session():
        try:
            import config # 确保 config 在这里能被导入
            if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "your_gemini_api_key_here":
                console.print("[red]错误: 请在config.py中设置有效的Gemini API密钥[/red]")
                return
            
            gemini_client = GeminiClient(api_key=config.GEMINI_API_KEY)
            # therapist_agent = TherapistAgent("专业心理督导", gemini_client) # Manager会自己创建默认的
            
            # 测试时使用的配置值
            test_history_length = 3 
            test_max_events = 4
            
            console.print(f"[cyan]测试 TherapySessionManager (history_length={test_history_length}, max_events={test_max_events})...[/cyan]")
            manager = TherapySessionManager(ai_client=gemini_client, 
                                          # therapist_agent=therapist_agent, # 可选
                                          conversation_history_length=test_history_length,
                                          max_events_to_show=test_max_events)

            logs_dir = Path(__file__).parent.parent / "logs" # 更可靠地定位logs目录
            logs_dir.mkdir(exist_ok=True)
            sample_final_report_path = logs_dir / "final_report.json"
            
            sample_final_report_content = {
                "simulation_summary": {"total_days": 30, "final_stage": "抑郁发展", "final_depression_level": "SEVERE", "total_events": 150},
                "protagonist_character_profile": {
                    "name": "李明", 
                    "age": 17,
                    "personality": {
                        "traits": ["内向", "敏感", "聪明", "善良"],
                        "openness": 6,
                        "conscientiousness": 7,
                        "extraversion": 3,
                        "agreeableness": 8,
                        "neuroticism": 7
                    },
                    "background": {
                        "family_situation": "单亲家庭，与母亲同住",
                        "academic_performance": "成绩优秀但压力较大"
                    }
                },
                "protagonist_journey": {"initial_state": "健康", "final_state": "抑郁, 压力9/10, 自尊0/10", "key_symptoms": ["情绪低落", "失眠", "食欲差"], "risk_factors": ["霸凌", "孤立", "学业压力"]},
                "significant_events": [{"description": f"事件{i}", "impact_score": -i} for i in range(1, test_max_events + 3)], 
                "ai_analysis": "这是一个AI对整个模拟过程的分析总结...非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常长的一段文本，用于测试摘要功能。" * 10
            }
            with open(sample_final_report_path, "w", encoding="utf-8") as f:
                json.dump(sample_final_report_content, f, ensure_ascii=False, indent=2)

            console.rule("[bold green]开始交互式咨询测试 (使用 final_report.json)[/bold green]")
            if manager.load_patient_data_from_file(str(sample_final_report_path)):
                await manager.start_interactive_session(supervision_interval=2) 
            else:
                console.print("[red]无法加载患者数据，交互式会话测试失败。[/red]")

        except ImportError:
            console.print("[red]错误: 请创建config.py并配置GEMINI_API_KEY (或确保其在PYTHONPATH中)[/red]")
        except Exception as e:
            console.print(f"[red]交互式会话测试发生错误: {e}[/red]")
            import traceback
            traceback.print_exc()

    asyncio.run(test_interactive_session()) 