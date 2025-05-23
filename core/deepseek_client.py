import openai
import asyncio
import json
from typing import Optional, Dict, Any
import logging

class DeepSeekClient:
    """DeepSeek API客户端"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com", model: str = "deepseek-chat"):
        """初始化DeepSeek客户端"""
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.logger = logging.getLogger(__name__)
        
    async def generate_response(self, prompt: str, context: Optional[Dict] = None) -> str:
        """生成回应"""
        try:
            # 构建完整的提示词
            full_prompt = self._build_prompt(prompt, context)
            
            # 生成内容
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.7,
                max_tokens=2048
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"生成回应时出错: {e}")
            return "抱歉，我现在无法回应。"
    
    def _build_prompt(self, prompt: str, context: Optional[Dict] = None) -> str:
        """构建完整的提示词"""
        if not context:
            return prompt
            
        context_str = json.dumps(context, ensure_ascii=False, indent=2)
        return f"上下文信息：\n{context_str}\n\n{prompt}"
    
    async def get_emotion_analysis(self, text: str) -> Dict[str, Any]:
        """分析文本中的情绪"""
        prompt = f"""
        请分析以下文本中的情绪状态，返回JSON格式的结果：
        
        文本："{text}"
        
        请返回包含以下字段的JSON：
        {{
            "primary_emotion": "主要情绪（开心/中性/焦虑/悲伤/抑郁/愤怒/困惑）",
            "emotion_intensity": "情绪强度（1-10）",
            "stress_indicators": ["压力指标列表"],
            "depression_risk": "抑郁风险（0-4，0=健康，4=严重）"
        }}
        
        只返回JSON格式的结果，不要添加其他文字。
        """
        
        try:
            response = await self.generate_response(prompt)
            # 尝试解析JSON
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].strip()
            else:
                json_str = response.strip()
            
            return json.loads(json_str)
        except Exception as e:
            self.logger.error(f"情绪分析失败: {e}")
            return {
                "primary_emotion": "中性",
                "emotion_intensity": 5,
                "stress_indicators": [],
                "depression_risk": 0
            }
    
    async def generate_agent_response(self, agent_profile: Dict, situation: str, 
                                    history: list = None) -> str:
        """为特定agent生成回应"""
        history_str = ""
        if history:
            history_str = "\n".join([f"- {h}" for h in history[-5:]])  # 只取最近5条历史
            
        prompt = f"""
        你是一个虚拟角色，请根据以下信息进行角色扮演：
        
        角色信息：
        {json.dumps(agent_profile, ensure_ascii=False, indent=2)}
        
        当前情况：{situation}
        
        最近的互动历史：
        {history_str}
        
        请以这个角色的身份，用自然的语言回应当前情况。回应应该：
        1. 符合角色的性格特点和背景
        2. 考虑角色当前的心理状态
        3. 体现角色与其他人的关系
        4. 用第一人称回应
        5. 长度控制在50-200字以内
        
        直接给出角色的回应，不要添加额外的说明。
        """
        
        return await self.generate_response(prompt)
    
    async def analyze_interaction_impact(self, interaction: str, 
                                       participants: list) -> Dict[str, Any]:
        """分析互动对参与者的心理影响"""
        prompt = f"""
        请分析以下互动对参与者心理状态的影响：
        
        互动内容：{interaction}
        参与者：{', '.join(participants)}
        
        请返回JSON格式的分析结果：
        {{
            "overall_impact": "整体影响（正面/负面/中性）",
            "impact_score": "影响分数（-10到10）",
            "affected_emotions": ["受影响的情绪"],
            "long_term_effects": "长期影响描述",
            "participant_impacts": {{
                "参与者名称": {{
                    "emotional_change": "情绪变化",
                    "stress_change": "压力变化（-5到5）",
                    "relationship_change": "关系变化描述"
                }}
            }}
        }}
        
        只返回JSON格式的结果，不要添加其他文字。
        """
        
        try:
            response = await self.generate_response(prompt)
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].strip()
            else:
                json_str = response.strip()
            
            return json.loads(json_str)
        except Exception as e:
            self.logger.error(f"互动影响分析失败: {e}")
            return {
                "overall_impact": "中性",
                "impact_score": 0,
                "affected_emotions": [],
                "long_term_effects": "无明显影响",
                "participant_impacts": {}
            } 