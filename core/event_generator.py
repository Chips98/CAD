"""
动态事件生成器 - 基于模板分析和智能发散 + LLM增强
根据现有事件模板和人物信息，生成符合逻辑的新事件
集成LLM事件生成器和混合影响计算器
"""

import random
import re
import json
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
import logging

from models.psychology_models import LifeEvent, EventType
from core.llm_event_generator import LLMEventGenerator
from core.hybrid_impact_calculator import HybridImpactCalculator
from core.probabilistic_impact import ProbabilisticImpactModel

class EventGenerator:
    """智能事件生成器 - 基于模板分析和发散生成"""
    
    def __init__(self, ai_client, event_templates: Dict, character_mapping: Dict, config=None):
        self.ai_client = ai_client
        self.event_templates = event_templates
        self.character_mapping = character_mapping
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.event_history = []
        
        # 加载LLM增强配置
        self.llm_config = self._load_llm_config()
        
        # LLM增强组件
        self.llm_event_generator = None
        self.hybrid_calculator = None
        self.probabilistic_model = None
        
        if self.ai_client and self.llm_config.get("llm_integration", {}).get("event_generation", {}).get("enabled", False):
            self.llm_event_generator = LLMEventGenerator(ai_client)
            self.hybrid_calculator = HybridImpactCalculator(ai_client, self.llm_config.get("hybrid_calculation", {}))
            
        if self.llm_config.get("probabilistic_modeling", {}).get("enabled", False):
            self.probabilistic_model = ProbabilisticImpactModel(self.llm_config.get("probabilistic_modeling", {}))
        
        # 原有的分析模板和构建智能生成系统
        self.template_analyzer = TemplateAnalyzer(event_templates, character_mapping)
        self.context_extractor = ContextExtractor(config, character_mapping)
        self.logic_validator = LogicValidator(config)
        self.divergent_generator = DivergentGenerator(ai_client)
        
        # 初始化分析结果
        self.template_patterns = self.template_analyzer.analyze_patterns()
        self.character_context = self.context_extractor.extract_context()
        self.generation_rules = self._build_generation_rules()
        
        self.logger.info(f"增强事件生成器初始化完成，LLM增强: {'启用' if self.llm_event_generator else '禁用'}")
    
    def _load_llm_config(self) -> Dict:
        """加载LLM增强配置"""
        try:
            config_path = "/Users/zl_24/Documents/Codes/2025/2025-07/CAD-main/config/llm_enhancement_config.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"加载LLM配置失败: {e}")
            return {}
    
    def _build_generation_rules(self) -> Dict[str, Any]:
        """构建事件生成规则"""
        protagonist_age = self.character_context.get("protagonist_age", 17)
        life_stage = self.character_context.get("life_stage", "高中生")
        
        rules = {
            "age_appropriate_activities": self._get_age_appropriate_activities(protagonist_age),
            "valid_relationships": self._get_valid_relationships(),
            "emotional_patterns": self._analyze_emotional_patterns(),
            "activity_constraints": self._build_activity_constraints(life_stage),
            "character_interactions": self._map_character_interactions()
        }
        
        return rules
    
    def _get_age_appropriate_activities(self, age: int) -> Dict[str, List[str]]:
        """根据年龄获取合适的活动"""
        if age <= 15:  # 初中
            return {
                "academic": ["上课", "考试", "作业", "学习", "复习"],
                "social": ["和同学玩", "课间聊天", "一起吃饭", "参加活动"],
                "personal": ["看书", "运动", "听音乐", "画画", "睡觉"],
                "family": ["和父母聊天", "吃饭", "看电视", "做家务"]
            }
        elif age <= 18:  # 高中
            return {
                "academic": ["上课", "考试", "作业", "学习", "复习", "讨论问题", "准备高考"],
                "social": ["和朋友聊天", "一起学习", "运动", "参加社团", "课外活动"],
                "personal": ["阅读", "运动", "听音乐", "思考未来", "独处"],
                "family": ["和父母交流", "家庭聚餐", "分享学校生活", "寻求建议"]
            }
        elif age <= 22:  # 大学
            return {
                "academic": ["上课", "研究", "实习", "项目", "论文", "考试", "讨论"],
                "social": ["朋友聚会", "恋爱", "社团活动", "聚餐", "旅行"],
                "personal": ["锻炼", "爱好", "思考人生", "规划未来", "自我提升"],
                "family": ["汇报近况", "节假日回家", "寻求支持", "分享成长"]
            }
        else:  # 成年
            return {
                "academic": ["工作学习", "技能提升", "培训", "会议"],
                "social": ["同事聚会", "朋友聚餐", "恋爱关系", "社交活动"],
                "personal": ["工作", "理财", "健身", "兴趣爱好", "自我发展"],
                "family": ["照顾家庭", "亲子关系", "家庭决策", "经济支持"]
            }
    
    def _get_valid_relationships(self) -> Dict[str, str]:
        """获取有效的人际关系映射"""
        relationships = {}
        for char_id, char_name in self.character_mapping.items():
            if char_id == "protagonist":
                continue
            
            # 根据character_id推断关系类型
            if char_id in ["father", "mother", "parent"]:
                relationships[char_name] = "家人"
            elif char_id in ["teacher", "mentor", "instructor"]:
                relationships[char_name] = "老师/导师"
            elif char_id in ["friend", "classmate", "roommate"]:
                relationships[char_name] = "朋友/同学"
            elif char_id in ["girlfriend", "boyfriend", "lover"]:
                relationships[char_name] = "恋人"
            elif char_id in ["bully", "competitor", "rival"]:
                relationships[char_name] = "竞争者/敌对"
            else:
                relationships[char_name] = "其他"
        
        return relationships
    
    def _analyze_emotional_patterns(self) -> Dict[str, List[str]]:
        """分析情感模式"""
        return {
            "positive": ["获得认可", "成功完成", "感到开心", "收到好消息", "表现出色", "得到支持"],
            "negative": ["遭到拒绝", "表现不佳", "感到压力", "遇到挫折", "失望", "焦虑", "担心"],
            "neutral": ["参加活动", "进行讨论", "日常交流", "寻求建议", "例行学习", "普通对话"]
        }
    
    def _build_activity_constraints(self, life_stage: str) -> Dict[str, Any]:
        """构建活动约束"""
        if life_stage == "高中生":
            return {
                "allowed_times": ["早上", "上午", "下午", "傍晚", "晚上"],
                "allowed_locations": ["学校", "教室", "图书馆", "操场", "食堂", "家里", "走廊"],
                "forbidden_activities": ["工作", "开会", "出差", "商务", "管理"],
                "forbidden_relationships": ["下属", "同事", "客户", "老板"]
            }
        elif life_stage == "大学生":
            return {
                "allowed_times": ["早上", "上午", "下午", "傍晚", "晚上", "深夜"],
                "allowed_locations": ["大学", "宿舍", "图书馆", "实验室", "食堂", "咖啡厅", "家里"],
                "forbidden_activities": ["正式工作", "管理岗位", "商务决策"],
                "forbidden_relationships": ["下属", "正式同事"]
            }
        else:
            return {
                "allowed_times": ["早上", "上午", "下午", "傍晚", "晚上"],
                "allowed_locations": ["办公室", "家里", "会议室", "餐厅", "商场"],
                "forbidden_activities": [],
                "forbidden_relationships": []
            }
    
    def _map_character_interactions(self) -> Dict[str, List[str]]:
        """映射角色互动模式"""
        interactions = {}
        relationships = self._get_valid_relationships()
        
        for char_name, relation_type in relationships.items():
            if relation_type == "家人":
                interactions[char_name] = ["关心", "支持", "询问", "建议", "聊天", "担心"]
            elif relation_type == "老师/导师":
                interactions[char_name] = ["指导", "评价", "建议", "认可", "批评", "教导"]
            elif relation_type == "朋友/同学":
                interactions[char_name] = ["聊天", "玩耍", "学习", "分享", "支持", "讨论"]
            elif relation_type == "恋人":
                interactions[char_name] = ["关爱", "陪伴", "交流", "支持", "理解", "亲密"]
            elif relation_type == "竞争者/敌对":
                interactions[char_name] = ["竞争", "冲突", "挑衅", "比较", "对立"]
            else:
                interactions[char_name] = ["交流", "互动", "接触"]
        
        return interactions
    
    async def generate_event(self, 
                           category: str, 
                           sentiment: str,
                           protagonist_state: Dict,
                           stage_config: Dict,
                           force_unique: bool = True) -> Tuple[str, List[str], int]:
        """
        智能生成事件 - LLM增强版本
        """
        # 1. 分析当前上下文
        context = self._build_current_context(category, sentiment, protagonist_state, stage_config)
        
        # 2. LLM增强事件生成
        if self.llm_event_generator and random.random() < self.llm_config.get("llm_integration", {}).get("event_generation", {}).get("generation_probability", 0.3):
            try:
                # 使用LLM生成上下文化事件
                event_data = await self.llm_event_generator.generate_contextual_event(context, sentiment)
                generated_event = event_data["description"]
                participants = event_data["participants"]
                base_impact = event_data["impact_score"]
                
                self.logger.debug(f"LLM生成事件: {generated_event}")
                
            except Exception as e:
                self.logger.error(f"LLM事件生成失败，回退到传统方法: {e}")
                # 回退到传统生成方法
                return await self._generate_traditional_event(category, sentiment, context, stage_config)
        else:
            # 传统生成方法
            return await self._generate_traditional_event(category, sentiment, context, stage_config)
        
        # 3. 使用混合影响计算器计算最终影响
        if self.hybrid_calculator:
            try:
                # 创建临时事件对象用于影响计算
                from models.psychology_models import PsychologicalState
                current_psychological_state = self._dict_to_psychological_state(protagonist_state)
                temp_event = self._create_temp_event(generated_event, participants, base_impact)
                
                impact_result = await self.hybrid_calculator.calculate_comprehensive_impact(
                    temp_event, current_psychological_state, context
                )
                
                final_impact = impact_result["total_impact"]
                
                self.logger.debug(f"混合影响计算: {base_impact} -> {final_impact:.2f}")
                
            except Exception as e:
                self.logger.error(f"混合影响计算失败: {e}")
                final_impact = base_impact
        else:
            final_impact = base_impact
        
        # 4. 应用概率性调整
        if self.probabilistic_model:
            try:
                prob_context = {
                    "personality": context.get("protagonist_state", {}).get("personality", {}),
                    "psychological_state": self._dict_to_psychological_state(protagonist_state),
                    "time_context": {"hour": datetime.now().hour, "is_weekend": datetime.now().weekday() >= 5},
                    "social_context": {"group_size": len(participants), "social_support": 0.5}
                }
                
                final_impact = self.probabilistic_model.apply_normal_variation(final_impact)
                final_impact = self.probabilistic_model.apply_individual_variance(
                    final_impact, prob_context.get("personality", {}))
                
                self.logger.debug(f"概率性调整后影响: {final_impact:.2f}")
                
            except Exception as e:
                self.logger.error(f"概率性调整失败: {e}")
        
        # 5. 记录生成历史
        self.event_history.append({
            "event": generated_event,
            "category": category,
            "sentiment": sentiment,
            "participants": participants,
            "impact": final_impact,
            "timestamp": datetime.now(),
            "llm_enhanced": True
        })
        
        return generated_event, participants, int(final_impact)
    
    async def _generate_traditional_event(self, category: str, sentiment: str, 
                                        context: Dict, stage_config: Dict) -> Tuple[str, List[str], int]:
        """传统事件生成方法"""
        # 选择基础模板模式
        base_pattern = self.template_analyzer.select_best_pattern(category, sentiment, context)
        
        # 发散生成新事件
        if self.ai_client and random.random() < 0.7:  # 70%概率使用AI发散
            generated_event = await self.divergent_generator.generate_from_pattern(
                base_pattern, context, self.generation_rules
            )
        else:
            # 使用规则生成
            generated_event = self._rule_based_generation(base_pattern, context)
        
        # 逻辑验证和修正
        validated_event = self.logic_validator.validate_and_fix(generated_event, context)
        
        # 提取参与者和计算影响
        participants = self._extract_participants(validated_event)
        impact_score = self._calculate_impact_score(sentiment, context["protagonist_state"], stage_config)
        
        # 记录生成历史
        self.event_history.append({
            "event": validated_event,
            "pattern": base_pattern,
            "category": category,
            "sentiment": sentiment,
            "timestamp": datetime.now(),
            "llm_enhanced": False
        })
        
        return validated_event, participants, impact_score
    
    def _dict_to_psychological_state(self, state_dict: Dict):
        """将字典转换为PsychologicalState对象"""
        from models.psychology_models import PsychologicalState, EmotionState, DepressionLevel, CognitiveAffectiveState
        
        # 创建基础状态
        emotion = EmotionState.NEUTRAL
        depression_level = DepressionLevel.HEALTHY
        
        # 从字典中提取信息
        if "emotion" in state_dict:
            try:
                emotion = EmotionState(state_dict["emotion"])
            except:
                emotion = EmotionState.NEUTRAL
        
        if "depression_level" in state_dict:
            try:
                if isinstance(state_dict["depression_level"], str):
                    depression_level = getattr(DepressionLevel, state_dict["depression_level"])
                else:
                    depression_level = DepressionLevel(state_dict["depression_level"])
            except:
                depression_level = DepressionLevel.HEALTHY
        
        # 创建CAD状态
        cad_state = CognitiveAffectiveState()
        if "cad_state" in state_dict:
            cad_dict = state_dict["cad_state"]
            if "affective_tone" in cad_dict:
                cad_state.affective_tone = cad_dict["affective_tone"]
            # 可以添加更多CAD状态字段的转换
        
        return PsychologicalState(
            emotion=emotion,
            depression_level=depression_level,
            stress_level=state_dict.get("stress_level", 5),
            self_esteem=state_dict.get("self_esteem", 5),
            social_connection=state_dict.get("social_connection", 5),
            academic_pressure=state_dict.get("academic_pressure", 5),
            cad_state=cad_state
        )
    
    def _create_temp_event(self, description: str, participants: List[str], impact_score: int):
        """创建临时事件对象"""
        from models.psychology_models import LifeEvent, EventType
        
        return LifeEvent(
            event_type=EventType.ACADEMIC_FAILURE,  # 默认类型
            description=description,
            impact_score=impact_score,
            timestamp=datetime.now().isoformat(),
            participants=participants
        )
    
    def _build_current_context(self, category: str, sentiment: str, state: Dict, stage_config: Dict) -> Dict:
        """构建当前生成上下文"""
        return {
            "category": category,
            "sentiment": sentiment,
            "protagonist_state": state,
            "stage_config": stage_config,
            "character_context": self.character_context,
            "generation_rules": self.generation_rules,
            "recent_events": self.event_history[-5:] if self.event_history else []
        }
    
    def _rule_based_generation(self, base_pattern: Dict, context: Dict) -> str:
        """基于规则的事件生成"""
        pattern_structure = base_pattern.get("structure", "")
        pattern_elements = base_pattern.get("elements", {})
        
        # 替换角色
        event = pattern_structure
        for placeholder, char_name in pattern_elements.get("characters", {}).items():
            # 直接使用配置中的角色名
            if placeholder in self.character_mapping:
                event = event.replace(f"{{{placeholder}}}", self.character_mapping[placeholder])
            else:
                # 如果占位符不在映射中，尝试智能选择
                selected_char = self._select_appropriate_character(placeholder, context)
                event = event.replace(f"{{{placeholder}}}", selected_char)
        
        # 替换活动和其他占位符
        remaining_placeholders = re.findall(r'\{(\w+)\}', event)
        for placeholder in remaining_placeholders:
            if placeholder == "subject":
                event = event.replace(f"{{{placeholder}}}", self._get_smart_subject(context))
            elif placeholder == "location":
                event = event.replace(f"{{{placeholder}}}", self._get_smart_location(context))
            elif placeholder == "time":
                event = event.replace(f"{{{placeholder}}}", self._get_smart_time(context))
            elif placeholder == "emotion":
                sentiment = context.get("sentiment", "neutral")
                emotional_words = self.generation_rules["emotional_patterns"].get(sentiment, [""])
                if emotional_words:
                    emotion = random.choice(emotional_words)
                    event = event.replace(f"{{{placeholder}}}", emotion)
            else:
                # 尝试选择合适的活动
                activity = self._select_appropriate_activity(placeholder, context)
                event = event.replace(f"{{{placeholder}}}", activity)
        
        return event
    
    def _get_smart_subject(self, context: Dict) -> str:
        """智能选择科目"""
        age = self.character_context.get("protagonist_age", 17)
        if age <= 15:  # 初中
            return random.choice(["语文", "数学", "英语", "物理", "化学", "生物", "历史", "地理"])
        elif age <= 18:  # 高中
            return random.choice(["语文", "数学", "英语", "物理", "化学", "生物", "政治", "历史", "地理"])
        else:  # 大学
            return random.choice(["高等数学", "专业课", "英语", "选修课", "实验课"])
    
    def _get_smart_location(self, context: Dict) -> str:
        """智能选择地点"""
        allowed_locations = self.generation_rules["activity_constraints"]["allowed_locations"]
        category = context.get("category", "personal")
        
        # 根据事件类别优选地点
        if category == "academic":
            preferred = ["教室", "图书馆", "学校"]
        elif category == "social":
            preferred = ["操场", "食堂", "走廊"]
        elif category == "family":
            preferred = ["家里"]
        else:
            preferred = allowed_locations
        
        # 在允许地点中选择优选地点
        valid_locations = [loc for loc in preferred if loc in allowed_locations]
        return random.choice(valid_locations) if valid_locations else random.choice(allowed_locations)
    
    def _get_smart_time(self, context: Dict) -> str:
        """智能选择时间"""
        category = context.get("category", "personal")
        
        # 根据事件类别选择合理时间
        if category == "academic":
            return random.choice(["上午", "下午"])
        elif category == "social":
            return random.choice(["中午", "下午", "傍晚"])
        elif category == "family":
            return random.choice(["傍晚", "晚上"])
        else:
            return random.choice(["早上", "上午", "中午", "下午", "傍晚", "晚上"])
    
    def _select_appropriate_character(self, char_type: str, context: Dict) -> str:
        """选择合适的角色"""
        # 首先检查是否是已知的占位符类型
        type_mapping = {
            "friend": "朋友/同学",
            "teacher": "老师/导师", 
            "parent": "家人",
            "father": "家人",
            "mother": "家人",
            "classmate": "朋友/同学",
            "mentor": "老师/导师"
        }
        
        target_type = type_mapping.get(char_type, char_type)
        relationships = self.generation_rules["valid_relationships"]
        
        # 根据关系类型过滤角色
        suitable_chars = [
            char_name for char_name, relation in relationships.items()
            if target_type in relation or relation in target_type
        ]
        
        if suitable_chars:
            return random.choice(suitable_chars)
        
        # 兜底：返回任意角色
        available_chars = list(relationships.keys())
        return random.choice(available_chars) if available_chars else "朋友"
    
    def _select_appropriate_activity(self, activity_type: str, context: Dict) -> str:
        """选择合适的活动"""
        category = context.get("category", "personal")
        age_activities = self.generation_rules["age_appropriate_activities"]
        
        if category in age_activities:
            activities = age_activities[category]
            # 过滤禁止活动
            constraints = self.generation_rules["activity_constraints"]
            forbidden = constraints.get("forbidden_activities", [])
            valid_activities = [a for a in activities if not any(f in a for f in forbidden)]
            
            if valid_activities:
                return random.choice(valid_activities)
        
        return "进行活动"
    
    def _extract_participants(self, event: str) -> List[str]:
        """提取事件参与者"""
        participants = []
        
        # 检查所有已知角色
        for char_name in self.character_mapping.values():
            if char_name in event:
                participants.append(char_name)
        
        # 确保主角在列表中
        protagonist = self.character_mapping.get("protagonist", "主角")
        if protagonist not in participants:
            participants.insert(0, protagonist)
            
        return participants
    
    def _calculate_impact_score(self, sentiment: str, state: Dict, stage_config: Dict) -> int:
        """计算影响分数"""
        base_scores = {
            "positive": random.randint(2, 5),
            "negative": random.randint(-6, -2),
            "neutral": random.randint(-1, 1)
        }
        
        score = base_scores.get(sentiment, 0)
        
        # 根据当前状态调整
        stress_level = state.get('stress_level', 5)
        if stress_level > 7:
            if score < 0:
                score = int(score * 1.5)
            elif score > 0:
                score = int(score * 0.7)
        
        # 根据阶段调整
        stress_modifier = stage_config.get('stress_modifier', 1.0)
        if score < 0:
            score = int(score * stress_modifier)
            
        return max(-10, min(10, score))
    
    async def generate_conditional_event(self, 
                                       condition_name: str, 
                                       condition_config: Dict, 
                                       protagonist_state: Dict) -> Optional[Tuple[str, List[str], int]]:
        """
        生成条件事件 - 根据主角状态触发特定条件事件
        """
        try:
            # 检查条件是否满足
            condition_func = condition_config.get("condition")
            if not condition_func or not condition_func(protagonist_state):
                return None
            
            # 获取可用事件模板
            available_events = condition_config.get("events", [])
            if not available_events:
                self.logger.warning(f"条件事件 {condition_name} 没有可用的事件模板")
                return None
            
            # 随机选择一个事件模板
            selected_template = random.choice(available_events)
            
            # 构建生成上下文
            context = {
                "category": "conditional",
                "sentiment": "negative",  # 条件事件通常是负面的
                "protagonist_state": protagonist_state,
                "character_context": self.character_context,
                "generation_rules": self.generation_rules,
                "condition_name": condition_name
            }
            
            # 创建模拟的模式结构
            pattern = {
                "template": selected_template,
                "structure": selected_template,
                "category": "conditional",
                "sentiment": "negative",
                "elements": {
                    "characters": self._extract_characters_from_template(selected_template),
                    "activities": {},
                    "others": {}
                },
                "keywords": [condition_name],
                "emotional_tone": "消极",
                "complexity": selected_template.count("{")
            }
            
            # 生成事件
            if self.ai_client and random.random() < 0.5:  # 50%概率使用AI
                generated_event = await self.divergent_generator.generate_from_pattern(
                    pattern, context, self.generation_rules
                )
            else:
                # 使用规则生成
                generated_event = self._rule_based_generation(pattern, context)
            
            # 验证和修正
            validated_event = self.logic_validator.validate_and_fix(generated_event, context)
            
            # 提取参与者
            participants = self._extract_participants(validated_event)
            
            # 计算影响分数（条件事件通常影响较大）
            impact_score = self._calculate_conditional_impact(condition_name, protagonist_state)
            
            # 记录条件事件
            self.event_history.append({
                "event": validated_event,
                "pattern": pattern,
                "category": "conditional",
                "sentiment": "negative",
                "condition": condition_name,
                "timestamp": datetime.now()
            })
            
            self.logger.info(f"条件事件触发: {condition_name} -> {validated_event}")
            
            return validated_event, participants, impact_score
            
        except Exception as e:
            self.logger.error(f"生成条件事件 {condition_name} 时发生错误: {e}")
            return None
    
    def _extract_characters_from_template(self, template: str) -> Dict[str, str]:
        """从模板中提取角色占位符"""
        placeholders = re.findall(r'\{(\w+)\}', template)
        characters = {}
        
        for placeholder in placeholders:
            if placeholder in self.character_mapping:
                characters[placeholder] = self.character_mapping[placeholder]
        
        return characters
    
    def _calculate_conditional_impact(self, condition_name: str, protagonist_state: Dict) -> int:
        """计算条件事件的影响分数"""
        # 条件事件通常有较大的负面影响
        base_impacts = {
            "low_grades": -4,
            "high_stress": -5,
            "social_isolation": -6,
            "family_conflict": -5,
            "health_issues": -7
        }
        
        base_score = base_impacts.get(condition_name, -4)
        
        # 根据当前状态调整影响
        stress_level = protagonist_state.get('stress_level', 5)
        if stress_level > 8:
            base_score = int(base_score * 1.5)  # 高压力时影响更大
        
        depression_level = protagonist_state.get('depression_level', 'MILD')
        if depression_level in ['MODERATE', 'SEVERE']:
            base_score = int(base_score * 1.3)  # 抑郁状态下影响更大
        
        return max(-10, base_score)
    
    def get_event_variety_score(self) -> float:
        """计算事件多样性分数"""
        if not self.event_history:
            return 0.0
        
        # 统计不同类别的事件数量
        categories = [event.get("category", "unknown") for event in self.event_history]
        unique_categories = len(set(categories))
        total_events = len(categories)
        
        # 计算多样性分数
        variety_score = (unique_categories / max(1, total_events)) * 100
        return round(variety_score, 2)


class TemplateAnalyzer:
    """模板分析器 - 分析现有事件模板的结构和模式"""
    
    def __init__(self, event_templates: Dict, character_mapping: Dict):
        self.event_templates = event_templates
        self.character_mapping = character_mapping
        
    def analyze_patterns(self) -> List[Dict]:
        """分析模板模式"""
        patterns = []
        
        for category, sentiments in self.event_templates.items():
            for sentiment, templates in sentiments.items():
                for template in templates:
                    pattern = self._analyze_single_template(template, category, sentiment)
                    patterns.append(pattern)
        
        return patterns
    
    def _analyze_single_template(self, template: str, category: str, sentiment: str) -> Dict:
        """分析单个模板"""
        # 提取占位符
        placeholders = re.findall(r'\{(\w+)\}', template)
        
        # 分类占位符
        characters = {}
        activities = {}
        others = {}
        
        for placeholder in placeholders:
            if placeholder in self.character_mapping:
                characters[placeholder] = self.character_mapping[placeholder]
            elif placeholder in ["subject", "location", "time"]:
                others[placeholder] = "contextual"
            else:
                activities[placeholder] = "activity"
        
        # 分析结构
        structure_keywords = self._extract_keywords(template)
        emotional_tone = self._analyze_emotional_tone(template, sentiment)
        
        return {
            "template": template,
            "category": category,
            "sentiment": sentiment,
            "structure": template,
            "elements": {
                "characters": characters,
                "activities": activities,
                "others": others
            },
            "keywords": structure_keywords,
            "emotional_tone": emotional_tone,
            "complexity": len(placeholders)
        }
    
    def _extract_keywords(self, template: str) -> List[str]:
        """提取关键词"""
        # 移除占位符后提取关键词
        text = re.sub(r'\{[^}]+\}', '', template)
        keywords = []
        
        # 简单的关键词提取
        for word in ["获得", "收到", "完成", "表现", "感到", "参加", "准备", "讨论", "分享"]:
            if word in text:
                keywords.append(word)
        
        return keywords
    
    def _analyze_emotional_tone(self, template: str, sentiment: str) -> str:
        """分析情感基调"""
        positive_words = ["获得", "成功", "认可", "好", "开心", "支持"]
        negative_words = ["拒绝", "失败", "压力", "不佳", "担心", "焦虑"]
        
        pos_count = sum(1 for word in positive_words if word in template)
        neg_count = sum(1 for word in negative_words if word in template)
        
        if pos_count > neg_count:
            return "积极"
        elif neg_count > pos_count:
            return "消极"
        else:
            return "中性"
    
    def select_best_pattern(self, category: str, sentiment: str, context: Dict) -> Dict:
        """选择最佳模板模式"""
        # 过滤匹配的模式
        matching_patterns = [
            p for p in self.analyze_patterns()
            if p["category"] == category and p["sentiment"] == sentiment
        ]
        
        if not matching_patterns:
            # 退而求其次，只匹配类别
            matching_patterns = [
                p for p in self.analyze_patterns()
                if p["category"] == category
            ]
        
        if not matching_patterns:
            # 最后兜底
            matching_patterns = self.analyze_patterns()
        
        # 简单选择策略：随机选择
        return random.choice(matching_patterns) if matching_patterns else {
            "template": "{protagonist}度过了平凡的一天",
            "category": category,
            "sentiment": sentiment,
            "structure": "{protagonist}度过了平凡的一天",
            "elements": {"characters": {"protagonist": "主角"}},
            "keywords": [],
            "emotional_tone": "中性",
            "complexity": 1
        }


class ContextExtractor:
    """上下文提取器 - 从配置中提取角色和环境信息"""
    
    def __init__(self, config, character_mapping: Dict):
        self.config = config
        self.character_mapping = character_mapping
    
    def extract_context(self) -> Dict:
        """提取完整上下文"""
        if not self.config or not hasattr(self.config, 'CHARACTERS'):
            return self._get_default_context()
        
        protagonist_config = self.config.CHARACTERS.get("protagonist", {})
        
        return {
            "protagonist_name": protagonist_config.get("name", "主角"),
            "protagonist_age": protagonist_config.get("age", 17),
            "protagonist_type": protagonist_config.get("type", "StudentAgent"),
            "life_stage": self._infer_life_stage(protagonist_config.get("age", 17)),
            "available_characters": list(self.character_mapping.values()),
            "scenario_type": getattr(self.config, 'SCENARIO_TYPE', 'high_school')
        }
    
    def _infer_life_stage(self, age: int) -> str:
        """推断人生阶段"""
        if age <= 15:
            return "初中生"
        elif age <= 18:
            return "高中生"
        elif age <= 22:
            return "大学生"
        else:
            return "成年人"
    
    def _get_default_context(self) -> Dict:
        """默认上下文"""
        return {
            "protagonist_name": "主角",
            "protagonist_age": 17,
            "protagonist_type": "StudentAgent",
            "life_stage": "高中生",
            "available_characters": [],
            "scenario_type": "high_school"
        }


class LogicValidator:
    """逻辑验证器 - 确保生成的事件符合逻辑"""
    
    def __init__(self, config):
        self.config = config
    
    def validate_and_fix(self, event: str, context: Dict) -> str:
        """验证并修正事件"""
        # 基本逻辑检查
        if not self._basic_logic_check(event, context):
            return self._generate_fallback_event(context)
        
        # 年龄适当性检查
        if not self._age_appropriateness_check(event, context):
            return self._fix_age_inappropriate_content(event, context)
        
        return event
    
    def _basic_logic_check(self, event: str, context: Dict) -> bool:
        """基本逻辑检查"""
        # 检查事件是否为空或过短
        if not event or len(event.strip()) < 5:
            return False
        
        # 检查是否包含主角
        protagonist_name = context.get("character_context", {}).get("protagonist_name", "主角")
        if protagonist_name not in event and "主角" not in event:
            return False
        
        return True
    
    def _age_appropriateness_check(self, event: str, context: Dict) -> bool:
        """年龄适当性检查"""
        age = context.get("character_context", {}).get("protagonist_age", 17)
        
        if age <= 18:
            # 禁止的成年人内容 - 更全面的检查
            forbidden_adult_content = [
                "结婚", "离婚", "妻子", "丈夫", "老婆", "老公", "儿子", "女儿", "孩子",
                "工作", "下班", "上班", "同事", "老板", "员工", "职场", "薪水", "工资",
                "办公室", "会议室", "公司", "写字楼", "商务", "客户", "出差", "加班"
            ]
            
            # 检查是否包含任何禁止内容
            for forbidden in forbidden_adult_content:
                if forbidden in event:
                    return False
        
        return True
    
    def _fix_age_inappropriate_content(self, event: str, context: Dict) -> str:
        """修正年龄不当内容"""
        age = context.get("character_context", {}).get("protagonist_age", 17)
        
        if age <= 18:
            # 简单替换不当内容
            replacements = {
                "工作": "学习",
                "下班": "放学",
                "同事": "同学",
                "老板": "老师",
                "员工": "学生"
            }
            
            for old, new in replacements.items():
                event = event.replace(old, new)
        
        return event
    
    def _generate_fallback_event(self, context: Dict) -> str:
        """生成兜底事件"""
        protagonist_name = context.get("character_context", {}).get("protagonist_name", "主角")
        life_stage = context.get("character_context", {}).get("life_stage", "学生")
        
        return f"{protagonist_name}作为{life_stage}度过了平凡的一天"


class DivergentGenerator:
    """发散生成器 - 基于模式和上下文生成新事件"""
    
    def __init__(self, ai_client):
        self.ai_client = ai_client
    
    async def generate_from_pattern(self, pattern: Dict, context: Dict, rules: Dict) -> str:
        """基于模式发散生成新事件"""
        if not self.ai_client:
            return pattern.get("template", "发生了一件事")
        
        prompt = self._build_generation_prompt(pattern, context, rules)
        
        try:
            generated = await self.ai_client.generate_response(prompt)
            return generated.strip()
        except Exception as e:
            logging.error(f"AI发散生成失败: {e}")
            return pattern.get("template", "发生了一件事")
    
    def _build_generation_prompt(self, pattern: Dict, context: Dict, rules: Dict) -> str:
        """构建生成提示词"""
        character_context = context.get("character_context", {})
        protagonist_name = character_context.get("protagonist_name", "主角")
        age = character_context.get("protagonist_age", 17)
        life_stage = character_context.get("life_stage", "学生")
        
        template_example = pattern.get("template", "")
        category = pattern.get("category", "")
        sentiment = pattern.get("sentiment", "")
        keywords = ", ".join(pattern.get("keywords", []))
        
        available_characters = ", ".join(context.get("character_context", {}).get("available_characters", []))
        
        prompt = f"""
请基于以下信息生成一个新的事件描述：

参考模板：{template_example}
事件类别：{category}
情感倾向：{sentiment}
关键词：{keywords}

角色信息：
- 主角：{protagonist_name}（{age}岁{life_stage}）
- 可用角色：{available_characters}

生成要求：
1. 保持与参考模板相似的结构和风格
2. 符合{age}岁{life_stage}的身份设定
3. 事件要真实可信，符合日常生活逻辑
4. 长度控制在15-30字
5. 体现{sentiment}的情感倾向

直接返回生成的事件描述，不要其他内容。
        """
        
        return prompt