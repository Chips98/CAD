from typing import Dict, List, Any, Union
from agents.base_agent import BaseAgent
from models.psychology_models import EmotionState, DepressionLevel

class TeacherAgent(BaseAgent):
    """教师Agent"""
    
    def __init__(self, name: str, age: int, personality: Dict[str, Any], 
                 ai_client: Union['GeminiClient', 'DeepSeekClient'], subject: str):
        super().__init__(name, age, personality, ai_client)
        self.subject = subject
        self.teaching_experience = personality.get("experience_years", 5)
        self.teaching_style = personality.get("teaching_style", "传统型")
        self.strictness = personality.get("strictness", 5)  # 1-10
        self.empathy_level = personality.get("empathy", 5)  # 1-10
        self.expectations = personality.get("expectations", "中等")  # 低/中等/高
        
    def get_role_description(self) -> str:
        """获取角色描述"""
        return f"一位教授{self.subject}的{self.age}岁教师，教学风格{self.teaching_style}，有{self.teaching_experience}年教学经验"
    
    def get_current_concerns(self) -> List[str]:
        """获取当前关注的问题"""
        concerns = [f"{self.subject}教学质量", "学生学习进度", "课堂纪律"]
        
        if self.expectations == "高":
            concerns.insert(0, "学生成绩提升")
        
        if self.empathy_level > 6:
            concerns.append("学生心理状态")
        
        if self.strictness > 7:
            concerns.append("学生行为规范")
            
        return concerns[:4]
    
    async def give_feedback_on_performance(self, student_performance: str,
                                         recent_grades: List[int]) -> str:
        """对学生表现给出反馈"""
        avg_grade = sum(recent_grades) / len(recent_grades) if recent_grades else 0
        
        if self.strictness > 6:
            if avg_grade < 70:
                situation = f"学生{student_performance}，最近平均成绩{avg_grade:.1f}，我觉得需要严格要求"
            else:
                situation = f"学生{student_performance}，成绩{avg_grade:.1f}还可以，但要保持"
        else:
            situation = f"学生{student_performance}，我想给出建设性的反馈"
            
        return await self.respond_to_situation(situation)
    
    async def handle_classroom_situation(self, situation_type: str, 
                                       student_behavior: str) -> str:
        """处理课堂情况"""
        if self.strictness > 7:
            situation = f"课堂上{situation_type}，学生{student_behavior}，我认为需要立即纠正"
        elif self.empathy_level > 6:
            situation = f"课堂上{situation_type}，学生{student_behavior}，我想了解背后的原因"
        else:
            situation = f"课堂上{situation_type}，学生{student_behavior}，我按照常规处理"
            
        return await self.respond_to_situation(situation)
    
    async def notice_student_change(self, student_name: str, 
                                  behavioral_change: str) -> str:
        """注意到学生变化"""
        if self.empathy_level > 6:
            situation = f"注意到{student_name}{behavioral_change}，我担心他的状况"
        elif self.strictness > 6:
            situation = f"注意到{student_name}{behavioral_change}，可能影响学习"
        else:
            situation = f"注意到{student_name}{behavioral_change}"
            
        return await self.respond_to_situation(situation)

class ClassmateAgent(BaseAgent):
    """同学Agent"""
    
    def __init__(self, name: str, age: int, personality: Dict[str, Any], 
                 ai_client: Union['GeminiClient', 'DeepSeekClient'], relationship_with_protagonist: str):
        super().__init__(name, age, personality, ai_client)
        self.relationship_with_protagonist = relationship_with_protagonist
        self.academic_level = personality.get("academic_performance", 6)  # 1-10
        self.popularity = personality.get("popularity", 5)  # 1-10
        self.empathy_level = personality.get("empathy", 5)  # 1-10
        self.competitiveness = personality.get("competitive", 5)  # 1-10
        
    def get_role_description(self) -> str:
        """获取角色描述"""
        return f"一位{self.age}岁的同学，与主角关系为{self.relationship_with_protagonist}，学习成绩{'优秀' if self.academic_level > 7 else '一般'}"
    
    def get_current_concerns(self) -> List[str]:
        """获取当前关注的问题"""
        concerns = ["学习成绩", "同学关系", "课外活动"]
        
        if self.competitiveness > 6:
            concerns.insert(0, "学习排名")
        
        if self.popularity > 6:
            concerns.append("社交活动")
        
        if self.empathy_level > 6:
            concerns.append("朋友的状况")
            
        return concerns[:4]
    
    async def interact_with_protagonist(self, context: str) -> str:
        """与主角互动"""
        if self.relationship_with_protagonist == "好友":
            situation = f"在{context}的情况下，想和好朋友聊聊"
        elif self.relationship_with_protagonist == "竞争对手":
            if self.competitiveness > 6:
                situation = f"在{context}的情况下，感觉需要展示自己的优势"
            else:
                situation = f"在{context}的情况下，正常与同学交流"
        else:  # 普通同学
            situation = f"在{context}的情况下，和同学的日常互动"
            
        return await self.respond_to_situation(situation)
    
    async def react_to_protagonist_change(self, observed_change: str) -> str:
        """对主角变化的反应"""
        if self.empathy_level > 6:
            situation = f"注意到同学{observed_change}，我想关心一下"
        elif self.relationship_with_protagonist == "竞争对手":
            situation = f"注意到同学{observed_change}，这可能影响竞争态势"
        else:
            situation = f"注意到同学{observed_change}，随便聊聊"
            
        return await self.respond_to_situation(situation)
    
    async def participate_in_group_activity(self, activity: str, 
                                          group_members: List[str]) -> str:
        """参与集体活动"""
        members_str = "、".join(group_members)
        situation = f"和{members_str}一起参加{activity}"
        return await self.respond_to_situation(situation)

class BullyAgent(ClassmateAgent):
    """霸凌者Agent - 继承自ClassmateAgent"""
    
    def __init__(self, name: str, age: int, personality: Dict[str, Any], 
                 ai_client: Union['GeminiClient', 'DeepSeekClient']):
        # 设置为霸凌者关系
        super().__init__(name, age, personality, ai_client, "霸凌者")
        self.aggression_level = personality.get("aggression", 8)  # 1-10
        self.insecurity_level = personality.get("insecurity", 7)  # 1-10
        self.need_for_control = personality.get("control_need", 8)  # 1-10
        
        # 霸凌者通常共情能力较低
        self.empathy_level = min(3, self.empathy_level)
        
    def get_role_description(self) -> str:
        """获取角色描述"""
        return f"一位{self.age}岁的霸凌者，攻击性较强，但内心缺乏安全感"
    
    def get_current_concerns(self) -> List[str]:
        """获取当前关注的问题"""
        return ["维持地位", "控制他人", "掩饰脆弱", "获得关注"]
    
    async def bully_behavior(self, target: str, context: str) -> str:
        """霸凌行为"""
        if self.need_for_control > 7:
            situation = f"在{context}的情况下，想要控制{target}，显示我的权威"
        elif self.insecurity_level > 6:
            situation = f"在{context}的情况下，通过贬低{target}来让自己感觉更好"
        else:
            situation = f"在{context}的情况下，对{target}进行挑衅"
            
        return await self.respond_to_situation(situation)
    
    async def react_to_resistance(self, target_response: str) -> str:
        """对反抗的反应"""
        if self.aggression_level > 7:
            situation = f"面对反抗：{target_response}，我感到愤怒，想要加强控制"
        else:
            situation = f"面对反抗：{target_response}，我想要维持威权"
            
        return await self.respond_to_situation(situation)

class BestFriendAgent(ClassmateAgent):
    """最好朋友Agent - 继承自ClassmateAgent"""
    
    def __init__(self, name: str, age: int, personality: Dict[str, Any], 
                 ai_client: Union['GeminiClient', 'DeepSeekClient']):
        # 设置为好友关系
        super().__init__(name, age, personality, ai_client, "好友")
        self.loyalty_level = personality.get("loyalty", 9)  # 1-10
        self.emotional_support_ability = personality.get("support_ability", 8)  # 1-10
        self.shared_interests = personality.get("shared_interests", ["学习", "运动"])
        
        # 好朋友通常共情能力较强
        self.empathy_level = max(7, self.empathy_level)
        
    def get_role_description(self) -> str:
        """获取角色描述"""
        return f"一位{self.age}岁的最好朋友，忠诚度高，善于提供情感支持"
    
    def get_current_concerns(self) -> List[str]:
        """获取当前关注的问题"""
        concerns = super().get_current_concerns()
        concerns.insert(0, "朋友的幸福")
        return concerns[:4]
    
    async def provide_emotional_support(self, friend_emotion: EmotionState) -> str:
        """提供情感支持"""
        if friend_emotion in [EmotionState.DEPRESSED, EmotionState.SAD]:
            situation = f"看到好朋友情绪{friend_emotion.value}，我想要给予最大的支持和安慰"
        elif friend_emotion == EmotionState.ANXIOUS:
            situation = f"朋友显得{friend_emotion.value}，我想帮助他放松"
        else:
            situation = f"想要关心一下朋友的状况"
            
        return await self.respond_to_situation(situation)
    
    async def share_activity(self, activity: str) -> str:
        """分享活动"""
        if activity in self.shared_interests:
            situation = f"和好朋友一起{activity}，这是我们都喜欢的"
        else:
            situation = f"虽然{activity}不是我最喜欢的，但愿意陪朋友一起"
            
        return await self.respond_to_situation(situation)
    
    async def notice_friend_isolation(self, isolation_behavior: str) -> str:
        """注意到朋友孤立"""
        situation = f"发现朋友{isolation_behavior}，我很担心，想要主动接近"
        return await self.respond_to_situation(situation) 