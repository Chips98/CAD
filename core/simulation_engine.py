import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from pathlib import Path

from core.ai_client_factory import ai_client_factory
from core.gemini_client import GeminiClient
from core.deepseek_client import DeepSeekClient
from models.psychology_models import (
    LifeEvent, EventType, PsychologicalState, EmotionState, 
    DepressionLevel, Relationship
)
from agents.base_agent import BaseAgent
from agents.student_agent import StudentAgent
from agents.family_agents import FatherAgent, MotherAgent, SiblingAgent
from agents.school_agents import TeacherAgent, ClassmateAgent, BullyAgent, BestFriendAgent

class SimulationEngine:
    """心理健康模拟引擎"""
    
    def __init__(self, simulation_id: str, model_provider: str = None):
        self.ai_client = ai_client_factory.get_client(model_provider)
        self.model_provider = model_provider or getattr(__import__('config'), 'DEFAULT_MODEL_PROVIDER', 'gemini')
        self.simulation_id = simulation_id
        self.simulation_log_dir = Path("logs") / self.simulation_id
        self.simulation_log_dir.mkdir(parents=True, exist_ok=True)
        
        self.agents: Dict[str, BaseAgent] = {}
        self.protagonist: Optional[StudentAgent] = None
        self.current_day = 1
        self.simulation_log: List[Dict[str, Any]] = []
        self.story_stages = [
            "健康阶段", "压力积累", "初期问题", "关系恶化", "抑郁发展"
        ]
        self.current_stage = 0
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"SimulationEngine initialized for simulation ID: {self.simulation_id}")
        self.logger.info(f"Using AI model provider: {self.model_provider}")
        self.logger.info(f"Output directory set to: {self.simulation_log_dir}")
        
    def setup_simulation(self):
        """设置模拟环境"""
        self.protagonist = StudentAgent(
            name="李明",
            age=17,
            personality={
                "traits": ["内向", "敏感", "努力", "完美主义"],
                "openness": 6,
                "conscientiousness": 8,
                "extraversion": 4,
                "agreeableness": 7,
                "neuroticism": 6
            },
            ai_client=self.ai_client
        )
        self.agents["李明"] = self.protagonist
        
        father = FatherAgent(
            name="李建国",
            age=45,
            personality={
                "occupation": "工程师",
                "parenting_style": "严厉型",
                "expectations": "考上重点大学",
                "traditional_values": True,
                "work_pressure": 7,
                "communication_style": "直接但缺乏情感表达"
            },
            ai_client=self.ai_client
        )
        self.agents["李建国"] = father
        
        mother = MotherAgent(
            name="王秀芳",
            age=42,
            personality={
                "occupation": "会计",
                "parenting_style": "焦虑型",
                "expectations": "孩子健康快乐",
                "emotional_sensitivity": 9,
                "anxiety_level": 8,
                "nurturing_instinct": 9
            },
            ai_client=self.ai_client
        )
        self.agents["王秀芳"] = mother
        
        math_teacher = TeacherAgent(
            name="张老师",
            age=38,
            personality={
                "experience_years": 15,
                "teaching_style": "严厉型",
                "strictness": 8,
                "empathy": 4,
                "expectations": "高"
            },
            ai_client=self.ai_client,
            subject="数学"
        )
        self.agents["张老师"] = math_teacher
        
        best_friend = BestFriendAgent(
            name="王小明",
            age=17,
            personality={
                "empathy": 9,
                "loyalty": 9,
                "support_ability": 8,
                "shared_interests": ["篮球", "游戏", "学习"]
            },
            ai_client=self.ai_client
        )
        self.agents["王小明"] = best_friend
        
        bully = BullyAgent(
            name="刘强",
            age=18,
            personality={
                "aggression": 9,
                "insecurity": 8,
                "control_need": 9,
                "popularity": 6
            },
            ai_client=self.ai_client
        )
        self.agents["刘强"] = bully
        
        competitor = ClassmateAgent(
            name="陈优秀",
            age=17,
            personality={
                "competitive": 9,
                "empathy": 3,
                "popularity": 7,
                "academic_performance": 9
            },
            ai_client=self.ai_client,
            relationship_with_protagonist="竞争对手"
        )
        self.agents["陈优秀"] = competitor
        
        self._setup_relationships()
        
    def _setup_relationships(self):
        """建立agent之间的关系"""
        relationships = [
            Relationship("李明", "李建国", "父子", 6, 6, 3),
            Relationship("李明", "王秀芳", "母子", 8, 8, 2),
            Relationship("李明", "王小明", "好友", 9, 9, 1),
            Relationship("李明", "刘强", "同学", 2, 1, 8),
            Relationship("李明", "陈优秀", "同学", 4, 3, 6),
            Relationship("李明", "张老师", "师生", 5, 4, 4),
        ]
        
        for rel in relationships:
            if rel.person_a in self.agents:
                self.agents[rel.person_a].add_relationship(rel)
            if rel.person_b in self.agents:
                self.agents[rel.person_b].add_relationship(rel)
    
    async def run_simulation(self, days: int = 30):
        """运行模拟"""
        self.logger.info(f"开始心理健康模拟 (ID: {self.simulation_id})")
        
        for day in range(1, days + 1):
            self.current_day = day
            if day <= days * 0.2:
                self.current_stage = 0
            elif day <= days * 0.4:
                self.current_stage = 1
            elif day <= days * 0.6:
                self.current_stage = 2
            elif day <= days * 0.8:
                self.current_stage = 3
            else:
                self.current_stage = 4
            
            self.logger.info(f"第{day}天 - {self.story_stages[self.current_stage]} (模拟ID: {self.simulation_id})")
            
            await self._simulate_day()
            self._log_daily_state()
            await self._check_and_trigger_events()
            
        self.logger.info(f"模拟结束 (ID: {self.simulation_id})")
        final_report_content = await self._generate_final_report()
        return final_report_content
    
    async def _simulate_day(self):
        """模拟一天的活动"""
        if self.current_stage == 0:
            await self._simulate_normal_day()
        elif self.current_stage == 1:
            await self._simulate_stress_building()
        elif self.current_stage == 2:
            await self._simulate_early_problems()
        elif self.current_stage == 3:
            await self._simulate_relationship_deterioration()
        else:
            await self._simulate_depression_development()
    
    async def _simulate_normal_day(self):
        """模拟正常一天"""
        events = [
            "上学路上与好友愉快交谈",
            "数学课认真听讲",
            "午休时间和同学聊天",
            "篮球课后练习",
            "回家后完成作业"
        ]
        
        for event in events:
            await self._process_interaction(event, ["李明"])
            
    async def _simulate_stress_building(self):
        """模拟压力积累阶段"""
        events = [
            "数学考试成绩不理想",
            "父亲对成绩表示不满",
            "老师批评学习态度",
            "作业量增加感到压力",
            "开始熬夜学习"
        ]
        
        poor_grade_event = LifeEvent(
            event_type=EventType.ACADEMIC_FAILURE,
            description="数学考试只考了72分",
            impact_score=-4,
            timestamp=datetime.now().isoformat(),
            participants=["李明", "张老师"]
        )
        self.protagonist.add_life_event(poor_grade_event)
        self.protagonist.add_grade("数学", 72)
        
        for event in events:
            participants = self._identify_participants(event)
            await self._process_interaction(event, participants)
    
    async def _simulate_early_problems(self):
        """模拟初期问题阶段"""
        events = [
            "连续几次考试成绩下降",
            "开始被同学嘲笑成绩",
            "与好友发生小摩擦",
            "在课堂上被老师点名批评",
            "回家后被父母责备"
        ]
        
        rejection_event = LifeEvent(
            event_type=EventType.SOCIAL_REJECTION,
            description="一些同学开始疏远自己",
            impact_score=-5,
            timestamp=datetime.now().isoformat(),
            participants=["李明", "陈优秀", "刘强"]
        )
        self.protagonist.add_life_event(rejection_event)
        
        for event in events:
            participants = self._identify_participants(event)
            await self._process_interaction(event, participants)
    
    async def _simulate_relationship_deterioration(self):
        """模拟关系恶化阶段"""
        events = [
            "刘强开始有针对性的嘲讽",
            "与父亲发生激烈争吵",
            "感觉老师对自己有偏见",
            "发现朋友在背后议论自己",
            "开始逃避社交活动"
        ]
        
        bullying_event = LifeEvent(
            event_type=EventType.BULLYING,
            description="在教室里被刘强当众嘲笑",
            impact_score=-7,
            timestamp=datetime.now().isoformat(),
            participants=["李明", "刘强"]
        )
        self.protagonist.add_life_event(bullying_event)
        
        self.protagonist.update_relationship("刘强", closeness_change=-2, trust_change=-3, conflict_change=3)
        self.protagonist.update_relationship("李建国", closeness_change=-2, trust_change=-2, conflict_change=2)
        
        for event in events:
            participants = self._identify_participants(event)
            await self._process_interaction(event, participants)
    
    async def _simulate_depression_development(self):
        """模拟抑郁症发展阶段"""
        events = [
            "开始出现睡眠问题",
            "对以前喜欢的活动失去兴趣",
            "经常感到疲惫和无望",
            "在家中变得沉默寡言",
            "学习成绩继续下滑"
        ]
        
        depression_event = LifeEvent(
            event_type=EventType.EXAM_STRESS,
            description="面对期末考试感到极度绝望",
            impact_score=-8,
            timestamp=datetime.now().isoformat(),
            participants=["李明"]
        )
        self.protagonist.add_life_event(depression_event)
        
        for event in events:
            participants = self._identify_participants(event)
            await self._process_interaction(event, participants)
            
        await self.protagonist.internal_monologue("感觉自己陷入了无尽的黑暗中")
    
    def _identify_participants(self, event: str) -> List[str]:
        """识别事件参与者"""
        participants = ["李明"]
        
        if "父亲" in event or "争吵" in event:
            participants.append("李建国")
        if "母亲" in event or "家" in event:
            participants.append("王秀芳")
        if "老师" in event or "课堂" in event:
            participants.append("张老师")
        if "朋友" in event or "王小明" in event:
            participants.append("王小明")
        if "刘强" in event or "嘲笑" in event or "嘲讽" in event:
            participants.append("刘强")
        if "同学" in event:
            participants.extend(["陈优秀", "王小明"])
            
        return list(set(participants))
    
    async def _process_interaction(self, event_description: str, participants: List[str]):
        """处理互动事件"""
        self.logger.info(f"事件: {event_description} (参与者: {', '.join(participants)})")
        
        responses = {}
        for agent_name in participants:
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                response = await agent.respond_to_situation(event_description)
                responses[agent_name] = response
                self.logger.info(f"{agent_name} 回应: {response}")
        
        impact_analysis = await self.ai_client.analyze_interaction_impact(
            event_description, participants
        )
        
        self._apply_interaction_effects(impact_analysis, participants)
        
        interaction_log_entry = {
            "day": self.current_day,
            "stage": self.story_stages[self.current_stage],
            "event": event_description,
            "participants": participants,
            "responses": responses,
            "impact": impact_analysis,
            "timestamp": datetime.now().isoformat()
        }
        self.simulation_log.append(interaction_log_entry)
    
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
    
    async def _check_and_trigger_events(self):
        """检查并触发特殊事件"""
        if self.protagonist.psychological_state.depression_level.value >= 2:
            if random.random() < 0.3:
                await self._trigger_family_concern()
        
        if self.protagonist.psychological_state.depression_level.value >= 3:
            if random.random() < 0.4:
                await self._trigger_friend_concern()
    
    async def _trigger_family_concern(self):
        """触发家人关心事件"""
        mother = self.agents.get("王秀芳")
        if mother and isinstance(mother, MotherAgent):
            concern_response = await mother.comfort_child(
                self.protagonist.psychological_state.emotion
            )
            self.logger.info(f"家人关心事件 - 王秀芳: {concern_response}")
            
            self.protagonist.psychological_state.social_connection = min(10,
                self.protagonist.psychological_state.social_connection + 1)
    
    async def _trigger_friend_concern(self):
        """触发朋友担心事件"""
        friend = self.agents.get("王小明")
        if friend and isinstance(friend, BestFriendAgent):
            support_response = await friend.provide_emotional_support(
                self.protagonist.psychological_state.emotion
            )
            self.logger.info(f"朋友关心事件 - 王小明: {support_response}")
            
            self.protagonist.psychological_state.stress_level = max(0,
                self.protagonist.psychological_state.stress_level - 1)
    
    def _log_daily_state(self):
        """记录每日状态到特定模拟子目录"""
        state_log = {
            "day": self.current_day,
            "stage": self.story_stages[self.current_stage],
            "protagonist_state": self.protagonist.get_detailed_status(),
            "depression_symptoms": self.protagonist.get_depression_symptoms(),
            "risk_factors": self.protagonist._identify_risk_factors(),
            "relationships": {name: rel.to_dict() for name, rel in self.protagonist.relationships.items()}
        }
        
        daily_state_file_path = self.simulation_log_dir / f"day_{self.current_day}_state.json"
        try:
            with open(daily_state_file_path, "w", encoding="utf-8") as f:
                json.dump(state_log, f, ensure_ascii=False, indent=2)
            self.logger.info(f"每日状态已保存到: {daily_state_file_path}")
        except IOError as e:
            self.logger.error(f"无法写入每日状态文件 {daily_state_file_path}: {e}")
    
    async def _generate_final_report(self):
        """生成最终报告并保存到特定模拟子目录"""
        report = {
            "simulation_summary": {
                "simulation_id": self.simulation_id,
                "total_days": self.current_day,
                "final_stage": self.story_stages[self.current_stage],
                "final_depression_level": self.protagonist.psychological_state.depression_level.name,
                "total_events": len(self.simulation_log)
            },
            "protagonist_journey": {
                "initial_state": "健康",
                "final_state": self.protagonist.get_status_summary(),
                "key_symptoms": self.protagonist.get_depression_symptoms(),
                "risk_factors": self.protagonist._identify_risk_factors()
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
        
        prompt = f"""
        请对以下心理健康模拟结果进行专业分析和总结 (模拟ID: {self.simulation_id})：
        
        {json.dumps(report, ensure_ascii=False, indent=2)}
        
        请从以下角度分析：
        1. 抑郁症发展过程分析 (基于每日状态变化和关键事件)
        2. 关键风险因素识别 (不仅仅是最终状态，而是整个过程中的)
        3. 干预机会点分析 (在哪个阶段或事件后进行干预可能最有效)
        4. 对现实情况的启示 (对青少年心理健康的普遍性建议)
        5. 总结本次模拟的特点和主角的独特性。
        请确保分析的专业性和深度。
        """
        
        self.logger.info("正在生成AI分析总结...")
        try:
            ai_analysis = await self.ai_client.generate_response(prompt)
            report["ai_analysis"] = ai_analysis
            self.logger.info("AI分析总结已生成。")
        except Exception as e:
            self.logger.error(f"生成AI分析时发生错误: {e}")
            report["ai_analysis"] = "AI分析生成失败。"
        
        final_report_file_path = self.simulation_log_dir / "final_report.json"
        try:
            with open(final_report_file_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            self.logger.info(f"最终报告已保存到: {final_report_file_path}")
        except IOError as e:
            self.logger.error(f"无法写入最终报告文件 {final_report_file_path}: {e}")
            
        return report 