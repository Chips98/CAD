"""
增强配置示例：展示如何定义角色以便自动处理占位符
"""

from typing import Dict, List, Any

# 场景类型（可选）
SCENARIO_TYPE = "university"  # 可选: "high_school", "university", "workplace"

# 人物配置 - 展示各种定义角色的方式
CHARACTERS = {
    # 主角
    "protagonist": {
        "type": "StudentAgent",
        "name": "张晓",
        "age": 22,
        "description": "计算机专业大四学生",
        "personality": {
            "traits": ["理想主义", "自我要求高", "社交焦虑"],
            "openness": 8,
            "conscientiousness": 7,
            "extraversion": 3,
            "agreeableness": 6,
            "neuroticism": 7
        }
    },
    
    # 使用 extra_params 定义关系
    "roommate": {
        "type": "ClassmateAgent",
        "name": "李雷",
        "age": 22,
        "personality": {
            "empathy": 7,
            "competitive": 5,
            "popularity": 8
        },
        "extra_params": {
            "relationship_with_protagonist": "室友兼同学"
        }
    },
    
    # 使用 role_type 定义角色类型
    "advisor": {
        "type": "TeacherAgent",
        "name": "王教授",
        "age": 50,
        "role_type": "学术导师",
        "personality": {
            "experience_years": 25,
            "teaching_style": "严格型",
            "empathy": 6
        }
    },
    
    # 使用 description 字段
    "intern_buddy": {
        "type": "ClassmateAgent", 
        "name": "小刘",
        "age": 23,
        "description": "实习同事",
        "personality": {
            "empathy": 8,
            "support_ability": 7
        }
    },
    
    # 系统会从 type 自动推断
    "mother": {
        "type": "MotherAgent",
        "name": "张母",
        "age": 48,
        "personality": {
            "parenting_style": "关怀过度型",
            "anxiety_level": 7,
            "empathy": 8
        }
    },
    
    # 自定义角色
    "counselor": {
        "type": "TeacherAgent",
        "name": "陈老师", 
        "age": 35,
        "role_type": "心理咨询师",
        "personality": {
            "empathy": 9,
            "professional_skill": 8
        }
    }
}

# 关系配置
RELATIONSHIPS = [
    {"person_a": "张晓", "person_b": "李雷", "type": "室友", "closeness": 7, "trust": 6, "conflict": 2},
    {"person_a": "张晓", "person_b": "王教授", "type": "师生", "closeness": 5, "trust": 7, "conflict": 1},
    {"person_a": "张晓", "person_b": "小刘", "type": "同事", "closeness": 6, "trust": 5, "conflict": 1},
    {"person_a": "张晓", "person_b": "张母", "type": "母子", "closeness": 8, "trust": 9, "conflict": 3},
    {"person_a": "张晓", "person_b": "陈老师", "type": "咨询关系", "closeness": 4, "trust": 6, "conflict": 0},
]

# 事件模板 - 使用配置中定义的角色ID作为占位符
EVENT_TEMPLATES = {
    "academic": {
        "positive": [
            "{protagonist}完成了毕业论文的一个重要章节",
            "{advisor}对{protagonist}的研究进展表示认可",
            "{roommate}和{protagonist}一起在{location}复习"
        ],
        "negative": [
            "{protagonist}的论文被{advisor}要求大幅修改",
            "{time}，{protagonist}在{location}准备答辩时感到焦虑",
            "看到{roommate}已经拿到offer，{protagonist}感到压力"
        ],
        "neutral": [
            "{protagonist}参加了{time}的组会",
            "{advisor}安排{protagonist}准备下周的汇报"
        ]
    },
    "social": {
        "positive": [
            "{intern_buddy}邀请{protagonist}一起吃午饭",
            "{roommate}和{protagonist}在{time}一起看电影放松",
            "{counselor}帮助{protagonist}缓解了压力"
        ],
        "negative": [
            "{protagonist}拒绝了{roommate}的聚会邀请",
            "{mother}的过度关心让{protagonist}感到烦躁"
        ],
        "neutral": [
            "{protagonist}和{intern_buddy}在{location}讨论工作"
        ]
    },
    "personal": {
        "positive": [
            "{time}，{protagonist}在{location}运动后感觉好多了",
            "{protagonist}完成了一个个人项目"
        ],
        "negative": [
            "{protagonist}在{time}失眠，担心未来",
            "独自在{location}，{protagonist}感到孤独"
        ],
        "neutral": [
            "{protagonist}在{location}整理简历"
        ]
    }
}

# 阶段配置
STAGE_CONFIG = {
    "准备阶段": {
        "event_weights": {"positive": 0.5, "negative": 0.3, "neutral": 0.2},
        "event_categories": ["academic", "social", "personal"],
        "stress_modifier": 1.0,
        "relationship_decay": 0.98
    },
    "压力上升": {
        "event_weights": {"positive": 0.3, "negative": 0.5, "neutral": 0.2},
        "event_categories": ["academic", "personal"],
        "stress_modifier": 1.3,
        "relationship_decay": 0.95
    },
    "情绪低谷": {
        "event_weights": {"positive": 0.2, "negative": 0.6, "neutral": 0.2},
        "event_categories": ["personal", "social"],
        "stress_modifier": 1.6,
        "relationship_decay": 0.9
    }
}

# 条件事件 - 也可以使用自定义占位符
CONDITIONAL_EVENTS = {
    "need_help": {
        "condition": lambda state: state.get("stress_level", 0) > 8,
        "events": [
            "{counselor}主动联系{protagonist}提供帮助",
            "{advisor}注意到{protagonist}的状态不佳",
            "{mother}打电话表示担心{protagonist}"
        ]
    },
    "social_isolation": {
        "condition": lambda state: state.get("social_connection", 10) < 3,
        "events": [
            "{roommate}敲门问{protagonist}是否需要帮助",
            "{intern_buddy}发消息关心{protagonist}",
            "{protagonist}意识到自己已经很久没有社交了"
        ]
    }
}

# 可选：定义额外的占位符值
SUBJECTS = ["机器学习", "软件工程", "数据结构", "毕业设计", "实习项目"]
LOCATIONS = ["实验室", "图书馆", "宿舍", "咖啡厅", "教学楼"]
TIMES = ["清晨", "上午", "中午", "下午", "傍晚", "深夜"] 