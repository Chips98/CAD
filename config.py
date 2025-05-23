# 配置文件
# 请将你的API密钥填入下方或创建config_local.py文件

GEMINI_API_KEY = "your_gemini_api_key_here"

# 模拟参数
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

