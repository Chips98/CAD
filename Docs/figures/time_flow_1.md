sequenceDiagram
    participant U as 用户
    participant M as Main.py
    participant SE as SimulationEngine
    participant EG as EventGenerator
    participant AG as Agents
    participant AI as AI Client
    participant TSM as TherapySessionManager
    
    Note over U,TSM: 心理健康模拟流程
    
    U->>M: 启动程序
    M->>M: 选择AI提供商
    M->>SE: 创建模拟引擎
    SE->>SE: 加载配置文件
    SE->>AG: 初始化7个智能体
    SE->>EG: 初始化事件生成器
    
    loop 30天模拟
        SE->>SE: 确定当前阶段
        SE->>EG: 生成当日事件
        EG->>AI: 调用AI生成事件
        AI-->>EG: 返回事件描述
        EG-->>SE: 返回事件和参与者
        SE->>AG: 处理事件影响
        AG->>AG: 更新心理状态
        SE->>SE: 记录当日状态
    end
    
    SE->>SE: 生成最终报告
    SE-->>M: 模拟完成
    M-->>U: 显示结果摘要
    
    Note over U,TSM: 心理咨询流程
    
    U->>M: 选择心理咨询
    M->>TSM: 创建咨询管理器
    TSM->>TSM: 加载患者数据
    TSM-->>U: 显示患者状态
    
    loop 咨询对话
        U->>TSM: 输入咨询内容
        TSM->>AI: 生成患者回应
        AI-->>TSM: 返回回应内容
        TSM->>TSM: 评估对话效果
        TSM->>TSM: 更新治疗进展
        TSM-->>U: 显示患者回应
        
        alt 触发督导
            TSM->>AI: 请求AI督导
            AI-->>TSM: 返回督导建议
            TSM-->>U: 显示督导建议
        end
        
        alt 查看进展
            U->>TSM: 输入'p'查看进展
            TSM-->>U: 显示治疗进展
        end
    end
    
    TSM->>TSM: 保存咨询记录
    TSM-->>U: 咨询结束