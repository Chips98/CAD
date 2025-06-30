#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
心理状态显示工具模块
提供丰富的彩色心理状态显示功能
"""

from typing import Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.layout import Layout
from rich.box import ROUNDED, SIMPLE, HEAVY
import json
import locale
import sys

# 设置控制台编码，解决中文显示问题
try:
    # 尝试设置UTF-8编码
    if sys.platform.startswith('win'):
        # Windows系统
        console = Console(force_terminal=True, width=120)
    else:
        # macOS/Linux系统  
        console = Console(force_terminal=True, width=120, legacy_windows=False)
        
    # 尝试设置locale为UTF-8
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
        except:
            pass  # 如果设置失败就使用默认
            
except Exception:
    # 如果设置失败，使用默认配置
    console = Console()

def format_psychological_state_for_web(state_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    为Web界面格式化心理状态数据
    
    Args:
        state_data: 心理状态数据
        
    Returns:
        格式化后的Web显示数据
    """
    formatted_data = {
        'basic_info': {},
        'cad_state': {},
        'mood_indicators': {},
        'risk_factors': []
    }
    
    # 基本信息
    formatted_data['basic_info'] = {
        'depression_level': state_data.get('depression_level', '未知'),
        'mood_score': _get_color_indicator(state_data.get('mood_score', 5), 'mood'),
        'stress_level': _get_color_indicator(state_data.get('stress_level', 5), 'stress'),
        'energy_level': _get_color_indicator(state_data.get('energy_level', 5), 'energy')
    }
    
    # CAD状态
    cad_state = state_data.get('cad_state', {})
    if cad_state:
        formatted_data['cad_state'] = {
            'self_belief': _get_cad_indicator(cad_state.get('self_belief', 0)),
            'world_belief': _get_cad_indicator(cad_state.get('world_belief', 0)),
            'future_belief': _get_cad_indicator(cad_state.get('future_belief', 0)),
            'rumination': _get_cad_indicator(cad_state.get('rumination', 0)),
            'distortions': _get_cad_indicator(cad_state.get('distortions', 0)),
            'social_withdrawal': _get_cad_indicator(cad_state.get('social_withdrawal', 0)),
            'avolition': _get_cad_indicator(cad_state.get('avolition', 0)),
            'affective_tone': _get_cad_indicator(cad_state.get('affective_tone', 0))
        }
    
    # 情绪指标
    formatted_data['mood_indicators'] = {
        'anxiety': _get_color_indicator(state_data.get('anxiety_level', 5), 'negative'),
        'happiness': _get_color_indicator(state_data.get('happiness_level', 5), 'positive'),
        'anger': _get_color_indicator(state_data.get('anger_level', 5), 'negative'),
        'sadness': _get_color_indicator(state_data.get('sadness_level', 5), 'negative')
    }
    
    # 风险因素
    if state_data.get('depression_level') in ['SEVERE', 'CRITICAL']:
        formatted_data['risk_factors'].append('重度抑郁风险')
    if cad_state.get('social_withdrawal', 0) > 0.7:
        formatted_data['risk_factors'].append('社交退缩严重')
    if cad_state.get('rumination', 0) > 0.7:
        formatted_data['risk_factors'].append('反刍思维严重')
    
    return formatted_data

def _get_cad_indicator(value: float) -> Dict[str, Any]:
    """获取CAD指标的颜色和描述"""
    if value < 0.3:
        return {'value': value, 'color': 'success', 'level': '正常', 'description': '状态良好'}
    elif value < 0.6:
        return {'value': value, 'color': 'warning', 'level': '轻度', 'description': '需要关注'}
    elif value < 0.8:
        return {'value': value, 'color': 'danger', 'level': '中度', 'description': '需要干预'}
    else:
        return {'value': value, 'color': 'dark', 'level': '重度', 'description': '紧急干预'}

def _get_color_indicator(value: float, indicator_type: str) -> Dict[str, Any]:
    """获取指标的颜色和描述"""
    if indicator_type in ['negative', 'stress']:
        # 负向指标：值越高越糟糕
        if value < 3:
            return {'value': value, 'color': 'success', 'level': '低'}
        elif value < 7:
            return {'value': value, 'color': 'warning', 'level': '中'}
        else:
            return {'value': value, 'color': 'danger', 'level': '高'}
    else:
        # 正向指标：值越高越好
        if value < 3:
            return {'value': value, 'color': 'danger', 'level': '低'}
        elif value < 7:
            return {'value': value, 'color': 'warning', 'level': '中'}
        else:
            return {'value': value, 'color': 'success', 'level': '高'}

# 中文字段映射
FIELD_TRANSLATIONS = {
    "emotion": "情绪状态",
    "depression_level": "抑郁程度", 
    "stress_level": "压力水平",
    "self_esteem": "自尊水平",
    "social_connection": "社交连接",
    "academic_pressure": "学业压力",
    "affective_tone": "情感基调",
    "self_belief": "自我信念",
    "world_belief": "世界信念", 
    "future_belief": "未来信念",
    "rumination": "反刍思维",
    "distortions": "认知扭曲",
    "social_withdrawal": "社交退缩",
    "avolition": "动机缺失"
}

# 抑郁程度映射（完整10级精细分级系统）
DEPRESSION_LEVEL_MAP = {
    # 数字映射
    0: "最佳状态",
    1: "健康正常", 
    2: "最小症状",
    3: "轻度风险",
    4: "轻度抑郁",
    5: "中轻度抑郁",
    6: "中度抑郁",
    7: "中重度抑郁",
    8: "重度抑郁",
    9: "极重度抑郁",
    # 字符串映射
    "OPTIMAL": "最佳状态",
    "HEALTHY": "健康正常",
    "MINIMAL_SYMPTOMS": "最小症状",
    "MILD_RISK": "轻度风险", 
    "MILD": "轻度抑郁",
    "MODERATE_MILD": "中轻度抑郁",
    "MODERATE": "中度抑郁",
    "MODERATE_SEVERE": "中重度抑郁",
    "SEVERE": "重度抑郁",
    "CRITICAL": "极重度抑郁"
}

# 抑郁程度颜色映射
DEPRESSION_LEVEL_COLORS = {
    0: "bright_green",    # 最佳状态
    1: "green",           # 健康正常
    2: "bright_cyan",     # 最小症状
    3: "cyan",            # 轻度风险
    4: "yellow",          # 轻度抑郁
    5: "bright_yellow",   # 中轻度抑郁
    6: "bright_magenta",  # 中度抑郁
    7: "magenta",         # 中重度抑郁
    8: "red",             # 重度抑郁
    9: "bright_red"       # 极重度抑郁
}

def get_depression_level_color(level) -> str:
    """
    根据抑郁级别获取对应颜色
    
    Args:
        level: 抑郁级别（数字或字符串）
        
    Returns:
        颜色名称
    """
    # 如果是字符串，转换为数字
    if isinstance(level, str):
        level_map = {
            "OPTIMAL": 0, "HEALTHY": 1, "MINIMAL_SYMPTOMS": 2,
            "MILD_RISK": 3, "MILD": 4, "MODERATE_MILD": 5,
            "MODERATE": 6, "MODERATE_SEVERE": 7, "SEVERE": 8, "CRITICAL": 9
        }
        level = level_map.get(level, 5)  # 默认中等级别
    
    return DEPRESSION_LEVEL_COLORS.get(level, "yellow")

def get_color_for_value(value: float, is_negative_better: bool = False) -> str:
    """
    根据数值获取颜色
    
    Args:
        value: 数值
        is_negative_better: 是否负值更好（如反刍思维、社交退缩等）
    
    Returns:
        颜色名称
    """
    if is_negative_better:
        # 对于负值更好的指标（如反刍、退缩等）
        if value <= 2:
            return "bright_green"
        elif value <= 5:
            return "yellow"
        else:
            return "bright_red"
    else:
        # 对于正值更好的指标
        if value < 0:
            return "bright_red"
        elif value <= 2:
            return "red"
        elif value <= 5:
            return "yellow"
        elif value <= 7:
            return "green"
        else:
            return "bright_green"

def format_therapy_strategy(strategy_text: str) -> Panel:
    """
    格式化治疗策略分析文本
    
    Args:
        strategy_text: 策略分析文本
        
    Returns:
        格式化的Panel
    """
    # 解析策略文本
    lines = strategy_text.strip().split('\n')
    
    # 创建策略内容
    strategy_content = Text()
    
    for line in lines:
        line = line.strip()
        if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.')):
            # 策略要点 - 使用蓝色
            strategy_content.append(f"  {line}\n", style="bright_blue")
        elif line:
            # 其他文本 - 使用淡蓝色
            strategy_content.append(f"{line}\n", style="blue")
    
    return Panel(
        strategy_content,
        title="🧠 [bold magenta]治疗策略分析[/bold magenta]",
        border_style="magenta",
        box=ROUNDED,
        expand=False
    )

def display_psychological_state(patient_data: Dict[str, Any], 
                              turn_number: Optional[int] = None,
                              show_strategy: bool = True) -> None:
    """
    显示患者的详细心理状态
    
    Args:
        patient_data: 患者数据
        turn_number: 轮次数
        show_strategy: 是否显示策略分析
    """
    
    # 创建主表格
    state_table = Table(
        title=f"📊 [bold cyan]患者心理状态详情[/bold cyan]" + (f" - 第{turn_number}轮" if turn_number else ""),
        box=HEAVY,
        title_style="bold cyan",
        expand=True
    )
    
    state_table.add_column("维度", style="bold white", width=12)
    state_table.add_column("数值", justify="center", width=8)
    state_table.add_column("状态", style="bold", width=15)
    state_table.add_column("描述", width=25)
    
    # 基础心理状态
    basic_state = patient_data.get('current_mental_state', {})
    
    # 情绪状态
    emotion = basic_state.get('emotion', '未知')
    emotion_color = "yellow" if emotion in ['焦虑', '困惑'] else "red" if emotion in ['抑郁', '悲伤'] else "green"
    state_table.add_row(
        FIELD_TRANSLATIONS.get('emotion', '情绪状态'),
        "-",
        f"[{emotion_color}]{emotion}[/{emotion_color}]",
        "当前主导情绪"
    )
    
    # 抑郁程度
    depression_level = basic_state.get('depression_level', 0)
    depression_text = DEPRESSION_LEVEL_MAP.get(depression_level, str(depression_level))
    depression_color = get_depression_level_color(depression_level)
    
    # 添加级别描述
    level_descriptions = {
        0: "心理状态最佳", 1: "心理健康正常", 2: "轻微抑郁倾向",
        3: "需要关注", 4: "需要支持", 5: "需要专业指导",
        6: "需要治疗干预", 7: "需要密切治疗", 8: "需要强化治疗", 9: "需要紧急干预"
    }
    
    level_num = depression_level if isinstance(depression_level, int) else {
        "OPTIMAL": 0, "HEALTHY": 1, "MINIMAL_SYMPTOMS": 2, "MILD_RISK": 3, "MILD": 4,
        "MODERATE_MILD": 5, "MODERATE": 6, "MODERATE_SEVERE": 7, "SEVERE": 8, "CRITICAL": 9
    }.get(depression_level, 5)
    
    state_table.add_row(
        FIELD_TRANSLATIONS.get('depression_level', '抑郁程度'),
        f"级别 {level_num}",
        f"[{depression_color}]{depression_text}[/{depression_color}]",
        level_descriptions.get(level_num, "需要评估")
    )
    
    # 基础指标
    basic_indicators = ['stress_level', 'self_esteem', 'social_connection', 'academic_pressure']
    for indicator in basic_indicators:
        value = basic_state.get(indicator, 0)
        if value is not None:
            color = get_color_for_value(value, indicator in ['stress_level', 'academic_pressure'])
            state_table.add_row(
                FIELD_TRANSLATIONS.get(indicator, indicator),
                f"{value:.1f}" if isinstance(value, float) else str(value),
                f"[{color}]●[/{color}]",
                get_status_description(indicator, value)
            )
    
    # CAD状态部分
    cad_state = basic_state.get('cad_state', {})
    if cad_state:
        # 添加分隔线
        state_table.add_row("", "", "", "", style="dim")
        state_table.add_row(
            "[bold yellow]CAD认知模型[/bold yellow]", 
            "", "", "[dim]认知-情感动力学状态[/dim]", 
            style="bold yellow"
        )
        
        # 情感基调
        affective_tone = cad_state.get('affective_tone', 0)
        tone_color = get_color_for_value(affective_tone, False)
        state_table.add_row(
            FIELD_TRANSLATIONS.get('affective_tone', '情感基调'),
            f"{affective_tone:.2f}",
            f"[{tone_color}]●[/{tone_color}]",
            get_affective_tone_description(affective_tone)
        )
        
        # 核心信念
        core_beliefs = cad_state.get('core_beliefs', {})
        if core_beliefs:
            belief_indicators = ['self_belief', 'world_belief', 'future_belief']
            for belief in belief_indicators:
                value = core_beliefs.get(belief, 0)
                color = get_color_for_value(value, False)
                state_table.add_row(
                    FIELD_TRANSLATIONS.get(belief, belief),
                    f"{value:.2f}",
                    f"[{color}]●[/{color}]",
                    get_belief_description(belief, value)
                )
        
        # 认知加工
        cognitive_processing = cad_state.get('cognitive_processing', {})
        if cognitive_processing:
            processing_indicators = ['rumination', 'distortions']
            for indicator in processing_indicators:
                value = cognitive_processing.get(indicator, 0)
                color = get_color_for_value(value, True)  # 这些指标越低越好
                state_table.add_row(
                    FIELD_TRANSLATIONS.get(indicator, indicator),
                    f"{value:.2f}",
                    f"[{color}]●[/{color}]",
                    get_cognitive_description(indicator, value)
                )
        
        # 行为倾向
        behavioral_inclination = cad_state.get('behavioral_inclination', {})
        if behavioral_inclination:
            behavior_indicators = ['social_withdrawal', 'avolition']
            for indicator in behavior_indicators:
                value = behavioral_inclination.get(indicator, 0)
                color = get_color_for_value(value, True)  # 这些指标越低越好
                state_table.add_row(
                    FIELD_TRANSLATIONS.get(indicator, indicator),
                    f"{value:.2f}",
                    f"[{color}]●[/{color}]",
                    get_behavioral_description(indicator, value)
                )
    
    # 显示表格
    console.print()
    console.print(state_table)
    console.print()

def get_status_description(indicator: str, value: float) -> str:
    """获取状态描述"""
    if indicator == 'stress_level':
        if value >= 8: return "极高压力"
        elif value >= 6: return "高压力"
        elif value >= 4: return "中等压力"
        elif value >= 2: return "轻微压力"
        else: return "无压力"
    elif indicator == 'self_esteem':
        if value >= 8: return "自尊心很强"
        elif value >= 6: return "自尊心较强"
        elif value >= 4: return "自尊心一般"
        elif value >= 2: return "自尊心较低"
        else: return "自尊心很低"
    elif indicator == 'social_connection':
        if value >= 8: return "社交关系很好"
        elif value >= 6: return "社交关系较好"
        elif value >= 4: return "社交关系一般"
        elif value >= 2: return "社交关系较差"
        else: return "社交关系很差"
    elif indicator == 'academic_pressure':
        if value >= 8: return "学业压力极大"
        elif value >= 6: return "学业压力较大"
        elif value >= 4: return "学业压力适中"
        elif value >= 2: return "学业压力较小"
        else: return "无学业压力"
    else:
        return f"数值: {value}"

def get_affective_tone_description(value: float) -> str:
    """获取情感基调描述"""
    if value >= 5: return "非常乐观积极"
    elif value >= 2: return "较为乐观"
    elif value >= -2: return "情感中性"
    elif value >= -5: return "较为悲观"
    else: return "非常悲观消极"

def get_belief_description(belief_type: str, value: float) -> str:
    """获取信念描述"""
    if belief_type == 'self_belief':
        if value >= 5: return "自我价值感很强"
        elif value >= 1: return "对自己较为满意"
        elif value >= -1: return "自我感觉中性"
        elif value >= -5: return "自我价值感较低"
        else: return "严重自我否定"
    elif belief_type == 'world_belief':
        if value >= 5: return "世界观很积极"
        elif value >= 1: return "对世界较为乐观"
        elif value >= -1: return "世界观中性"
        elif value >= -5: return "对世界较为悲观"
        else: return "世界观很消极"
    elif belief_type == 'future_belief':
        if value >= 5: return "对未来很乐观"
        elif value >= 1: return "对未来较有希望"
        elif value >= -1: return "对未来态度中性"
        elif value >= -5: return "对未来较为悲观"
        else: return "对未来很绝望"
    else:
        return f"数值: {value}"

def get_cognitive_description(indicator: str, value: float) -> str:
    """获取认知加工描述"""
    if indicator == 'rumination':
        if value >= 7: return "严重反刍思维"
        elif value >= 5: return "明显反刍思维"
        elif value >= 3: return "轻度反刍思维"
        elif value >= 1: return "偶有反刍思维"
        else: return "无反刍思维"
    elif indicator == 'distortions':
        if value >= 7: return "严重认知扭曲"
        elif value >= 5: return "明显认知扭曲"
        elif value >= 3: return "轻度认知扭曲"
        elif value >= 1: return "偶有认知偏差"
        else: return "认知清晰"
    else:
        return f"数值: {value}"

def get_behavioral_description(indicator: str, value: float) -> str:
    """获取行为倾向描述"""
    if indicator == 'social_withdrawal':
        if value >= 7: return "严重社交退缩"
        elif value >= 5: return "明显社交退缩"
        elif value >= 3: return "轻度社交退缩"
        elif value >= 1: return "偶有社交回避"
        else: return "社交正常"
    elif indicator == 'avolition':
        if value >= 7: return "严重动机缺失"
        elif value >= 5: return "明显动机缺失" 
        elif value >= 3: return "轻度动机缺失"
        elif value >= 1: return "偶有动机不足"
        else: return "动机正常"
    else:
        return f"数值: {value}"

def display_therapist_response_with_strategy(therapist_message: str, 
                                           strategy_analysis: Optional[str] = None,
                                           turn_number: Optional[int] = None) -> None:
    """
    显示治疗师回应和策略分析
    
    Args:
        therapist_message: 治疗师消息
        strategy_analysis: 策略分析文本
        turn_number: 轮次数
    """
    # 显示治疗师消息
    therapist_panel = Panel(
        Text(therapist_message, style="white"),
        title=f"👨‍⚕️ [bold green]AI治疗师[/bold green]" + (f" - 第{turn_number}轮" if turn_number else ""),
        border_style="green",
        box=ROUNDED,
        expand=True
    )
    
    console.print()
    console.print(therapist_panel)
    
    # 显示策略分析
    if strategy_analysis:
        console.print()
        console.print(format_therapy_strategy(strategy_analysis))

def display_patient_response(patient_message: str, 
                           patient_data: Dict[str, Any],
                           turn_number: Optional[int] = None) -> None:
    """
    显示患者回应和心理状态
    
    Args:
        patient_message: 患者消息
        patient_data: 患者数据
        turn_number: 轮次数
    """
    # 显示患者消息
    patient_panel = Panel(
        Text(patient_message, style="white"),
        title=f"💭 [bold yellow]患者 (李明)[/bold yellow]" + (f" - 第{turn_number}轮回应" if turn_number else ""),
        border_style="yellow", 
        box=ROUNDED,
        expand=True
    )
    
    console.print()
    console.print(patient_panel)
    
    # 显示详细心理状态
    display_psychological_state(patient_data, turn_number)

def create_session_header(session_type: str, patient_name: str = "李明") -> None:
    """
    创建会话头部显示
    
    Args:
        session_type: 会话类型
        patient_name: 患者姓名
    """
    header_text = Text()
    header_text.append("🧠 抑郁症模拟系统 - ", style="bold cyan")
    header_text.append(session_type, style="bold yellow")
    header_text.append(f"\n患者: {patient_name}", style="white")
    header_text.append("\n" + "="*60, style="dim")
    
    header_panel = Panel(
        header_text,
        title="心理治疗会话",
        border_style="cyan",
        box=HEAVY
    )
    
    console.print()
    console.print(header_panel)
    console.print()