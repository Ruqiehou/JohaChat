# 更新日志

所有重要版本变更记录。

## v3.5.0 (2026-05-30)

### 架构重构

本次版本对项目进行了大规模的架构简化和命名规范化，提升了代码可读性和维护性。

#### 适配层（adapter）提级
- **`adapter/` 从 `joha/` 提升到项目根目录**，作为独立包，与 `joha/` 核心包平级
- 内部导入使用 `adapter.config`、`adapter.core` 等，外部导入从 `joha.adapter` 改为 `adapter`
- **移除 `adapter/config/` 子目录**，配置文件直接放在 `adapter/` 下，结构更扁平
- **移除 `napcat_launcher.py`**（自动拉起 NapCat），改为纯连接检测，用户需手动启动 NapCat
- **移除 `config.example.yaml`**，只保留 `connection.yaml` 作为唯一配置文件
- **`bot_client.py` 重命名为 `message_client.py`**，职责更清晰

#### 连接器职责分离
- **`NapCatClient`**（连接层）：专注于 WebSocket 连接管理、消息收发、API 调用
- **`MessageClient`**（封装层）：专注于事件路由、装饰器注册、生命周期管理
- 消息回调通过 `set_message_callback()` 注入，消除两层之间的重复定义

#### 核心层（core）扁平化
- 移除 `core/handlers/`、`core/builders/`、`core/utils/` 三个子目录
- 所有模块直接放在 `core/` 下，import 路径从 `joha.core.handlers.xxx` 简化为 `joha.core.xxx`

#### 命名规范化
| 旧名称 | 新名称 | 说明 |
|--------|--------|------|
| `AIBot` | `ChatEngine` | AI 对话引擎，更符合现代命名 |
| `ai_bot` / `get_ai_bot()` | `chat_engine` / `get_chat_engine()` | 全局实例和获取函数 |
| `BotClient` | `MessageClient` | 消息客户端，突出消息处理职责 |

#### 数据目录外提
- `joha/storage/` 提升到项目根目录 `storage/`
- 新增 `joha/config/paths.py` 集中定义所有存储路径
- 运行时通过 `ensure_storage_dirs()` 自动创建目录，无需手动初始化

#### IPv4/IPv6 兼容
- WebSocket 连接自动将 `localhost` 替换为 `127.0.0.1`，避免 IPv6 解析问题
- 配置示例和默认值统一使用 `127.0.0.1`

### 热重载
- 新增 `core/hot_reload.py`，基于 watchdog 监控 `joha/` 目录文件变化，支持开发时模块热重载

### 配置优先级
`run.py` 支持在代码中自定义连接配置，优先级：
1. 代码中设置的 `WS_URL` / `ACCESS_TOKEN` / `BOT_UIN`
2. `adapter/connection.yaml` 中的配置
3. 内置默认值

### 文件变更清单

**新增**
- `joha/config/paths.py` — 集中路径定义
- `joha/core/hot_reload.py` — 热重载模块
- `joha/adapter/config.py` — 配置管理（从子目录提升）
- `joha/adapter/connection.yaml` — 连接配置（从子目录提升）
- `joha/adapter/message_client.py` — 消息客户端（从 bot_client.py 重命名）
- `joha/core/service.py` — 消息处理服务（从 handlers/ 提升）
- `joha/core/message_handler.py` — 消息处理器（从 handlers/ 提升）
- `joha/core/commands.py` — 命令处理器（从 handlers/ 提升）
- `joha/core/message_builder.py` — 消息构建器（从 builders/ 提升）
- `joha/core/message_queue.py` — 消息队列（从 builders/ 提升）
- `CHANGELOG.md` — 更新日志

**删除**
- `joha/adapter/config/` — 配置子目录
- `joha/adapter/config.example.yaml` — 示例配置
- `joha/adapter/napcat_launcher.py` — NapCat 自动拉起
- `joha/adapter/bot_client.py` — 旧客户端文件
- `joha/core/handlers/` — 处理器子目录
- `joha/core/builders/` — 构建器子目录
- `joha/core/utils/` — 工具子目录
- `joha/storage/` — 旧存储目录（已迁移至根目录）
- `hot_reload.py` — 根目录旧热重载文件
