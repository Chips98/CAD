# 青少年抑郁症模拟器系统分析

## 1. 系统概述

青少年抑郁症模拟器（Adolescent-Depression-Simulator）是一个基于大语言模型的心理健康模拟系统，通过多智能体协同工作，模拟青少年从健康状态逐渐发展为抑郁症的完整心理过程，并提供专业的心理咨询对话功能。

### 1.1 核心特征
- **多智能体协同**：7个不同性格的AI角色进行真实的人际互动
- **科学心理建模**：基于抑郁症发展的5阶段模型
- **动态关系网络**：角色间关系随时间变化和事件影响而演化
- **多AI提供商支持**：同时支持Google Gemini和DeepSeek API
- **完整治疗流程**：模拟结束后可进行30天记忆回溯的心理咨询对话
- **恢复机制**：模拟真实心理治疗的渐进改善过程

### 1.2 应用场景
- 心理健康研究和教学
- 心理咨询师培训
- 抑郁症科普教育
- 心理干预效果评估
- 青少年心理健康预防

## 2. 系统架构

### 2.1 整体架构
```
┌─────────────────────────────────────────────────────────────┐
│                    用户界面层 (main.py)                      │
│              Rich Terminal UI + 菜单系统                    │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                   业务逻辑层                               │
│  ┌─────────────────┐    ┌──────────────────────────────┐   │
│  │  SimulationEngine│    │  TherapySessionManager       │   │
│  │  (模拟引擎)       │    │  (心理咨询管理器)              │   │
│  └─────────────────┘    └──────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                   核心组件层                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │
│  │EventGenerator│  │ AI Clients  │  │ Agent System    │    │
│  │(事件生成器)   │  │(AI客户端)   │  │(智能体系统)      │    │
│  └─────────────┘  └─────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                   数据模型层                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │
│  │Psychology   │  │Configuration│  │  Data Storage   │    │
│  │Models       │  │System       │  │  (JSON/Logs)    │    │
│  └─────────────┘  └─────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 核心模块分析

#### 2.2.1 模拟引擎 (SimulationEngine)
**文件**: `core/simulation_engine.py`

**主要功能**:
- 管理整个30天模拟过程的执行
- 协调各智能体之间的交互
- 控制抑郁症发展的5个阶段转换
- 处理事件对心理状态的影响
- 生成详细的模拟报告

**核心方法**:
```python
class SimulationEngine:
    def __init__(self, simulation_id: str, config_module: str, model_provider: str)
    def setup_simulation(self)  # 初始化智能体和关系网络
    async def run_simulation(self, days: int = 30)  # 执行30天模拟
    async def _simulate_day(self)  # 模拟单天活动
    def _determine_stage(self, current_day: int, total_days: int)  # 确定当前阶段
    async def _generate_final_report(self)  # 生成最终报告
```

#### 2.2.2 事件生成器 (EventGenerator)
**文件**: `core/event_generator.py`

**核心创新**:
- **模板分析系统**: 分析现有事件模板提取模式
- **智能发散生成**: 基于AI的创新事件生成
- **逻辑验证机制**: 确保生成事件的合理性和年龄适宜性
- **多样性保证**: 避免重复事件，提高真实感

**关键组件**:
```python
class TemplateAnalyzer:  # 模板模式分析
class ContextExtractor:  # 上下文信息提取  
class LogicValidator:    # 逻辑验证和修正
class DivergentGenerator: # AI发散生成
```

#### 2.2.3 智能体系统
**文件**: `agents/` 目录

**智能体类型**:
- **BaseAgent**: 所有智能体的基类，提供基础心理状态管理
- **StudentAgent**: 主角李明，会经历抑郁症发展过程
- **FamilyAgent**: 家庭成员基类
  - **FatherAgent**: 父亲，严厉型教育风格
  - **MotherAgent**: 母亲，焦虑型关爱风格
- **SchoolAgent**: 学校相关角色
  - **TeacherAgent**: 教师，影响学业压力
  - **BestFriendAgent**: 好友，提供情感支持
  - **BullyAgent**: 霸凌者，制造负面事件
  - **ClassmateAgent**: 同学，包括竞争对手
- **TherapistAgent**: 心理咨询师，用于治疗阶段

#### 2.2.4 心理咨询管理器 (TherapySessionManager)
**文件**: `core/therapy_session_manager.py`

**创新功能**:
- **动态抑郁程度调整**: 根据咨询效果实时调整患者状态
- **治疗效果评估**: 每轮对话自动评分(0-10分)
- **治疗联盟追踪**: 监测咨询师与患者的信任关系
- **AI督导功能**: 提供专业的咨询建议和风险评估
- **恢复机制**: 模拟真实心理治疗的渐进改善过程

**核心算法**:
```python
# 抑郁程度改善条件
if avg_effectiveness >= 7.0 and therapeutic_alliance >= 6.0:
    # 降低抑郁程度
    current_level = max(0, current_level - 1)
    
# 恶化条件  
elif avg_effectiveness < 3.0 and therapeutic_alliance < 3.0:
    # 提高抑郁程度
    current_level = min(4, current_level + 1)
```

## 3. 心理学模型

### 3.1 抑郁症发展阶段
系统基于科学的抑郁症发展模型，定义了5个递进阶段：

1. **健康阶段**: 正常青少年生活，偶有压力
2. **压力积累**: 学业、社交压力开始增加
3. **初期问题**: 出现明显的情绪和行为变化
4. **关系恶化**: 人际关系受损，社交回避
5. **抑郁发展**: 严重抑郁症状，需要专业干预

### 3.2 心理状态建模
```python
@dataclass
class PsychologicalState:
    emotion: EmotionState           # 当前情绪状态
    depression_level: DepressionLevel # 抑郁程度(0-4级)
    stress_level: int              # 压力水平(0-10)
    self_esteem: int               # 自尊水平(0-10)
    social_connection: int         # 社交连接度(0-10)
    academic_pressure: int         # 学业压力(0-10)
```

### 3.3 事件影响机制
每个生活事件都会影响心理状态的多个维度：

```python
def _process_event_impact(self, event: LifeEvent):
    impact = event.impact_score
    
    # 调整压力和自尊
    if impact < 0:  # 负面事件
        self.stress_level = min(10, self.stress_level + abs(impact) // 2)
        self.self_esteem = max(0, self.self_esteem - abs(impact) // 3)
    
    # 根据累积负面事件判断抑郁风险
    negative_events = [e for e in recent_events if e.impact_score < -3]
    if len(negative_events) >= 3:
        self.depression_level = DepressionLevel.MILD_RISK
```

## 4. AI集成架构

### 4.1 多AI提供商支持
**文件**: `core/ai_client_factory.py`

系统支持多个AI提供商，实现了统一的接口：

```python
class AIClientFactory:
    def get_client(self, provider: str) -> Union[GeminiClient, DeepSeekClient]
    def get_available_providers(self) -> list
    def test_connection(self, provider: str) -> bool
```

**支持的AI提供商**:
- **Google Gemini**: `core/gemini_client.py`
- **DeepSeek**: `core/deepseek_client.py`

### 4.2 智能对话生成
每个智能体都具备基于个性和状态的对话能力：

```python
async def respond_to_situation(self, situation: str, other_agents: List[BaseAgent]) -> str:
    profile = self.get_profile()  # 获取角色档案
    history = self.dialogue_history[-5:]  # 获取对话历史
    
    response = await self.ai_client.generate_agent_response(
        profile, situation, history
    )
    return response
```

## 5. 配置系统

### 5.1 智能体配置
**文件**: `sim_config/simulation_config.py`

系统提供了完整的角色定制能力：

```python
CHARACTERS = {
    "protagonist": {
        "type": "StudentAgent",
        "name": "李明",
        "age": 17,
        "personality": {
            "traits": ["内向", "敏感", "努力", "完美主义"],
            "openness": 6,
            "conscientiousness": 8,
            "extraversion": 4,
            "agreeableness": 7,
            "neuroticism": 6
        }
    },
    # ... 其他角色配置
}
```

### 5.2 事件模板系统
支持四大类事件模板：

1. **学业事件** (academic): 考试、作业、课堂表现
2. **社交事件** (social): 朋友互动、霸凌、同伴关系
3. **家庭事件** (family): 亲子关系、家庭氛围
4. **个人事件** (personal): 内心体验、个人活动

每类事件分为正面、负面、中性三种情感倾向。

### 5.3 关系网络配置
```python
RELATIONSHIPS = [
    {"person_a": "李明", "person_b": "李建国", "type": "父子", 
     "closeness": 6, "trust": 6, "conflict": 3},
    {"person_a": "李明", "person_b": "王秀芳", "type": "母子", 
     "closeness": 8, "trust": 8, "conflict": 2},
    # ... 其他关系配置
]
```

## 6. 数据管理

### 6.1 数据存储结构
```
logs/
├── sim_20240101_120000/          # 模拟运行目录
│   ├── final_report.json         # 最终综合报告
│   ├── simulation.log            # 详细执行日志
│   ├── day_1_state.json          # 每日状态记录
│   ├── day_2_state.json
│   ├── ...
│   ├── day_30_state.json
│   └── therapy_session_*.json    # 心理咨询记录
```

### 6.2 报告生成
系统自动生成详细的JSON格式报告：

```json
{
    "simulation_summary": {
        "simulation_id": "sim_20240101_120000",
        "total_days": 30,
        "final_depression_level": "SEVERE",
        "total_events": 127,
        "final_stage": "抑郁发展"
    },
    "protagonist_journey": {
        "final_state": "李明：情绪严重抑郁...",
        "key_symptoms": ["情绪低落", "社交回避", "睡眠问题"],
        "risk_factors": ["高学业压力", "社交孤立", "低自尊"]
    },
    "significant_events": [...],
    "ai_analysis": "专业AI分析报告...",
    "protagonist_character_profile": {...}
}
```

## 7. 用户交互

### 7.1 主程序界面
**文件**: `main.py`

提供Rich终端UI的交互式菜单：

1. **运行心理健康模拟**（30天）
2. **与模拟主角进行心理咨询对话**
3. **查看现有模拟报告**
4. **退出系统**

### 7.2 心理咨询界面
**文件**: `start_therapy_from_logs.py`

专门的心理咨询启动程序：
- 选择模拟运行记录
- 选择数据加载方式（最终报告/特定日期/完整历史）
- 进入交互式咨询对话
- 实时显示治疗进展和效果评估

### 7.3 设置管理
支持动态调整系统参数：
- 对话历史长度
- 事件显示数量
- AI督导功能开关
- 督导触发间隔

## 8. 技术特点

### 8.1 异步处理
系统大量使用异步编程，提高AI调用效率：

```python
async def run_simulation(self, days: int = 30):
    for day in range(1, days + 1):
        await self._simulate_day()
        
async def _simulate_day(self):
    for _ in range(event_count):
        event_desc, participants, impact = await self.event_generator.generate_event(...)
        await self._process_event(event_desc, participants, impact)
```

### 8.2 模块化设计
- 清晰的模块边界和职责分离
- 可扩展的智能体系统
- 可配置的事件生成机制
- 支持多种AI提供商的统一接口

### 8.3 错误处理
- 完善的异常捕获和日志记录
- 优雅的降级处理
- 用户友好的错误提示

### 8.4 性能优化
- 单例模式的AI客户端管理
- 智能的事件缓存机制
- 高效的数据序列化

## 9. 创新点

### 9.1 科学性
- 基于真实抑郁症发展模型的5阶段设计
- 多维度心理状态建模
- 科学的事件影响评估机制

### 9.2 真实性
- 7个不同性格的AI角色真实互动
- 动态关系网络随时间演化
- 基于模板但避免重复的事件生成

### 9.3 交互性
- 完整的30天记忆回溯咨询功能
- 动态抑郁程度调整机制
- AI督导和治疗效果评估

### 9.4 可扩展性
- 支持自定义场景和角色配置
- 多AI提供商接口
- 模块化的架构设计

## 10. 应用价值

### 10.1 教育价值
- 为心理学专业学生提供实践平台
- 帮助理解抑郁症的发展过程
- 训练心理咨询技能

### 10.2 研究价值
- 生成大量心理发展数据
- 验证干预策略效果
- 探索不同因素对心理健康的影响

### 10.3 社会价值
- 提高公众对抑郁症的认识
- 促进心理健康意识
- 为政策制定提供参考

## 11. 技术栈总结

- **编程语言**: Python 3.8+
- **AI集成**: Google Gemini API, DeepSeek API
- **UI框架**: Rich (终端UI)
- **异步处理**: asyncio
- **数据格式**: JSON
- **配置管理**: Python模块
- **日志系统**: Python logging
- **依赖管理**: pip + requirements.txt

## 12. 发展方向

### 12.1 短期优化
- 增加更多AI提供商支持
- 优化事件生成算法
- 完善督导功能

### 12.2 中期扩展
- 支持Web界面
- 增加数据可视化
- 集成真实心理评估量表

### 12.3 长期愿景
- 建立心理健康知识图谱
- 开发移动应用
- 集成VR/AR技术提供沉浸式体验

这个系统代表了AI在心理健康领域应用的创新尝试，通过技术手段为心理健康教育、研究和干预提供了强有力的工具支持。 