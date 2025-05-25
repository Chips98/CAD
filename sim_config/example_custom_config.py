"""
示例：自定义模拟配置
这个例子展示了一个不同的场景：大学生面临就业压力
"""

from typing import Dict, List, Any

# 人物配置
CHARACTERS = {
    "protagonist": {
        "type": "StudentAgent",
        "name": "张晓",
        "age": 22,
        "personality": {
            "traits": ["理想主义", "自我要求高", "社交焦虑", "创造力强"],
            "openness": 8,
            "conscientiousness": 7,
            "extraversion": 3,
            "agreeableness": 6,
            "neuroticism": 7
        }
    },
    "roommate": {
        "type": "ClassmateAgent",
        "name": "李雷",
        "age": 22,
        "personality": {
            "empathy": 7,
            "competitive": 5,
            "popularity": 8,
            "academic_performance": 7
        },
        "extra_params": {
            "relationship_with_protagonist": "室友"
        }
    },
    "mentor": {
        "type": "TeacherAgent",
        "name": "陈教授",
        "age": 45,
        "personality": {
            "experience_years": 20,
            "teaching_style": "启发型",
            "strictness": 5,
            "empathy": 8,
            "expectations": "中等"
        },
        "extra_params": {
            "subject": "计算机科学"
        }
    },
    "girlfriend": {
        "type": "BestFriendAgent",
        "name": "小美",
        "age": 21,
        "personality": {
            "empathy": 8,
            "loyalty": 8,
            "support_ability": 7,
            "shared_interests": ["电影", "音乐", "旅行"]
        }
    }
}

# 关系配置
RELATIONSHIPS = [
    {"person_a": "张晓", "person_b": "李雷", "type": "室友", "closeness": 7, "trust": 6, "conflict": 2},
    {"person_a": "张晓", "person_b": "陈教授", "type": "师生", "closeness": 6, "trust": 8, "conflict": 1},
    {"person_a": "张晓", "person_b": "小美", "type": "恋人", "closeness": 9, "trust": 8, "conflict": 2},
]

# 事件模板
EVENT_TEMPLATES = {
    "academic": {
        "positive": [
            "{protagonist}的毕业设计获得{mentor}的认可",
            "{protagonist}收到了实习offer",
            "{roommate}和{protagonist}一起准备面试"
        ],
        "negative": [
            "{protagonist}的简历又被拒绝了",
            "{protagonist}在面试中表现不佳",
            "看到同学都找到了工作，{protagonist}感到压力"
        ],
        "neutral": [
            "{protagonist}参加了校园招聘会",
            "{mentor}给{protagonist}一些就业建议"
        ]
    },
    "social": {
        "positive": [
            "{girlfriend}陪{protagonist}散步谈心",
            "{roommate}分享了找工作的经验"
        ],
        "negative": [
            "{protagonist}因为压力对{girlfriend}发脾气",
            "{protagonist}拒绝参加同学聚会"
        ],
        "neutral": [
            "{protagonist}和{roommate}在宿舍聊天"
        ]
    },
    "personal": {
        "positive": [
            "{protagonist}坚持运动后感觉好多了",
            "{protagonist}完成了一个个人项目"
        ],
        "negative": [
            "{protagonist}整夜失眠担心未来",
            "{protagonist}开始怀疑自己的能力"
        ],
        "neutral": [
            "{protagonist}在图书馆准备简历"
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
    "求职焦虑": {
        "event_weights": {"positive": 0.3, "negative": 0.5, "neutral": 0.2},
        "event_categories": ["academic", "personal"],
        "stress_modifier": 1.3,
        "relationship_decay": 0.95
    },
    "挫折累积": {
        "event_weights": {"positive": 0.2, "negative": 0.6, "neutral": 0.2},
        "event_categories": ["academic", "social", "personal"],
        "stress_modifier": 1.6,
        "relationship_decay": 0.9
    },
    "自我怀疑": {
        "event_weights": {"positive": 0.1, "negative": 0.7, "neutral": 0.2},
        "event_categories": ["personal", "social"],
        "stress_modifier": 1.8,
        "relationship_decay": 0.85
    },
    "情绪崩溃": {
        "event_weights": {"positive": 0.05, "negative": 0.8, "neutral": 0.15},
        "event_categories": ["personal"],
        "stress_modifier": 2.0,
        "relationship_decay": 0.8
    }
}

# 条件事件
CONDITIONAL_EVENTS = {
    "multiple_rejections": {
        "condition": lambda state: state.get("rejection_count", 0) > 5,
        "events": [
            "{protagonist}开始怀疑自己的专业选择",
            "{girlfriend}担心{protagonist}的状态",
            "{mentor}主动找{protagonist}谈话"
        ]
    },
    "relationship_strain": {
        "condition": lambda state: state.get("social_connection", 10) < 4,
        "events": [
            "{girlfriend}提出需要谈谈他们的关系",
            "{roommate}感觉{protagonist}变得很难相处",
            "{protagonist}推掉了所有社交活动"
        ]
    }
}