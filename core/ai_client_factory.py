from typing import Union, Optional
import logging
from .gemini_client import GeminiClient
from .deepseek_client import DeepSeekClient
import config

class AIClientFactory:
    """AI客户端工厂类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._gemini_client = None
        self._deepseek_client = None
    
    def get_client(self, provider: Optional[str] = None) -> Union[GeminiClient, DeepSeekClient]:
        """
        获取AI客户端实例
        
        Args:
            provider: 模型提供商，可选值为 "gemini" 或 "deepseek"
                     如果为None，则使用默认配置
        
        Returns:
            对应的AI客户端实例
        """
        if provider is None:
            provider = getattr(config, 'DEFAULT_MODEL_PROVIDER', 'gemini')
        
        if provider.lower() == 'gemini':
            return self._get_gemini_client()
        elif provider.lower() == 'deepseek':
            return self._get_deepseek_client()
        else:
            self.logger.warning(f"未知的模型提供商: {provider}, 使用默认的Gemini客户端")
            return self._get_gemini_client()
    
    def _get_gemini_client(self) -> GeminiClient:
        """获取Gemini客户端实例（单例模式）"""
        if self._gemini_client is None:
            api_key = getattr(config, 'GEMINI_API_KEY', '')
            if not api_key:
                raise ValueError("GEMINI_API_KEY 未设置，请在config.py中配置")
            self._gemini_client = GeminiClient(api_key)
            self.logger.info("Gemini客户端已初始化")
        return self._gemini_client
    
    def _get_deepseek_client(self) -> DeepSeekClient:
        """获取DeepSeek客户端实例（单例模式）"""
        if self._deepseek_client is None:
            api_key = getattr(config, 'DEEPSEEK_API_KEY', '')
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY 未设置，请在config.py中配置")
            
            base_url = getattr(config, 'DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
            model = getattr(config, 'DEEPSEEK_MODEL', 'deepseek-chat')
            
            self._deepseek_client = DeepSeekClient(
                api_key=api_key,
                base_url=base_url,
                model=model
            )
            self.logger.info(f"DeepSeek客户端已初始化，模型: {model}")
        return self._deepseek_client
    
    def get_available_providers(self) -> list:
        """获取可用的模型提供商列表"""
        providers = []
        
        # 检查Gemini
        if hasattr(config, 'GEMINI_API_KEY') and config.GEMINI_API_KEY and config.GEMINI_API_KEY.strip():
            providers.append('gemini')
        
        # 检查DeepSeek
        if hasattr(config, 'DEEPSEEK_API_KEY') and config.DEEPSEEK_API_KEY and config.DEEPSEEK_API_KEY.strip():
            providers.append('deepseek')
        
        return providers
    
    def test_connection(self, provider: str) -> bool:
        """
        测试指定提供商的连接
        
        Args:
            provider: 模型提供商名称
            
        Returns:
            连接是否成功
        """
        try:
            client = self.get_client(provider)
            # 简单的测试请求
            import asyncio
            
            async def test():
                response = await client.generate_response("测试连接，请回复'连接成功'")
                return response is not None and len(response) > 0
            
            return asyncio.run(test())
        except Exception as e:
            self.logger.error(f"测试{provider}连接失败: {e}")
            return False

# 全局工厂实例
ai_client_factory = AIClientFactory() 