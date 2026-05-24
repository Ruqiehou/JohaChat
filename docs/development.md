# Joha 二次开发指南

## 1. 开发环境搭建

### 1.1 前置要求

- Python >= 3.9
- 运行中的 NapCatQQ（WebSocket 端口开放）
- Git

### 1.2 安装步骤

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd JohaChat

# 2. 创建虚拟环境（推荐）
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 复制配置文件
cp joha/config/config.example.json joha/config/config.json
cp joha/adapter/config/config.example.yaml joha/adapter/config/connection.yaml

# 5. 编辑配置文件（填入 API Key、QQ 号等）
# joha/config/config.json
# joha/adapter/config/connection.yaml

# 6. 运行
python run.py
```

---

## 2. 项目结构速查

```
JohaChat/
├── run.py                          # 统一启动入口
├── requirements.txt                # Python 依赖
│
├── joha/                           # 核心代码包
│   ├── adapter/                    # NapCatQQ 适配层
│   │   ├── bot_client.py           # MessageClient 入口
│   │   ├── napcat_launcher.py      # NapCat 自动启动
│   │   ├── core/                   # WebSocket、事件、API
│   │   └── config/                 # 连接配置
│   │
│   ├── core/                       # 编排入口层
│   │   ├── handlers/               # 消息处理、命令、服务
│   │   ├── builders/               # 上下文构建、消息队列
│   │   └── utils/                  # 运行时上下文、工具注册、后处理
│   │
│   ├── ai/                         # AI 驱动层
│   │   ├── clients.py              # OpenAI 协议客户端
│   │   ├── providers.py            # 多 Provider 管理
│   │   ├── bot.py                  # ChatEngine 聊天引擎
│   │   ├── generator.py            # 回复生成器
│   │   └── classifier.py           # 文本分类器
│   │
│   ├── decision/                   # 决策大脑层
│   │   ├── decision_engine.py      # 决策引擎总控
│   │   ├── reply_decision.py       # 回复概率计算
│   │   ├── reply_config.py         # 决策配置热加载
│   │   ├── intent_classifier.py    # 意图分类
│   │   ├── command_analyzer.py     # 自然语言命令分析
│   │   ├── group_state.py          # 群组状态追踪
│   │   └── cooldown.py             # 冷却管理
│   │
│   ├── managers/                   # 数据管理层
│   │   ├── personas.py             # 人设管理
│   │   ├── style_learner.py        # 风格学习
│   │   ├── history_manager.py      # 历史记录
│   │   ├── user_profile.py         # 用户画像
│   │   └── admin.py                # 管理员系统
│   │
│   ├── tools/                      # 工具层
│   │   ├── knowledge/              # 知识库 RAG 引擎
│   │   ├── search/                 # 网络搜索
│   │   └── webpage/                # 网页抓取
│   │
│   └── config/                     # 配置与基础设施
│       ├── managers/               # 配置管理器
│       └── infrastructure/         # 日志、缓存
│
├── docs/                           # 文档目录
├── logs/                           # 运行日志
└── README.md                       # 项目说明
```

---

## 3. 添加新命令

以添加 `/天气 <城市>` 命令为例：

### 步骤 1：在 commands.py 中注册命令

编辑 `joha/core/handlers/commands.py`：

```python
async def handle_weather(cmd_args: str, event, api) -> str:
    """处理 /天气 命令"""
    city = cmd_args.strip()
    if not city:
        return "请指定城市，例如：/天气 北京"
    
    # 调用天气 API
    weather_info = await fetch_weather(city)
    return weather_info

# 在命令路由表中注册
COMMAND_HANDLERS = {
    # ... 已有命令
    "/天气": handle_weather,
}
```

### 步骤 2：添加自然语言别名（可选）

编辑 `joha/decision/command_analyzer.py` 的别名映射：

```python
COMMAND_ALIASES = {
    # ... 已有别名
    "天气": "/天气",
    "查天气": "/天气",
}
```

---

## 4. 添加新工具

工具系统采用**函数 + 元信息**模式，支持自动发现。

### 步骤 1：创建工具文件

创建 `joha/tools/weather.py`：

```python
"""天气查询工具"""

TOOL_META = {
    "name": "weather",
    "description": "查询指定城市的当前天气",
    "parameters": {
        "city": {"type": "string", "description": "城市名称"}
    }
}

async def query_weather(city: str) -> str:
    """查询天气"""
    # 实现天气 API 调用
    import aiohttp
    
    async with aiohttp.ClientSession() as session:
        # 替换为实际天气 API
        url = f"https://api.weather.example.com/v1/current?city={city}"
        async with session.get(url) as resp:
            data = await resp.json()
            return f"{city}当前天气：{data['weather']}，温度：{data['temp']}°C"
```

### 步骤 2：注册到工具注册表

编辑 `joha/core/utils/tool_registry.py`：

```python
from joha.tools.weather import query_weather, TOOL_META

# 在注册表中添加
TOOL_REGISTRY = {
    # ... 已有工具
    "weather": {
        "meta": TOOL_META,
        "func": query_weather,
    },
}
```

---

## 5. 添加新的 LLM Provider

在 `joha/config/config.json` 的 `llm.providers` 数组中添加：

```json
{
  "name": "openrouter",
  "label": "OpenRouter",
  "api_key": "sk-or-v1-xxx",
  "base_url": "https://openrouter.ai/api/v1",
  "model": "anthropic/claude-3.5-sonnet"
}
```

只要 API 兼容 OpenAI 协议，无需修改代码即可使用。

---

## 6. 修改决策参数

编辑 `joha/config/reply_decision.json`，修改后无需重启：

```bash
# 方式 1：管理员群内发送命令
/知识库刷新

# 方式 2：代码中手动触发
from joha.decision.reply_config import reply_cfg
reply_cfg.reload()
```

---

## 7. 调试技巧

### 7.1 开启调试模式

在 `joha/adapter/config/connection.yaml` 中设置：

```yaml
settings:
  debug: true
```

### 7.2 查看日志

```bash
# 实时查看日志
tail -f joha/storage/johalog/ai.log

# Windows
Get-Content joha/storage/johalog/ai.log -Wait
```

### 7.3 本地测试决策逻辑

```python
from joha.decision.decision_engine import DecisionEngine
from joha.decision.reply_config import reply_cfg

engine = DecisionEngine()

# 构建测试上下文
context = {
    "group_id": 123456,
    "user_id": 987654,
    "message": "大家好",
    "is_at_bot": False,
    "is_reply_to_bot": False,
}

# 计算回复概率
prob = engine.compute_reply_prob(context)
print(f"回复概率: {prob:.4f}")
print(f"阈值: {reply_cfg.thresholds.group}")
print(f"是否回复: {prob >= reply_cfg.thresholds.group}")
```

### 7.4 测试 LLM 调用

```python
from joha.ai.bot import ChatEngine

def test():
    engine = ChatEngine()
    response = engine.chat("你好，请介绍一下自己")
    print(response)

test()
```

---

## 8. 代码规范

- 使用 `async/await` 处理所有 IO 操作
- 日志使用 `joha.config.infrastructure.logger.tprint()`
- 配置读取使用 `config_manager.get(key, default)`
- 新增模块需在 `__init__.py` 中暴露公共接口
- 工具类函数需添加 `TOOL_META` 元信息

---

## 9. 常见问题

**Q: 新增模块后导入失败？**
A: 检查 `__init__.py` 是否正确暴露，以及是否有循环导入。

**Q: 命令不响应？**
A: 检查：
1. 命令是否已注册到 `COMMAND_HANDLERS`
2. 用户是否有权限执行该命令
3. 机器人是否处于被动模式

**Q: LLM 返回异常？**
A: 检查：
1. API Key 是否正确
2. `base_url` 和 `model` 是否匹配 Provider
3. 查看 `joha/storage/johalog/ai.log` 中的错误详情
