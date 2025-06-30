# 配置参数详细注释文档

本文档详细说明了`config/`目录下所有JSON配置文件中的参数含义和使用方法。

## 📋 目录

- [api_config.json - AI API配置](#api_configjson---ai-api配置)
- [simulation_params.json - 模拟基础参数](#simulation_paramsjson---模拟基础参数)
- [human_therapy_config.json - 人-AI治疗配置](#human_therapy_configjson---人-ai治疗配置)
- [ai_to_ai_therapy_config.json - AI-AI治疗配置](#ai_to_ai_therapy_configjson---ai-ai治疗配置)
- [therapy_guidance_config.json - 通用治疗配置](#therapy_guidance_configjson---通用治疗配置)
- [scenarios/default_adolescent.json - 场景配置](#scenariosdefault_adolescentjson---场景配置)

---

## api_config.json - AI API配置

### 基本结构
```json
{
  "description": "AI API服务配置文件",
  "default_provider": "deepseek",
  "providers": { ... }
}
```

### 参数说明

#### 顶级参数
- **`description`** (string): 配置文件描述信息
- **`default_provider`** (string): 默认使用的AI提供商
  - 可选值: `"deepseek"`, `"gemini"`, `"qwen"`
  - 系统启动时优先使用此提供商

#### providers 对象
每个AI提供商的配置结构：

##### DeepSeek配置 (`providers.deepseek`)
- **`api_key`** (string): DeepSeek API密钥
  - 从 https://platform.deepseek.com 获取
  - 必须设置有效值才能使用
- **`base_url`** (string): API基础URL
  - 默认: `"https://api.deepseek.com/v1"`
- **`model`** (string): 使用的模型名称
  - 默认: `"deepseek-chat"`
- **`max_tokens`** (integer): 单次请求最大令牌数
  - 范围: 1-8192，默认: 4096
- **`temperature`** (float): 生成文本的随机性
  - 范围: 0.0-2.0，默认: 0.7
  - 0.0 = 完全确定性，2.0 = 最大随机性
- **`enabled`** (boolean): 是否启用此提供商
  - `true`: 启用，`false`: 禁用

##### Gemini配置 (`providers.gemini`)
- **`api_key`** (string): Google Gemini API密钥
  - 从 https://makersuite.google.com 获取
- **`model`** (string): Gemini模型版本
  - 默认: `"gemini-1.5-flash"`
  - 可选: `"gemini-1.5-pro"`, `"gemini-1.0-pro"`
- **`max_tokens`** (integer): 最大输出令牌数
  - 默认: 4096
- **`temperature`** (float): 生成创造性
  - 默认: 0.7
- **`enabled`** (boolean): 启用状态

##### 通义千问配置 (`providers.qwen`)
- **`api_key`** (string): 阿里云通义千问API密钥
- **`model`** (string): 模型名称
  - 默认: `"qwen-turbo"`
- **其他参数**: 同上

---

## simulation_params.json - 模拟基础参数

### 基本结构
```json
{
  "description": "心理健康模拟基础参数配置",
  "simulation": { ... },
  "logging": { ... },
  "recovery": { ... }
}
```

### 参数说明

#### simulation 对象 - 模拟运行参数
- **`simulation_days`** (integer): 模拟总天数
  - 范围: 1-365，默认: 30
  - 影响模拟的时间跨度和发展阶段
- **`events_per_day`** (integer): 每日事件数量
  - 范围: 1-10，默认: 5
  - 控制每天发生的心理事件密度
- **`simulation_speed`** (integer): 模拟速度倍数
  - 范围: 1-10，默认: 1
  - 用于加速测试，数值越大越快
- **`depression_development_stages`** (integer): 抑郁发展阶段数
  - 范围: 3-10，默认: 5
  - 定义心理状态发展的阶段数量
- **`interaction_frequency`** (integer): 互动频率
  - 范围: 1-10，默认: 3
  - 控制角色间的互动密度

#### logging 对象 - 日志记录参数
- **`log_level`** (string): 日志级别
  - 可选值: `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`
  - 默认: `"INFO"`
- **`save_daily_states`** (boolean): 是否保存每日状态
  - `true`: 保存每日状态JSON文件
  - `false`: 仅保存最终报告
- **`enable_debug_mode`** (boolean): 调试模式
  - `true`: 启用详细调试信息
  - `false`: 标准模式

#### recovery 对象 - 恢复评估参数
- **`improvement_threshold`** (float): 改善阈值
  - 范围: 1.0-10.0，默认: 7.0
  - 用于判断治疗效果的门槛
- **`alliance_threshold`** (float): 治疗联盟阈值
  - 范围: 1.0-10.0，默认: 6.0
  - 评估治疗关系质量的标准
- **`evaluation_interval`** (integer): 评估间隔（天）
  - 范围: 1-30，默认: 5
  - 多久进行一次恢复状态评估
- **`deterioration_threshold`** (float): 恶化阈值
  - 范围: 1.0-10.0，默认: 3.0
  - 触发干预的恶化程度

---

## human_therapy_config.json - 人-AI治疗配置

### 基本结构
```json
{
  "description": "人-AI对话治疗专用配置",
  "therapy_effectiveness": { ... },
  "cad_state_changes": { ... },
  "conversation_settings": { ... },
  "supervision_settings": { ... }
}
```

### 参数说明

#### therapy_effectiveness 对象 - 治疗有效性参数
- **`base_improvement_factor`** (float): 基础改善因子
  - 范围: 0.1-1.0，默认: 0.6
  - 每轮治疗的基础改善程度
- **`max_improvement_per_turn`** (float): 单轮最大改善
  - 范围: 0.1-2.0，默认: 1.0
  - 防止过度乐观的改善速度
- **`min_improvement_per_turn`** (float): 单轮最小改善
  - 范围: 0.0-1.0，默认: 0.2
  - 确保最小治疗效果
- **`technique_weight`** (float): 技术权重
  - 范围: 0.0-1.0，默认: 0.5
  - 治疗技术对效果的影响程度
- **`openness_weight`** (float): 开放度权重
  - 范围: 0.0-1.0，默认: 0.3
  - 患者开放程度的影响
- **`connection_weight`** (float): 连接权重
  - 范围: 0.0-1.0，默认: 0.2
  - 治疗关系对效果的影响

#### cad_state_changes 对象 - CAD状态变化参数

##### core_beliefs 子对象 - 核心信念变化
- **`self_belief_change_rate`** (float): 自我信念变化率
  - 范围: 0.01-1.0，默认: 0.18
  - 控制自我信念的改变速度
- **`world_belief_change_rate`** (float): 世界观信念变化率
  - 范围: 0.01-1.0，默认: 0.15
- **`future_belief_change_rate`** (float): 未来信念变化率
  - 范围: 0.01-1.0，默认: 0.22
- **`stability_factor`** (float): 稳定性因子
  - 范围: 0.1-1.0，默认: 0.80
  - 信念系统的稳定性，越高越难改变

##### cognitive_processing 子对象 - 认知处理变化
- **`rumination_reduction_rate`** (float): 反刍思维减少率
  - 范围: 0.01-1.0，默认: 0.25
- **`distortions_reduction_rate`** (float): 认知扭曲减少率
  - 范围: 0.01-1.0，默认: 0.20
- **`positive_reframe_bonus`** (float): 积极重构奖励
  - 范围: 0.01-1.0，默认: 0.15

##### behavioral_patterns 子对象 - 行为模式变化
- **`social_withdrawal_change_rate`** (float): 社交退缩变化率
  - 范围: 0.01-1.0，默认: 0.18
- **`avolition_change_rate`** (float): 意志缺失变化率
  - 范围: 0.01-1.0，默认: 0.20
- **`activity_engagement_bonus`** (float): 活动参与奖励
  - 范围: 0.01-1.0，默认: 0.12

#### conversation_settings 对象 - 对话设置
- **`conversation_history_length`** (integer): 对话历史长度
  - 范围: 5-100，默认: 20
  - 系统记忆的对话轮数
- **`max_events_to_show`** (integer): 最大显示事件数
  - 范围: 5-50，默认: 20
  - 在治疗中展示的关键事件数量
- **`response_timeout`** (integer): 响应超时（秒）
  - 范围: 10-300，默认: 60
- **`auto_save_interval`** (integer): 自动保存间隔（轮）
  - 范围: 1-20，默认: 5

#### supervision_settings 对象 - 督导设置
- **`enable_supervision`** (boolean): 启用督导
  - `true`: 启用AI督导功能
  - `false`: 禁用督导
- **`supervision_interval`** (integer): 督导间隔（轮）
  - 范围: 1-20，默认: 5
  - 每隔几轮进行一次督导分析
- **`supervision_analysis_depth`** (string): 督导分析深度
  - 可选值: `"BASIC"`, `"COMPREHENSIVE"`, `"DETAILED"`
  - 默认: `"COMPREHENSIVE"`
- **`supervision_feedback_level`** (string): 督导反馈级别
  - 可选值: `"MINIMAL"`, `"MODERATE"`, `"EXTENSIVE"`

---

## ai_to_ai_therapy_config.json - AI-AI治疗配置

### 结构与参数

与`human_therapy_config.json`结构相似，但参数值针对AI自动化治疗进行了优化：

#### 主要差异
- **治疗有效性参数更保守**: 避免AI过度乐观
  - `base_improvement_factor`: 0.4 (vs 0.6)
  - `max_improvement_per_turn`: 0.6 (vs 1.0)
- **CAD状态变化更缓慢**: 模拟真实治疗的渐进性
  - 所有变化率降低20-30%
- **对话设置更自动化**:
  - `max_turns`: 15 (AI专用参数)
  - `auto_progress_tracking`: true

---

## therapy_guidance_config.json - 通用治疗配置

### 作用
为了向后兼容而保留的通用治疗配置文件。新系统优先使用专用的人-AI或AI-AI配置文件。

### 参数
包含两套配置的通用版本，参数含义与专用配置文件相同。

---

## scenarios/default_adolescent.json - 场景配置

### 基本结构
```json
{
  "name": "青少年抑郁发展模拟",
  "description": "模拟17岁高中生的抑郁症发展过程",
  "characters": { ... },
  "relationships": [ ... ],
  "stage_config": { ... },
  "event_templates": { ... },
  "conditional_events": { ... },
  "cad_impact_rules": { ... }
}
```

### 参数说明

#### 顶级参数
- **`name`** (string): 场景名称
- **`description`** (string): 场景详细描述
- **`target_age_group`** (string): 目标年龄组
- **`estimated_duration`** (string): 预估时长

#### characters 对象 - 角色配置
每个角色的配置结构：
```json
"protagonist": {
  "name": "钟林",
  "age": 17,
  "type": "StudentAgent",
  "personality": { ... },
  "background": { ... }
}
```

##### 角色通用参数
- **`name`** (string): 角色姓名
- **`age`** (integer): 年龄
- **`type`** (string): Agent类型
  - 可选: `"StudentAgent"`, `"FatherAgent"`, `"MotherAgent"`, `"TeacherAgent"`, `"ClassmateAgent"`, `"BestFriendAgent"`

##### personality 子对象 - 性格配置
- **`traits`** (array): 性格特征列表
- **`stress_threshold`** (integer): 压力阈值 (1-10)
- **`resilience_level`** (integer): 抗压能力 (1-10)
- **`social_tendency`** (string): 社交倾向
  - 可选: `"内向"`, `"外向"`, `"适中"`

##### background 子对象 - 背景信息
- **`family_environment`** (string): 家庭环境描述
- **`academic_pressure`** (integer): 学业压力 (1-10)
- **`social_status`** (string): 社会地位
- **`previous_trauma`** (array): 既往创伤列表

#### relationships 数组 - 关系配置
每个关系的配置：
```json
{
  "person_a": "钟林",
  "person_b": "钟父",
  "type": "父子关系",
  "closeness": 6,
  "trust_level": 7,
  "conflict_frequency": 3
}
```

##### 关系参数
- **`person_a`**, **`person_b`** (string): 关系双方的姓名
- **`type`** (string): 关系类型
- **`closeness`** (integer): 亲密度 (1-10)
- **`trust_level`** (integer): 信任度 (1-10)
- **`conflict_frequency`** (integer): 冲突频率 (1-10)

#### stage_config 对象 - 阶段配置
每个发展阶段的配置：
```json
"健康阶段": {
  "duration_days": 5,
  "event_weights": { ... },
  "event_categories": [ ... ],
  "stress_modifier": 1.0,
  "relationship_decay": 1.0
}
```

##### 阶段参数
- **`duration_days`** (integer): 阶段持续天数
- **`event_weights`** (object): 事件情感权重
  - `"positive"`: 积极事件权重
  - `"neutral"`: 中性事件权重  
  - `"negative"`: 消极事件权重
- **`event_categories`** (array): 事件类别列表
- **`stress_modifier`** (float): 压力修正系数
- **`relationship_decay`** (float): 关系衰减系数

#### event_templates 对象 - 事件模板
不同类别和情感的事件模板：
```json
"academic": {
  "positive": [ "考试成绩优异", "得到老师表扬" ],
  "neutral": [ "普通的课堂学习", "完成日常作业" ],
  "negative": [ "考试失利", "作业质量差" ]
}
```

#### conditional_events 对象 - 条件事件
基于角色状态触发的特殊事件：
```json
"severe_depression_trigger": {
  "condition": "depression_level > 7 and social_connection < 3",
  "events": [ ... ],
  "probability": 0.3
}
```

#### cad_impact_rules 对象 - CAD影响规则
定义事件对CAD状态的影响规则：
```json
"academic_failure": {
  "self_belief_impact": -0.8,
  "future_belief_impact": -0.6,
  "rumination_increase": 0.5
}
```

---

## 🔧 配置使用建议

### 开发环境配置
- 设置较小的`simulation_days` (2-5天) 用于快速测试
- 启用`enable_debug_mode` 获取详细调试信息
- 使用较高的`simulation_speed` 加速开发

### 生产环境配置
- 使用完整的`simulation_days` (30天) 获得完整体验
- 禁用调试模式以提高性能
- 设置适当的API调用限制

### 治疗配置优化
- 根据患者类型调整`therapy_effectiveness`参数
- 为不同严重程度设置不同的`cad_state_changes`参数
- 调整`supervision_interval`平衡质量和效率

### 场景定制
- 根据研究目标修改`characters`和`relationships`
- 调整`stage_config`控制发展速度
- 添加特定的`conditional_events`模拟关键情况

---

## ⚠️ 重要注意事项

1. **API密钥安全**: 
   - 不要将包含真实API密钥的配置文件提交到版本控制
   - 使用环境变量或密钥管理服务

2. **参数范围**: 
   - 严格遵守文档中的参数范围
   - 超出范围可能导致意外行为

3. **配置一致性**: 
   - 确保相关配置文件之间的参数一致性
   - 特别注意治疗配置与场景配置的匹配

4. **性能考虑**: 
   - 较高的`events_per_day`和较低的`supervision_interval`会增加API调用频率
   - 根据API配额调整相关参数

5. **实验重现**: 
   - 记录用于重要实验的配置版本
   - 使用版本控制管理配置变化 