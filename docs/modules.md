# Joha 模块说明文档

## 目录

- [adapter 适配层](#adapter-适配层)
- [core 编排层](#core-编排层)
- [ai AI驱动层](#ai-ai驱动层)
- [decision 决策层](#decision-决策层)
- [managers 管理层](#managers-管理层)
- [tools 工具层](#tools-工具层)
- [config 基础设施](#config-基础设施)

---

## adapter 适配层

路径: `joha/adapter/`

负责与 NapCatQQ 消息平台对接，提供 WebSocket 连接和事件抽象。

### bot_client.py
- **类**: `BotClient`
- **职责**: WebSocket 客户端入口，封装连接、心跳、重连逻辑
- **关键方法**:
  - `on_group_message()`: 装饰器，注册群消息事件回调
  - `start()`: 启动连接循环
  - `api`: 属性，暴露消息发送 API

### napcat_launcher.py
- **职责**: 自动检测 NapCatQQ 进程状态，支持自动启动
- **关键函数**:
  - `ensure_napcat_running()`: 确保 NapCatQQ 在运行

### core/ 子包

| 文件 | 类/函数 | 职责 |
|------|---------|------|
| `client.py` | `NapCatClient` | 底层 WebSocket 连接管理 |
| `api.py` | `BotAPI` | OneBot 协议 API 封装（发送消息等） |
| `events.py` | `GroupMessageEvent` 等 | 事件数据模型 |
| `event_bus.py` | `EventBus` | 内部事件总线，发布/订阅模式 |
| `event_dispatcher.py` | `EventDispatcher` | 事件分发器，将事件路由到对应处理器 |
| `emoji_map.py` | — | QQ 表情 ID 与文字映射 |
| `interfaces.py` | 接口定义 | 抽象接口 |

### config/ 子包

| 文件 | 职责 |
|------|------|
| `config.py` | 配置读取与解析 |
| `connection.yaml` | 实际连接配置 |
| `config.example.yaml` | 连接配置模板 |

---

## core 编排层

路径: `joha/core/`

负责消息流入后的完整处理流水线。

### handlers/message_handler.py
- **类**: `MessageProcessor`（或等效函数）
- **职责**: 
  - 接收原始群消息事件
  - 提取文本、图片、@信息等
  - 检测斜杠命令并直通返回
  - 检测@/回复关系
  - 将消息送入队列合并系统

### handlers/commands.py
- **职责**: 所有斜杠命令的解析与路由
- **支持命令**:
  - 全员: `/好评`, `/差评`, `/群状态`
  - 管理员: `/帮助`, `/全局启动`, `/全局关闭`, `/本群启动`, `/本群关闭`, `/模式`, `/管理员列表`, `/添加管理员`, `/删除管理员`, `/模型`, `/当前模型`, `/切换模型`, `/风格`, `/清除风格`, `/统计`, `/人设`, `/知识库统计`, `/知识库刷新`, `/知识库搜索`, `/知识库添加`, `/知识库重复`

### handlers/service.py
- **类**: `MessageService`
- **职责**: 核心业务编排
  - 判断群组模式（active/passive）
  - 调用学习模块记录历史、学习风格
  - 调用决策引擎判断是否回复
  - 调用生成器构建回复

### builders/message_builder.py
- **职责**: 为 LLM 构建完整的对话上下文
  - 组装系统提示词（含人设）
  - 注入历史消息
  - 调用 RAG 检索相关知识并注入上下文

### builders/message_queue.py
- **类**: `MessageQueueManager`
- **职责**: 
  - 维护各群的消息队列
  - 在 `merge_window` 时间内合并多条消息
  - 队列满或超时时触发批量处理

### utils/ 子包

| 文件 | 职责 |
|------|------|
| `runtime_context.py` | 运行时全局上下文（bot_uin 等） |
| `persona_monitor.py` | 人设参数监控与稳定性报告 |
| `tool_registry.py` | 工具自动发现与注册 |
| `response_postprocessor.py` | 回复后处理（过滤、格式化） |
| `image_utils.py` | 图片格式转换与处理 |
| `clean_history.py` | 历史记录清洗与压缩 |

---

## ai AI驱动层

路径: `joha/ai/`

负责 LLM 调用，封装多 Provider 差异。

### clients.py
- **类**: `AIClient`
- **职责**: OpenAI 协议兼容的底层 API 调用
- **关键方法**:
  - `chat_completion()`: 发送对话请求
  - `stream_chat()`: 流式对话（如支持）

### providers.py
- **类**: `ProviderManager`
- **职责**: 
  - 管理多个 LLM Provider
  - 运行时切换当前 Provider
  - 返回当前激活的客户端配置

### bot.py
- **类**: `AIBot`
- **职责**: 高层对话封装，隐藏 Provider 切换细节
- **关键方法**:
  - `chat()`: 发送消息并获取回复
  - `switch_provider()`: 切换模型

### generator.py
- **类**: `ReplyGenerator`
- **职责**: 基于 MessageBuilder 构建的上下文，调用 AIBot 生成回复
- **包含逻辑**: 工具调用循环、RAG 结果注入

### classifier.py
- **类**: `TextClassifier`
- **职责**: 文本分类任务（意图识别、情感分析等）

---

## decision 决策层

路径: `joha/decision/`

Joha 的核心大脑，决定是否回复消息。

### decision_engine.py
- **类**: `DecisionEngine`
- **职责**: 总分架构的"总控"，按顺序调用各子模块
- **流水线**:
  1. `build_context()`: 构建决策上下文
  2. `intent_classifier`: 意图分类
  3. `compute_reply_prob()`: 计算回复概率
  4. `should_reply()`: 综合判断是否回复

### reply_decision.py
- **类**: `ReplyDecision`
- **职责**: 核心概率计算
- **算法**:
  - 收集各因子分数（反馈权重、群动态、内容质量、意图等）
  - Logit 累加
  - Sigmoid 归一化到 `[0, 1]`
  - 与阈值比较

### reply_config.py
- **类**: `ReplyConfig`
- **职责**: 
  - 懒加载 `reply_decision.json`
  - 支持热重载
  - 提供配置项的属性访问

### intent_classifier.py
- **类**: `IntentClassifier`
- **职责**: AI + 规则双重意图识别
- **输出**: 意图类型 + 置信度

### command_analyzer.py
- **类**: `CommandAnalyzer`
- **职责**: 自然语言命令解析
- **示例**: "帮助" → `/帮助`, "模型列表" → `/模型`

### group_state.py
- **类**: `GroupStateTracker`
- **职责**: 
  - 追踪每个群的消息频率
  - 计算群活跃度等级（very_busy / busy / normal / quiet / dead）
  - 持久化到 `joha/storage/group_states.json`

### cooldown.py
- **类**: `CooldownManager`
- **职责**: 
  - 维护单群冷却和全局冷却状态
  - 检查是否可以回复
  - 记录每次回复时间

---

## managers 管理层

路径: `joha/managers/`

负责各类数据的持久化与管理。

### personas.py
- **类**: `PersonaManager`
- **职责**: 
  - 多维度人设参数管理
  - 性格维度、表达风格、社交行为、语言特征、话题偏好
  - 默认人设为"大学生"角色

### style_learner.py
- **类**: `StyleLearner`
- **职责**: 
  - 自动学习群成员说话风格
  - 提取词汇习惯、句式特征、表情使用等
  - 数据存储在 `joha/storage/styles/`

### history_manager.py
- **类**: `HistoryManager`
- **职责**: 
  - 聊天记录的增删查
  - 按群、按用户维度的历史查询
  - 历史清洗与压缩

### user_profile.py
- **类**: `UserProfileManager`
- **职责**: 
  - 用户画像持久化
  - 记录用户偏好、聊天习惯、互动频率
  - 存储在 `joha/storage/user_profiles.json`

### admin.py
- **类**: `AdminManager`
- **职责**: 
  - 管理员列表维护
  - 权限检查（`is_admin(user_id)`）
  - 支持多级权限

---

## tools 工具层

路径: `joha/tools/`

采用函数 + 元信息模式，支持自动发现注册。

### knowledge/core.py
- **类**: `KnowledgeBase`
- **职责**: 
  - 本地 RAG 引擎
  - BM25 检索算法
  - 分片式 JSON 存储（每片 100 条）
  - 增量热重载
- **存储位置**: `joha/storage/txt/knowledge_*.json`

### search/
- **职责**: 网络搜索工具
- **配置**: 在 `config.json` 中配置搜索 API

### webpage/
- **职责**: 网页内容抓取
- **输入**: URL
- **输出**: 网页正文摘要

### link_preview/
- **职责**: 链接预览
- **输出**: 标题、摘要、图片

---

## config 基础设施

路径: `joha/config/`

### managers/config_manager.py
- **类**: `ConfigManager`
- **职责**: 
  - JSON 配置文件读取
  - 环境变量覆盖（`JOHA_*` 前缀）
  - 配置项访问接口 `get(key, default)`

### managers/group_mode_config.py
- **类**: `GroupModeConfig`
- **职责**: 
  - 逐群的 active/passive 模式管理
  - 持久化到 `joha/storage/group_modes.json`

### infrastructure/logger.py
- **类**: `Logger`
- **职责**: 
  - 多级别日志（DEBUG/INFO/WARNING/ERROR）
  - 文件轮转
  - 预定义日志记录器
  - 便捷函数 `tprint(level, message)`

### infrastructure/cache.py
- **类**: `Cache`
- **职责**: 
  - LRU 缓存
  - TTL 过期
  - 函数结果缓存装饰器
