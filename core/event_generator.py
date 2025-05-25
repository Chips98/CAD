"""
动态事件生成器
根据当前状态和配置生成多样化的事件
"""

import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

from models.psychology_models import LifeEvent, EventType

class EventGenerator:
    """动态事件生成器"""
    
    def __init__(self, ai_client, event_templates: Dict, character_mapping: Dict):
        self.ai_client = ai_client
        self.event_templates = event_templates
        self.character_mapping = character_mapping  # 角色名称映射
        self.logger = logging.getLogger(__name__)
        self.event_history = []  # 记录已生成的事件，避免重复
        
    async def generate_event(self, 
                           category: str, 
                           sentiment: str,
                           protagonist_state: Dict,
                           stage_config: Dict,
                           force_unique: bool = True) -> Tuple[str, List[str], int]:
        """
        生成事件
        返回: (事件描述, 参与者列表, 影响分数)
        """
        # 1. 从模板中选择基础事件
        templates = self.event_templates.get(category, {}).get(sentiment, [])
        if not templates:
            return await self._generate_ai_event(category, sentiment, protagonist_state)
        
        # 2. 选择一个模板
        if force_unique:
            # 过滤掉最近使用过的模板
            available_templates = [t for t in templates if t not in self.event_history[-10:]]
            if not available_templates:
                available_templates = templates
        else:
            available_templates = templates
            
        template = random.choice(available_templates)
        
        # 3. 填充模板
        event_description = self._fill_template(template, protagonist_state)
        
        # 4. 使用AI增强事件描述
        enhanced_event = await self._enhance_event_with_ai(
            event_description, category, sentiment, protagonist_state
        )
        
        # 5. 识别参与者
        participants = self._extract_participants(enhanced_event)
        
        # 6. 计算影响分数
        impact_score = self._calculate_impact_score(sentiment, protagonist_state, stage_config)
        
        # 记录事件
        self.event_history.append(template)
        
        return enhanced_event, participants, impact_score
    
    def _fill_template(self, template: str, state: Dict) -> str: 
        """填充事件模板"""
        # 基础替换
        replacements = {
            "{protagonist}": self.character_mapping.get("protagonist", "李明"),
            "{father}": self.character_mapping.get("father", "父亲"),
            "{mother}": self.character_mapping.get("mother", "母亲"),
            "{teacher}": self.character_mapping.get("math_teacher", "老师"),
            "{friend}": self.character_mapping.get("best_friend", "朋友"),
            "{bully}": self.character_mapping.get("bully", "同学"),
            "{competitor}": self.character_mapping.get("competitor", "同学"),
            "{subject}": random.choice(["数学", "语文", "英语", "物理", "化学"])
        }
        
        event = template
        for key, value in replacements.items():
            event = event.replace(key, value)
            
        return event
    
    async def _enhance_event_with_ai(self, 
                                    base_event: str, 
                                    category: str, 
                                    sentiment: str,
                                    state: Dict) -> str:
        """使用AI增强事件描述，使其更加生动和符合当前情境"""
        prompt = f"""
        请根据以下信息，将基础事件描述扩展为更生动、具体的描述：
        
        基础事件：{base_event}
        事件类别：{category}
        情感倾向：{sentiment}
        
        主角当前状态：
        - 压力水平：{state.get('stress_level', 5)}/10
        - 抑郁程度：{state.get('depression_level', 'MODERATE')}
        - 社交连接：{state.get('social_connection', 5)}/10
        
        要求：
        1. 保持原事件的核心内容
        2. 添加具体的细节（时间、地点、对话片段等）
        3. 描述要符合青少年的真实生活
        4. 长度控制在50-100字
        5. 保留所有人物名称不变
        
        直接返回增强后的事件描述，不要其他内容。
        """
        
        try:
            enhanced = await self.ai_client.generate_response(prompt)
            return enhanced.strip()
        except Exception as e:
            self.logger.error(f"AI增强事件失败: {e}")
            return base_event
    
    async def _generate_ai_event(self, 
                                category: str, 
                                sentiment: str,
                                state: Dict) -> Tuple[str, List[str], int]:
        """当没有合适模板时，完全由AI生成事件"""
        prompt = f"""
        请生成一个符合以下条件的事件：
        
        事件类别：{category}（学业/社交/家庭/个人）
        情感倾向：{sentiment}（积极/消极/中性）
        
        主角信息：
        - 姓名：李明（17岁高中生）
        - 当前压力：{state.get('stress_level', 5)}/10
        - 抑郁程度：{state.get('depression_level', 'MODERATE')}
        
        可用角色：
        - 父亲：李建国
        - 母亲：王秀芳
        - 好友：王小明
        - 霸凌者：刘强
        - 竞争对手：陈优秀
        - 数学老师：张老师
        
        要求：
        1. 事件要真实、符合高中生活
        2. 明确包含相关人物
        3. 50-100字的描述
        4. 避免过于戏剧化
        
        直接返回事件描述。
        """
        
        try:
            event = await self.ai_client.generate_response(prompt)
            event = event.strip()
            participants = self._extract_participants(event)
            impact = self._calculate_impact_score(sentiment, state, {})
            return event, participants, impact
        except Exception as e:
            self.logger.error(f"AI生成事件失败: {e}")
            return "李明度过了平凡的一天", ["李明"], 0
    
    def _extract_participants(self, event: str) -> List[str]:
        """从事件描述中提取参与者"""
        participants = []
        
        # 检查所有已知角色
        for char_key, char_name in self.character_mapping.items():
            if char_name in event:
                participants.append(char_name)
        
        # 确保主角始终在参与者列表中
        protagonist = self.character_mapping.get("protagonist", "李明")
        if protagonist not in participants:
            participants.insert(0, protagonist)
            
        return participants
    
    def _calculate_impact_score(self, 
                               sentiment: str, 
                               state: Dict,
                               stage_config: Dict) -> int:
        """计算事件的影响分数"""
        base_scores = {
            "positive": random.randint(1, 4),
            "negative": random.randint(-6, -2),
            "neutral": random.randint(-1, 1)
        }
        
        score = base_scores.get(sentiment, 0)
        
        # 根据当前状态调整影响
        stress_level = state.get('stress_level', 5)
        if stress_level > 7:
            # 高压力下，负面事件影响更大
            if score < 0:
                score = int(score * 1.5)
            # 正面事件影响减小
            elif score > 0:
                score = int(score * 0.7)
        
        # 根据阶段调整
        stress_modifier = stage_config.get('stress_modifier', 1.0)
        if score < 0:
            score = int(score * stress_modifier)
            
        return max(-10, min(10, score))  # 限制在-10到10之间
    
    async def generate_conditional_event(self, 
                                       condition_name: str,
                                       condition_config: Dict,
                                       state: Dict) -> Optional[Tuple[str, List[str], int]]:
        """生成条件触发的特殊事件"""
        if not condition_config.get("condition", lambda x: False)(state):
            return None
            
        events = condition_config.get("events", [])
        if not events:
            return None
            
        template = random.choice(events)
        event = self._fill_template(template, state)
        
        # 条件事件通常有更大的影响
        impact       = random.randint(-8, -5)
        participants = self._extract_participants(event)
        
        self.logger.info(f"触发条件事件 [{condition_name}]: {event}")
        
        return event, participants, impact
    
    def get_event_variety_score(self) -> float:
        """计算事件多样性分数（0-1）"""
        if len(self.event_history) < 10:
            return 1.0
            
        recent_events = self.event_history[-20:]
        unique_events = len(set(recent_events))
        
        return unique_events / len(recent_events)