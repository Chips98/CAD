# 青少年抑郁症模拟器用户指南

## 📚 目录
1. [快速开始](#快速开始)
2. [环境配置](#环境配置)
3. [功能详解](#功能详解)
4. [配置自定义](#配置自定义)
5. [数据分析](#数据分析)
6. [常见问题](#常见问题)
7. [最佳实践](#最佳实践)

## 快速开始

### 第一步：环境准备
```bash
# 1. 克隆项目
git clone https://github.com/Benioh/Adolescent-Depression-Simulator.git
cd Adolescent-Depression-Simulator

# 2. 安装依赖
pip install -r requirements.txt

# 3. 检查Python版本（需要3.8+）
python --version
```

### 第二步：API配置
编辑 `config.py` 文件，至少配置一个AI提供商：

#### 方案A：使用DeepSeek API（推荐）
```python
# DeepSeek API配置（高性价比）
DEEPSEEK_API_KEY = "sk-your-deepseek-api-key"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"
DEFAULT_MODEL_PROVIDER = "deepseek"
```

#### 方案B：使用Gemini API
```python
# Gemini API配置
GEMINI_API_KEY = "your-gemini-api-key"
DEFAULT_MODEL_PROVIDER = "gemini"
```

### 第三步：运行系统
```bash
# 启动主程序
python main.py

# 或指定配置文件
python main.py -c sim_config.simulation_config
```

## 环境配置

### API密钥获取

#### DeepSeek API
1. 访问 [DeepSeek开放平台](https://platform.deepseek.com/)
2. 注册账户并完成实名认证
3. 进入"API管理"页面
4. 创建新的API密钥
5. 复制密钥到 `config.py` 中

**优势**：
- 成本低廉（约为Gemini的1/5）
- 中文支持优秀
- 速度快

#### Google Gemini API
1. 访问 [Google AI Studio](https://makersuite.google.com/)
2. 创建或选择项目
3. 生成API密钥
4. 配置到 `config.py` 中

**优势**：
- 功能强大
- 响应质量高
- 生态完善

### 系统参数配置

```python
# config.py 重要参数说明

# 模拟参数
SIMULATION_SPEED = 0                    # 模拟延迟（秒），0为无延迟
DEPRESSION_DEVELOPMENT_STAGES = 5       # 抑郁发展阶段数
INTERACTION_FREQUENCY = 3              # 每日事件生成频率

# 咨询功能参数
CONVERSATION_HISTORY_LENGTH = 20        # AI记忆的对话轮数
MAX_EVENTS_TO_SHOW = 20                # 状态面板显示的事件数量

# AI督导功能
ENABLE_SUPERVISION = True              # 是否启用督导
SUPERVISION_INTERVAL = 5               # 每N轮对话触发督导
SUPERVISION_ANALYSIS_DEPTH = "COMPREHENSIVE"  # 督导深度
```

## 功能详解

### 1. 心理健康模拟

#### 启动模拟
```bash
python main.py
# 选择：1. 运行心理健康模拟（30天）
```

#### 模拟过程
1. **AI提供商选择**：如果配置了多个API，系统会提示选择
2. **角色设置**：显示7个AI角色的详细信息
3. **30天模拟**：自动运行，实时显示进度
4. **报告生成**：模拟结束后自动生成详细报告

#### 输出文件
```
logs/sim_20240101_120000/
├── final_report.json         # 综合分析报告
├── simulation.log           # 详细执行日志
├── day_1_state.json         # 第1天状态
├── day_2_state.json         # 第2天状态
├── ...                      # ...
└── day_30_state.json        # 第30天状态
```

### 2. 心理咨询对话

#### 启动咨询
```bash
# 方式1：通过主程序
python main.py
# 选择：2. 与模拟主角进行心理咨询对话

# 方式2：直接启动咨询
python start_therapy_from_logs.py
```

#### 咨询功能
- **完整记忆**：AI记住30天的所有经历
- **动态评估**：每轮对话自动评估治疗效果
- **进展追踪**：监测抑郁程度变化和治疗联盟
- **AI督导**：专业咨询建议和风险提示

#### 特殊命令
```
输入 'p' 或 'progress' - 查看治疗进展
输入 'q' 或 'quit' - 退出咨询
输入 's' 或 'settings' - 调整设置
```

### 3. 报告查看

#### 查看方式
```bash
python main.py
# 选择：3. 查看现有模拟报告
```

#### 报告内容
- **模拟概览**：总天数、最终状态、事件统计
- **心理症状**：识别的抑郁症状列表
- **风险因素**：影响心理健康的关键因素
- **AI分析**：专业的心理健康评估

### 4. 数据加载选项

在心理咨询中，可选择不同的数据加载方式：

```
1. 最终报告 (final_report.json)      # 快速加载，包含核心信息
2. 特定日期状态 (day_X_state.json)   # 加载某一天的详细状态
3. 完整历史数据 (all_history)        # 加载所有30天的详细记录
4. 仅每日事件 (all_daily_events)     # 只加载事件记录
```

## 配置自定义

### 创建自定义角色

#### 1. 复制配置模板
```bash
cp sim_config/simulation_config.py sim_config/my_config.py
```

#### 2. 修改角色配置
```python
# my_config.py
CHARACTERS = {
    "protagonist": {
        "type": "StudentAgent",
        "name": "小王",  # 修改姓名
        "age": 16,       # 修改年龄
        "personality": {
            "traits": ["外向", "乐观", "努力"],  # 修改性格特征
            "openness": 8,
            "conscientiousness": 7,
            "extraversion": 8,  # 提高外向性
            "agreeableness": 8,
            "neuroticism": 3    # 降低神经质
        }
    },
    # 修改其他角色...
}
```

#### 3. 使用自定义配置
```bash
python main.py -c sim_config.my_config
```

### 自定义事件模板

```python
# 在配置文件中添加新的事件模板
EVENT_TEMPLATES = {
    "academic": {
        "positive": [
            "{protagonist}在编程比赛中获得奖项",
            "{teacher}推荐{protagonist}参加科技夏令营",
            # 添加更多正面学业事件...
        ],
        "negative": [
            "{protagonist}的科学实验失败了",
            # 添加更多负面学业事件...
        ]
    }
    # 添加其他类别...
}
```

### 调整抑郁发展阶段

```python
STAGE_CONFIG = {
    "新增阶段": {
        "event_weights": {"positive": 0.4, "negative": 0.4, "neutral": 0.2},
        "event_categories": ["academic", "social"],
        "stress_modifier": 1.1,      # 压力放大倍数
        "relationship_decay": 0.92   # 关系衰减率
    }
}
```

## 数据分析

### 1. 报告文件解析

#### final_report.json 结构
```json
{
    "simulation_summary": {
        "simulation_id": "sim_20240101_120000",
        "total_days": 30,
        "final_depression_level": "SEVERE",
        "total_events": 127,
        "event_variety_score": 0.85,
        "final_stage": "抑郁发展"
    },
    "protagonist_journey": {
        "initial_state": "健康的高二学生...",
        "final_state": "严重抑郁状态...",
        "key_symptoms": ["情绪低落", "社交回避", "失眠"],
        "risk_factors": ["高学业压力", "霸凌经历", "家庭期望过高"]
    },
    "significant_events": [
        {
            "day": 15,
            "description": "刘强在走廊里嘲笑李明",
            "impact_score": -6,
            "participants": ["李明", "刘强"]
        }
    ],
    "daily_progression": [...],
    "ai_analysis": "根据30天的观察...",
    "treatment_recommendations": [...]
}
```

#### day_X_state.json 结构
```json
{
    "day": 15,
    "current_stage": "初期问题",
    "protagonist": {
        "name": "李明",
        "current_mental_state": {
            "emotion": "悲伤",
            "depression_level": "MODERATE",
            "stress_level": 7,
            "self_esteem": 4,
            "social_connection": 3,
            "academic_pressure": 8
        }
    },
    "events": [
        {
            "description": "考试成绩不理想",
            "impact_score": -5,
            "participants": ["李明", "张老师"]
        }
    ],
    "relationship_states": {...}
}
```

### 2. 数据可视化建议

#### Python分析脚本示例
```python
import json
import matplotlib.pyplot as plt
from pathlib import Path

def analyze_simulation(sim_id):
    # 读取数据
    sim_dir = Path(f"logs/{sim_id}")
    
    # 分析每日状态变化
    stress_levels = []
    depression_levels = []
    
    for day in range(1, 31):
        day_file = sim_dir / f"day_{day}_state.json"
        if day_file.exists():
            with open(day_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                mental_state = data['protagonist']['current_mental_state']
                stress_levels.append(mental_state['stress_level'])
                depression_levels.append(mental_state.get('depression_level', 0))
    
    # 绘制图表
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.plot(stress_levels, label='压力水平')
    plt.title('压力水平变化')
    plt.xlabel('天数')
    plt.ylabel('压力水平 (0-10)')
    
    plt.subplot(1, 2, 2)
    plt.plot(depression_levels, label='抑郁程度', color='red')
    plt.title('抑郁程度变化')
    plt.xlabel('天数')
    plt.ylabel('抑郁程度 (0-4)')
    
    plt.tight_layout()
    plt.savefig(f'{sim_id}_analysis.png')
    plt.show()

# 使用示例
analyze_simulation("sim_20240101_120000")
```

## 常见问题

### Q1: API调用失败怎么办？
**A**: 
1. 检查网络连接
2. 验证API密钥是否正确
3. 确认API余额是否充足
4. 尝试切换到另一个AI提供商

### Q2: 模拟过程中断怎么办？
**A**: 
1. 检查logs目录中的simulation.log文件
2. 确认已生成的day_X_state.json文件
3. 可以使用已有数据进行咨询
4. 重新运行模拟会创建新的simulation_id

### Q3: 如何提高模拟质量？
**A**: 
1. 使用更强的AI模型（如Gemini）
2. 调整事件生成频率
3. 自定义更丰富的事件模板
4. 优化角色性格设置

### Q4: 咨询对话不够自然怎么办？
**A**: 
1. 增加对话历史长度
2. 提供更多背景事件信息
3. 使用完整历史数据加载模式
4. 启用AI督导功能

### Q5: 内存不足怎么办？
**A**: 
1. 减少对话历史长度
2. 降低事件显示数量
3. 使用最终报告而非完整历史
4. 定期清理logs目录

## 最佳实践

### 1. 模拟设计最佳实践

#### 角色配置
- **平衡性格特征**：避免极端值，保持真实性
- **合理年龄设置**：确保符合目标场景
- **多样化关系**：建立复杂但合理的关系网络

#### 事件模板
- **现实基础**：基于真实青少年经历设计事件
- **情感平衡**：正面、负面、中性事件合理分配
- **发展性**：事件应体现心理状态的渐进变化

### 2. 咨询对话最佳实践

#### 咨询技巧
- **倾听优先**：多问开放性问题，少做评判
- **感同身受**：理解AI角色的心理状态
- **循序渐进**：从浅入深，建立信任关系
- **专业边界**：保持咨询师的专业态度

#### 对话策略
```
良好开场：
"我注意到你最近经历了很多困难，你愿意和我聊聊吗？"

有效追问：
"当时你的感受是什么？"
"这件事对你意味着什么？"
"你是怎么应对的？"

情感支持：
"听起来你确实很不容易。"
"你的感受是完全可以理解的。"
"你已经很努力了。"
```

### 3. 数据分析最佳实践

#### 数据收集
- **多次模拟**：运行多个不同配置的模拟
- **对比分析**：比较不同干预策略的效果
- **长期跟踪**：分析心理状态的变化趋势

#### 结果解读
- **定量分析**：关注数值变化趋势
- **定性分析**：分析具体事件和行为
- **综合评估**：结合多维度指标判断

### 4. 系统维护最佳实践

#### 文件管理
```bash
# 定期清理旧日志
find logs/ -name "sim_*" -mtime +30 -exec rm -rf {} \;

# 备份重要数据
tar -czf backup_$(date +%Y%m%d).tar.gz logs/

# 监控磁盘空间
du -sh logs/
```

#### 性能优化
- **限制并发**：避免同时运行多个模拟
- **监控资源**：关注CPU和内存使用
- **定期重启**：长时间运行后重启程序

### 5. 教学应用最佳实践

#### 课堂使用
1. **理论讲解**：先介绍抑郁症理论基础
2. **观摩模拟**：集体观看一次完整模拟
3. **小组实践**：分组进行自定义配置实验
4. **讨论分析**：分享观察结果和心得体会

#### 作业设计
- **配置设计**：要求学生设计不同的角色配置
- **对比实验**：比较不同配置下的结果差异
- **咨询练习**：进行模拟心理咨询对话
- **报告撰写**：分析模拟结果并提出干预建议

---

## 技术支持

如遇到技术问题，请：
1. 查看logs目录中的错误日志
2. 检查GitHub项目的Issues页面
3. 提交详细的bug报告
4. 参与项目讨论和改进

**项目地址**: https://github.com/Benioh/Adolescent-Depression-Simulator
**文档更新**: 2024年1月 