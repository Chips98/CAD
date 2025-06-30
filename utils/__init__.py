#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具模块初始化
配置终端编码和显示设置
"""

import os
import sys
import locale

def setup_terminal_encoding():
    """设置终端编码，解决中文显示问题"""
    try:
        # 设置环境变量
        if sys.platform.startswith('darwin'):  # macOS
            os.environ['LC_ALL'] = 'en_US.UTF-8'
            os.environ['LANG'] = 'en_US.UTF-8'
        elif sys.platform.startswith('linux'):  # Linux
            os.environ['LC_ALL'] = 'C.UTF-8'
            os.environ['LANG'] = 'C.UTF-8'
        elif sys.platform.startswith('win'):  # Windows
            os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # 设置locale
        try:
            if sys.platform.startswith('darwin'):
                locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
            elif sys.platform.startswith('linux'):
                locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except locale.Error:
            # 如果设置失败，尝试其他编码
            try:
                locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
            except locale.Error:
                pass  # 使用系统默认
                
        # 设置标准输出编码
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
            
    except Exception as e:
        print(f"Warning: Failed to setup terminal encoding: {e}")

# 在导入时自动设置编码
setup_terminal_encoding()
