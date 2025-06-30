#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
抑郁症模拟系统Web界面启动脚本
简化版启动器，确保依赖安装和系统运行
"""

import sys
import subprocess
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()

def check_requirements():
    """检查并安装必要的依赖"""
    requirements = [
        'flask', 'flask-socketio', 'rich'
    ]
    
    missing = []
    for req in requirements:
        try:
            __import__(req.replace('-', '_'))
        except ImportError:
            missing.append(req)
    
    if missing:
        console.print(f"[yellow]缺少依赖: {', '.join(missing)}[/yellow]")
        console.print("[cyan]正在安装依赖...[/cyan]")
        
        for req in missing:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', req])
                console.print(f"[green]✅ {req} 安装成功[/green]")
            except subprocess.CalledProcessError:
                console.print(f"[red]❌ {req} 安装失败[/red]")
                return False
    
    return True

def main():
    """主启动函数"""
    console.print(Panel.fit(
        "[bold cyan]🌐 抑郁症模拟系统 Web界面[/bold cyan]\n"
        "[dim]启动Web服务器...[/dim]",
        border_style="cyan"
    ))
    
    # 检查依赖
    if not check_requirements():
        console.print("[red]依赖安装失败，无法启动Web服务[/red]")
        return
    
    # 确保目录存在
    Path("logs").mkdir(exist_ok=True)
    Path("web/static").mkdir(exist_ok=True)
    Path("web/templates").mkdir(exist_ok=True)
    
    console.print("[green]✅ 依赖检查完成[/green]")
    console.print("[cyan]🚀 启动Web服务器...[/cyan]")
    console.print("[dim]访问地址: http://localhost:5000[/dim]")
    
    try:
        # 导入并运行Flask应用
        from web.app import app, socketio
        socketio.run(app, debug=False, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
    except ImportError as e:
        console.print(f"[red]导入错误: {e}[/red]")
        console.print("[yellow]请确保在正确的目录运行此脚本[/yellow]")
    except Exception as e:
        console.print(f"[red]启动失败: {e}[/red]")

if __name__ == "__main__":
    main() 