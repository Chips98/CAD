import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from pathlib import Path
import importlib
import sys

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).resolve().parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from core.ai_client_factory import ai_client_factory
from core.event_generator import EventGenerator
from models.psychology_models import (
    LifeEvent, EventType, PsychologicalState, EmotionState, 
    DepressionLevel, Relationship
)
from agents.base_agent import BaseAgent

class SimulationEngine:
    """抽象的心理健康模拟引擎"""
    
    def __init__(self, 
                 simulation_id: str, 
                 config_module: str = "sim_config.simulation_config",
                 model_provider: str = None,
                 config_data: Dict[str, Any] = None,
                 psychological_model = None):
        """
        初始化模拟引擎
        
        Args:
            simulation_id: 模拟ID
            config_module: 配置模块路径（向后兼容）
            model_provider: AI模型提供商
            config_data: 完整配置数据（来自新的JSON系统）
            psychological_model: 心理模型实例
        """
        self.simulation_id = simulation_id
        self.simulation_log_dir = Path("logs") / self.simulation_id
        self.simulation_log_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载配置 - 支持新的JSON配置系统
        if config_data:
            # 使用新的JSON配置数据
            self.config = self._create_config_object(config_data)
            config_source = "JSON配置系统"
        else:
            # 向后兼容旧的模块配置系统
            self.config = importlib.import_module(config_module)
            config_source = config_module
        
        # 初始化AI客户端
        self.ai_client = ai_client_factory.get_client(model_provider)
        self.model_provider = model_provider or getattr(__import__('config'), 'DEFAULT_MODEL_PROVIDER', 'gemini')
        
        # 初始化组件
        self.agents: Dict[str, BaseAgent] = {}
        self.protagonist: Optional[BaseAgent] = None
        self.current_day = 1
        self.simulation_log: List[Dict[str, Any]] = []
        self.story_stages = list(self.config.STAGE_CONFIG.keys())
        self.current_stage = 0
        
        # 初始化事件生成器
        self.event_generator = None
        
        # 初始化Rich Console用于美化显示
        self.console = Console()
        
        # 初始化对话记录列表
        self.conversation_log = []
        
        # 存储心理模型实例
        self.psychological_model = psychological_model
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"SimulationEngine initialized for simulation ID: {self.simulation_id}")
        self.logger.info(f"Using configuration from: {config_source}")
        self.logger.info(f"Using AI model provider: {self.model_provider}")
        if psychological_model:
            self.logger.info(f"Using psychological model: {psychological_model.get_display_name()}")
    
    def _create_config_object(self, config_data: Dict[str, Any]):
        """
        从JSON配置数据创建类似模块的配置对象
        
        Args:
            config_data: 完整的配置数据字典
            
        Returns:
            可以像模块一样访问的配置对象
        """
        class ConfigObject:
            def __init__(self, data):
                # 提取场景配置
                scenario = data.get('scenario', {})
                
                # 设置主要配置属性
                self.CHARACTERS = scenario.get('characters', {})
                self.RELATIONSHIPS = scenario.get('relationships', [])
                self.EVENT_TEMPLATES = scenario.get('event_templates', {})
                self.STAGE_CONFIG = scenario.get('stage_config', {})
                self.CONDITIONAL_EVENTS = scenario.get('conditional_events', {})
                self.CAD_IMPACT_RULES = scenario.get('cad_impact_rules', {})
                
                # 设置模拟参数
                simulation_config = data.get('simulation', {})
                self.SIMULATION_DAYS = simulation_config.get('simulation_days', 30)
                self.EVENTS_PER_DAY = simulation_config.get('events_per_day', 5)
                self.SIMULATION_SPEED = simulation_config.get('simulation_speed', 1)
                self.DEPRESSION_DEVELOPMENT_STAGES = simulation_config.get('depression_development_stages', 5)
                self.INTERACTION_FREQUENCY = simulation_config.get('interaction_frequency', 3)
                
                # 设置日志参数
                logging_config = data.get('logging', {})
                self.LOG_LEVEL = logging_config.get('log_level', 'INFO')
                self.SAVE_DAILY_STATES = logging_config.get('save_daily_states', True)
                self.ENABLE_DEBUG_MODE = logging_config.get('enable_debug_mode', False)
                
                # 设置治疗参数
                therapy_config = data.get('therapy', {})
                self.CONVERSATION_HISTORY_LENGTH = therapy_config.get('conversation_history_length', 20)
                self.MAX_EVENTS_TO_SHOW = therapy_config.get('max_events_to_show', 20)
                self.ENABLE_SUPERVISION = therapy_config.get('enable_supervision', True)
                self.SUPERVISION_INTERVAL = therapy_config.get('supervision_interval', 5)
                self.SUPERVISION_ANALYSIS_DEPTH = therapy_config.get('supervision_analysis_depth', 'COMPREHENSIVE')
                
                # 设置恢复参数
                recovery_config = data.get('recovery', {})
                self.IMPROVEMENT_THRESHOLD = recovery_config.get('improvement_threshold', 7.0)
                self.ALLIANCE_THRESHOLD = recovery_config.get('alliance_threshold', 6.0)
                self.EVALUATION_INTERVAL = recovery_config.get('evaluation_interval', 5)
                self.DETERIORATION_THRESHOLD = recovery_config.get('deterioration_threshold', 3.0)
        
        return ConfigObject(config_data)
        
    def setup_simulation(self):
        """根据配置设置模拟环境"""
        # 创建角色名称映射
        character_mapping = {}
        
        # 动态创建agents
        for char_id, char_config in self.config.CHARACTERS.items():
            agent = self._create_agent(char_id, char_config)
            if agent:
                self.agents[agent.name] = agent
                character_mapping[char_id] = agent.name
                
                if char_id == "protagonist":
                    self.protagonist = agent
        
        # 设置关系
        self._setup_relationships()
        
        # 初始化事件生成器
        self.event_generator = EventGenerator(
            self.ai_client,
            self.config.EVENT_TEMPLATES,
            character_mapping,
            self.config
        )
        
        self.logger.info(f"Simulation setup complete with {len(self.agents)} agents")
        
    def _create_agent(self, agent_id: str, config: Dict) -> Optional[BaseAgent]:
        """动态创建agent实例"""
        agent_type = config.get("type")
        if not agent_type:
            self.logger.error(f"No type specified for agent {agent_id}")
            return None
            
        try:
            # 动态导入agent类
            if agent_type in ["FatherAgent", "MotherAgent", "SiblingAgent"]:
                module = importlib.import_module("agents.family_agents")
            elif agent_type in ["TeacherAgent", "ClassmateAgent", "BullyAgent", "BestFriendAgent"]:
                module = importlib.import_module("agents.school_agents")
            elif agent_type == "StudentAgent":
                module = importlib.import_module("agents.student_agent")
            else:
                self.logger.error(f"Unknown agent type: {agent_type}")
                return None
                
            agent_class = getattr(module, agent_type)
            
            # 准备参数
            kwargs = {
                "name": config.get("name"),
                "age": config.get("age"),
                "personality": config.get("personality"),
                "ai_client": self.ai_client,
                "psychological_model": self.psychological_model
            }
            
            # 添加额外参数
            if "extra_params" in config:
                kwargs.update(config["extra_params"])
                
            return agent_class(**kwargs)
            
        except Exception as e:
            self.logger.error(f"Failed to create agent {agent_id}: {e}")
            return None
    
    def _setup_relationships(self):
        """根据配置建立agent之间的关系"""
        for rel_config in self.config.RELATIONSHIPS:
            rel = Relationship(
                person_a=rel_config["person_a"],
                person_b=rel_config["person_b"],
                relationship_type=rel_config["type"],
                closeness=rel_config["closeness"],
                trust_level=rel_config["trust"],
                conflict_level=rel_config["conflict"]
            )
            
            if rel.person_a in self.agents:
                self.agents[rel.person_a].add_relationship(rel)
            if rel.person_b in self.agents:
                self.agents[rel.person_b].add_relationship(rel)
    
    async def run_simulation(self, days: int = 30):
        """运行模拟（美化版）"""
        self.logger.info(f"开始心理健康模拟 (ID: {self.simulation_id})")
        
        # 显示模拟开始信息
        start_panel = Panel.fit(
            f"[bold cyan]🚀 开始心理健康模拟[/bold cyan]\n"
            f"[dim]模拟ID: {self.simulation_id}[/dim]\n"
            f"[dim]总天数: {days}天[/dim]\n"
            f"[dim]主角: {self.protagonist.name if self.protagonist else '未知'}[/dim]",
            border_style="cyan",
            title="📊 模拟开始"
        )
        self.console.print(start_panel)
        
        for day in range(1, days + 1):
            self.current_day = day
            self.current_stage = self._determine_stage(day, days)
            stage_name = self.story_stages[self.current_stage]
            
            # 美化每日标题显示
            day_panel = Panel.fit(
                f"[bold blue]第 {day} 天[/bold blue] - [yellow]{stage_name}[/yellow]\n"
                f"[dim]阶段进度: {self.current_stage + 1}/{len(self.story_stages)}[/dim]",
                border_style="blue",
                title=f"📅 Day {day}"
            )
            self.console.print(day_panel)
            
            self.logger.info(f"第{day}天 - {stage_name} (模拟ID: {self.simulation_id})")
            
            await self._simulate_day()
            self._log_daily_state()
            
            # 添加分隔符
            self.console.print()
            
        # 保存对话记录
        self._save_conversation_log()
            
        self.logger.info(f"模拟结束 (ID: {self.simulation_id})")
        final_report_content = await self._generate_final_report()
        return final_report_content
    
    def _determine_stage(self, current_day: int, total_days: int) -> int:
        """根据进度确定当前阶段"""
        progress = current_day / total_days
        stage_count = len(self.story_stages)
        return min(int(progress * stage_count), stage_count - 1)
    
    async def _simulate_day(self):
        """模拟一天的活动"""
        stage_name = self.story_stages[self.current_stage]
        stage_config = self.config.STAGE_CONFIG[stage_name]
        
        # 生成今天的事件数量
        event_count = random.randint(3, 6)
        
        for _ in range(event_count):
            # 根据权重选择事件类型
            sentiment = self._choose_sentiment(stage_config["event_weights"])
            category = random.choice(stage_config["event_categories"])
            
            # 生成事件
            event_desc, participants, impact = await self.event_generator.generate_event(
                category=category,
                sentiment=sentiment,
                protagonist_state=self._get_protagonist_state(),
                stage_config=stage_config
            )
            
            # 处理事件
            await self._process_event(event_desc, participants, impact)
            
        # 检查条件事件
        await self._check_conditional_events(stage_config)
        
        # 应用阶段效果
        self._apply_stage_effects(stage_config)
        
        # === 新增：每日CAD状态演化 ===
        if self.protagonist and hasattr(self.protagonist, '_perform_daily_cad_evolution'):
            self.protagonist._perform_daily_cad_evolution()
    
    def _choose_sentiment(self, weights: Dict[str, float]) -> str:
        """根据权重选择情感倾向"""
        sentiments = list(weights.keys())
        probabilities = list(weights.values())
        return random.choices(sentiments, weights=probabilities)[0]
    
    def _get_protagonist_state(self) -> Dict:
        """获取主角当前状态（包含CAD-MD深度状态）"""
        if not self.protagonist:
            return {}
            
        state = self.protagonist.psychological_state
        base_state = {
            "stress_level": state.stress_level,
            "depression_level": state.depression_level.name,
            "social_connection": state.social_connection,
            "self_esteem": state.self_esteem,
            "recent_grades": getattr(self.protagonist, 'grades', {})
        }
        
        # === 新增：将CAD状态拍平，支持条件事件访问 ===
        if hasattr(state, 'cad_state'):
            flattened_cad = state.get_flattened_cad_state()
            base_state.update(flattened_cad)
        
        return base_state
    
    async def _process_event(self, event_description: str, participants: List[str], impact_score: int):
        """处理单个事件（美化版）"""
        # 确定事件颜色和图标
        if impact_score < -5:
            event_color = "red"
            event_icon = "💥"
            event_type = EventType.BULLYING if "嘲笑" in event_description else EventType.ACADEMIC_FAILURE
        elif impact_score < -2:
            event_color = "yellow"
            event_icon = "⚠️"
            event_type = EventType.SOCIAL_REJECTION
        elif impact_score < 0:
            event_color = "blue"
            event_icon = "😔"
            event_type = EventType.PEER_PRESSURE
        else:
            event_color = "green"
            event_icon = "😊"
            event_type = EventType.PEER_PRESSURE
        
        # 美化事件显示
        event_panel = Panel.fit(
            f"[{event_color}]{event_icon} {event_description}[/{event_color}]\n"
            f"[dim]参与者: {', '.join(participants)}[/dim]\n"
            f"[dim]影响分数: {impact_score}[/dim]",
            border_style=event_color,
            title="🎭 事件发生"
        )
        # 显示事件面板
        self.console.print(event_panel)
        
        self.logger.info(f"事件: {event_description} (参与者: {', '.join(participants)})")
        
        # 创建生活事件
        life_event = LifeEvent(
            event_type=event_type,
            description=event_description,
            impact_score=impact_score,
            timestamp=datetime.now().isoformat(),
            participants=participants
        )
        
        if self.protagonist and self.protagonist.name in participants:
            self.protagonist.add_life_event(life_event)
        
        # 获取参与者响应并美化显示
        responses = {}
        for agent_name in participants:
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                response = await agent.respond_to_situation(event_description)
                responses[agent_name] = response
                
                # 美化角色回应显示
                if agent_name == self.protagonist.name:
                    response_color = "cyan"
                    response_icon = "💭"
                else:
                    response_color = "white"
                    response_icon = "💬"
                
                response_panel = Panel.fit(
                    f"[{response_color}]{response}[/{response_color}]",
                    border_style=response_color,
                    title=f"{response_icon} {agent_name}"
                )
                # 显示角色响应面板
                self.console.print(response_panel)
                
                self.logger.info(f"【{agent_name}】 回应: {response}")
                
                # 记录对话到conversation_log
                self.conversation_log.append({
                    "day": self.current_day,
                    "stage": self.story_stages[self.current_stage],
                    "timestamp": datetime.now().isoformat(),
                    "event": event_description,
                    "speaker": agent_name,
                    "content": response,
                    "impact_score": impact_score
                })
        
        # 分析互动影响
        impact_analysis = await self.ai_client.analyze_interaction_impact(
            event_description, participants
        )
        
        # 应用影响
        self._apply_interaction_effects(impact_analysis, participants)
        
        # 记录事件
        self.simulation_log.append({
            "day": self.current_day,
            "stage": self.story_stages[self.current_stage],
            "event": event_description,
            "participants": participants,
            "responses": responses,
            "impact": impact_analysis,
            "timestamp": datetime.now().isoformat()
        })
    
    async def _check_conditional_events(self, stage_config: Dict):
        """检查并触发条件事件"""
        protagonist_state = self._get_protagonist_state()
        
        for condition_name, condition_config in self.config.CONDITIONAL_EVENTS.items():
            result = await self.event_generator.generate_conditional_event(
                condition_name, condition_config, protagonist_state
            )
            
            if result:
                event_desc, participants, impact = result
                await self._process_event(event_desc, participants, impact)
    
    def _apply_stage_effects(self, stage_config: Dict):
        """应用阶段性效果"""
        if not self.protagonist:
            return
            
        # 应用压力修正
        stress_modifier = stage_config.get("stress_modifier", 1.0)
        current_stress = self.protagonist.psychological_state.stress_level
        new_stress = min(10, max(0, int(current_stress * stress_modifier)))
        self.protagonist.psychological_state.stress_level = new_stress
        
        # 应用关系衰减
        relationship_decay = stage_config.get("relationship_decay", 1.0)
        for rel_name, relationship in self.protagonist.relationships.items():
            relationship.closeness = max(0, int(relationship.closeness * relationship_decay))
            relationship.trust_level = max(0, int(relationship.trust_level * relationship_decay))
    
    def _apply_interaction_effects(self, impact_analysis: Dict[str, Any], 
                                 participants: List[str]):
        """应用互动效果到agents"""
        if "participant_impacts" in impact_analysis:
            for agent_name, impacts in impact_analysis["participant_impacts"].items():
                if agent_name in self.agents:
                    agent = self.agents[agent_name]
                    
                    if "stress_change" in impacts:
                        stress_change = impacts.get("stress_change", 0)
                        if isinstance(stress_change, (int, float)):
                            agent.psychological_state.stress_level = max(0, min(10,
                                agent.psychological_state.stress_level + stress_change))
    
    def _log_daily_state(self):
        """记录每日状态（包含CAD状态）"""
        if not self.protagonist:
            return
            
        # 收集所有事件
        daily_events = []
        for event in self.simulation_log:
            if event["day"] == self.current_day:
                daily_events.append({
                    "description": event["event"],
                    "participants": event["participants"],
                    "impact_score": event.get("impact", {}).get("impact_score", 0)
                })
        
        # 获取主角当前的心理状态（包含CAD状态）
        current_mental_state = self.protagonist.psychological_state.to_dict()
        
        # 确保CAD状态被包含
        if hasattr(self.protagonist, 'cad_state') and self.protagonist.cad_state:
            current_mental_state["cad_state"] = {
                "affective_tone": self.protagonist.cad_state.affective_tone,
                "core_beliefs": {
                    "self_belief": self.protagonist.cad_state.core_beliefs.self_belief,
                    "world_belief": self.protagonist.cad_state.core_beliefs.world_belief,
                    "future_belief": self.protagonist.cad_state.core_beliefs.future_belief
                },
                "cognitive_processing": {
                    "rumination": self.protagonist.cad_state.cognitive_processing.rumination,
                    "distortions": self.protagonist.cad_state.cognitive_processing.distortions
                },
                "behavioral_inclination": {
                    "social_withdrawal": self.protagonist.cad_state.behavioral_inclination.social_withdrawal,
                    "avolition": self.protagonist.cad_state.behavioral_inclination.avolition
                }
            }
        elif hasattr(self.protagonist.psychological_state, 'cad_state') and self.protagonist.psychological_state.cad_state:
            if "cad_state" not in current_mental_state:
                current_mental_state["cad_state"] = self.protagonist.psychological_state.cad_state.to_dict()
        
        state_log = {
            "day": self.current_day,
            "stage": self.story_stages[self.current_stage],
            "events": daily_events,
            "protagonist": {
                "name": self.protagonist.name,
                "age": self.protagonist.age,
                "current_mental_state": current_mental_state,
                "symptoms": self.protagonist.get_depression_symptoms(),
                "risk_factors": self.protagonist._identify_risk_factors()
            },
            "relationships": {
                name: rel.to_dict() 
                for name, rel in self.protagonist.relationships.items()
            }
        }
        
        # 保存到文件
        daily_state_file = self.simulation_log_dir / f"day_{self.current_day}_state.json"
        try:
            with open(daily_state_file, "w", encoding="utf-8") as f:
                json.dump(state_log, f, ensure_ascii=False, indent=2)
            self.logger.info(f"每日状态已保存到: {daily_state_file}")
        except IOError as e:
            self.logger.error(f"无法写入每日状态文件: {e}")
    
    def _save_conversation_log(self):
        """保存对话记录到JSON文件"""
        if not self.conversation_log:
            return
            
        conversation_file = self.simulation_log_dir / "conversation_log.json"
        try:
            conversation_data = {
                "simulation_id": self.simulation_id,
                "protagonist_name": self.protagonist.name if self.protagonist else "未知",
                "total_conversations": len(self.conversation_log),
                "conversations": self.conversation_log,
                "generated_at": datetime.now().isoformat()
            }
            
            with open(conversation_file, "w", encoding="utf-8") as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"对话记录已保存到: {conversation_file}")
            
            # 在控制台显示保存信息
            save_panel = Panel.fit(
                f"[bold green]💾 对话记录已保存[/bold green]\n"
                f"[dim]文件位置: {conversation_file}[/dim]\n"
                f"[dim]总对话数: {len(self.conversation_log)}[/dim]",
                border_style="green",
                title="📝 记录保存"
            )
            self.console.print(save_panel)
            
        except IOError as e:
            self.logger.error(f"无法保存对话记录文件: {e}")
            self.console.print(f"[red]❌ 对话记录保存失败: {e}[/red]")
    
    def _validate_json_structure(self, obj, path="root"):
        """验证JSON结构，检查是否有不可序列化的对象"""
        try:
            if isinstance(obj, dict):
                for key, value in obj.items():
                    self._validate_json_structure(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    self._validate_json_structure(item, f"{path}[{i}]")
            elif isinstance(obj, (str, int, float, bool, type(None))):
                # 这些类型都是JSON安全的
                pass
            else:
                # 检查是否有__dict__属性，可能是对象
                if hasattr(obj, '__dict__'):
                    raise ValueError(f"在路径 {path} 发现不可序列化的对象: {type(obj)}")
                # 尝试转换为字符串
                str(obj)
        except Exception as e:
            self.logger.error(f"JSON结构验证失败在路径 {path}: {e}")
            raise

    async def _generate_final_report(self):
        """生成最终报告"""
        if not self.protagonist:
            return {}
        
        # 获取主角的角色配置信息
        protagonist_config = self.config.CHARACTERS.get("protagonist", {})
        character_profile = {
            "name": protagonist_config.get("name", self.protagonist.name),
            "age": protagonist_config.get("age", self.protagonist.age),
            "personality": protagonist_config.get("personality", {}),
            "background": protagonist_config.get("background", {}),
            "initial_relationships": protagonist_config.get("relationships", {})
        }
            
        # 获取CAD状态信息
        cad_state_data = {}
        if hasattr(self.protagonist, 'cad_state') and self.protagonist.cad_state:
            cad_state_data = {
                "affective_tone": self.protagonist.cad_state.affective_tone,
                "core_beliefs": {
                    "self_belief": self.protagonist.cad_state.core_beliefs.self_belief,
                    "world_belief": self.protagonist.cad_state.core_beliefs.world_belief,
                    "future_belief": self.protagonist.cad_state.core_beliefs.future_belief
                },
                "cognitive_processing": {
                    "rumination": self.protagonist.cad_state.cognitive_processing.rumination,
                    "distortions": self.protagonist.cad_state.cognitive_processing.distortions
                },
                "behavioral_inclination": {
                    "social_withdrawal": self.protagonist.cad_state.behavioral_inclination.social_withdrawal,
                    "avolition": self.protagonist.cad_state.behavioral_inclination.avolition
                }
            }
        elif hasattr(self.protagonist.psychological_state, 'cad_state') and self.protagonist.psychological_state.cad_state:
            cad_state_data = self.protagonist.psychological_state.cad_state.to_dict()

        # 获取最终心理状态（包含CAD状态）
        final_psychological_state = self.protagonist.psychological_state.to_dict()
        if cad_state_data:
            final_psychological_state["cad_state"] = cad_state_data

        report = {
            "simulation_summary": {
                "simulation_id": self.simulation_id,
                "total_days": self.current_day,
                "final_stage": self.story_stages[self.current_stage],
                "final_depression_level": self.protagonist.psychological_state.depression_level.value,
                "total_events": len(self.simulation_log),
                "event_variety_score": self.event_generator.get_event_variety_score()
            },
            "protagonist_character_profile": character_profile,
            "final_psychological_state": final_psychological_state,
            "protagonist_journey": {
                "initial_state": "健康",
                "final_state": self.protagonist.get_status_summary(),
                "key_symptoms": self.protagonist.get_depression_symptoms(),
                "risk_factors": self.protagonist._identify_risk_factors(),
                "cad_state": cad_state_data  # 单独添加CAD状态用于快速访问
            },
            "relationship_changes": {
                name: rel.to_dict() 
                for name, rel in self.protagonist.relationships.items()
            },
            "significant_events": [
                event.to_dict() for event in self.protagonist.life_events
                if event.impact_score <= -5
            ]
        }
        
        # AI分析（增强版，包含CAD状态分析）
        cad_analysis_section = ""
        if cad_state_data:
            # 导入CAD状态映射器进行专业分析
            try:
                from models.cad_state_mapper import CADStateMapper
                from models.psychology_models import CognitiveAffectiveState, CoreBeliefs, CognitiveProcessing, BehavioralInclination
                
                # 重构CAD状态对象
                cad_obj = CognitiveAffectiveState(
                    affective_tone=cad_state_data.get("affective_tone", 0),
                    core_beliefs=CoreBeliefs(
                        self_belief=cad_state_data.get("core_beliefs", {}).get("self_belief", 0),
                        world_belief=cad_state_data.get("core_beliefs", {}).get("world_belief", 0),
                        future_belief=cad_state_data.get("core_beliefs", {}).get("future_belief", 0)
                    ),
                    cognitive_processing=CognitiveProcessing(
                        rumination=cad_state_data.get("cognitive_processing", {}).get("rumination", 0),
                        distortions=cad_state_data.get("cognitive_processing", {}).get("distortions", 0)
                    ),
                    behavioral_inclination=BehavioralInclination(
                        social_withdrawal=cad_state_data.get("behavioral_inclination", {}).get("social_withdrawal", 0),
                        avolition=cad_state_data.get("behavioral_inclination", {}).get("avolition", 0)
                    )
                )
                
                cad_analysis_section = f"""
        
6. CAD认知-情感-行为状态分析：
{CADStateMapper.generate_therapist_analysis(cad_obj, self.protagonist.name)}

治疗优先级建议：
{', '.join(CADStateMapper.identify_treatment_priorities(cad_obj))}
"""
            except Exception as e:
                self.logger.warning(f"生成CAD状态分析时出错: {e}")
                cad_analysis_section = f"""
        
6. CAD认知-情感-行为状态分析：
- 情感基调: {cad_state_data.get("affective_tone", 0):.1f}/10
- 自我信念: {cad_state_data.get("core_beliefs", {}).get("self_belief", 0):.1f}/10
- 世界观信念: {cad_state_data.get("core_beliefs", {}).get("world_belief", 0):.1f}/10
- 未来信念: {cad_state_data.get("core_beliefs", {}).get("future_belief", 0):.1f}/10
- 反刍思维: {cad_state_data.get("cognitive_processing", {}).get("rumination", 0):.1f}/10
- 认知扭曲: {cad_state_data.get("cognitive_processing", {}).get("distortions", 0):.1f}/10
- 社交退缩: {cad_state_data.get("behavioral_inclination", {}).get("social_withdrawal", 0):.1f}/10
- 意志缺失: {cad_state_data.get("behavioral_inclination", {}).get("avolition", 0):.1f}/10
"""

        prompt = f"""
        请对以下心理健康模拟结果进行专业分析和总结：
        
        {json.dumps(report, ensure_ascii=False, indent=2)}
        
        请从以下角度分析：
        1. 抑郁症发展过程分析
        2. 关键风险因素识别
        3. 干预机会点分析
        4. 对现实情况的启示
        5. 本次模拟的特点{cad_analysis_section}
        
        请特别关注患者的认知-情感-行为三元模型(CAD)状态，这对理解抑郁症的认知机制至关重要。
        请确保分析的专业性和深度。
        """
        
        try:
            ai_analysis = await self.ai_client.generate_response(prompt)
            report["ai_analysis"] = ai_analysis
        except Exception as e:
            self.logger.error(f"生成AI分析时发生错误: {e}")
            report["ai_analysis"] = "AI分析生成失败。"
        
        # 保存报告
        final_report_file = self.simulation_log_dir / "final_report.json"
        try:
            # 验证JSON结构
            self._validate_json_structure(report)
            
            with open(final_report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            self.logger.info(f"最终报告已保存到: {final_report_file}")
            
            # 验证生成的JSON格式是否正确
            try:
                with open(final_report_file, "r", encoding="utf-8") as f:
                    json.load(f)
                self.logger.info("JSON格式验证通过")
            except json.JSONDecodeError as json_error:
                self.logger.error(f"生成的JSON格式有误: {json_error}")
                
        except IOError as e:
            self.logger.error(f"无法写入最终报告文件: {e}")
        except ValueError as e:
            self.logger.error(f"JSON结构验证失败: {e}")
            
        return report 