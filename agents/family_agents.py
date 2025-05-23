from typing import Dict, List, Any, Union
from agents.base_agent import BaseAgent
from models.psychology_models import EmotionState, DepressionLevel, EventType

class FamilyAgent(BaseAgent):
    """家庭成员Agent基类"""
    
    def __init__(self, name: str, age: int, personality: Dict[str, Any], 
                 ai_client: Union['GeminiClient', 'DeepSeekClient'], relationship_to_student: str):
        super().__init__(name, age, personality, ai_client)
        self.relationship_to_student = relationship_to_student
        self.parenting_style = personality.get("parenting_style", "平衡型")
        self.emotional_availability = personality.get("emotional_availability", 5)
        
    def get_role_description(self) -> str:
        """获取角色描述"""
        return f"学生的{self.relationship_to_student}，{self.age}岁，{self.parenting_style}教育风格"
    
    def get_current_concerns(self) -> List[str]:
        """获取当前关注的问题"""
        base_concerns = ["孩子的学习", "孩子的健康", "家庭关系", "未来发展"]
        
        # 根据角色特点调整关注点
        if "严厉" in self.parenting_style:
            base_concerns.insert(0, "学习成绩")
        elif "焦虑" in self.parenting_style:
            base_concerns.insert(0, "孩子的情绪状态")
            
        return base_concerns[:4]
    
    async def express_concern(self, child_state: Dict[str, Any]) -> str:
        """表达对孩子的关心"""
        situation = f"看到孩子最近状态：{child_state}，作为{self.relationship_to_student}想要表达关心"
        return await self.respond_to_situation(situation)
    
    async def discipline_child(self, misbehavior: str) -> str:
        """管教孩子"""
        situation = f"孩子出现了{misbehavior}的行为，需要进行管教"
        return await self.respond_to_situation(situation)
    
    async def provide_support(self, child_difficulty: str) -> str:
        """提供支持"""
        situation = f"孩子遇到了{child_difficulty}的困难，需要提供支持和建议"
        return await self.respond_to_situation(situation)
    
    async def discuss_academic_performance(self, grades: Dict[str, int]) -> str:
        """讨论学习成绩"""
        avg_grade = sum(grades.values()) / len(grades) if grades else 0
        grade_summary = f"平均成绩{avg_grade:.1f}分"
        situation = f"看到孩子的成绩单，{grade_summary}，要和孩子谈论学习情况"
        return await self.respond_to_situation(situation)
    
    async def notice_mood_change(self, previous_mood: str, current_mood: str) -> str:
        """注意到情绪变化"""
        situation = f"注意到孩子的情绪从{previous_mood}变成了{current_mood}，作为家长想要了解和帮助"
        return await self.respond_to_situation(situation)

class FatherAgent(FamilyAgent):
    """父亲Agent"""
    
    def __init__(self, name: str, age: int, personality: Dict[str, Any], 
                 ai_client: Union['GeminiClient', 'DeepSeekClient']):
        super().__init__(name, age, personality, ai_client, "父亲")
        self.occupation = personality.get("occupation", "未知")
        self.work_stress = personality.get("work_pressure", 5)
        self.traditional_values = personality.get("traditional_values", True)
        self.communication_style = personality.get("communication_style", "直接")
        
    def get_current_concerns(self) -> List[str]:
        """获取当前关注的问题"""
        concerns = super().get_current_concerns()
        
        # 父亲特有关注点
        if self.traditional_values:
            concerns.insert(0, "家庭责任和纪律")
        if self.work_stress > 6:
            concerns.append("工作压力对家庭的影响")
            
        return concerns[:4]
    
    async def set_expectations(self, academic_goal: str) -> str:
        """设定期望"""
        situation = f"对孩子设定{academic_goal}的期望，希望孩子能够达到"
        return await self.respond_to_situation(situation)
    
    async def career_guidance(self, child_interests: List[str]) -> str:
        """职业指导"""
        interests_str = "、".join(child_interests)
        situation = f"了解到孩子对{interests_str}感兴趣，想要给出职业发展建议"
        return await self.respond_to_situation(situation)

class MotherAgent(FamilyAgent):
    """母亲Agent"""
    
    def __init__(self, name: str, age: int, personality: Dict[str, Any], 
                 ai_client: Union['GeminiClient', 'DeepSeekClient']):
        super().__init__(name, age, personality, ai_client, "母亲")
        self.nurturing_instinct = personality.get("nurturing_instinct", 8)
        self.anxiety_level = personality.get("anxiety_level", 5)
        self.emotional_sensitivity = personality.get("emotional_sensitivity", 7)
        
    def get_current_concerns(self) -> List[str]:
        """获取当前关注的问题"""
        concerns = super().get_current_concerns()
        
        # 母亲特有关注点
        if self.anxiety_level > 6:
            concerns.insert(0, "孩子的安全和健康")
        if self.emotional_sensitivity > 7:
            concerns.insert(0, "孩子的情感需求")
            
        return concerns[:4]
    
    async def comfort_child(self, child_emotion: EmotionState) -> str:
        """安慰孩子"""
        emotion_desc = child_emotion.value
        situation = f"看到孩子情绪{emotion_desc}，想要给予安慰和支持"
        return await self.respond_to_situation(situation)
    
    async def prepare_meal_with_care(self, child_mood: str) -> str:
        """贴心准备食物"""
        situation = f"注意到孩子心情{child_mood}，想要通过准备孩子喜欢的食物来表达关爱"
        return await self.respond_to_situation(situation)
    
    async def inquire_about_friends(self, social_situation: str) -> str:
        """询问朋友情况"""
        situation = f"关心孩子的社交情况：{social_situation}，想要了解更多"
        return await self.respond_to_situation(situation)

class SiblingAgent(BaseAgent):
    """兄弟姐妹Agent"""
    
    def __init__(self, name: str, age: int, personality: Dict[str, Any], 
                 ai_client: Union['GeminiClient', 'DeepSeekClient'], relationship_type: str):
        super().__init__(name, age, personality, ai_client)
        self.relationship_type = relationship_type  # "哥哥", "弟弟", "姐姐", "妹妹"
        self.competitiveness = personality.get("competitive", 5)
        self.supportiveness = personality.get("supportive", 6)
        
    def get_role_description(self) -> str:
        """获取角色描述"""
        return f"学生的{self.relationship_type}，{self.age}岁"
    
    def get_current_concerns(self) -> List[str]:
        """获取当前关注的问题"""
        return ["兄弟姐妹关系", "父母关注分配", "学习比较", "共同成长"]
    
    async def sibling_interaction(self, interaction_type: str) -> str:
        """兄弟姐妹互动"""
        situation = f"和兄弟姐妹进行{interaction_type}的互动"
        return await self.respond_to_situation(situation)
    
    async def compete_for_attention(self, context: str) -> str:
        """争夺关注"""
        situation = f"在{context}的情况下，感觉需要获得更多父母的关注"
        return await self.respond_to_situation(situation)
    
    async def offer_sibling_support(self, sibling_problem: str) -> str:
        """提供兄弟姐妹支持"""
        situation = f"看到兄弟姐妹遇到{sibling_problem}的问题，想要提供帮助"
        return await self.respond_to_situation(situation) 