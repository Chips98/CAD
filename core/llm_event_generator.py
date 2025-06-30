"""
LLM事件生成器 - 基于模板扩展生成多样化事件
支持读取所有scenarios下的事件模板并进行LLM增强生成
"""

import json
import random
import re
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

from models.psychology_models import LifeEvent, EventType


class LLMEventGenerator:
    """LLM事件生成器 - 基于现有模板扩展生成多样化事件"""
    
    def __init__(self, ai_client, config_path: str = None):
        self.ai_client = ai_client
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        
        # 事件模板和角色映射
        self.event_templates = {}
        self.character_mapping = {}
        self.scenario_config = {}
        
        # 生成历史和质量控制
        self.generation_history = []
        self.quality_threshold = 0.7
        self.generation_probability = 0.3  # 30%概率使用LLM生成
        
        # 加载配置
        self._load_scenario_configs()
        
        self.logger.info(f"LLM事件生成器初始化完成，加载了{len(self.event_templates)}个场景的事件模板")
    
    def _load_scenario_configs(self):
        """加载所有scenario配置文件"""
        scenarios_dir = Path("/Users/zl_24/Documents/Codes/2025/2025-07/CAD-main/config/scenarios")
        
        if not scenarios_dir.exists():
            self.logger.warning(f"scenarios目录不存在: {scenarios_dir}")
            return
        
        # 遍历所有json配置文件
        for json_file in scenarios_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                scenario_name = json_file.stem
                self.logger.info(f"加载场景配置: {scenario_name}")
                
                # 提取事件模板
                if "event_templates" in config:
                    self.event_templates[scenario_name] = config["event_templates"]
                
                # 提取角色映射
                if "characters" in config:
                    char_mapping = {}
                    for char_id, char_info in config["characters"].items():
                        if isinstance(char_info, dict) and "name" in char_info:
                            char_mapping[char_id] = char_info["name"]
                    self.character_mapping[scenario_name] = char_mapping
                
                # 保存完整配置
                self.scenario_config[scenario_name] = config
                
            except Exception as e:
                self.logger.error(f"加载场景配置失败 {json_file}: {e}")
    
    async def expand_event_templates(self, base_templates: Dict, scenario_name: str = None) -> Dict:
        """基于现有模板进行LLM扩展生成"""
        expanded_templates = {}
        
        for category, sentiments in base_templates.items():
            expanded_templates[category] = {}
            
            for sentiment, templates in sentiments.items():
                expanded_templates[category][sentiment] = list(templates)  # 保留原模板
                
                # 使用LLM生成扩展模板
                if len(templates) > 0 and random.random() < self.generation_probability:
                    try:
                        new_templates = await self._generate_similar_templates(
                            templates, category, sentiment, scenario_name
                        )
                        expanded_templates[category][sentiment].extend(new_templates)
                        
                    except Exception as e:
                        self.logger.error(f"LLM扩展模板失败 {category}-{sentiment}: {e}")
        
        return expanded_templates
    
    async def _generate_similar_templates(self, base_templates: List[str], 
                                        category: str, sentiment: str, 
                                        scenario_name: str = None) -> List[str]:
        """基于基础模板生成相似的新模板"""
        if not self.ai_client:
            return []
        
        # 获取角色映射信息
        char_mapping = self.character_mapping.get(scenario_name, {})
        char_info = self._get_character_context(scenario_name)
        
        # 构建prompt
        prompt = self._build_template_expansion_prompt(
            base_templates, category, sentiment, char_mapping, char_info
        )
        
        try:
            response = await self.ai_client.generate_response(prompt)
            new_templates = self._parse_generated_templates(response)
            
            # 质量验证
            validated_templates = self._validate_templates(new_templates, base_templates)
            
            self.logger.info(f"生成并验证了{len(validated_templates)}个新模板 ({category}-{sentiment})")
            return validated_templates
            
        except Exception as e:
            self.logger.error(f"生成模板时出错: {e}")
            return []
    
    def _build_template_expansion_prompt(self, base_templates: List[str],
                                       category: str, sentiment: str,
                                       char_mapping: Dict, char_info: Dict) -> str:
        """构建模板扩展的prompt"""
        
        # 角色信息
        protagonist = char_mapping.get("protagonist", "主角")
        age = char_info.get("age", 17)
        available_chars = ", ".join([f"{k}: {v}" for k, v in char_mapping.items()])
        
        # 基础模板示例
        template_examples = "\n".join([f"- {template}" for template in base_templates[:3]])
        
        prompt = f"""
你是一个心理学专家和事件设计师，需要基于现有事件模板生成新的相似事件。

角色设定：
- 主角：{protagonist}（{age}岁）
- 可用角色：{available_chars}

现有事件模板（{category}类别，{sentiment}情感）：
{template_examples}

请基于这些模板，生成3-5个结构相似但内容不同的新事件模板。

要求：
1. 保持相同的占位符格式（如 {{protagonist}}, {{teacher}} 等）
2. 符合{age}岁主角的年龄特征和生活场景
3. 体现{sentiment}的情感倾向
4. 事件要真实可信，符合{category}类别的特点
5. 每个事件15-25字
6. 使用中文

输出格式：
每行一个模板，不需要编号或其他说明文字。
"""
        
        return prompt.strip()
    
    def _get_character_context(self, scenario_name: str) -> Dict:
        """获取角色上下文信息"""
        if not scenario_name or scenario_name not in self.scenario_config:
            return {"age": 17, "life_stage": "高中生"}
        
        config = self.scenario_config[scenario_name]
        protagonist_info = config.get("characters", {}).get("protagonist", {})
        
        age = protagonist_info.get("age", 17)
        life_stage = "小学生" if age <= 12 else "初中生" if age <= 15 else "高中生" if age <= 18 else "大学生"
        
        return {
            "age": age,
            "life_stage": life_stage,
            "personality": protagonist_info.get("personality", {}),
            "background": protagonist_info.get("background", {})
        }
    
    def _parse_generated_templates(self, response: str) -> List[str]:
        """解析LLM生成的模板"""
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        templates = []
        
        for line in lines:
            # 移除可能的编号和格式
            clean_line = re.sub(r'^\d+[\.\-\s]*', '', line)
            clean_line = re.sub(r'^[\-\*\+]\s*', '', clean_line)
            clean_line = clean_line.strip()
            
            # 基本验证
            if len(clean_line) > 5 and '{' in clean_line:
                templates.append(clean_line)
        
        return templates
    
    def _validate_templates(self, new_templates: List[str], base_templates: List[str]) -> List[str]:
        """验证生成的模板质量"""
        validated = []
        
        for template in new_templates:
            if self._is_template_valid(template, base_templates):
                validated.append(template)
        
        return validated
    
    def _is_template_valid(self, template: str, base_templates: List[str]) -> bool:
        """检查模板是否有效"""
        # 基本格式检查
        if len(template) < 10 or len(template) > 50:
            return False
        
        # 必须包含占位符
        if not re.search(r'\{[a-zA-Z_]+\}', template):
            return False
        
        # 不能与现有模板过于相似
        for base in base_templates:
            similarity = self._calculate_similarity(template, base)
            if similarity > 0.8:  # 相似度过高
                return False
        
        # 不能包含不当内容
        forbidden_words = ["死", "杀", "血", "暴力", "性", "毒品"]
        if any(word in template for word in forbidden_words):
            return False
        
        return True
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度（简单实现）"""
        words1 = set(text1)
        words2 = set(text2)
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0
    
    async def generate_contextual_event(self, context: Dict, sentiment: str) -> Dict:
        """基于上下文生成个性化事件"""
        if not self.ai_client:
            return self._generate_fallback_event(context, sentiment)
        
        try:
            prompt = self._build_contextual_event_prompt(context, sentiment)
            response = await self.ai_client.generate_response(prompt)
            
            event_data = self._parse_contextual_event_response(response, context)
            
            # 记录生成历史
            self.generation_history.append({
                "event": event_data,
                "context": context,
                "sentiment": sentiment,
                "timestamp": datetime.now(),
                "llm_generated": True
            })
            
            return event_data
            
        except Exception as e:
            self.logger.error(f"生成上下文事件失败: {e}")
            return self._generate_fallback_event(context, sentiment)
    
    def _build_contextual_event_prompt(self, context: Dict, sentiment: str) -> str:
        """构建上下文事件生成prompt"""
        protagonist_state = context.get("protagonist_state", {})
        recent_events = context.get("recent_events", [])
        scenario_name = context.get("scenario_name", "default")
        
        # 获取角色信息
        char_mapping = self.character_mapping.get(scenario_name, {})
        char_info = self._get_character_context(scenario_name)
        protagonist = char_mapping.get("protagonist", "主角")
        
        # 当前状态描述
        depression_level = protagonist_state.get("depression_level", "HEALTHY")
        stress_level = protagonist_state.get("stress_level", 5)
        
        # 最近事件摘要
        recent_summary = "无特殊事件"
        if recent_events:
            recent_summary = "; ".join([event.get("description", "")[:20] for event in recent_events[-3:]])
        
        prompt = f"""
你是一个心理学专家，需要为一个心理模拟系统生成符合当前状态的生活事件。

角色信息：
- 姓名：{protagonist}
- 年龄：{char_info.get('age', 17)}岁
- 当前抑郁程度：{depression_level}
- 当前压力水平：{stress_level}/10
- 最近发生的事件：{recent_summary}

请生成一个{sentiment}的生活事件，要求：
1. 符合角色年龄和当前心理状态
2. 与最近事件有合理的连续性
3. 事件描述15-30字
4. 包含具体的参与者
5. 估计对心理状态的影响程度(-10到+10)

输出格式（JSON）：
{{
  "description": "事件描述",
  "participants": ["参与者1", "参与者2"],
  "impact_score": 数值,
  "emotional_intensity": 0.0-1.0,
  "category": "academic/social/family/personal"
}}
"""
        
        return prompt.strip()
    
    def _parse_contextual_event_response(self, response: str, context: Dict) -> Dict:
        """解析上下文事件生成响应"""
        try:
            # 清理响应文本
            clean_response = response.strip()
            if not clean_response:
                raise ValueError("响应为空")
            
            # 处理可能的markdown格式
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            clean_response = clean_response.strip()
            
            # 尝试解析JSON
            import json
            data = json.loads(clean_response)
            
            # 验证必要字段
            required_fields = ["description", "participants", "impact_score"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"缺少必要字段: {field}")
            
            # 规范化数据
            data["impact_score"] = max(-10, min(10, int(data["impact_score"])))
            data["emotional_intensity"] = max(0.0, min(1.0, float(data.get("emotional_intensity", 0.5))))
            data["category"] = data.get("category", "personal")
            data["llm_generated"] = True
            
            self.logger.debug(f"成功解析事件响应: {data['description']}")
            return data
            
        except Exception as e:
            self.logger.error(f"解析事件响应失败: {e}\n原始响应: {response[:200]}")
            return self._generate_fallback_event(context, "neutral")
    
    def _generate_fallback_event(self, context: Dict, sentiment: str) -> Dict:
        """生成后备事件"""
        scenario_name = context.get("scenario_name", "default")
        char_mapping = self.character_mapping.get(scenario_name, {})
        protagonist = char_mapping.get("protagonist", "主角")
        
        fallback_events = {
            "positive": f"{protagonist}度过了平静的一天",
            "negative": f"{protagonist}感到有些疲惫",
            "neutral": f"{protagonist}进行了日常活动"
        }
        
        return {
            "description": fallback_events.get(sentiment, f"{protagonist}度过了普通的一天"),
            "participants": [protagonist],
            "impact_score": 1 if sentiment == "positive" else -1 if sentiment == "negative" else 0,
            "emotional_intensity": 0.3,
            "category": "personal",
            "llm_generated": False
        }
    
    async def classify_event_impact(self, event_description: str) -> Dict:
        """使用LLM分析事件的心理影响"""
        if not self.ai_client:
            return self._default_impact_classification()
        
        try:
            prompt = f"""
作为心理学专家，请分析以下事件对心理状态的影响：

事件：{event_description}

请从以下维度评估影响（-3到+3）：
1. 对抑郁状态的影响
2. 对焦虑水平的影响  
3. 对自尊水平的影响
4. 对社交连接的影响

输出格式（JSON）：
{{
  "depression_impact": 数值,
  "anxiety_impact": 数值,
  "self_esteem_impact": 数值,
  "social_impact": 数值,
  "confidence_level": 0.0-1.0,
  "reasoning": "分析原因"
}}
"""
            
            response = await self.ai_client.generate_response(prompt)
            return self._parse_impact_analysis(response)
            
        except Exception as e:
            self.logger.error(f"分析事件影响失败: {e}")
            return self._default_impact_classification()
    
    def _parse_impact_analysis(self, response: str) -> Dict:
        """解析影响分析响应"""
        try:
            import json
            data = json.loads(response.strip())
            
            # 规范化数值
            for key in ["depression_impact", "anxiety_impact", "self_esteem_impact", "social_impact"]:
                if key in data:
                    data[key] = max(-3.0, min(3.0, float(data[key])))
            
            data["confidence_level"] = max(0.0, min(1.0, float(data.get("confidence_level", 0.5))))
            
            return data
            
        except Exception as e:
            self.logger.error(f"解析影响分析失败: {e}")
            return self._default_impact_classification()
    
    def _default_impact_classification(self) -> Dict:
        """默认影响分类"""
        return {
            "depression_impact": 0.0,
            "anxiety_impact": 0.0,
            "self_esteem_impact": 0.0,
            "social_impact": 0.0,
            "confidence_level": 0.3,
            "reasoning": "默认分类，无LLM分析"
        }
    
    def get_generation_statistics(self) -> Dict:
        """获取生成统计信息"""
        total_events = len(self.generation_history)
        llm_events = sum(1 for event in self.generation_history if event.get("llm_generated", False))
        
        return {
            "total_generated_events": total_events,
            "llm_generated_events": llm_events,
            "llm_generation_rate": llm_events / total_events if total_events > 0 else 0,
            "loaded_scenarios": len(self.event_templates),
            "average_event_length": self._calculate_average_event_length()
        }
    
    def _calculate_average_event_length(self) -> float:
        """计算平均事件长度"""
        if not self.generation_history:
            return 0.0
        
        lengths = []
        for item in self.generation_history:
            event = item.get("event", {})
            description = event.get("description", "")
            lengths.append(len(description))
        
        return sum(lengths) / len(lengths) if lengths else 0.0


class EnhancedLifeEvent(LifeEvent):
    """增强的生活事件类，包含LLM生成的额外信息"""
    
    def __init__(self, event_type: EventType, description: str, impact_score: int,
                 timestamp: str, participants: List[str],
                 emotional_intensity: float = 0.5,
                 cognitive_impact_type: List[str] = None,
                 duration_effect: str = "短期",
                 llm_generated: bool = False,
                 generation_prompt: str = ""):
        
        super().__init__(event_type, description, impact_score, timestamp, participants)
        
        self.emotional_intensity = emotional_intensity
        self.cognitive_impact_type = cognitive_impact_type or []
        self.duration_effect = duration_effect
        self.llm_generated = llm_generated
        self.generation_prompt = generation_prompt
    
    def to_dict(self) -> Dict:
        """转换为字典，包含增强字段"""
        base_dict = super().to_dict()
        base_dict.update({
            "emotional_intensity": self.emotional_intensity,
            "cognitive_impact_type": self.cognitive_impact_type,
            "duration_effect": self.duration_effect,
            "llm_generated": self.llm_generated,
            "generation_prompt": self.generation_prompt
        })
        return base_dict