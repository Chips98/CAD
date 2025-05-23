# 心理健康Agent模拟框架

一个基于大语言模型的心理健康模拟系统，通过多Agent协同展示学生从健康状态逐渐发展为抑郁症的心理过程，并提供完整的心理咨询对话功能。

## 📖 项目概述

本项目通过多个AI智能体（Agent）模拟真实的人际互动环境，展示一个高中生李明在学业压力、人际关系等多重因素影响下，心理健康状况逐步恶化直至患上抑郁症的完整过程。模拟结束后，您可以与保留完整30天记忆的李明进行心理咨询对话，体验真实的心理治疗过程。

**🆕 最新更新：现已支持多AI提供商！**
- ✅ **Google Gemini API** - 强大的AI能力
- ✅ **DeepSeek API** - 高性价比的国产AI选择  
- ✅ **智能切换** - 程序启动时可选择AI提供商
- ✅ **统一体验** - 所有功能在不同AI下保持一致

## 🎯 主要功能

### 🏥 心理模拟系统
- **多Agent协同**：7个不同性格的AI角色互动
- **多AI提供商支持**：支持Gemini和DeepSeek，可自由选择
- **心理状态建模**：科学的抑郁症发展模型（5个阶段）
- **动态关系网络**：角色间关系随时间变化
- **真实场景模拟**：学校、家庭等多种环境
- **详细数据记录**：完整的心理变化轨迹，自动保存到子文件夹

## 📋 系统要求

- Python 3.8+
- **AI API密钥**（选择其一或两者都配置）：
  - Google Gemini API密钥 或
  - DeepSeek API密钥
- 稳定的网络连接
- Rich库（用于美观的终端界面）

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/Benioh/Adolescent-Depression-Simulator.git
cd Adolescent-Depression-Simulator

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

编辑配置文件 `config.py`，添加您的API密钥：

#### 方案一：使用Gemini API（Google）
```python
# Gemini API配置
GEMINI_API_KEY = "your_gemini_api_key_here"

# 设置默认提供商为Gemini
DEFAULT_MODEL_PROVIDER = "gemini"
```

**获取Gemini API密钥：**
1. 访问 [Google AI Studio](https://makersuite.google.com/)
2. 创建新项目或选择现有项目
3. 生成API密钥
4. 将密钥复制到 `config.py` 文件中

#### 方案二：使用DeepSeek API（推荐，高性价比）
```python
# DeepSeek API配置
DEEPSEEK_API_KEY = "your_deepseek_api_key_here"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# 设置默认提供商为DeepSeek
DEFAULT_MODEL_PROVIDER = "deepseek"
```

**获取DeepSeek API密钥：**
1. 访问 [DeepSeek开放平台](https://platform.deepseek.com/)
2. 注册账户并完成验证
3. 进入API管理页面
4. 创建新的API密钥
5. 将密钥复制到 `config.py` 文件中

#### 方案三：同时配置两者（推荐）
```python
# 同时配置两个API，程序启动时可选择
GEMINI_API_KEY = "your_gemini_api_key_here"

DEEPSEEK_API_KEY = "your_deepseek_api_key_here"  
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# 设置默认提供商（可选择任一个）
DEFAULT_MODEL_PROVIDER = "deepseek"  # 或 "gemini"
```

### 3. AI提供商选择

程序启动时会自动检测已配置的API密钥：

- **单一提供商**：自动使用已配置的API
- **多个提供商**：显示选择菜单，让您选择使用哪个AI
- **智能默认**：可以设置默认提供商，按回车即可使用

选择界面示例：
```
┏━━━━━━┳━━━━━━━━━━┳━━━━━━┓
┃ 编号 ┃ 提供商   ┃ 状态 ┃
┡━━━━━━╇━━━━━━━━━━╇━━━━━━┩
│ 1    │ GEMINI   │ 可用 │
│ 2    │ DEEPSEEK │ 默认 │
└──────┴──────────┴──────┘
请选择AI提供商 (1-2) 或回车使用默认:
```

### 4. 配置参数说明

编辑 `config.py` 中的关键参数：

```python
# AI提供商配置
GEMINI_API_KEY = ""                    # Google Gemini API密钥
DEEPSEEK_API_KEY = ""                  # DeepSeek API密钥  
DEEPSEEK_BASE_URL = "https://api.deepseek.com"  # DeepSeek API基础URL
DEEPSEEK_MODEL = "deepseek-chat"       # DeepSeek模型名称
DEFAULT_MODEL_PROVIDER = "deepseek"    # 默认AI提供商：gemini 或 deepseek

# 模拟相关参数
SIMULATION_SPEED = 1                    # 模拟速度（秒），控制30天模拟的执行间隔
LOG_LEVEL = "INFO"                     # 日志级别：DEBUG, INFO, WARNING, ERROR
DEPRESSION_DEVELOPMENT_STAGES = 5       # 抑郁发展阶段数（影响心理状态层次性）
INTERACTION_FREQUENCY = 3              # 交互频率（影响事件生成密度）

# 咨询相关参数（可在程序中动态调整）
CONVERSATION_HISTORY_LENGTH = 20        # AI记忆的对话轮数
MAX_EVENTS_TO_SHOW = 20                # 患者状态面板显示的事件数

# 督导相关参数
ENABLE_SUPERVISION = True              # 是否启用AI督导功能
SUPERVISION_INTERVAL = 5               # 督导间隔（每N轮对话触发一次督导）
SUPERVISION_ANALYSIS_DEPTH = "COMPREHENSIVE"  # 督导分析深度：BASIC, STANDARD, COMPREHENSIVE
```

### 5. 使用方式

## 📋 系统结构

```
mental_health_agent/
├── agents/                    # Agent角色定义
│   ├── base_agent.py         # Agent基类
│   ├── student_agent.py      # 学生主角
│   ├── family_agents.py      # 家庭成员
│   ├── school_agents.py      # 学校人员
│   └── therapist_agent.py    # 心理咨询师督导
├── core/                     # 核心组件
│   ├── gemini_client.py      # Gemini API封装
│   ├── deepseek_client.py    # DeepSeek API封装
│   ├── ai_client_factory.py  # AI客户端工厂（多提供商支持）
│   ├── simulation_engine.py  # 模拟引擎
│   └── therapy_session_manager.py  # 咨询会话管理器
├── models/                   # 数据模型
│   └── psychology_models.py  # 心理学模型
├── logs/                     # 日志文件
│   └── sim_YYYYMMDD_HHMMSS/  # 模拟运行子目录
│       ├── final_report.json # 最终模拟报告
│       ├── day_X_state.json  # 每日心理状态
│       └── therapy_*.json    # 咨询对话记录
├── main.py                   # 主程序入口
├── start_therapy_from_logs.py # 心理咨询主程序
└── config.py                 # 配置文件
``` 

## 🙏 致谢

- Google Gemini API 提供强大的AI能力
- DeepSeek API 提供高性价比的国产AI服务
- Rich库提供美观的终端界面
- 心理学研究为模拟提供理论基础 