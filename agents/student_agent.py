from typing import Dict, List, Any
from agents.base_agent import BaseAgent
from models.psychology_models import EmotionState, DepressionLevel
from core.gemini_client import GeminiClient

class StudentAgent(BaseAgent):
    """学生Agent - 主角，将经历抑郁症发展过程"""
    
    def __init__(self, name: str, age: int, personality: Dict[str, Any], 
                 gemini_client: GeminiClient):
        super().__init__(name, age, personality, gemini_client)
        
        # 学生特有属性
        self.grade = "高二"
        self.academic_performance = 7  # 1-10分
        self.favorite_subjects = ["数学", "物理"]
        self.extracurricular_activities = ["篮球", "画画"]
        self.friend_circle = []  # 朋友圈
        self.academic_goals = "考上重点大学"
        self.recent_grades = {}  # 最近成绩记录
        
        # 初始化学业压力
        self.psychological_state.academic_pressure = 6
        
    def get_role_description(self) -> str:
        """获取角色描述"""
        return f"一名{self.grade}的学生，{self.age}岁，性格{self.personality.get('traits', [])}，学习成绩{self.get_performance_level()}，目标是{self.academic_goals}"
    
    def get_performance_level(self) -> str:
        """获取学习成绩水平描述"""
        if self.academic_performance >= 8:
            return "优秀"
        elif self.academic_performance >= 6:
            return "良好"
        elif self.academic_performance >= 4:
            return "中等"
        else:
            return "较差"
    
    def get_current_concerns(self) -> List[str]:
        """获取当前关注的问题"""
        concerns = []
        
        # 根据抑郁程度调整关注点
        if self.psychological_state.depression_level == DepressionLevel.HEALTHY:
            concerns = ["学习成绩", "朋友关系", "兴趣爱好", "未来规划"]
        elif self.psychological_state.depression_level == DepressionLevel.MILD_RISK:
            concerns = ["学习压力", "人际关系", "自我价值", "父母期望"]
        elif self.psychological_state.depression_level == DepressionLevel.MODERATE:
            concerns = ["学习焦虑", "社交恐惧", "自我怀疑", "情绪控制"]
        elif self.psychological_state.depression_level == DepressionLevel.SEVERE:
            concerns = ["存在意义", "孤独感", "绝望感", "自我厌恶"]
        else:  # CRITICAL
            concerns = ["生活无望", "极度孤独", "自我伤害念头", "逃避现实"]
        
        # 根据压力水平调整
        if self.psychological_state.stress_level > 7:
            concerns.insert(0, "overwhelming_stress")
        
        # 根据社交连接度调整
        if self.psychological_state.social_connection < 3:
            concerns.append("社交孤立")
            
        return concerns[:4]  # 最多返回4个关注点
    
    def add_grade(self, subject: str, score: int):
        """添加成绩"""
        self.recent_grades[subject] = score
        
        # 更新学术表现
        if self.recent_grades:
            avg_score = sum(self.recent_grades.values()) / len(self.recent_grades)
            self.academic_performance = avg_score / 10  # 转换为0-10分
        
        # 根据成绩调整心理状态
        if score < 60:  # 不及格
            self.psychological_state.stress_level = min(10, self.psychological_state.stress_level + 2)
            self.psychological_state.self_esteem = max(0, self.psychological_state.self_esteem - 2)
            self.psychological_state.academic_pressure = min(10, self.psychological_state.academic_pressure + 1)
        elif score >= 90:  # 优秀
            self.psychological_state.stress_level = max(0, self.psychological_state.stress_level - 1)
            self.psychological_state.self_esteem = min(10, self.psychological_state.self_esteem + 1)
    
    def add_friend(self, friend_name: str):
        """添加朋友"""
        if friend_name not in self.friend_circle:
            self.friend_circle.append(friend_name)
            self.psychological_state.social_connection = min(10, 
                self.psychological_state.social_connection + 1)
    
    def lose_friend(self, friend_name: str):
        """失去朋友"""
        if friend_name in self.friend_circle:
            self.friend_circle.remove(friend_name)
            self.psychological_state.social_connection = max(0,
                self.psychological_state.social_connection - 2)
            self.psychological_state.stress_level = min(10,
                self.psychological_state.stress_level + 1)
    
    async def study_behavior(self, subject: str) -> str:
        """学习行为"""
        if self.psychological_state.depression_level.value >= 2:
            # 抑郁时学习困难
            situation = f"需要学习{subject}，但感到很难集中注意力和保持动力"
        else:
            situation = f"正在学习{subject}"
            
        return await self.respond_to_situation(situation)
    
    async def social_interaction_response(self, interaction_type: str, 
                                        other_person: str) -> str:
        """社交互动回应"""
        if self.psychological_state.depression_level.value >= 3:
            # 重度抑郁时倾向于回避
            situation = f"面对{other_person}的{interaction_type}，但内心想要逃避"
        elif self.psychological_state.depression_level.value >= 1:
            # 轻度风险时谨慎回应
            situation = f"和{other_person}进行{interaction_type}，但感到有些不安"
        else:
            situation = f"和{other_person}进行{interaction_type}"
            
        return await self.respond_to_situation(situation)
    
    def get_depression_symptoms(self) -> List[str]:
        """获取当前抑郁症状"""
        symptoms = []
        
        level = self.psychological_state.depression_level.value
        
        if level >= 1:  # 轻度风险
            symptoms.extend(["情绪低落", "对活动失去兴趣", "睡眠问题"])
        
        if level >= 2:  # 中度
            symptoms.extend(["注意力不集中", "自我价值感低", "疲劳感"])
        
        if level >= 3:  # 重度
            symptoms.extend(["绝望感", "社交回避", "食欲改变"])
        
        if level >= 4:  # 严重
            symptoms.extend(["自我伤害念头", "极度孤独", "现实逃避"])
        
        return symptoms
    
    def get_detailed_status(self) -> Dict[str, Any]:
        """获取详细状态信息"""
        return {
            **self.get_profile(),
            "academic_info": {
                "grade": self.grade,
                "performance": self.get_performance_level(),
                "recent_grades": self.recent_grades,
                "favorite_subjects": self.favorite_subjects,
                "academic_goals": self.academic_goals
            },
            "social_info": {
                "friend_circle": self.friend_circle,
                "extracurricular_activities": self.extracurricular_activities
            },
            "mental_health": {
                "depression_symptoms": self.get_depression_symptoms(),
                "risk_factors": self._identify_risk_factors()
            }
        }
    
    def _identify_risk_factors(self) -> List[str]:
        """识别抑郁风险因素"""
        risk_factors = []
        
        if self.psychological_state.academic_pressure > 7:
            risk_factors.append("高学业压力")
        
        if self.psychological_state.social_connection < 4:
            risk_factors.append("社交孤立")
        
        if self.psychological_state.self_esteem < 4:
            risk_factors.append("低自尊")
        
        if self.academic_performance < 4:
            risk_factors.append("学业失败")
        
        if len(self.friend_circle) < 2:
            risk_factors.append("缺乏朋友支持")
        
        # 检查最近的负面事件
        recent_negative_events = [e for e in self.life_events[-5:] if e.impact_score < -3]
        if len(recent_negative_events) >= 2:
            risk_factors.append("近期负面事件频发")
        
        return risk_factors 