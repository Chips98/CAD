# 🧠 智能心理健康模拟系统

<div style="text-align: center;">
  <img src="https://github.com/user-attachments/assets/4fedb65a-5774-440a-810e-ef3c550072f5" width="300" alt="depression">
</div>

一个基于大语言模型和科学心理学理论的多Agent心理健康模拟系统，通过模块化心理模型深度模拟抑郁症发展过程，并提供完整的心理咨询对话功能。

## 📖 项目概述

本项目通过多个AI智能体（Agent）模拟真实的人际互动环境，结合先进的心理学理论（CAD认知-情感-抑郁模型），支持用户自定义场景与事件。系统可自由组合学业压力、职场竞争，或家庭矛盾等因素，深度模拟不同人群在各类复杂情境下抑郁症产生的完整过程。模拟结束后，可与具备完整记忆回溯功能的虚拟角色开展心理咨询对话，为心理健康研究、心理咨询教学与科普体验，提供高度真实、可定制化的沉浸式交互场景。

## 🌟 创新亮点

### 🧩 模块化心理模型系统
- **四种心理模型**: 基础规则、CAD增强、LLM驱动、混合模型
- **科学理论支撑**: 基于Beck认知三角、CAD理论等心理学原理
- **智能模型选择**: 交互式配置界面，支持参数自定义
- **自适应融合**: 混合模型可根据场景自动调整权重

### 🎯 CAD理论深度集成
- **认知-情感-抑郁模型**: 完整实现CAD(Cognitive-Affective-Depression)理论
- **核心信念系统**: 建模自我、世界、未来三维信念结构
- **认知处理机制**: 模拟思维反刍、认知扭曲等关键过程
- **行为倾向预测**: 社交退缩、意志缺失等行为模式演化

### 🚀 多AI提供商架构
- **无缝切换**: Google Gemini、DeepSeek等多AI提供商支持
- **智能回退**: AI调用失败时自动切换到备用模型
- **统一接口**: 不同AI提供商保持一致的用户体验
- **成本优化**: 可根据成本和性能需求选择最佳提供商

## 🎯 主要功能

### 🏥 智能心理模拟系统
- **多Agent协同**: 7个不同性格的AI角色真实互动
- **模块化心理模型**: 四种可选的心理状态评估模型
- **科学心理建模**: 基于CAD理论的抑郁症发展模型（5个阶段）
- **动态关系网络**: 角色间关系随时间和事件变化
- **真实场景模拟**: 学校、家庭等多种环境的复杂互动
- **详细数据记录**: 完整的心理变化轨迹，包含CAD状态演化

### 🌟 心理咨询恢复机制
- **动态抑郁程度调整**: 根据咨询效果，患者的抑郁程度可以逐步改善或恶化
- **治疗效果评估**: 每轮对话后自动评估治疗效果（0-10分）
- **治疗联盟追踪**: 监测咨询师与患者之间的信任关系（0-10分）
- **实时进展反馈**: 识别突破性时刻和风险指标
- **渐进式改善**: 模拟真实心理治疗的渐进过程

### 🔧 高度自定义系统
- **抽象模拟引擎**: 支持JSON配置的场景和人物定制
- **动态事件生成**: 结合模板和AI生成，避免重复
- **灵活配置系统**: 可创建不同的心理健康场景
- **事件多样性保证**: 智能避免重复事件，提高真实感

### 🤖 多AI提供商支持
- ✅ **Google Gemini API** - 强大的AI理解能力
- ✅ **DeepSeek API** - 高性价比的国产AI选择  
- ✅ **智能切换** - 程序启动时可选择AI提供商
- ✅ **统一体验** - 所有功能在不同AI下保持一致

## 🧠 心理模型详解

### 1. 基础规则模型 (Basic Rules)
**特点**: 快速、轻量、规则驱动
- 适用场景: 快速测试、教学演示
- 计算方式: 基于预定义规则和权重
- 优点: 执行速度快，资源消耗低
- 缺点: 准确性相对较低

```python
# 使用基础规则模型
python main.py --model basic_rules
```

### 2. CAD增强模型 (CAD Enhanced) 🌟推荐
**特点**: 科学、准确、符合心理学原理
- 理论基础: Beck认知三角 + CAD理论
- 核心组件:
  - **情感基调** (Affective Tone): 整体情绪倾向
  - **核心信念** (Core Beliefs): 自我/世界/未来三维信念
  - **认知处理** (Cognitive Processing): 思维反刍、认知扭曲
  - **行为倾向** (Behavioral Inclination): 社交退缩、意志缺失

```python
# 使用CAD增强模型（推荐）
python main.py --model cad_enhanced
```

### 3. LLM驱动模型 (LLM Driven)
**特点**: 智能、深度、上下文感知
- 适用场景: 深度分析、复杂案例
- 计算方式: 大语言模型实时评估
- 优点: 高准确性，强上下文理解
- 缺点: 计算成本高，依赖网络

```python
# 使用LLM驱动模型
python main.py --model llm_driven
```

### 4. 混合模型 (Hybrid) 🚀最佳
**特点**: 平衡、智能、自适应
- 融合策略: 多模型加权融合
- 智能调度: 根据事件重要性决定是否使用LLM
- 并行处理: 支持异步计算提高效率
- 自适应权重: 根据模型性能动态调整

```python
# 使用混合模型（最佳性能）
python main.py --model hybrid
```

### 交互式模型选择
```bash
# 启动交互式模型选择界面
python main.py --interactive-model
```

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
git clone https://github.com/your-repo/CAD-Depression-Simulator.git
cd CAD-Depression-Simulator

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

创建配置文件 `config/api_config.json`：

```json
{
  "gemini": {
    "api_key": "your_gemini_api_key_here",
    "model": "gemini-pro"
  },
  "deepseek": {
    "api_key": "your_deepseek_api_key_here",
    "base_url": "https://api.deepseek.com",
    "model": "deepseek-chat"
  },
  "default_provider": "deepseek"
}
```

**获取API密钥：**

#### Gemini API（Google）
1. 访问 [Google AI Studio](https://makersuite.google.com/)
2. 创建新项目或选择现有项目
3. 生成API密钥

#### DeepSeek API（推荐）
1. 访问 [DeepSeek开放平台](https://platform.deepseek.com/)
2. 注册账户并完成验证
3. 创建新的API密钥

### 3. 使用方式

#### 基础使用
```bash
# 使用默认心理模型运行
python main.py

# 指定心理模型
python main.py --model cad_enhanced

# 交互式选择模型
python main.py --interactive-model

# 查看帮助
python main.py --help
```

#### 心理模型配置
程序运行后选择菜单选项 **5. 心理模型配置** 进行详细设置：
- 选择模型类型
- 自定义模型参数
- 保存配置供下次使用

#### 开始心理咨询
```bash
# 与模拟对象进行心理咨询（人工咨询师）
python start_therapy_from_logs.py

# AI咨询师自动对话
python start_ai_to_ai_therapy.py

# 网页界面（实验性功能）
python start_web.py
```

## 🔧 高级配置

### 场景配置文件
配置文件位于 `config/scenarios/` 目录：
- `default_adolescent.json` - 默认青少年抑郁症模拟
- `workplace_stress.json` - 职场压力场景示例
- `family_conflict.json` - 家庭矛盾场景示例

### 心理模型参数调优
```json
{
  "model_configs": {
    "cad_enhanced": {
      "belief_impact_strength": 0.4,
      "affective_amplification": 1.3,
      "rumination_threshold": 6.0,
      "cognitive_distortion_rate": 0.1
    },
    "hybrid": {
      "basic_rules_weight": 0.3,
      "cad_weight": 0.4,
      "llm_weight": 0.3,
      "enable_adaptive_weights": true
    }
  }
}
```

## 📊 数据输出

### 模拟报告
每次模拟会在 `logs/sim_YYYYMMDD_HHMMSS/` 目录生成：
- `final_report.json` - 完整模拟报告，包含CAD状态分析
- `day_X_state.json` - 每日心理状态详细记录
- `conversation_log.json` - 角色对话记录
- `simulation.log` - 详细运行日志

### CAD状态追踪
系统会详细记录CAD理论各维度的变化：
```json
{
  "cad_state": {
    "affective_tone": 3.2,
    "core_beliefs": {
      "self_belief": 2.8,
      "world_belief": 3.5,
      "future_belief": 2.1
    },
    "cognitive_processing": {
      "rumination": 6.7,
      "distortions": 5.2
    },
    "behavioral_inclination": {
      "social_withdrawal": 4.8,
      "avolition": 3.9
    }
  }
}
```

## 📋 系统架构

```
CAD-Depression-Simulator/
├── agents/                     # Agent角色定义
│   ├── base_agent.py          # Agent基类（支持心理模型）
│   ├── student_agent.py       # 学生主角
│   ├── family_agents.py       # 家庭成员
│   ├── school_agents.py       # 学校人员
│   └── therapist_agent.py     # 心理咨询师
├── core/                      # 核心组件
│   ├── ai_client_factory.py   # AI客户端工厂
│   ├── simulation_engine.py   # 模拟引擎（支持心理模型）
│   ├── event_generator.py     # 事件生成器
│   └── therapy_session_manager.py # 咨询会话管理
├── models/                    # 数据模型与心理模型
│   ├── psychology_models.py   # 心理学数据模型
│   ├── psychological_model_base.py # 心理模型基类
│   ├── basic_rules_model.py   # 基础规则模型
│   ├── cad_enhanced_model.py  # CAD增强模型
│   ├── llm_driven_model.py    # LLM驱动模型
│   ├── hybrid_model.py        # 混合模型
│   ├── model_selector.py      # 模型选择器
│   └── cad_state_mapper.py    # CAD状态映射器
├── config/                    # 配置文件
│   ├── api_config.json        # AI API配置
│   ├── scenarios/             # 场景配置
│   └── psychological_model_config.json # 心理模型配置
├── logs/                      # 运行日志
│   └── sim_YYYYMMDD_HHMMSS/   # 模拟运行目录
├── utils/                     # 工具模块
├── web/                       # 网页界面（实验性）
├── main.py                    # 主程序入口
├── start_therapy_from_logs.py # 心理咨询程序
├── start_ai_to_ai_therapy.py  # AI咨询师程序
└── start_web.py               # 网页界面启动
```

## 🧪 使用示例

### 示例1：基础模拟
```bash
# 使用CAD模型进行30天抑郁症发展模拟
python main.py --model cad_enhanced

# 选择场景和AI提供商
# 观察详细的心理状态变化过程
# 查看生成的分析报告
```

### 示例2：心理咨询
```bash
# 完成模拟后，进行心理咨询
python start_therapy_from_logs.py

# 与虚拟患者对话
# 观察治疗效果和进展
# 查看CAD状态改善情况
```

### 示例3：模型对比
```bash
# 使用不同模型进行同一场景的模拟对比
python main.py --model basic_rules    # 快速模拟
python main.py --model cad_enhanced   # 科学模拟  
python main.py --model hybrid         # 智能模拟
```

## 🔬 技术特性

### 核心算法
- **CAD状态更新算法**: 基于认知-情感-抑郁理论的状态转换
- **混合模型融合**: 多模型加权平均与智能调度
- **自适应权重调整**: 基于模型性能的动态权重优化
- **一致性验证**: 多模型结果的一致性检查机制

### 性能优化
- **异步处理**: 支持并行模型计算
- **智能缓存**: LLM结果缓存机制
- **回退策略**: 多层次的错误恢复机制
- **资源管理**: 内存和计算资源的智能分配

### 扩展性设计
- **插件式架构**: 易于添加新的心理模型
- **配置驱动**: JSON配置文件支持快速场景定制
- **模块化组件**: 独立的功能模块便于维护
- **标准化接口**: 统一的模型和组件接口

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出改进建议！

### 添加新心理模型
1. 继承 `PsychologicalModelBase` 基类
2. 实现必要的方法接口
3. 在 `ModelFactory` 中注册新模型
4. 添加配置项和测试

### 添加新场景
1. 创建新的JSON配置文件
2. 定义角色、关系和事件模板
3. 添加场景特定的心理规则
4. 编写测试用例

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- **心理学理论支持**: Beck认知理论、CAD模型等
- **技术栈**: Python、Rich、Asyncio等
- **AI支持**: Google Gemini、DeepSeek等

## 📞 联系方式

- 项目主页: [GitHub Repository]
- 问题反馈: [Issues]
- 邮箱: [your-email@example.com]

---

**本项目仅用于研究和教育目的，不能替代专业的心理健康诊断和治疗。如需专业帮助，请咨询合格的心理健康专家。**