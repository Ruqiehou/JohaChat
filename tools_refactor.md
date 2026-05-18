# Masu 工具模块子目录化重构

## 调整说明

将 `masu/tools/` 下散落的工具文件按工具拆分到独立子目录，每个工具一个文件夹，结构更清晰、易维护。

---

## 新目录结构

```
masu/tools/
├── __init__.py              # 统一导出（导入路径改为子目录）
├── search/                  # 搜索工具
│   ├── __init__.py
│   ├── core.py              # SearchTool 实现类（原 search.py）
│   └── tool.py              # TOOL_META + execute（原 search_tool.py）
├── webpage/                 # 网页抓取工具
│   ├── __init__.py
│   ├── core.py              # WebpageTool 实现类（原 webpage.py）
│   └── tool.py              # TOOL_META + execute（原 webpage_tool.py）
├── link_preview/            # 链接预览工具
│   ├── __init__.py
│   └── tool.py              # LinkPreviewTool 实现类（原 link_preview.py）
├── knowledge/               # 知识库搜索工具
│   ├── __init__.py
│   ├── core.py              # KnowledgeBase + 搜索函数（原 knowledge_search.py）
│   └── tool.py              # TOOL_META + execute（原 knowledge_tool.py）
└── screenshot/              # 网页截图工具
    ├── __init__.py
    ├── core.py              # ScreenshotTool 实现类（原 screenshot.py）
    └── tool.py              # TOOL_META + execute（原 screenshot_tool.py）
```

---

## 涉及的文件与变更

### 1. 新增文件（14 个）

| 文件 | 说明 |
|------|------|
| `masu/tools/search/__init__.py` | 搜索子包，导出 SearchTool |
| `masu/tools/search/core.py` | SearchTool 实现类，从原 `search.py` 迁移 |
| `masu/tools/search/tool.py` | TOOL_META + execute，从原 `search_tool.py` 迁移 |
| `masu/tools/webpage/__init__.py` | 网页抓取子包，导出 WebpageTool |
| `masu/tools/webpage/core.py` | WebpageTool 实现类，从原 `webpage.py` 迁移 |
| `masu/tools/webpage/tool.py` | TOOL_META + execute，从原 `webpage_tool.py` 迁移 |
| `masu/tools/link_preview/__init__.py` | 链接预览子包，导出 LinkPreviewTool |
| `masu/tools/link_preview/tool.py` | LinkPreviewTool 实现类，从原 `link_preview.py` 迁移 |
| `masu/tools/knowledge/__init__.py` | 知识库子包，导出所有知识库相关接口 |
| `masu/tools/knowledge/core.py` | KnowledgeBase + 搜索函数，从原 `knowledge_search.py` 迁移 |
| `masu/tools/knowledge/tool.py` | TOOL_META + execute，从原 `knowledge_tool.py` 迁移 |
| `masu/tools/screenshot/__init__.py` | 截图子包，导出 ScreenshotTool |
| `masu/tools/screenshot/core.py` | ScreenshotTool 实现类，从原 `screenshot.py` 迁移 |
| `masu/tools/screenshot/tool.py` | TOOL_META + execute，从原 `screenshot_tool.py` 迁移 |

### 2. 删除文件（9 个）

| 文件 | 迁移去向 |
|------|----------|
| `masu/tools/search.py` | `masu/tools/search/core.py` |
| `masu/tools/search_tool.py` | `masu/tools/search/tool.py` |
| `masu/tools/webpage.py` | `masu/tools/webpage/core.py` |
| `masu/tools/webpage_tool.py` | `masu/tools/webpage/tool.py` |
| `masu/tools/link_preview.py` | `masu/tools/link_preview/tool.py` |
| `masu/tools/knowledge_search.py` | `masu/tools/knowledge/core.py` |
| `masu/tools/knowledge_tool.py` | `masu/tools/knowledge/tool.py` |
| `masu/tools/screenshot.py` | `masu/tools/screenshot/core.py` |
| `masu/tools/screenshot_tool.py` | `masu/tools/screenshot/tool.py` |

### 3. 修改文件（3 个）

#### `masu/core/tool_registry.py`

`auto_discover()` 重构：

- 原先扫描 `tools/*.py` 顶层文件，导入 `masu.tools.{stem}`
- 改为先扫描 `tools/*/tool.py` 子目录，导入 `masu.tools.{subdir}.tool`
- 保留对顶层 `*_tool.py` 的兼容扫描（旧格式过渡）
- 提取 `_load_tool_from_module()` 方法消除重复逻辑

关键代码：

```python
def auto_discover(self):
    # 1. 新格式：扫描子目录 tools/<name>/tool.py
    for subdir in sorted(tools_path.iterdir()):
        if not subdir.is_dir() or subdir.name.startswith("_"):
            continue
        tool_file = subdir / "tool.py"
        if not tool_file.exists():
            continue
        module_name = f"masu.tools.{subdir.name}.tool"
        self._load_tool_from_module(module_name, subdir.name)

    # 2. 旧格式兼容：扫描 *_tool.py
    for py_file in tools_path.glob("*_tool.py"):
        ...
```

#### `masu/tools/__init__.py`

导入路径从顶层文件改为子目录：

```python
# 改前
from .search import SearchTool
from .webpage import WebpageTool
from .link_preview import LinkPreviewTool
from .knowledge_search import KnowledgeBaseSearchTool, get_kb_search_tool
from .knowledge_search import KnowledgeBase, get_knowledge_base, search_knowledge_base
from .screenshot import ScreenshotTool

# 改后
from .search.core import SearchTool
from .webpage.core import WebpageTool
from .link_preview.tool import LinkPreviewTool
from .knowledge.core import (
    KnowledgeBaseSearchTool, get_kb_search_tool,
    KnowledgeBase, get_knowledge_base, search_knowledge_base,
)
from .screenshot.core import ScreenshotTool
```

#### `masu/core/service.py`

顶层导入和函数内导入各一处：

```python
# 改前
from masu.tools.knowledge_search import get_knowledge_base

# 改后
from masu.tools.knowledge.core import get_knowledge_base
```

### 4. `knowledge/core.py` 路径适配

`knowledge/core.py` 比原 `knowledge_search.py` 深一层目录，`TXT_DIR` 的 `os.path.dirname` 调用从 3 次改为 4 次：

```python
# 原 knowledge_search.py（masu/tools/ 下）
TXT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "storage", "konw"
)

# 现 knowledge/core.py（masu/tools/knowledge/ 下）
TXT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "storage", "konw"
)
```

---

## 影响范围

- **外部调用**：所有通过 `from masu.tools import xxx` 的代码不受影响（`__init__.py` 统一导出）
- **唯一例外**：`service.py` 中直接 `from masu.tools.knowledge_search import get_knowledge_base` → 已更新
- **ToolRegistry 自动发现**：改为扫描子目录 `tool.py`，同时保留 `*_tool.py` 兼容

---

## 验证方式

```bash
# 1. 语法检查
python -c "
import ast
files = [
  'masu/tools/__init__.py',
  'masu/tools/search/__init__.py', 'masu/tools/search/core.py', 'masu/tools/search/tool.py',
  'masu/tools/webpage/__init__.py', 'masu/tools/webpage/core.py', 'masu/tools/webpage/tool.py',
  'masu/tools/link_preview/__init__.py', 'masu/tools/link_preview/tool.py',
  'masu/tools/knowledge/__init__.py', 'masu/tools/knowledge/core.py', 'masu/tools/knowledge/tool.py',
  'masu/tools/screenshot/__init__.py', 'masu/tools/screenshot/core.py', 'masu/tools/screenshot/tool.py',
  'masu/core/tool_registry.py', 'masu/core/service.py',
]
all(ast.parse(open(f, encoding='utf-8').read()) for f in files)
print(f'OK: {len(files)} files')
"

# 2. 导入测试（验证模块可正常加载）
python -c "from masu.tools import search_tool, webpage_tool, link_preview_tool, kb_search_tool, screenshot_tool; print('Import OK')"
```
