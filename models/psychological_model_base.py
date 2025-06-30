"""
心理模型基础抽象类
定义了所有心理模型必须实现的接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from models.psychology_models import LifeEvent, PsychologicalState


class PsychologicalModelType(Enum):
    """心理模型类型枚举"""
    BASIC_RULES = "basic_rules"          # 基础规则模型
    CAD_ENHANCED = "cad_enhanced"        # CAD增强模型  
    LLM_DRIVEN = "llm_driven"           # LLM驱动模型
    HYBRID = "hybrid"                   # 混合模型


@dataclass
class ModelImpactResult:
    """模型影响结果"""
    # 基础心理指标变化
    depression_change: float = 0.0       # 抑郁程度变化
    anxiety_change: float = 0.0          # 焦虑水平变化  
    stress_change: float = 0.0           # 压力水平变化
    self_esteem_change: float = 0.0      # 自尊水平变化
    social_connection_change: float = 0.0 # 社交连接变化
    
    # CAD状态变化（如果支持）
    affective_tone_change: float = 0.0   # 情感基调变化
    self_belief_change: float = 0.0      # 自我信念变化
    world_belief_change: float = 0.0     # 世界信念变化
    future_belief_change: float = 0.0    # 未来信念变化
    rumination_change: float = 0.0       # 思维反刍变化
    distortion_change: float = 0.0       # 认知扭曲变化
    social_withdrawal_change: float = 0.0 # 社交退缩变化
    avolition_change: float = 0.0        # 动机缺失变化
    
    # 模型元信息
    model_type: str = ""                 # 使用的模型类型
    confidence: float = 1.0              # 模型置信度
    reasoning: str = ""                  # 计算理由
    processing_time: float = 0.0         # 处理时间（毫秒）
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "basic_changes": {
                "depression_change": self.depression_change,
                "anxiety_change": self.anxiety_change,
                "stress_change": self.stress_change,
                "self_esteem_change": self.self_esteem_change,
                "social_connection_change": self.social_connection_change
            },
            "cad_changes": {
                "affective_tone_change": self.affective_tone_change,
                "self_belief_change": self.self_belief_change,
                "world_belief_change": self.world_belief_change,
                "future_belief_change": self.future_belief_change,
                "rumination_change": self.rumination_change,
                "distortion_change": self.distortion_change,
                "social_withdrawal_change": self.social_withdrawal_change,
                "avolition_change": self.avolition_change
            },
            "meta": {
                "model_type": self.model_type,
                "confidence": self.confidence,
                "reasoning": self.reasoning,
                "processing_time": self.processing_time
            }
        }


class PsychologicalModelBase(ABC):
    """心理模型基础抽象类"""
    
    def __init__(self, model_type: PsychologicalModelType, config: Dict[str, Any] = None):
        """
        初始化心理模型
        
        Args:
            model_type: 模型类型
            config: 模型配置参数
        """
        self.model_type = model_type
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{model_type.value}")
        self.is_initialized = False
        
        # 模型统计信息
        self.total_calculations = 0
        self.total_processing_time = 0.0
        self.error_count = 0
        
        # 初始化模型
        self._initialize_model()
    
    @abstractmethod
    def _initialize_model(self):
        """初始化模型特定组件"""
        pass
    
    @abstractmethod
    async def calculate_impact(self, 
                             event: LifeEvent, 
                             current_state: PsychologicalState,
                             context: Dict[str, Any] = None) -> ModelImpactResult:
        """
        计算事件对心理状态的影响
        
        Args:
            event: 生活事件
            current_state: 当前心理状态
            context: 上下文信息（人格、历史事件等）
            
        Returns:
            ModelImpactResult: 影响计算结果
        """
        pass
    
    @abstractmethod
    def supports_cad_state(self) -> bool:
        """返回模型是否支持CAD状态计算"""
        pass
    
    @abstractmethod
    def supports_async_processing(self) -> bool:
        """返回模型是否支持异步处理"""
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "type": self.model_type.value,
            "supports_cad": self.supports_cad_state(),
            "supports_async": self.supports_async_processing(),
            "is_initialized": self.is_initialized,
            "config": self.config,
            "statistics": {
                "total_calculations": self.total_calculations,
                "average_processing_time": (
                    self.total_processing_time / self.total_calculations 
                    if self.total_calculations > 0 else 0
                ),
                "error_rate": (
                    self.error_count / self.total_calculations 
                    if self.total_calculations > 0 else 0
                )
            }
        }
    
    def _record_calculation(self, processing_time: float, success: bool = True):
        """记录计算统计信息"""
        self.total_calculations += 1
        self.total_processing_time += processing_time
        if not success:
            self.error_count += 1
    
    def get_display_name(self) -> str:
        """获取模型显示名称"""
        display_names = {
            PsychologicalModelType.BASIC_RULES: "基础规则模型",
            PsychologicalModelType.CAD_ENHANCED: "CAD认知增强模型", 
            PsychologicalModelType.LLM_DRIVEN: "LLM驱动模型",
            PsychologicalModelType.HYBRID: "混合模型"
        }
        return display_names.get(self.model_type, self.model_type.value)
    
    def get_description(self) -> str:
        """获取模型描述"""
        descriptions = {
            PsychologicalModelType.BASIC_RULES: 
                "基于简单规则的心理状态更新，快速但相对简单",
            PsychologicalModelType.CAD_ENHANCED: 
                "结合认知-情感-抑郁(CAD)理论的增强模型，更符合心理学原理",
            PsychologicalModelType.LLM_DRIVEN: 
                "完全基于大语言模型的心理评估，最为智能但耗时较长",
            PsychologicalModelType.HYBRID: 
                "结合多种模型优势的混合方案，平衡准确性与效率"
        }
        return descriptions.get(self.model_type, "未知模型类型")


class ModelFactory:
    """心理模型工厂类"""
    
    _model_registry = {}
    
    @classmethod
    def register_model(cls, model_type: PsychologicalModelType, model_class):
        """注册模型类"""
        cls._model_registry[model_type] = model_class
    
    @classmethod
    def create_model(cls, 
                    model_type: PsychologicalModelType, 
                    config: Dict[str, Any] = None,
                    ai_client = None) -> PsychologicalModelBase:
        """
        创建心理模型实例
        
        Args:
            model_type: 模型类型
            config: 模型配置
            ai_client: AI客户端（LLM模型需要）
            
        Returns:
            PsychologicalModelBase: 模型实例
        """
        if model_type not in cls._model_registry:
            raise ValueError(f"未注册的模型类型: {model_type}")
        
        model_class = cls._model_registry[model_type]
        
        # 检查是否需要AI客户端
        if hasattr(model_class, 'REQUIRES_AI_CLIENT') and model_class.REQUIRES_AI_CLIENT:
            if ai_client is None:
                raise ValueError(f"模型 {model_type.value} 需要AI客户端")
            return model_class(model_type, config, ai_client)
        else:
            return model_class(model_type, config)
    
    @classmethod
    def get_available_models(cls) -> List[PsychologicalModelType]:
        """获取可用的模型类型列表"""
        return list(cls._model_registry.keys())
    
    @classmethod
    def get_model_info_all(cls) -> Dict[PsychologicalModelType, Dict[str, Any]]:
        """获取所有模型的信息"""
        info = {}
        for model_type in cls._model_registry:
            try:
                # 创建临时实例获取信息
                temp_model = cls.create_model(model_type, {})
                info[model_type] = {
                    "display_name": temp_model.get_display_name(),
                    "description": temp_model.get_description(),
                    "supports_cad": temp_model.supports_cad_state(),
                    "supports_async": temp_model.supports_async_processing(),
                    "requires_ai_client": hasattr(cls._model_registry[model_type], 'REQUIRES_AI_CLIENT') 
                                        and cls._model_registry[model_type].REQUIRES_AI_CLIENT
                }
            except Exception as e:
                info[model_type] = {
                    "display_name": "错误",
                    "description": f"模型初始化失败: {e}",
                    "supports_cad": False,
                    "supports_async": False,
                    "requires_ai_client": True
                }
        return info


# 自动导入并注册所有模型
def _auto_import_models():
    """自动导入所有心理模型"""
    try:
        # 导入各个模型文件，这会触发它们的注册语句
        import models.basic_rules_model
        import models.cad_enhanced_model
        import models.llm_driven_model
        import models.hybrid_model
    except ImportError as e:
        # 如果某些模型导入失败，记录警告但不中断
        logging.getLogger(__name__).warning(f"自动导入模型失败: {e}")

# 在模块导入时自动注册所有模型
_auto_import_models()