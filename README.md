# 心理健康Agent模拟框架
![depression](https://github.com/user-attachments/assets/4fedb65a-5774-440a-810e-ef3c550072f5)
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

### 🌟 心理咨询恢复机制
- **动态抑郁程度调整**：根据咨询效果，患者的抑郁程度可以逐步改善或恶化
- **治疗效果评估**：每轮对话后自动评估治疗效果（0-10分）
- **治疗联盟追踪**：监测咨询师与患者之间的信任关系（0-10分）
- **实时进展反馈**：识别突破性时刻和风险指标
- **渐进式改善**：模拟真实心理治疗的渐进过程

### 🔧 自定义场景人物
- **抽象模拟引擎**：支持自定义场景和人物配置
- **动态事件生成**：结合模板和AI生成，避免重复
- **灵活配置系统**：可创建不同的心理健康场景
- **事件多样性保证**：智能避免重复事件，提高真实感

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

# 恢复机制参数（自动生效）
# - 改善条件：平均效果分数≥7.0 且 治疗联盟≥6.0
# - 恶化条件：平均效果分数<3.0 且 治疗联盟<3.0
# - 评估间隔：每5轮对话检查一次抑郁程度变化
```

### 5. 使用方式

#### 运行模拟
```bash
# 使用默认配置运行
python main.py

# 指定配置文件运行
python main.py -c sim_config.simulation_config  # 默认配置
python main.py -c sim_config.example_custom_config  # 自定义配置示例

# 查看帮助
python main.py -h
```
- 选择AI提供商（如果配置了多个）
- 观看30天的心理发展过程
- 模拟结束后自动生成报告

#### 开始心理咨询
```bash
python start_therapy_from_logs.py
```
- 选择一个已完成的模拟记录
- 与保留完整记忆的李明进行对话
- **恢复机制使用**：
  - 输入 `p` 或 `progress` 查看治疗进展
  - 系统会自动评估每轮对话的效果
  - 每5轮对话检查是否可以改善抑郁程度
  - 突破性时刻会有特殊提示
  - 风险指标会触发警告

#### 恢复机制说明

**抑郁程度等级**：
- `HEALTHY` (0) - 健康
- `MILD_RISK` (1) - 轻度风险  
- `MODERATE` (2) - 中度抑郁
- `SEVERE` (3) - 重度抑郁
- `CRITICAL` (4) - 严重抑郁

**改善条件**：
- 最近5轮对话的平均效果分数 ≥ 7.0
- 治疗联盟分数 ≥ 6.0
- 至少进行了5轮对话

**注意事项**：
- 恢复是渐进的过程，需要持续的积极对话
- 治疗联盟（信任关系）是恢复的关键
- 系统会根据患者当前状态调整回应方式
- 恶化也是可能的，需要调整咨询策略

## 📋 系统结构

```
Adolescent-Depression-Simulator/
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
│   ├── simulation_engine.py  # 抽象模拟引擎
│   ├── event_generator.py    # 动态事件生成器
│   └── therapy_session_manager.py  # 咨询会话管理器
├── sim_config/               # 模拟配置文件
│   ├── __init__.py          # Python包标识
│   ├── simulation_config.py  # 默认模拟配置
│   └── example_custom_config.py # 自定义配置示例
├── models/                   # 数据模型
│   └── psychology_models.py  # 心理学模型
├── logs/                     # 日志文件
│   └── sim_YYYYMMDD_HHMMSS/  # 模拟运行子目录
│       ├── final_report.json # 最终模拟报告
│       ├── day_X_state.json  # 每日心理状态
│       └── therapy_*.json    # 咨询对话记录（含恢复进展）
├── main.py                   # 主程序入口
├── start_therapy_from_logs.py # 心理咨询主程序
└── config.py                 # 配置文件
``` 

## 🎨 自定义模拟场景

系统支持创建自定义的心理健康模拟场景。您可以：

### 重要说明：配置文件夹结构

模拟配置文件存放在 `sim_config/` 文件夹中：
- `sim_config/simulation_config.py` - 默认的青少年抑郁症模拟配置
- `sim_config/example_custom_config.py` - 大学生就业压力场景示例

### 创建自定义配置
1. 复制 `sim_config/simulation_config.py` 为新文件（如 `sim_config/my_scenario.py`）
2. 编辑新文件，修改人物、关系、事件模板等配置
3. 使用命令行参数运行：
   ```bash
   python main.py -c sim_config.my_scenario
   ```




