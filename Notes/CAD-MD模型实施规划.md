# CAD-MD模型实施规划 (Cognitive-Affective Dynamics Model of Depression)

## 📋 项目现状分析

### 当前系统优势
1. **完善的双阶段架构**：模拟阶段 + 咨询阶段的设计理念很好
2. **多AI提供商支持**：Gemini和DeepSeek的兼容性
3. **基础心理状态建模**：已有PsychologicalState基础框架
4. **完整的事件驱动机制**：BaseAgent._process_event_impact已实现基础逻辑
5. **恢复机制框架**：TherapySessionManager已有治疗效果评估

### 当前系统局限
1. **心理模型深度不足**：仅有6个维度的基础状态，缺乏认知层面的细致建模
2. **事件影响过于简化**：主要基于impact_score的线性计算，缺乏内在认知动力学
3. **对话质量有限**：AI角色回应缺乏深层心理状态的支撑
4. **治疗机制不够专业**：缺乏基于认知行为疗法的科学干预逻辑

## 🎯 CAD-MD模型目标

### 核心理念
将现有的"事件驱动行为模拟"与"内在认知动力学建模"深度融合，实现从"是什么"到"为什么"的跨越。

### 五大维度构成
1. **情感基调 (Affective Tone)**：个体长期稳定的情感背景
2. **核心信念 (Core Beliefs)**：贝克认知三角 - 自我/世界/未来信念
3. **认知加工 (Cognitive Processing)**：思维反刍 + 认知扭曲
4. **情绪状态 (Emotional State)**：即时情感反应（保留现有）
5. **行为倾向 (Behavioral Inclination)**：社交退缩 + 动机降低

## 📋 三阶段实施方案

## 阶段一：奠定数据与状态基础 (Foundation)

### 1.1 扩展心理模型数据结构

**目标文件**：`models/psychology_models.py`

**任务1.1.1：新增CAD-MD核心数据类**
```python
@dataclass
class CoreBeliefs:
    """核心信念 - 贝克认知三角"""
    self_belief: float = 0.0      # 自我信念 (-10: 极负面, 10: 极正面)
    world_belief: float = 0.0     # 世界信念 (-10 to 10)
    future_belief: float = 0.0    # 未来信念 (-10 to 10)
    
    def to_dict(self): 
        return self.__dict__
    
    def get_textual_representation(self) -> Dict[str, str]:
        """转换为文本描述"""
        return {
            "self_belief": self._belief_to_text(self.self_belief, "self"),
            "world_belief": self._belief_to_text(self.world_belief, "world"),
            "future_belief": self._belief_to_text(self.future_belief, "future")
        }
    
    def _belief_to_text(self, score: float, belief_type: str) -> str:
        # 实现分数到文本的映射逻辑
        pass

@dataclass  
class CognitiveProcessing:
    """认知加工方式"""
    rumination: float = 0.0       # 负性思维反刍 (0: 无, 10: 严重)
    distortions: float = 0.0      # 认知扭曲程度 (0: 无, 10: 严重)
    
    def to_dict(self): 
        return self.__dict__

@dataclass
class BehavioralInclination:
    """行为倾向"""
    social_withdrawal: float = 0.0 # 社交退缩 (0: 无, 10: 严重)
    avolition: float = 0.0         # 动机降低/快感缺失 (0: 无, 10: 严重)
    
    def to_dict(self): 
        return self.__dict__

@dataclass
class CognitiveAffectiveState:
    """完整的认知-情感动力学状态"""
    affective_tone: float = 0.0    # 情感基调 (-10: 悲观, 10: 乐观)
    core_beliefs: CoreBeliefs = field(default_factory=CoreBeliefs)
    cognitive_processing: CognitiveProcessing = field(default_factory=CognitiveProcessing)
    behavioral_inclination: BehavioralInclination = field(default_factory=BehavioralInclination)
    
    def to_dict(self):
        return {
            "affective_tone": self.affective_tone,
            "core_beliefs": self.core_beliefs.to_dict(),
            "cognitive_processing": self.cognitive_processing.to_dict(),
            "behavioral_inclination": self.behavioral_inclination.to_dict()
        }
    
    def get_comprehensive_analysis(self) -> str:
        """生成用于AI prompt的综合分析"""
        # 实现详细的状态分析文本生成
        pass
```

**任务1.1.2：整合到PsychologicalState**
```python
@dataclass
class PsychologicalState:
    """心理状态 - 整合版"""
    # 原有字段保持不变
    emotion: EmotionState
    depression_level: DepressionLevel
    stress_level: int  # 0-10
    self_esteem: int   # 0-10
    social_connection: int  # 0-10
    academic_pressure: int  # 0-10
    
    # 新增CAD-MD深度建模
    cad_state: CognitiveAffectiveState = field(default_factory=CognitiveAffectiveState)
    
    def to_dict(self) -> Dict:
        base_dict = {
            "emotion": self.emotion.value,
            "depression_level": self.depression_level.value,
            "stress_level": self.stress_level,
            "self_esteem": self.self_esteem,
            "social_connection": self.social_connection,
            "academic_pressure": self.academic_pressure
        }
        base_dict.update({"cad_state": self.cad_state.to_dict()})
        return base_dict
```

### 1.2 创建状态映射工具

**新文件**：`models/cad_state_mapper.py`

**功能**：
- 分数到文本标签的映射
- 综合状态分析生成
- 为AI prompt提供可读性描述

## 阶段二：实现模拟阶段的动态演化逻辑 (Dynamics)

### 2.1 规则驱动更新引擎

**目标文件**：`agents/base_agent.py`

**任务2.1.1：核心更新方法**
```python
def _update_cad_state_by_rules(self, event: LifeEvent):
    """根据CAD-MD模型规则更新认知-情感状态"""
    cad = self.psychological_state.cad_state
    
    # === 外部事件的直接影响 ===
    if event.impact_score < 0:
        # 情感基调受影响（缓慢变化）
        cad.affective_tone = max(-10, cad.affective_tone + event.impact_score / 10.0)
        
        # 根据事件类型精准影响核心信念
        if "批评" in event.description or "失败" in event.description:
            cad.core_beliefs.self_belief += event.impact_score * 0.5
        if "孤立" in event.description or "霸凌" in event.description:
            cad.core_beliefs.world_belief += event.impact_score * 0.6
    
    # === 情感基调的放大效应 ===
    impact_modifier = 1.5 if cad.affective_tone < 0 else 0.8
    
    # === 核心信念驱动认知加工和行为 ===
    # 自我信念 -> 思维反刍
    if cad.core_beliefs.self_belief < -3:
        cad.cognitive_processing.rumination += (-cad.core_beliefs.self_belief / 5.0)
    
    # 世界信念 -> 社交退缩
    if cad.core_beliefs.world_belief < -3:
        cad.behavioral_inclination.social_withdrawal += (-cad.core_beliefs.world_belief / 4.0)
    
    # 未来信念综合计算
    cad.core_beliefs.future_belief = (cad.core_beliefs.self_belief + cad.core_beliefs.world_belief) / 2.0
    
    # === 认知-情绪相互作用 ===
    # 思维反刍 -> 负面情绪
    if cad.cognitive_processing.rumination > 6:
        self.psychological_state.emotion = EmotionState.ANXIOUS
    
    # 情绪 -> 加剧反刍（情绪惯性）
    if self.psychological_state.emotion in [EmotionState.SAD, EmotionState.DEPRESSED]:
        cad.cognitive_processing.rumination += 0.5
    
    # === 值域限制 ===
    self._clamp_cad_values()

def _perform_daily_cad_evolution(self):
    """每日CAD状态的自然演化"""
    cad = self.psychological_state.cad_state
    
    # 行为的长期反馈循环
    if cad.behavioral_inclination.social_withdrawal > 5:
        cad.core_beliefs.self_belief -= 0.1   # 社交退缩减少积极反馈
        cad.core_beliefs.world_belief -= 0.1
    
    # 状态的自然衰减
    cad.cognitive_processing.rumination *= 0.95  # 反刍每日衰减5%
    cad.affective_tone *= 0.98  # 情感基调向中性回归

def _clamp_cad_values(self):
    """限制CAD状态值在合理范围内"""
    cad = self.psychological_state.cad_state
    # 实现所有字段的值域限制
```

**任务2.1.2：接入现有事件流**
- 在`_process_event_impact`方法末尾调用`_update_cad_state_by_rules(event)`
- 确保每个事件都会触发CAD状态更新

### 2.2 模拟引擎集成

**目标文件**：`core/simulation_engine.py`

**任务2.2.1：每日演化调用**
- 在`_simulate_day`方法中调用`_perform_daily_cad_evolution()`
- 确保CAD状态每日都有自然演化

**任务2.2.2：状态日志增强**
- 修改`_get_protagonist_state`，将CAD状态"拍平"到字典中
- 支持条件事件访问新的认知维度

## 阶段三：升华对话引导阶段的应用 (Enhancement)

### 3.1 深度感知的AI主角

**目标文件**：`core/therapy_session_manager.py`

**任务3.1.1：创建状态分析工具**
```python
def _generate_cognitive_state_analysis(self, patient_data: Dict) -> str:
    """生成深度认知状态分析"""
    cad_state = patient_data.get('cad_state', {})
    
    # 从CAD状态生成心理学专业描述
    analysis = f"""
    === 深度认知状态分析 ===
    
    情感基调: {self._describe_affective_tone(cad_state.get('affective_tone', 0))}
    
    核心信念系统 (贝克认知三角):
    - 自我信念: {self._describe_self_belief(cad_state.get('core_beliefs', {}).get('self_belief', 0))}
    - 世界信念: {self._describe_world_belief(cad_state.get('core_beliefs', {}).get('world_belief', 0))}
    - 未来信念: {self._describe_future_belief(cad_state.get('core_beliefs', {}).get('future_belief', 0))}
    
    认知加工模式:
    - 思维反刍程度: {self._describe_rumination(cad_state.get('cognitive_processing', {}).get('rumination', 0))}
    - 认知扭曲程度: {self._describe_distortions(cad_state.get('cognitive_processing', {}).get('distortions', 0))}
    
    行为倾向:
    - 社交退缩: {self._describe_social_withdrawal(cad_state.get('behavioral_inclination', {}).get('social_withdrawal', 0))}
    - 动机降低: {self._describe_avolition(cad_state.get('behavioral_inclination', {}).get('avolition', 0))}
    """
    return analysis
```

**任务3.1.2：增强患者回应生成**
- 修改`_generate_prompt_for_patient`，注入详细的认知状态分析
- 要求AI基于深层认知状态进行角色扮演

### 3.2 专业督导增强

**目标文件**：`agents/therapist_agent.py`

**任务3.2.1：认知导向督导**
```python
async def provide_cad_based_supervision(self, patient_cad_state: Dict, 
                                      recent_dialogue: List[Dict]) -> Dict:
    """基于CAD模型的专业督导"""
    
    prompt = f"""
    作为专业心理督导，请基于患者的深层认知状态提供督导建议。
    
    患者CAD状态:
    {self._format_cad_state_for_supervision(patient_cad_state)}
    
    最近对话记录:
    {self._format_dialogue_for_supervision(recent_dialogue)}
    
    请从以下角度进行专业督导:
    1. 认知干预策略: 针对患者的核心信念，治疗师应采用何种CBT技术？
    2. 反刍处理: 如何帮助患者打破负性思维反刍循环？
    3. 行为激活: 针对社交退缩和动机降低，建议具体的行为干预？
    4. 治疗时机: 当前阶段最适合的治疗重点是什么？
    5. 风险评估: 基于认知状态，需要关注哪些风险指标？
    
    返回JSON格式的督导报告。
    """
    # 实现督导逻辑
```

### 3.3 认知康复机制

**目标文件**：`core/therapy_session_manager.py`

**任务3.3.1：基于认知的恢复评估**
```python
def _evaluate_cognitive_recovery_progress(self, recent_effectiveness_scores: List[float]) -> Dict:
    """基于CAD模型评估认知康复进展"""
    
    current_cad = self.patient_data.get('cad_state', {})
    
    # 认知改善指标
    self_belief_improvement = self._calculate_belief_improvement('self_belief')
    rumination_reduction = self._calculate_rumination_reduction()
    social_engagement_increase = self._calculate_social_engagement_increase()
    
    # 康复条件判断
    recovery_conditions = {
        'core_beliefs_improved': self_belief_improvement > 1.0 and 
                                current_cad.get('core_beliefs', {}).get('self_belief', -10) > -2.0,
        'rumination_controlled': current_cad.get('cognitive_processing', {}).get('rumination', 10) < 4.0,
        'behavioral_activation': current_cad.get('behavioral_inclination', {}).get('social_withdrawal', 10) < 5.0,
        'therapeutic_alliance_strong': self.therapeutic_alliance_score >= 6.0,
        'consistent_effectiveness': sum(recent_effectiveness_scores) / len(recent_effectiveness_scores) >= 7.0
    }
    
    return {
        'ready_for_improvement': all(recovery_conditions.values()),
        'improvement_factors': recovery_conditions,
        'recommended_next_steps': self._generate_recovery_recommendations(recovery_conditions)
    }
```

## 📅 实施时间线

### 第1周：阶段一实施
- **Day 1-2**: 实施任务1.1（数据结构扩展）
- **Day 3-4**: 实施任务1.2（状态映射工具）
- **Day 5**: 测试与调试阶段一功能

### 第2周：阶段二实施  
- **Day 1-3**: 实施任务2.1（规则驱动更新引擎）
- **Day 4-5**: 实施任务2.2（模拟引擎集成）
- **Day 6-7**: 完整模拟流程测试

### 第3周：阶段三实施
- **Day 1-2**: 实施任务3.1（深度AI主角）
- **Day 3-4**: 实施任务3.2（专业督导）
- **Day 5-6**: 实施任务3.3（认知康复机制）
- **Day 7**: 整体系统测试与优化

## 🧪 测试与验证策略

### 单元测试
- CAD状态更新逻辑测试
- 边界值和异常情况处理
- 状态映射功能验证

### 集成测试
- 完整30天模拟测试
- 不同事件类型的影响验证
- 咨询对话质量评估

### 用户验证
- 心理学专家评审
- 系统可用性测试
- 对话真实感验证

## 📊 成功指标

### 技术指标
- [ ] CAD-MD模型完整集成
- [ ] 认知状态动态演化正常
- [ ] AI对话质量显著提升
- [ ] 恢复机制基于认知指标

### 功能指标
- [ ] 模拟过程体现认知动力学
- [ ] 督导建议专业且针对性强
- [ ] 康复过程符合心理学理论
- [ ] 日志记录包含完整认知数据

### 用户体验指标
- [ ] 对话更加真实可信
- [ ] 督导建议实用性强
- [ ] 系统整体流畅性保持
- [ ] 专业人士认可度高

## ⚠️ 风险与缓解策略

### 技术风险
- **复杂度增加**：采用模块化设计，渐进式实施
- **性能影响**：优化计算逻辑，避免过度复杂的规则
- **兼容性问题**：保持向后兼容，新功能可选开启

### 内容风险
- **心理学准确性**：邀请专业人士审核模型
- **过度拟人化**：明确系统局限性，添加免责声明
- **治疗效果夸大**：强调系统的教育和研究用途

## 🎯 预期成果

完成后的系统将具备：
1. **深度心理建模**：基于贝克认知理论的科学建模
2. **动态认知演化**：真实的内在心理动力学模拟
3. **专业治疗支持**：基于CBT的督导和康复机制
4. **高质量对话**：基于深层认知状态的AI角色扮演

这将使ADS系统从一个"行为模拟器"升级为一个真正的"认知动力学平台"，为心理健康教育、研究和训练提供更专业、更深入的工具支持。 