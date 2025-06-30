from typing import Union, Optional
import logging
from .gemini_client import GeminiClient
from .deepseek_client import DeepSeekClient

class AIClientFactory:
    """AI客户端工厂类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._gemini_client = None
        self._deepseek_client = None
        self._qwen_client = None
        self._api_config = None
    
    def _load_config(self):
        """加载API配置"""
        if self._api_config is None:
            try:
                from config.config_loader import load_api_config
                self._api_config = load_api_config()
            except Exception as e:
                self.logger.error(f"加载API配置失败: {e}")
                self._api_config = {}
        return self._api_config
    
    def get_client(self, provider: Optional[str] = None) -> Union[GeminiClient, DeepSeekClient]:
        """
        获取AI客户端实例
        
        Args:
            provider: 模型提供商，可选值为 "gemini", "deepseek", "qwen"
                     如果为None，则使用默认配置
        
        Returns:
            对应的AI客户端实例
        """
        config = self._load_config()
        
        if provider is None:
            provider = config.get('default_provider', 'deepseek')
        
        if provider.lower() == 'gemini':
            return self._get_gemini_client()
        elif provider.lower() == 'deepseek':
            return self._get_deepseek_client()
        elif provider.lower() == 'qwen':
            return self._get_deepseek_client()
        else:
            self.logger.warning(f"未知的模型提供商: {provider}, 使用默认的DeepSeek客户端")
            return self._get_deepseek_client()
    
    def _get_gemini_client(self) -> GeminiClient:
        """获取Gemini客户端实例（单例模式）"""
        if self._gemini_client is None:
            config = self._load_config()
            providers = config.get('providers', {})
            gemini_config = providers.get('gemini', {})
            
            api_key = gemini_config.get('api_key', '')
            if not api_key or api_key == "your_gemini_api_key_here":
                raise ValueError("GEMINI_API_KEY 未设置，请在config/api_config.json中配置")
            
            self._gemini_client = GeminiClient(api_key)
            self.logger.info("Gemini客户端已初始化")
        return self._gemini_client
    
    def _get_deepseek_client(self) -> DeepSeekClient:
        """获取DeepSeek客户端实例（单例模式）"""
        if self._deepseek_client is None:
            config = self._load_config()
            providers = config.get('providers', {})
            deepseek_config = providers.get('deepseek', {})
            
            api_key = deepseek_config.get('api_key', '')
            if not api_key or api_key == "":
                raise ValueError("DEEPSEEK_API_KEY 未设置，请在config/api_config.json中配置")
            
            base_url = deepseek_config.get('base_url', 'https://api.deepseek.com')
            model = deepseek_config.get('model', 'deepseek-chat')
            
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
        config = self._load_config()
        api_providers = config.get('providers', {})
        
        # 检查所有配置的提供商
        for provider_name, provider_config in api_providers.items():
            if not provider_config.get('enabled', True):
                continue
                
            api_key = provider_config.get('api_key', '')
            
            # 根据不同提供商检查API密钥有效性
            if provider_name == 'gemini':
                if api_key and api_key != "your_gemini_api_key_here":
                    providers.append(provider_name)
            elif provider_name in ['deepseek', 'qwen']:
                if api_key and api_key.strip():
                    providers.append(provider_name)
        
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