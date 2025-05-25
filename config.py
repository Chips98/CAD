# 配置文件
# 请将你的API密钥填入下方或创建config_local.py文件

GEMINI_API_KEY = ""

# DeepSeek API配置
DEEPSEEK_API_KEY = "sk-e8c693550b8e4cf1a5541a7d7157dea1"  # 请填入您的DeepSeek API密钥
DEEPSEEK_BASE_URL = "https://api.deepseek.com"  # DeepSeek API基础URL

# 模型选择配置
DEFAULT_MODEL_PROVIDER = "deepseek"  # 可选: "gemini", "deepseek"
DEEPSEEK_MODEL = "deepseek-chat"  # DeepSeek模型名称

# 模拟参数
SIMULATION_SPEED = 0                    # 模拟速度（秒），控制30天模拟的执行间隔
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

