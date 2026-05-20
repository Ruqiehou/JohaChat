# Masu Adapter 更新说明

## 概述

基于 `masunew` 目录对 `masu` 目录进行更新，并新增 adapter 触发 napcat 功能。

## 主要更新内容

### 1. 新增 adapter 模块

从 `masunew` 复制完整的 adapter 模块到 `masu/adapter/`，包含：

- `bot_client.py` - 机器人客户端，装饰器模式入口
- `config/` - 配置管理模块
- `core/` - 核心模块（连接、API、事件、终端输出等）

### 2. 更新核心模块

#### `masu/core/service.py`
- 添加 `terminal` 模块导入和使用
- 改进日志输出，支持彩色终端显示

#### `masu/core/message_handler.py`
- 添加 `message_queue_manager` 导入
- 改进网页处理逻辑，增加错误检测和处理
- 使用消息队列进行智能合并

#### `masu/core/message_queue.py`
- 从 v3.0 升级到 v4.0
- 新增 LLM 智能合并功能（`LLMergeJudge` 类）
- 支持通过配置启用/禁用 LLM 合并判断

### 3. 更新 AI 模块

#### `masu/ai/clients.py`
- 改进响应处理逻辑，支持非标准格式响应
- 增强错误处理和兼容性

#### `masu/ai/providers.py`
- 配置路径从 `llm.providers` 改为 `chat-llm.providers`

### 4. 更新配置模块

#### `masu/config/config_manager.py`
- 配置路径从 `llm.providers` 改为 `chat-llm.providers`
- 统一配置读取方式

### 5. 新增 Adapter 触发 Napcat 功能

#### 新增文件：`run_adapter.py`

新的入口文件，使用 adapter 模块连接 napcat 并处理消息。

**功能特性：**
- 从配置读取 napcat 目录（默认为 `napcat`，与 run.py 同级）
- 支持自动启动 napcat（通过配置 `napcat.auto_start`）
- 注册群消息和私聊消息处理器
- 使用 adapter 模块的 BotClient 连接 napcat

#### 更新配置：`config.yaml`

新增 napcat 相关配置项：

```yaml
napcat:
  # ... 原有配置 ...
  auto_start: false          # 是否自动启动 napcat
  napcat_dir: napcat         # napcat 目录路径（相对于项目根目录）
```

#### 更新配置类：`masu/adapter/config/config.py`

新增配置方法：

```python
def set_napcat_dir(self, napcat_dir: str) -> None:
    """设置 napcat 目录"""

def set_auto_start(self, auto_start: bool) -> None:
    """设置是否自动启动 napcat"""
```

## 使用方法

### 方式一：手动启动 napcat 后运行

```bash
# 1. 先手动启动 napcat
cd napcat
launcher.bat

# 2. 运行 adapter
python run_adapter.py
```

### 方式二：配置自动启动 napcat

1. 编辑 `config.yaml`，设置：
   ```yaml
   napcat:
     auto_start: true
     napcat_dir: napcat  # napcat 目录路径
   ```

2. 运行 adapter：
   ```bash
   python run_adapter.py
   ```

### 方式三：使用原有入口

原有的 `run.py` 仍然可用，使用 ncatbot 模块：

```bash
python run.py
```

## 配置说明

### Napcat 目录配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `napcat.napcat_dir` | napcat 目录路径（相对于项目根目录） | `napcat` |
| `napcat.auto_start` | 是否自动启动 napcat | `false` |
| `napcat.ws_uri` | WebSocket 连接地址 | `ws://localhost:3001` |
| `napcat.access_token` | WebSocket 访问令牌 | 空 |

### 消息队列配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `message_queue.enabled` | 是否启用消息队列 | `true` |
| `message_queue.merge_window` | 消息合并时间窗口（秒） | `60.0` |
| `message_queue.max_queue_size` | 最大队列大小 | `5` |
| `message_queue.llm_merge_enabled` | 是否启用 LLM 智能合并 | `false` |

## 目录结构

```
masu-xinxin/
├── run.py              # 原有入口（ncatbot 模式）
├── run_adapter.py      # 新入口（adapter 模式）
├── config.yaml         # 配置文件
├── masu/
│   ├── adapter/        # 新增 adapter 模块
│   │   ├── bot_client.py
│   │   ├── config/
│   │   └── core/
│   ├── ai/
│   ├── config/
│   ├── core/
│   └── ...
└── napcat/             # napcat 目录（与 run.py 同级）
```

## 注意事项

1. **napcat 目录位置**：默认与 `run.py` 同级，目录名为 `napcat`，可通过配置修改
2. **自动启动权限**：napcat 启动需要管理员权限，自动启动功能可能需要以管理员身份运行
3. **配置兼容性**：原有配置文件兼容，新增配置项有默认值
4. **两种入口模式**：
   - `run.py`：使用 ncatbot 模块，直接调用 ncatbot API
   - `run_adapter.py`：使用 adapter 模块，通过 WebSocket 连接 napcat

## 更新日期

2026-05-20
