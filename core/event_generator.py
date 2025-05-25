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
    
    def __init__(self, ai_client, event_templates: Dict, character_mapping: Dict, config=None):
        self.ai_client = ai_client
        self.event_templates = event_templates
        self.character_mapping = character_mapping  # 角色名称映射
        self.config = config  # 配置模块
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
        # 自动构建替换规则
        replacements = {}
        
        # 1. 从character_mapping自动生成所有角色的替换规则
        for char_id, char_name in self.character_mapping.items():
            # 生成占位符格式 {char_id}
            placeholder = f"{{{char_id}}}"
            replacements[placeholder] = char_name
        
        # 2. 添加特殊的非角色占位符
        special_replacements = {
            "{subject}": self._get_random_subject(),
            "{time}": self._get_random_time(),
            "{location}": self._get_random_location(),
        }
        replacements.update(special_replacements)
        
        # 3. 执行替换
        event = template
        for placeholder, value in replacements.items():
            event = event.replace(placeholder, value)
        
        # 4. 检查是否有未替换的占位符（用于调试）
        import re
        unmatched = re.findall(r'\{(\w+)\}', event)
        if unmatched:
            self.logger.warning(f"未匹配的占位符: {unmatched}")
            
        return event
    
    def _get_random_subject(self) -> str:
        """获取随机科目"""
        # 如果配置中有科目列表，使用配置的
        if self.config and hasattr(self.config, 'SUBJECTS'):
            return random.choice(self.config.SUBJECTS)
        
        # 否则根据场景类型返回默认科目
        if self.config and hasattr(self.config, 'SCENARIO_TYPE'):
            scenario_type = self.config.SCENARIO_TYPE
            if scenario_type == "university":
                return random.choice(["高等数学", "计算机科学", "英语", "专业课", "通识课"])
            elif scenario_type == "workplace":
                return random.choice(["项目报告", "技术方案", "业务分析", "客户提案", "工作总结"])
        
        # 默认高中科目
        return random.choice(["数学", "语文", "英语", "物理", "化学"])
    
    def _get_random_time(self) -> str:
        """获取随机时间描述"""
        times = ["早上", "上午", "中午", "下午", "傍晚", "晚上", "深夜"]
        return random.choice(times)
    
    def _get_random_location(self) -> str:
        """获取随机地点"""
        # 根据场景类型返回不同的地点
        if self.config and hasattr(self.config, 'SCENARIO_TYPE'):
            scenario_type = self.config.SCENARIO_TYPE
            if scenario_type == "university":
                return random.choice(["教室", "图书馆", "宿舍", "食堂", "操场", "实验室"])
            elif scenario_type == "workplace":
                return random.choice(["办公室", "会议室", "茶水间", "电梯间", "停车场"])
        
        # 默认高中场景
        return random.choice(["教室", "操场", "食堂", "图书馆", "走廊"])
    
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
        3. 描述要符合角色的真实生活背景
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
        # 获取主角信息
        protagonist_name = self.character_mapping.get("protagonist", "主角")
        
        # 如果有配置，尝试获取更详细的信息
        protagonist_info = {"name": protagonist_name, "age": 17, "description": "学生"}
        if self.config and hasattr(self.config, 'CHARACTERS'):
            for char_id, char_info in self.config.CHARACTERS.items():
                if char_info.get('role') == 'protagonist' or char_info.get('name') == protagonist_name:
                    protagonist_info = char_info
                    break
        
        # 构建可用角色列表
        available_roles = []
        
        # 从 character_mapping 和配置构建角色列表
        for char_id, char_name in self.character_mapping.items():
            if char_id != "protagonist" and char_name:
                # 尝试从配置中获取角色描述
                role_desc = "角色"  # 默认描述
                
                if self.config and hasattr(self.config, 'CHARACTERS'):
                    char_config = self.config.CHARACTERS.get(char_id, {})
                    # 尝试获取角色类型或描述
                    if 'role_type' in char_config:
                        role_desc = char_config['role_type']
                    elif 'description' in char_config:
                        role_desc = char_config['description']
                    elif 'type' in char_config:
                        # 从类型推断角色描述
                        type_mapping = {
                            "FatherAgent": "父亲",
                            "MotherAgent": "母亲",
                            "TeacherAgent": "老师",
                            "ClassmateAgent": "同学",
                            "BestFriendAgent": "好友",
                            "BullyAgent": "霸凌者",
                            "SiblingAgent": "兄弟姐妹"
                        }
                        role_desc = type_mapping.get(char_config['type'], "角色")
                    
                    # 检查extra_params中的关系描述
                    if 'extra_params' in char_config:
                        if 'relationship_with_protagonist' in char_config['extra_params']:
                            role_desc = char_config['extra_params']['relationship_with_protagonist']
                
                role_line = f"- {role_desc}: {char_name}"
                available_roles.append(role_line)
        
        roles_text = "\n        ".join(available_roles)
        
        prompt = f"""
        请生成一个符合以下条件的事件：
        
        事件类别：{category}（学业/社交/家庭/个人）
        情感倾向：{sentiment}（积极/消极/中性）
        
        主角信息：
        - 姓名：{protagonist_info.get('name', '主角')}（{protagonist_info.get('age', 17)}岁{protagonist_info.get('description', '学生')}）
        - 当前压力：{state.get('stress_level', 5)}/10
        - 抑郁程度：{state.get('depression_level', 'MODERATE')}
        
        可用角色：
        {roles_text}
        
        要求：
        1. 事件要真实、符合角色背景
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
            protagonist_name = self.character_mapping.get("protagonist", "主角")
            return f"{protagonist_name}度过了平凡的一天", [protagonist_name], 0
    
    def _extract_participants(self, event: str) -> List[str]:
        """从事件描述中提取参与者"""
        participants = []
        
        # 检查所有已知角色
        for char_key, char_name in self.character_mapping.items():
            if char_name in event:
                participants.append(char_name)
        
        # 确保主角始终在参与者列表中
        protagonist = self.character_mapping.get("protagonist", "主角")
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