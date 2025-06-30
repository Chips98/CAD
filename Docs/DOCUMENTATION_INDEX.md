# 青少年抑郁症模拟器文档索引

## 📋 文档导航

欢迎使用青少年抑郁症模拟器！本项目提供了完整的文档体系，请根据您的角色和需求选择合适的阅读路径。

## 🎯 根据用户类型选择阅读路径

### 👨‍🎓 初次使用者
**建议阅读顺序**：
1. [README.md](README.md) - 了解项目概述和快速开始
2. [USER_GUIDE.md](USER_GUIDE.md) - 详细使用指南
3. 实际操作练习

**重点关注**：
- 环境配置
- API密钥设置
- 基本功能使用

### 👨‍🏫 教育工作者
**建议阅读顺序**：
1. [SYSTEM_ANALYSIS.md](SYSTEM_ANALYSIS.md) - 理解系统架构和心理学基础
2. [USER_GUIDE.md](USER_GUIDE.md) - 掌握操作方法
3. [USER_GUIDE.md#最佳实践](USER_GUIDE.md#最佳实践) - 教学应用指导

**重点关注**：
- 心理学模型
- 配置自定义
- 教学应用最佳实践
- 数据分析方法

### 👨‍💻 开发者
**建议阅读顺序**：
1. [SYSTEM_ANALYSIS.md](SYSTEM_ANALYSIS.md) - 深入理解系统架构
2. 代码文件结构分析
3. [USER_GUIDE.md#配置自定义](USER_GUIDE.md#配置自定义) - 扩展开发

**重点关注**：
- 模块化设计
- AI集成架构
- 扩展接口
- 性能优化

### 👨‍⚕️ 心理健康专业人士
**建议阅读顺序**：
1. [SYSTEM_ANALYSIS.md#心理学模型](SYSTEM_ANALYSIS.md#心理学模型) - 了解理论基础
2. [USER_GUIDE.md#咨询对话最佳实践](USER_GUIDE.md#咨询对话最佳实践) - 专业应用指导
3. 实际咨询功能体验

**重点关注**：
- 抑郁症发展阶段
- 心理状态建模
- 咨询技巧和策略
- 治疗效果评估

### 🔬 研究人员
**建议阅读顺序**：
1. [SYSTEM_ANALYSIS.md](SYSTEM_ANALYSIS.md) - 全面了解系统设计
2. [USER_GUIDE.md#数据分析](USER_GUIDE.md#数据分析) - 数据获取和分析方法
3. 数据文件格式说明

**重点关注**：
- 数据收集机制
- 实验设计方法
- 结果分析工具
- 研究应用价值

## 📁 文档文件说明

### 核心文档

#### [README.md](README.md)
- **内容**：项目概述、功能介绍、快速开始指南
- **适合**：所有用户的入门必读
- **长度**：中等（约266行）

#### [SYSTEM_ANALYSIS.md](SYSTEM_ANALYSIS.md)
- **内容**：深入的系统架构分析、技术实现详解
- **适合**：开发者、研究人员、深度用户
- **长度**：长篇（详细技术文档）

#### [USER_GUIDE.md](USER_GUIDE.md)
- **内容**：完整的使用指南、配置说明、最佳实践
- **适合**：所有用户的操作手册
- **长度**：长篇（全面使用指南）

#### [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
- **内容**：文档导航和阅读建议
- **适合**：帮助用户快速找到所需信息
- **长度**：中等（导航文档）

### 配置文件

#### [config.py](config.py)
- **内容**：系统参数配置
- **说明**：API密钥、模拟参数、咨询参数设置

#### [sim_config/simulation_config.py](sim_config/simulation_config.py)
- **内容**：默认角色和场景配置
- **说明**：角色性格、关系网络、事件模板定义

#### [sim_config/example_custom_config.py](sim_config/example_custom_config.py)
- **内容**：自定义配置示例
- **说明**：展示如何创建自定义场景

## 🎯 按功能查找信息

### 环境配置
- [USER_GUIDE.md#环境配置](USER_GUIDE.md#环境配置)
- [README.md#配置API密钥](README.md#配置api密钥)

### 基础使用
- [USER_GUIDE.md#功能详解](USER_GUIDE.md#功能详解)
- [README.md#使用方式](README.md#使用方式)

### 高级定制
- [USER_GUIDE.md#配置自定义](USER_GUIDE.md#配置自定义)
- [SYSTEM_ANALYSIS.md#配置系统](SYSTEM_ANALYSIS.md#配置系统)

### 技术原理
- [SYSTEM_ANALYSIS.md#系统架构](SYSTEM_ANALYSIS.md#系统架构)
- [SYSTEM_ANALYSIS.md#AI集成架构](SYSTEM_ANALYSIS.md#ai集成架构)

### 数据分析
- [USER_GUIDE.md#数据分析](USER_GUIDE.md#数据分析)
- [SYSTEM_ANALYSIS.md#数据管理](SYSTEM_ANALYSIS.md#数据管理)

### 问题解决
- [USER_GUIDE.md#常见问题](USER_GUIDE.md#常见问题)
- [USER_GUIDE.md#最佳实践](USER_GUIDE.md#最佳实践)

## 🔧 代码文件结构导览

```
Adolescent-Depression-Simulator/
├── main.py                          # 主程序入口
├── start_therapy_from_logs.py       # 心理咨询启动程序
├── config.py                        # 系统配置文件
├── 
├── core/                            # 核心模块
│   ├── simulation_engine.py        # 模拟引擎
│   ├── event_generator.py          # 事件生成器  
│   ├── therapy_session_manager.py  # 心理咨询管理器
│   ├── ai_client_factory.py        # AI客户端工厂
│   ├── gemini_client.py            # Gemini客户端
│   └── deepseek_client.py          # DeepSeek客户端
│
├── agents/                          # 智能体系统
│   ├── base_agent.py               # 基础智能体类
│   ├── student_agent.py            # 学生智能体（主角）
│   ├── family_agents.py            # 家庭成员智能体
│   ├── school_agents.py            # 学校相关智能体
│   └── therapist_agent.py          # 心理咨询师智能体
│
├── models/                          # 数据模型
│   └── psychology_models.py        # 心理学模型定义
│
├── sim_config/                      # 配置文件目录
│   ├── simulation_config.py        # 默认模拟配置
│   ├── example_custom_config.py    # 自定义配置示例
│   └── enhanced_config_example.py  # 增强配置示例
│
└── logs/                            # 输出日志目录
    └── sim_YYYYMMDD_HHMMSS/        # 模拟运行记录
        ├── final_report.json       # 最终报告
        ├── simulation.log          # 执行日志
        ├── day_X_state.json        # 每日状态
        └── therapy_session_*.json  # 咨询记录
```

## 📊 核心概念速查

### 抑郁症发展阶段
1. **健康阶段** - 正常青少年生活
2. **压力积累** - 学业和社交压力增加  
3. **初期问题** - 明显情绪和行为变化
4. **关系恶化** - 人际关系受损
5. **抑郁发展** - 严重症状需要干预

### 智能体角色
- **李明** (StudentAgent) - 主角，经历抑郁发展
- **李建国** (FatherAgent) - 父亲，严厉型教育
- **王秀芳** (MotherAgent) - 母亲，焦虑型关爱
- **张老师** (TeacherAgent) - 数学老师
- **王小明** (BestFriendAgent) - 好友
- **刘强** (BullyAgent) - 霸凌者
- **陈优秀** (ClassmateAgent) - 竞争对手

### 心理状态维度
- **情绪状态** (EmotionState) - 当前情绪
- **抑郁程度** (DepressionLevel) - 0-4级
- **压力水平** (stress_level) - 0-10分
- **自尊水平** (self_esteem) - 0-10分
- **社交连接** (social_connection) - 0-10分
- **学业压力** (academic_pressure) - 0-10分

### 事件类型
- **学业事件** (academic) - 考试、作业、课堂
- **社交事件** (social) - 朋友、霸凌、同伴
- **家庭事件** (family) - 亲子、家庭氛围
- **个人事件** (personal) - 内心、个人活动

## 🆘 获取帮助

### 技术支持
- **GitHub Issues**: [项目Issues页面](https://github.com/Benioh/Adolescent-Depression-Simulator/issues)
- **文档问题**: 查看文档中的常见问题部分
- **配置问题**: 参考USER_GUIDE.md中的配置说明

### 贡献指南
- **Bug报告**: 请提供详细的错误日志和复现步骤
- **功能建议**: 欢迎提出改进建议和新功能需求
- **文档改进**: 帮助完善文档内容和翻译

### 学术合作
- **研究合作**: 欢迎心理学和计算机科学领域的研究合作
- **教学应用**: 支持教育机构的教学应用需求
- **数据共享**: 在合规前提下可协商数据共享事宜

## 📈 版本信息

- **当前版本**: v1.0
- **更新日期**: 2024年1月
- **兼容性**: Python 3.8+
- **依赖**: Rich, AsyncIO, JSON

## 📝 文档维护

本文档索引会随项目更新而同步更新。如发现文档过时或错误，请及时反馈。

**最后更新**: 2024年1月  
**维护者**: 项目开发团队 