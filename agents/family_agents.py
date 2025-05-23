from typing import Dict, List, Any
from agents.base_agent import BaseAgent
from models.psychology_models import EmotionState
from core.gemini_client import GeminiClient

class ParentAgent(BaseAgent):
    """父母Agent基类"""
    
    def __init__(self, name: str, age: int, personality: Dict[str, Any], 
                 gemini_client: GeminiClient, relationship_to_student: str):
        super().__init__(name, age, personality, gemini_client)
        self.relationship_to_student = relationship_to_student  # "父亲" 或 "母亲"
        self.occupation = personality.get("occupation", "职员")
        self.parenting_style = personality.get("parenting_style", "权威型")
        self.expectations_for_child = personality.get("expectations", "考上好大学")
        self.stress_from_work = 5  # 工作压力 1-10
        self.concern_level_for_child = 6  # 对孩子的担心程度 1-10
        
    def get_role_description(self) -> str:
        """获取角色描述"""
        return f"一位{self.age}岁的{self.relationship_to_student}，从事{self.occupation}工作，采用{self.parenting_style}的教育方式，对孩子期望{self.expectations_for_child}"
    
    def get_current_concerns(self) -> List[str]:
        """获取当前关注的问题"""
        concerns = ["孩子的学习成绩", "孩子的未来发展", "家庭经济状况"]
        
        if self.concern_level_for_child > 7:
            concerns.insert(0, "孩子的心理健康")
        
        if self.stress_from_work > 7:
            concerns.append("工作压力")
            
        if self.parenting_style == "严厉型":
            concerns.append("孩子的纪律问题")
        elif self.parenting_style == "溺爱型":
            concerns.append("是否对孩子过于宽松")
        
        return concerns
    
    async def react_to_child_behavior(self, child_behavior: str, 
                                    child_emotion: EmotionState) -> str:
        """对孩子行为的反应"""
        # 根据教育方式调整反应
        if self.parenting_style == "严厉型":
            situation = f"看到孩子{child_behavior}，情绪显示{child_emotion.value}，我觉得需要严格管教"
        elif self.parenting_style == "溺爱型":
            situation = f"看到孩子{child_behavior}，情绪显示{child_emotion.value}，我很心疼想要保护"
        elif self.parenting_style == "民主型":
            situation = f"看到孩子{child_behavior}，情绪显示{child_emotion.value}，我想和孩子好好沟通"
        else:  # 忽视型
            situation = f"注意到孩子{child_behavior}，但我忙于自己的事情"
            
        return await self.respond_to_situation(situation)
    
    def increase_concern_for_child(self, amount: int = 1):
        """增加对孩子的担心"""
        self.concern_level_for_child = min(10, self.concern_level_for_child + amount)
        if self.concern_level_for_child > 8:
            self.psychological_state.stress_level = min(10, self.psychological_state.stress_level + 1)


class FatherAgent(ParentAgent):
    """父亲Agent"""
    
    def __init__(self, name: str, age: int, personality: Dict[str, Any], 
                 gemini_client: GeminiClient):
        super().__init__(name, age, personality, gemini_client, "父亲")
        
        # 父亲特有特征
        self.communication_style = personality.get("communication_style", "直接但不善表达情感")
        self.work_pressure = personality.get("work_pressure", 7)
        self.traditional_values = personality.get("traditional_values", True)
        
    def get_current_concerns(self) -> List[str]:
        """获取当前关注的问题"""
        concerns = super().get_current_concerns()
        
        if self.traditional_values:
            concerns.append("孩子是否足够坚强")
        
        concerns.append("作为家庭支柱的责任")
        
        return concerns
    
    async def give_advice_to_child(self, child_situation: str) -> str:
        """给孩子建议"""
        if self.traditional_values:
            situation = f"孩子遇到{child_situation}，我觉得应该教育他要坚强独立"
        else:
            situation = f"孩子遇到{child_situation}，我想给他一些实用的建议"
            
        return await self.respond_to_situation(situation)


class MotherAgent(ParentAgent):
    """母亲Agent"""
    
    def __init__(self, name: str, age: int, personality: Dict[str, Any], 
                 gemini_client: GeminiClient):
        super().__init__(name, age, personality, gemini_client, "母亲")
        
        # 母亲特有特征
        self.emotional_sensitivity = personality.get("emotional_sensitivity", 8)
        self.nurturing_instinct = personality.get("nurturing_instinct", 8)
        self.anxiety_level = personality.get("anxiety_level", 6)
        
    def get_current_concerns(self) -> List[str]:
        """获取当前关注的问题"""
        concerns = super().get_current_concerns()
        
        if self.emotional_sensitivity > 7:
            concerns.insert(0, "孩子的情绪变化")
        
        if self.anxiety_level > 7:
            concerns.append("各种潜在的危险")
        
        return concerns
    
    async def comfort_child(self, child_emotion: EmotionState) -> str:
        """安慰孩子"""
        if child_emotion in [EmotionState.SAD, EmotionState.DEPRESSED]:
            situation = f"看到孩子{child_emotion.value}，我的心都碎了，想要好好安慰他"
        elif child_emotion == EmotionState.ANXIOUS:
            situation = f"孩子显得{child_emotion.value}，我想帮他缓解压力"
        else:
            situation = f"想要关心一下孩子的情绪状态"
            
        return await self.respond_to_situation(situation)
    
    def detect_child_changes(self, child_behavior_changes: List[str]) -> bool:
        """检测孩子的变化"""
        # 母亲通常更容易察觉孩子的细微变化
        if self.emotional_sensitivity > 6:
            return len(child_behavior_changes) > 0
        else:
            return len(child_behavior_changes) > 2


class SiblingAgent(BaseAgent):
    """兄弟姐妹Agent"""
    
    def __init__(self, name: str, age: int, personality: Dict[str, Any], 
                 gemini_client: GeminiClient, relationship_type: str):
        super().__init__(name, age, personality, gemini_client)
        self.relationship_type = relationship_type  # "哥哥", "弟弟", "姐姐", "妹妹"
        self.closeness_to_sibling = personality.get("closeness", 6)
        self.competitive_with_sibling = personality.get("competitive", False)
        
    def get_role_description(self) -> str:
        """获取角色描述"""
        return f"一位{self.age}岁的{self.relationship_type}，与兄弟姐妹关系{'密切' if self.closeness_to_sibling > 6 else '一般'}"
    
    def get_current_concerns(self) -> List[str]:
        """获取当前关注的问题"""
        concerns = []
        
        if self.age < 15:
            concerns = ["学习", "游戏", "朋友"]
        elif self.age < 18:
            concerns = ["学习压力", "同学关系", "未来规划"]
        else:
            concerns = ["工作/大学", "恋爱", "独立生活"]
        
        if self.closeness_to_sibling > 7:
            concerns.append("兄弟姐妹的状况")
        
        if self.competitive_with_sibling:
            concerns.append("与兄弟姐妹的比较")
            
        return concerns
    
    async def interact_with_sibling(self, sibling_mood: EmotionState) -> str:
        """与兄弟姐妹互动"""
        if self.closeness_to_sibling > 6:
            if sibling_mood in [EmotionState.SAD, EmotionState.DEPRESSED]:
                situation = f"看到兄弟姐妹情绪{sibling_mood.value}，想要关心一下"
            else:
                situation = f"想和兄弟姐妹聊聊天"
        else:
            situation = f"和兄弟姐妹的日常互动"
            
        return await self.respond_to_situation(situation) 