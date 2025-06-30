"""
快速测试配置 - 用于CAD-MD模型验证
模拟天数减少，事件频率降低，专注于CAD状态演化测试
"""

# 基本参数
SIMULATION_DAYS = 5  # 减少到5天进行快速测试
EVENTS_PER_DAY_RANGE = (1, 2)  # 每天1-2个事件

# 角色配置
CHARACTERS = {
    "李明": {
        "age": 17,
        "role": "学生",
        "personality": {
            "traits": ["内向", "敏感", "聪明", "善良"],
            "openness": 6,
            "conscientiousness": 7,
            "extraversion": 3,
            "agreeableness": 8,
            "neuroticism": 7
        },
        "background": {
            "family_situation": "单亲家庭，与母亲同住",
            "academic_performance": "成绩优秀但压力较大"
        },
        "initial_state": {
            "emotion": "NEUTRAL",
            "stress_level": 3,
            "self_esteem": 6,
            "social_connection": 5,
            "academic_performance": 4,
            "depression_level": "HEALTHY"
        }
    }
}

# 简化的关系网络
RELATIONSHIPS = [
    {"person_a": "李明", "person_b": "王老师", "type": "师生", "quality": 6},
    {"person_a": "李明", "person_b": "张同学", "type": "同学", "quality": 4},
]

# 事件模板 - 专注于测试CAD状态变化
EVENT_TEMPLATES = [
    # 负面事件
    {
        "description": "考试成绩不理想，感到挫败",
        "probability": 0.3,
        "impact_score": -4,
        "triggers": ["academic_stress"],
        "affected_stats": ["stress_level", "self_esteem"]
    },
    {
        "description": "被同学嘲笑外貌，感到羞辱",
        "probability": 0.2,
        "impact_score": -5,
        "triggers": ["social_rejection"],
        "affected_stats": ["self_esteem", "social_connection"]
    },
    {
        "description": "与朋友发生争执，关系恶化",
        "probability": 0.2,
        "impact_score": -3,
        "triggers": ["interpersonal_conflict"],
        "affected_stats": ["social_connection", "stress_level"]
    },
    # 中性事件
    {
        "description": "平常的一天，没有特别的事情发生",
        "probability": 0.1,
        "impact_score": 0,
        "triggers": [],
        "affected_stats": []
    },
    # 轻微正面事件
    {
        "description": "收到老师的鼓励话语",
        "probability": 0.2,
        "impact_score": 2,
        "triggers": ["positive_feedback"],
        "affected_stats": ["self_esteem"]
    }
]

# 条件事件 - 基于CAD状态触发
CONDITIONAL_EVENTS = [
    {
        "description": "内心的负面想法越来越强烈，开始质疑自己的价值",
        "condition": lambda state: state.get("self_belief", 0) < -5,
        "probability": 0.8,
        "impact_score": -2,
        "triggers": ["rumination_spiral"]
    },
    {
        "description": "感到世界对自己充满敌意，更加孤立自己",
        "condition": lambda state: state.get("world_belief", 0) < -6,
        "probability": 0.7,
        "impact_score": -3,
        "triggers": ["social_withdrawal"]
    },
    {
        "description": "对未来感到绝望，觉得一切都不会好转",
        "condition": lambda state: state.get("future_belief", 0) < -7,
        "probability": 0.9,
        "impact_score": -4,
        "triggers": ["hopelessness"]
    }
]

# AI提供商配置
AI_PROVIDER_PREFERENCE = "deepseek"  # 优先使用DeepSeek进行测试

# 故事阶段配置
STAGE_CONFIG = {
    "初期适应": {"duration": 1, "focus": "学校环境适应"},
    "压力累积": {"duration": 2, "focus": "学业和社交压力"},
    "症状显现": {"duration": 1, "focus": "心理症状开始显现"},
    "恶化发展": {"duration": 1, "focus": "症状加重和功能受损"}
}
