from typing import Dict, List, Any
from agents.base_agent import BaseAgent
from models.psychology_models import EmotionState
from core.gemini_client import GeminiClient

class TeacherAgent(BaseAgent):
    """老师Agent"""
    
    def __init__(self, name: str, age: int, personality: Dict[str, Any], 
                 gemini_client: GeminiClient, subject: str):
        super().__init__(name, age, personality, gemini_client)
        self.subject = subject
        self.teaching_experience = personality.get("experience_years", 10)
        self.teaching_style = personality.get("teaching_style", "传统型")
        self.strictness_level = personality.get("strictness", 6)  # 1-10
        self.empathy_level = personality.get("empathy", 5)  # 1-10
        self.student_expectations = personality.get("expectations", "高")
        
    def get_role_description(self) -> str:
        """获取角色描述"""
        return f"一位教授{self.subject}的老师，{self.teaching_experience}年教学经验，教学风格{self.teaching_style}，对学生要求{self.student_expectations}"
    
    def get_current_concerns(self) -> List[str]:
        """获取当前关注的问题"""
        concerns = ["学生的学习成绩", "教学质量", "课堂纪律"]
        
        if self.empathy_level > 7:
            concerns.insert(0, "学生的心理健康")
        
        if self.strictness_level > 7:
            concerns.append("学生的行为规范")
        
        concerns.append("教学任务完成情况")
        
        return concerns
    
    async def respond_to_student_performance(self, student_name: str, 
                                           performance: str, score: int) -> str:
        """对学生表现的回应"""
        if score < 60:  # 不及格
            if self.teaching_style == "严厉型":
                situation = f"{student_name}{performance}，成绩{score}分，我需要严厉批评"
            elif self.empathy_level > 6:
                situation = f"{student_name}{performance}，成绩{score}分，我担心他的学习状况"
            else:
                situation = f"{student_name}{performance}，成绩{score}分，需要改进"
        elif score >= 90:  # 优秀
            situation = f"{student_name}{performance}，成绩{score}分，值得表扬"
        else:  # 一般
            situation = f"{student_name}{performance}，成绩{score}分，还有提升空间"
            
        return await self.respond_to_situation(situation)
    
    async def handle_student_problem(self, student_name: str, 
                                   problem_description: str) -> str:
        """处理学生问题"""
        if self.empathy_level > 7:
            situation = f"{student_name}遇到{problem_description}，我想耐心帮助他解决"
        elif self.strictness_level > 7:
            situation = f"{student_name}出现{problem_description}，需要严格处理"
        else:
            situation = f"{student_name}的{problem_description}需要处理"
            
        return await self.respond_to_situation(situation)
    
    def notice_student_change(self, student_name: str, changes: List[str]) -> bool:
        """注意到学生变化"""
        # 有经验且共情能力强的老师更容易注意到学生变化
        sensitivity = (self.empathy_level + self.teaching_experience / 2) / 10
        return len(changes) > (3 - sensitivity * 2)


class ClassmateAgent(BaseAgent):
    """同学Agent"""
    
    def __init__(self, name: str, age: int, personality: Dict[str, Any], 
                 gemini_client: GeminiClient, relationship_with_protagonist: str):
        super().__init__(name, age, personality, gemini_client)
        self.relationship_with_protagonist = relationship_with_protagonist  # "好友", "普通同学", "竞争对手", "霸凌者"
        self.popularity = personality.get("popularity", 5)  # 人气值 1-10
        self.academic_competitiveness = personality.get("competitive", 5)
        self.empathy_towards_others = personality.get("empathy", 5)
        self.social_influence = personality.get("social_influence", 5)
        
    def get_role_description(self) -> str:
        """获取角色描述"""
        return f"一位{self.age}岁的同学，在班级中{self.get_popularity_level()}，与主角关系：{self.relationship_with_protagonist}"
    
    def get_popularity_level(self) -> str:
        """获取人气水平"""
        if self.popularity >= 8:
            return "很受欢迎"
        elif self.popularity >= 6:
            return "比较受欢迎"
        elif self.popularity >= 4:
            return "普通"
        else:
            return "不太受欢迎"
    
    def get_current_concerns(self) -> List[str]:
        """获取当前关注的问题"""
        concerns = ["学习成绩", "朋友关系", "兴趣爱好"]
        
        if self.academic_competitiveness > 7:
            concerns.insert(0, "学习排名")
        
        if self.popularity > 7:
            concerns.append("维持人气")
        elif self.popularity < 4:
            concerns.append("改善人际关系")
        
        return concerns
    
    async def interact_with_protagonist(self, protagonist_mood: EmotionState,
                                      interaction_context: str) -> str:
        """与主角互动"""
        if self.relationship_with_protagonist == "好友":
            if protagonist_mood in [EmotionState.SAD, EmotionState.DEPRESSED]:
                situation = f"我的好朋友看起来{protagonist_mood.value}，在{interaction_context}的情况下，我想关心一下"
            else:
                situation = f"和好朋友在{interaction_context}的情况下交流"
                
        elif self.relationship_with_protagonist == "霸凌者":
            situation = f"在{interaction_context}的情况下，找机会针对主角"
            
        elif self.relationship_with_protagonist == "竞争对手":
            if "学习" in interaction_context or "成绩" in interaction_context:
                situation = f"在{interaction_context}的情况下，想要显示自己比主角优秀"
            else:
                situation = f"在{interaction_context}的情况下，与竞争对手的正常交流"
                
        else:  # 普通同学
            situation = f"在{interaction_context}的情况下，与同学的普通交流"
            
        return await self.respond_to_situation(situation)
    
    async def spread_rumor_or_gossip(self, rumor_content: str) -> str:
        """传播谣言或八卦"""
        if self.social_influence > 6:
            situation = f"听到关于{rumor_content}的消息，考虑是否告诉其他人"
        else:
            situation = f"听到{rumor_content}的消息，但不确定是否应该传播"
            
        return await self.respond_to_situation(situation)
    
    def would_help_protagonist(self, protagonist_situation: str) -> bool:
        """是否愿意帮助主角"""
        if self.relationship_with_protagonist == "好友":
            return True
        elif self.relationship_with_protagonist == "霸凌者":
            return False
        elif self.empathy_towards_others > 7:
            return True
        elif self.relationship_with_protagonist == "竞争对手":
            return False
        else:
            return self.empathy_towards_others > 5


class BullyAgent(ClassmateAgent):
    """霸凌者Agent"""
    
    def __init__(self, name: str, age: int, personality: Dict[str, Any], 
                 gemini_client: GeminiClient):
        personality["empathy"] = min(3, personality.get("empathy", 2))  # 低共情
        super().__init__(name, age, personality, gemini_client, "霸凌者")
        self.aggression_level = personality.get("aggression", 8)
        self.insecurity_level = personality.get("insecurity", 7)  # 内心不安全感
        self.need_for_control = personality.get("control_need", 8)
        
    def get_current_concerns(self) -> List[str]:
        """获取当前关注的问题"""
        concerns = ["维持自己的地位", "显示力量", "控制他人"]
        
        if self.insecurity_level > 7:
            concerns.append("掩饰自己的不安全感")
            
        return concerns
    
    async def initiate_bullying(self, target_weakness: str) -> str:
        """发起霸凌行为"""
        situation = f"注意到目标的{target_weakness}，这是一个很好的攻击点"
        return await self.respond_to_situation(situation)
    
    async def react_to_target_vulnerability(self, target_state: EmotionState) -> str:
        """对目标脆弱状态的反应"""
        if target_state in [EmotionState.SAD, EmotionState.DEPRESSED]:
            situation = f"看到目标显得{target_state.value}，这让我感到更有控制力"
        else:
            situation = f"目标看起来{target_state.value}，需要想办法让他屈服"
            
        return await self.respond_to_situation(situation)


class BestFriendAgent(ClassmateAgent):
    """最好朋友Agent"""
    
    def __init__(self, name: str, age: int, personality: Dict[str, Any], 
                 gemini_client: GeminiClient):
        personality["empathy"] = max(7, personality.get("empathy", 8))  # 高共情
        super().__init__(name, age, personality, gemini_client, "好友")
        self.loyalty_level = personality.get("loyalty", 9)
        self.emotional_support_ability = personality.get("support_ability", 8)
        self.shared_interests = personality.get("shared_interests", ["学习", "游戏"])
        
    def get_current_concerns(self) -> List[str]:
        """获取当前关注的问题"""
        concerns = super().get_current_concerns()
        concerns.insert(0, "好朋友的状况")
        return concerns
    
    async def provide_emotional_support(self, friend_emotion: EmotionState) -> str:
        """提供情感支持"""
        if friend_emotion in [EmotionState.SAD, EmotionState.DEPRESSED]:
            situation = f"我最好的朋友感到{friend_emotion.value}，我必须想办法帮助他"
        elif friend_emotion == EmotionState.ANXIOUS:
            situation = f"朋友显得{friend_emotion.value}，我想安慰他减轻压力"
        else:
            situation = f"想要和好朋友分享一些开心的事情"
            
        return await self.respond_to_situation(situation)
    
    def detect_friend_depression_signs(self, behavioral_changes: List[str]) -> bool:
        """检测朋友的抑郁征象"""
        # 最好的朋友通常能敏锐察觉变化
        return len(behavioral_changes) > 0 and self.emotional_support_ability > 6 