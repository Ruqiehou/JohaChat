# Joha 系统架构设计文档

## 1. 架构总览

Joha 采用**分层 + 事件驱动**的架构设计，从上到下分为：

```
┌─────────────────────────────────────────────┐
│           消息平台层 (NapCatQQ)              │  ← OneBot 协议 / WebSocket
├─────────────────────────────────────────────┤
│           适配层 (joha.adapter)              │  ← MessageClient、事件分发
├─────────────────────────────────────────────┤
│           编排层 (joha.core)                 │  ← 消息处理、命令路由、队列合并
├─────────────────────────────────────────────┤
│           决策层 (joha.decision)             │  ← 回复概率计算、意图分类
├─────────────────────────────────────────────┤
│           AI 驱动层 (joha.ai)                │  ← LLM 调用、多 Provider 管理
├─────────────────────────────────────────────┤
│           管理层 (joha.managers)             │  ← 人设、风格、历史、画像
├─────────────────────────────────────────────┤
│           工具层 (joha.tools)                │  ← 搜索、网页抓取、知识库 RAG
├─────────────────────────────────────────────┤
│           基础设施 (joha.config)             │  ← 配置、日志、缓存
└─────────────────────────────────────────────┘
```

---

## 2. 各层职责

### 2.1 适配层 (joha.adapter)

负责与外部消息平台（NapCatQQ）建立和维护连接。

| 模块 | 文件 | 职责 |
|------|------|------|
| MessageClient | `bot_client.py` | WebSocket 消息客户端封装，连接生命周期管理 |
| NapCat 启动器 | `napcat_launcher.py` | 自动检测/启动 NapCatQQ 进程 |
| 事件核心 | `core/` | API 封装、事件模型、事件总线、事件分发器 |
| 配置读取 | `config/` | 连接配置 (`connection.yaml`)、配置管理器 |

**关键类：**
- `MessageClient`: 入口类，负责 `ws_url` 连接、事件注册、消息收发
- `GroupMessageEvent`: 群消息事件模型
- `EventBus`: 内部事件总线，解耦消息接收与业务处理

### 2.2 编排层 (joha.core)

负责消息流入后的预处理、命令识别、业务编排。

| 模块 | 文件 | 职责 |
|------|------|------|
| 消息处理器 | `handlers/message_handler.py` | 消息接收、@/回复检测、队列合并调度 |
| 命令处理器 | `handlers/commands.py` | 斜杠命令解析与路由 |
| 业务服务 | `handlers/service.py` | 核心编排：学习 → 决策 → 生成的完整流水线 |
| 消息构建器 | `builders/message_builder.py` | LLM 上下文组装（含 RAG 检索注入） |
| 消息队列 | `builders/message_queue.py` | 短时间多条消息合并，减少冗余回复 |

**处理流水线：**
```
群消息事件
    ↓
MessageHandler.process_group_message()
    ├── 提取消息文本/图片
    ├── 斜杠命令直通返回
    ├── @/回复检测
    └── 消息队列合并
            ↓
    MessageService.process_message()
        ├── 判断群组模式 (active/passive)
        ├── 学习阶段：记录历史 + 风格学习
        ├── 决策阶段：DecisionEngine 流水线
        └── 生成阶段：构建上下文 → 调用 LLM
                    ↓
        BotAPI.send_group_message()
```

### 2.3 决策层 (joha.decision)

Joha 的核心亮点，负责判断机器人在什么场景下应该回复。

| 模块 | 文件 | 职责 |
|------|------|------|
| 决策引擎 | `decision_engine.py` | 总分架构的"总"，编排各子模块 |
| 回复决策 | `reply_decision.py` | Logit 累加 + Sigmoid 归一化计算回复概率 |
| 回复配置 | `reply_config.py` | `reply_decision.json` 的懒加载与热重载 |
| 意图分类 | `intent_classifier.py` | AI 意图识别（规则 + 模型双重判断） |
| 命令分析 | `command_analyzer.py` | 自然语言命令解析（如"帮助"→`/帮助`） |
| 群组状态 | `group_state.py` | 群活跃度追踪、消息频率统计 |
| 冷却管理 | `cooldown.py` | 防刷屏，限制短时间连续回复 |

**决策因子：**
1. **反馈权重层**：被@、被回复、提及昵称、包含疑问
2. **场景阈值层**：群活跃度、消息频率动态调整
3. **群动态调节**：活跃群降概率，冷清群升概率
4. **内容质量**：消息长度奖励/惩罚、垃圾信息检测
5. **意图融合**：规则分类 + AI 分类加权融合
6. **冷却管理**：时间窗口内限制回复次数

### 2.4 AI 驱动层 (joha.ai)

负责与各种 LLM API 交互，支持多 Provider 动态切换。

| 模块 | 文件 | 职责 |
|------|------|------|
| AI 客户端 | `clients.py` | OpenAI 协议兼容的 API 调用封装 |
| Provider 管理 | `providers.py` | 多 Provider 注册、切换、负载均衡 |
| Bot 封装 | `bot.py` | 高层对话接口，隐藏底层 Provider 细节 |
| 回复生成器 | `generator.py` | 基于上下文的回复生成逻辑 |
| 分类器 | `classifier.py` | 文本分类（意图、情感等） |

### 2.5 管理层 (joha.managers)

负责各类数据的持久化与管理。

| 模块 | 文件 | 职责 |
|------|------|------|
| 人设管理 | `personas.py` | 多维度人设参数管理（性格、表达、社交等） |
| 风格学习 | `style_learner.py` | 自动学习群成员说话风格 |
| 历史记录 | `history_manager.py` | 聊天记录的存取与清洗 |
| 用户画像 | `user_profile.py` | 用户偏好和聊天习惯持久化 |
| 管理员系统 | `admin.py` | 权限分级、管理员增删查 |

### 2.6 工具层 (joha.tools)

采用**函数 + 元信息**模式，支持自动发现注册。

| 模块 | 文件 | 职责 |
|------|------|------|
| 知识库 | `knowledge/core.py` | 本地 RAG 引擎，BM25 检索，分片式 JSON 存储 |
| 网络搜索 | `search/` | 可配置搜索 API |
| 网页抓取 | `webpage/` | 网页内容抓取与解析 |
| 链接预览 | `link_preview/` | 链接摘要生成 |

### 2.7 基础设施 (joha.config)

| 模块 | 文件 | 职责 |
|------|------|------|
| 配置管理器 | `managers/config_manager.py` | JSON 配置 + 环境变量覆盖 (`JOHA_*`) |
| 群组模式配置 | `managers/group_mode_config.py` | 逐群的 active/passive 模式持久化 |
| 日志系统 | `infrastructure/logger.py` | 多级别日志、文件轮转、预定义记录器 |
| 缓存系统 | `infrastructure/cache.py` | LRU 缓存、TTL 过期、函数结果缓存装饰器 |

---

## 3. 数据流向

```
NapCatQQ ──WebSocket──→ MessageClient ──EventBus──→ MessageHandler
                                                          │
                    ┌───────────────────────────────────────┘
                    ↓
            MessageService.process_message()
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
   HistoryManager StyleLearner  DecisionEngine
        │           │           │
        └───────────┴───────────┘
                    ↓
            MessageBuilder (含 RAG)
                    ↓
            ChatEngine / Generator
                    ↓
            BotAPI.send_group_message()
                    ↓
            NapCatQQ ──→ 群聊
```

---

## 4. 存储结构

```
joha/storage/
├── group_states.json       # 群组状态持久化
├── group_modes.json        # 群组模式配置
├── user_profiles.json      # 用户画像数据
├── cooldown.json           # 冷却状态
├── history/                # 聊天历史记录
├── styles/                 # 风格学习数据
├── johalog/                # 运行日志文件
└── txt/                    # 知识库分片文件 (knowledge_0001.json...)
```
