# Joha 常见问题 FAQ

## 基础使用

<details>
<summary><b>Q: Joha 是什么？</b></summary>

Joha（约哈）是一个基于 LLM 的智能群聊机器人框架，支持多模型切换、智能回复决策、风格学习、知识库检索等功能。它通过 WebSocket 连接 NapCatQQ 消息平台，自动监听群消息并智能回复。
</details>

<details>
<summary><b>Q: 机器人支持哪些消息平台？</b></summary>

目前主要通过 NapCatQQ（QQ 机器人框架）连接 QQ 群聊。只要是支持 OneBot 协议的消息平台，理论上都可以通过适配层接入。
</details>

<details>
<summary><b>Q: 支持哪些 AI 模型？</b></summary>

只要 API 兼容 OpenAI 协议即可。官方已测试的模型包括：
- DeepSeek-V4-Flash / DeepSeek-V3
- 通义千问 (Qwen) 系列
- GPT-4o / GPT-4o-mini
- Gemini 系列
- 任何兼容 OpenAI API 格式的模型
</details>

<details>
<summary><b>Q: 机器人的决策逻辑是什么？</b></summary>

Joha 采用基于概率计算的智能决策引擎。核心流程：
1. 收集反馈信号（被@、被回复、提问等）
2. 计算各因子得分（反馈权重 + 群动态 + 内容质量 + 意图）
3. Logit 累加 + Sigmoid 归一化得到回复概率 [0, 1]
4. 与配置的阈值比较，决定是否回复
</details>

---

## 配置问题

<details>
<summary><b>Q: 机器人不说话怎么办？</b></summary>

按以下顺序排查：
1. 发送 `/模式` 检查是否处于被动模式
2. 降低 `reply_decision.json` 中的 `thresholds.group`（如降到 0.45）
3. 检查 config.json 中 API Key 是否正确
4. 查看 `storage/johalog/ai.log` 日志
5. 确认 NapCatQQ 正常在线
</details>

<details>
<summary><b>Q: 机器人话太多怎么办？</b></summary>

1. 调高阈值：`thresholds.group` 调到 0.75
2. 切换到被动模式：`/全局关闭`
3. 增大冷却时间
4. 启用消息队列合并
</details>

<details>
<summary><b>Q: 如何添加更多管理员？</b></summary>

```
/添加管理员 <QQ号>
```

新增的管理员会拥有命令执行权限。查看当前管理员列表：`/管理员列表`。
</details>

<details>
<summary><b>Q: 如何运行时切换 AI 模型？</b></summary>

```
/模型          # 查看可用模型列表
/切换模型 <名称>   # 切换到指定模型（如 /切换模型 deepseek）
/当前模型      # 查看当前使用的模型
```
</details>

<details>
<summary><b>Q: 配置文件中的环境变量怎么用？</b></summary>

所有 `JOHA_` 前缀的环境变量会自动覆盖 JSON 配置中的对应项。例如：

```bash
export JOHA_LLM_ACTIVE_PROVIDER=deepseek
export JOHA_SETTINGS_DEBUG=false
```

这允许在不修改配置文件的情况下改变机器人行为，适合 Docker 部署等场景。
</details>

---

## 运行维护

<details>
<summary><b>Q: 如何查看运行日志？</b></summary>

日志文件位于 `storage/johalog/ai.log`。

实时查看：
```bash
# Linux/macOS
tail -f storage/johalog/ai.log

# Windows PowerShell
Get-Content storage/johalog/ai.log -Wait
```
</details>

<details>
<summary><b>Q: 机器人如何重启？</b></summary>

```bash
# 如果使用 systemd
sudo systemctl restart joha

# 如果直接运行
Ctrl+C 停止，然后 python run.py 重新启动
```
</details>

<details>
<summary><b>Q: 如何让机器人在服务器上稳定运行？</b></summary>

推荐使用 systemd 或 supervisord 守护进程：

```ini
# /etc/systemd/system/joha.service
[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/JohaChat
ExecStart=/path/to/venv/bin/python run.py
Restart=on-failure
RestartSec=10
```

```bash
sudo systemctl enable --now joha
```
</details>

<details>
<summary><b>Q: 如何更新到新版本？</b></summary>

```bash
git pull origin main
pip install -r requirements.txt
# 检查 config.example.json 是否有新增字段需要合并
# 重启机器人
```
</details>

---

## 知识库

<details>
<summary><b>Q: 知识库是做什么的？</b></summary>

知识库是 Joha 的本地 RAG（检索增强生成）引擎。当你添加了相关知识后，机器人在回复时能自动检索相关内容作为参考，使回答更准确、更专业。例如添加群规、FAQ、技术文档等。
</details>

<details>
<summary><b>Q: 如何添加知识条目？</b></summary>

```
/知识库添加 问题|答案
```

例如：`/知识库添加 本群主题是什么？|本群是 Joha 机器人的技术交流群`
</details>

<details>
<summary><b>Q: 知识库数据存在哪里？</b></summary>

存在 `storage/txt/` 目录下的分片 JSON 文件中（`knowledge_0001.json` 等），每片 100 条。建议定期备份此目录。
</details>

---

## 人设与风格

<details>
<summary><b>Q: 机器人的人设是什么？</b></summary>

默认人设为"大学生"角色，包含以下维度：
- **性格**：外向性、宜人性、尽责性、神经质、开放性（0-10）
- **表达风格**：话痨程度、正式度、情感表达、幽默感、自信度（0-10）
- **社交行为**：热情度、礼貌度、好奇心、共情力、耐心值（0-10）
- **语言特征**：表情符号、网络用语、语气词等

发送 `/人设` 查看详细参数。
</details>

<details>
<summary><b>Q: 机器人的风格学习是什么？</b></summary>

Joha 会学习群成员的说话风格（词汇习惯、句式特征、表情使用等），在回复时自动融入这些特征，使回复更自然地融入群聊氛围。
</details>

<details>
<summary><b>Q: 如何查看或清除某人的风格数据？</b></summary>

```
/风格 <QQ号>        # 查看用户的风格学习数据
/清除风格 <QQ号>    # 清除用户的风格数据
```
</details>

---

## 技术问题

<details>
<summary><b>Q: NapCatQQ 是什么？必须用吗？</b></summary>

NapCatQQ 是一个 QQ 机器人框架。如果你是 QQ 群聊场景，必须使用 NapCatQQ 或兼容 OneBot 协议的消息平台。从 [NapCatQQ GitHub](https://github.com/NapNeko/NapCatQQ) 下载安装。
</details>

<details>
<summary><b>Q: WebSocket 连接失败怎么办？</b></summary>

1. 确认 NapCatQQ 已启动
2. 确认 NapCatQQ 配置中开启了 WebSocket（端口 3002）
3. 确认 `connection.yaml` 中的 `ws_url` 与 NapCatQQ 的 websocket 地址一致
4. 检查防火墙是否阻止了本地连接
</details>

<details>
<summary><b>Q: API Key 放哪里最安全？</b></summary>

推荐使用环境变量方式：

```bash
export JOHA_LLM_PROVIDERS_0_API_KEY=sk-your-key
```

这样密钥不会出现在配置文件中，更安全。特别是在 Docker 或 CI/CD 环境中。
</details>

<details>
<summary><b>Q: 支持流式回复吗？</b></summary>

目前主要采用非流式回复（等 LLM 返回完整内容后一次性发送）。如需流式输出，需要修改 `joha/ai/clients.py` 中的 API 调用方式。
</details>

<details>
<summary><b>Q: Python 版本要求是什么？</b></summary>

需要 Python 3.9 及以上版本。推荐使用 Python 3.11+。
</details>

<details>
<summary><b>Q: 需要付费吗？</b></summary>

Johahat 框架本身是开源免费的（MIT 协议）。但使用的 LLM API 通常需要付费（按 token 计费），各 Provider 价格不同。
</details>
