# Joha（约哈）— 智能群聊机器人

> 🤖 基于 LLM 的智能群聊机器人框架，支持多模型切换、智能回复决策、风格学习、知识库检索。

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![ncatbot](https://img.shields.io/badge/ncatbot-4.4.1-orange.svg)

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [配置说明](#-配置说明) • [命令参考](#-命令参考) • [架构说明](#-架构说明)

</div>

---

## ✨ 功能特性

### 🎯 核心能力

| 特性 | 说明 |
|------|------|
| **智能回复决策** | 基于概率计算（Logit 累加 + Sigmoid 归一化）判断是否回复，避免废话刷屏 |
| **多模型切换** | 运行时动态切换 AI 模型（DeepSeek / 通义千问 / Gemini 等） |
| **消息队列合并** | 短时间内的多条消息自动合并，减少不必要的回复 |
| **多模态支持** | 支持图片理解（Qwen-VL、GPT-4o 等视觉模型） |
| **群组动态调节** | 根据群活跃度、消息频率、认可率自动调整回复阈值 |

### 🚀 进阶能力

| 特性 | 说明 |
|------|------|
| **风格学习** | 自动学习群成员说话风格,使回复更自然融入群聊 |
| **人设管理** | 基于多维度参数的精细化人设系统，支持动态调整性格特质、表达风格、社交行为等参数 |
| **知识库 (RAG)** | 基于文档检索增强生成，支持知识搜索、添加与管理 |
| **工具调用** | 支持搜索、网页抓取、知识库检索等工具 |
| **主动/被动模式** | 支持全局和逐群设置主动/被动回复模式 |
| **冷却系统** | 防刷屏机制，避免频繁回复 |
| **用户画像** | 记录用户偏好和聊天习惯 |
| **管理员系统** | 多级权限管理，管理员专属命令 |

---

## 🚀 快速开始

### 📋 环境要求

- **Python**: >= 3.9
- **消息平台适配器**: 运行中（如 NapCatQQ 等）
  - 示例: [NapCatQQ GitHub](https://github.com/NapNeko/NapCatQQ)
  - 确保 WebSocket 端口默认 3002 或自行配置

### 📦 安装步骤

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd "JohaBot"

# 2. 安装依赖
pip install ncatbot==4.4.1
pip install -r requirements.txt

# 3. 配置消息平台适配器
#    确保适配器已启动，WebSocket 端口为 3002（或修改 config.yaml）

# 4. 配置 AI API Key
#    复制配置示例文件
cp joha/config/config.example.json joha/config/config.json
cp config.example.yaml config.yaml
#    编辑 joha/config/config.json，填入你的 API Key

# 5. 运行机器人
python main.py
```

> ⚠️ **重要提示**: 必须安装 `ncatbot==4.4.1` 版本，其他版本可能存在兼容性问题！

### 📚 依赖清单

| 依赖 | 版本 | 用途 |
|------|------|------|
| `ncatbot` | **4.4.1** | 消息平台适配器核心（⚠️ 必须使用此版本） |
| `openai` | >=1.0.0 | LLM API 调用（兼容 OpenAI 协议） |
| `pyyaml` | >=6.0 | YAML 配置解析 |
| `jieba` | >=0.42.1 | 中文分词（知识库检索） |
| `python-dotenv` | >=1.0.0 | 环境变量管理（可选） |

---

## ⚙️ 配置说明

### 📝 配置文件概览

Joha 使用两个主要配置文件：

1. **config.yaml** - 消息平台连接配置
2. **joha/config/config.json** - 机器人主配置（LLM、决策参数等）

> 💡 **首次使用**: 请复制示例配置文件并修改：
> ```bash
> cp config.example.yaml config.yaml
> cp joha/config/config.example.json joha/config/config.json
> ```

### 1️⃣ 连接配置 — `config.yaml`

消息平台连接参数：

```yaml
root: ''          # 超级管理员 ID
bt_uin: ''         # 机器人 ID
napcat:
  ws_uri: ws://localhost:3002    # WebSocket 连接地址
  ws_token: token           # WebSocket 鉴权 Token
  webui_uri: http://localhost:6098  # NapCat WebUI
```

### 2️⃣ 主配置 — `joha/config/config.json`

包含所有运行参数，主要模块：

#### 🤖 LLM 模型配置

可配置多个 Provider，运行时通过命令切换：

```json
{
  "llm": {
    "active_provider": "deepseek",
    "providers": [
      {
        "name": "deepseek",
        "label": "深度求索",
        "api_key": "sk-xxx",
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-v4-flash",
        "default": true
      },
      {
        "name": "alibaba",
        "label": "阿里云（通义千问）",
        "api_key": "sk-xxx",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen3.5-omni-flash-2026-03-15"
      }
    ]
  }
}
```

#### 🧠 回复决策参数

核心调参区域，影响机器人的"话多话少"：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `thresholds.group` | 0.55 | 群聊回复概率阈值（越高越不爱说话） |
| `thresholds.private` | 0.4 | 私聊回复阈值 |
| `thresholds.admin` | 0.25 | 管理员回复阈值 |
| `feedback_weights.at_bot` | 2.5 | @机器人时的权重加成 |
| `feedback_weights.command` | 3.0 | 触发命令时的权重加成 |
| `group_dynamic.very_busy_score` | -0.8 | 非常活跃群减分 |
| `group_dynamic.dead_score` | 0.3 | 冷清群加分 |

#### 📨 消息队列配置

```json
{
  "message_queue": {
    "enabled": true,
    "merge_window": 120.0,
    "max_queue_size": 5
  }
}
```

- `merge_window`: 合并时间窗口（秒），此时间内多条消息会合并处理
- `max_queue_size`: 最大队列长度，超出后直接触发决策

---

## 📖 命令参考

### 👥 全员可用命令

| 命令 | 别名 | 说明 |
|------|------|------|
| `/好评` | `/good` | 记录正面反馈，调整决策参数 |
| `/差评` | `/bad` | 记录负面反馈，调整决策参数 |
| `/群状态` | — | 查看当前群的运行状态详情 |

### 🔧 管理员命令

| 命令 | 说明 |
|------|------|
| `/帮助` | 显示命令帮助列表 |
| `/全局启动` | 全局切换到主动模式（主动回复） |
| `/全局关闭` | 全局切换到被动模式（仅被@时回复） |
| `/本群启动` | 本群切换到主动模式 |
| `/本群关闭` | 本群切换到被动模式 |
| `/模式` | 查看当前全局模式 |
| `/模式 <群号>` | 查看指定群的模式 |
| `/管理员列表` | 查看所有管理员 |
| `/添加管理员 <ID>` | 添加管理员 |
| `/删除管理员 <ID>` | 删除管理员 |
| `/模型` | 查看可用模型列表 |
| `/当前模型` | 查看当前使用的模型 |
| `/切换模型 <名称>` | 切换到指定模型 |
| `/风格 <ID>` | 查看用户的风格学习数据 |
| `/清除风格 <ID>` | 清除用户的风格数据 |
| `/统计` | 查看机器人运行统计 |
| `/人设` | 查看人设稳定性报告 |
| `/知识库统计` | 查看知识库统计信息 |
| `/知识库刷新` | 刷新知识库索引 |
| `/知识库搜索 <关键词>` | 搜索知识库 |
| `/知识库添加 <问题\|回答>` | 添加新的知识条目 |
| `/知识库重复` | 查找知识库中的重复文档 |

> 💡 **提示**: 许多命令支持自然语言别名触发，例如发送"帮助"会自动转为`/帮助`，发送"模型列表"会自动转为`/模型`。

---

## 🏗️ 架构说明

### 项目结构

```
main.py                    ← 入口：启动 Bot，注册群消息事件
  │
  └─ joha/                 ← 核心包
       ├─ core/            ← 编排入口层（分拆为三个子模块）
       │    ├─ handlers/        — 处理器模块
       │    │    ├─ message.py        — 消息接收与预处理
       │    │    ├─ service.py        — 核心业务逻辑（学习 + 回复分离）
       │    │    └─ commands.py       — 命令处理
       │    ├─ builders/        — 构建器模块
       │    │    ├─ message_builder.py— LLM 上下文构建
       │    │    └─ message_queue.py  — 消息队列合并
       │    └─ utils/           — 工具模块
       │         ├─ runtime_context.py  — 运行时上下文
       │         ├─ persona_monitor.py  — 人设监控
       │         ├─ response_postprocessor.py — 回复后处理
       │         └─ clean_history.py    — 历史记录清洗
       │
       ├─ ai/              ← AI 驱动层
       │    ├─ clients.py        — AI 客户端抽象
       │    ├─ providers.py      — Provider 管理器
       │    ├─ bot.py            — AI Bot 封装
       │    ├─ generator.py      — 回复生成器
       │    └─ classifier.py     — 意图分类器
       │
       ├─ decision/        ← 决策大脑层
       │    ├─ reply_decision.py — 回复决策引擎
       │    ├─ reply_config.py   — 决策配置加载
       │    ├─ intent_classifier.py— 意图分类
       │    ├─ command_analyzer.py— 指令分析
       │    ├─ group_state.py    — 群组状态追踪
       │    ├─ cooldown.py       — 冷却管理
       │    ├─ knowledge/        — 知识库模块 (RAG)
       │    └─ tools/            — 工具（搜索等）
       │
       ├─ managers/        ← 数据管理层
       │    ├─ personas.py       — 人设管理
       │    ├─ style_learner.py  — 风格学习
       │    ├─ history_manager.py— 历史记录
       │    ├─ user_profile.py   — 用户画像
       │    └─ admin.py          — 管理员管理
       │
       └─ config/         ← 配置与基础设施
            ├─ config_manager.py— 配置管理器
            ├─ config.json      — 主配置文件
            ├─ group_mode_config.py — 群组模式配置
            ├─ logger.py        — 日志系统
            └─ cache.py         — 缓存管理
```

### 🔄 消息处理流程

```
群消息 → ncatbot 接收
         → MessageProcessor.process_group_message()
            → 消息队列合并（短时间多条消息）
            → 命令预处理（/命令）
            → MessageService.process_message()
                → 判断群组模式（active/passive）
                → 学习阶段：记录历史 + 学习风格
                → 决策阶段：计算回复概率
                   (上下文 → Logit累加 → Sigmoid归一化 → 阈值比较)
                → 生成阶段：构建上下文 → 调用 LLM → 返回回复
            → 发送回复到群聊
```

### 🎲 回复决策引擎

决策引擎是 Joha 的核心亮点，通过多层因素计算回复概率：

1. **反馈权重层**：是否被@、是否被回复、是否提及昵称、是否包含疑问
2. **场景阈值层**：根据群活跃度、消息频率动态调整阈值
3. **群动态调节**：非常活跃群降低回复概率，冷清群提高回复概率
4. **内容质量**：消息长度奖励/惩罚、垃圾信息检测
5. **意图融合**：规则分类和 AI 分类双重判断，加权融合
6. **冷却管理**：防止短时间内连续回复

最终概率通过 Sigmoid 函数归一化到 [0, 1]，与阈值比较决定是否回复。

### 📦 Core 模块结构

Core 模块采用分层设计，分拆为三个子模块：

| 子模块 | 职责 | 包含文件 |
|--------|------|----------|
| **handlers/** | 处理器模块 - 消息接收、处理和业务逻辑 | message.py, service.py, commands.py |
| **builders/** | 构建器模块 - 构建数据结构和上下文 | message_builder.py, message_queue.py |
| **utils/** | 工具模块 - 辅助功能和工具类 | runtime_context.py, persona_monitor.py, response_postprocessor.py, clean_history.py |

**导入示例：**
```python
# 从主入口导入（推荐）
from joha.core import message_service, message_processor, command_handler

# 从子模块导入
from joha.core.handlers import message_service
from joha.core.builders import message_builder
from joha.core.utils import runtime_context
```

详细结构说明请查看 `joha/core/README.md`。

---

## 🔧 高级配置

### 🌍 环境变量覆盖

配置管理器支持环境变量覆盖，可设置 `JOHA_` 前缀的环境变量来覆盖 `config.json` 中的值。

### 🎮 运行模式

| 模式 | 说明 |
|------|------|
| **主动模式 (active)** | 机器人根据决策引擎自动判断是否回复 |
| **被动模式 (passive)** | 仅在被@、被回复或触发命令时回复 |

可通过 `/全局启动`、`/全局关闭`、`/本群启动`、`/本群关闭` 命令切换。

### 🔄 多 Provider 策略

配置多个 LLM Provider 后，可在运行时通过 `/切换模型 <名称>` 动态切换，无需重启机器人。不同的 Provider 可用于不同的角色：

- **对话模型**：主动聊天使用的模型
- **意图识别模型**：可单独配置意图分类专用模型
- **工具调用模型**：可单独配置工具调用专用模型

### 👤 人设系统

Joha 使用基于多维度参数的精细化人设系统，通过调整性格特质、表达风格、社交行为等参数来塑造角色：

- **性格维度**：外向性、宜人性、尽责性、神经质、开放性（0-10）
- **表达风格**：话痨程度、正式度、情感表达、幽默感、自信度（0-10）
- **社交行为**：热情度、礼貌度、好奇心、共情力、耐心值（0-10）
- **语言特征**：表情符号、网络用语、语气词、打字错误容忍、句子长度
- **话题偏好**：感兴趣的话题、避免的话题、情绪倾向

当前默认人设为"大学生"角色，可通过 `/人设` 命令查看当前人设参数详情。

---

## 📁 目录结构

```
Joha/
├── main.py                  # 入口文件
├── config.yaml              # ncatbot 连接配置
├── config.example.yaml      # 配置示例（复制后使用）
├── requirements.txt         # Python 依赖
├── README.md                # 本文件
│
├── joha/                    # 核心代码包
│   ├── core/               # 编排入口层
│   ├── ai/                 # AI 驱动层
│   ├── decision/           # 决策大脑层
│   ├── managers/           # 数据管理层
│   └── config/             # 配置与基础设施
│
├── data/                    # 数据目录
├── logs/                    # 运行日志
├── napcat/                  # NapCat 相关
└── plugins/                 # 插件目录
```

### 💾 存储目录 `joha/storage/`

| 文件 | 说明 |
|------|------|
| `group_states.json` | 群组状态持久化 |
| `group_modes.json` | 群组模式配置 |
| `user_profiles.json` | 用户画像数据 |
| `cooldown.json` | 冷却状态 |
| `history/` | 聊天历史记录 |
| `styles/` | 风格学习数据 |
| `johalog/` | 运行日志文件 |
| `txt/` | 对话记录文本文件 |

---

## ❓ 常见问题

<details>
<summary><b>🤔 Q: 机器人不说话？</b></summary>

- 检查是否处于被动模式（使用 `/模式` 查看）
- 检查 `thresholds.group` 是否过高，可适当调低（如从 0.55 调到 0.45）
- 检查 API Key 是否正确配置
- 检查消息平台适配器是否正常运行
- 查看日志文件 `joha/storage/johalog/ai.log` 排查错误

</details>

<details>
<summary><b>💬 Q: 机器人话太多？</b></summary>

- 调高 `thresholds.group`（如 0.55 → 0.75）
- 切换到被动模式：`/全局关闭`
- 调大冷却时间
- 启用消息队列合并功能

</details>

<details>
<summary><b>🔄 Q: 如何添加更多 AI 模型？</b></summary>

在 `joha/config/config.json` 的 `llm.providers` 数组中添加新的 Provider 配置，只需 API 兼容 OpenAI 协议即可。

示例：
```json
{
  "name": "your_provider",
  "label": "自定义模型",
  "api_key": "your-api-key",
  "base_url": "https://api.example.com/v1",
  "model": "model-name",
  "default": false
}
```

</details>

<details>
<summary><b>📚 Q: 知识库文件存放在哪里？</b></summary>

知识库数据存储在 `joha/decision/knowledge/` 目录下，支持纯文本文档格式。

</details>

<details>
<summary><b>⚠️ Q: 为什么必须使用 ncatbot 4.4.1？</b></summary>

Joha 针对 ncatbot 4.4.1 版本进行了优化和测试，其他版本可能存在 API 兼容性问题或功能异常。请使用以下命令安装正确版本：

```bash
pip install ncatbot==4.4.1
```

</details>

---

## 📄 许可证

本项目基于 MIT 许可证开源。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，欢迎通过 GitHub Issues 联系。

---

<div align="center">

**Made with ❤️ by Joha Team**

⭐ 如果这个项目对你有帮助，请给我们一个 Star！

</div>
