"""
知识库搜索工具 v2.0
提供对本地知识库的搜索、统计和管理功能
"""
from typing import Dict, List, Optional
from datetime import datetime
from joha.decision.knowledge.base import get_knowledge_base


class KnowledgeBaseSearchTool:
    """知识库搜索工具类"""

    def __init__(self):
        self._kb = get_knowledge_base()

    def search(self, query: str, num_results: int = 5, **kwargs) -> str:
        try:
            results = self._kb.search(query, top_k=num_results, **kwargs)

            if not results:
                return "在知识库中未找到相关结果"

            formatted_results = []
            for i, result in enumerate(results, 1):
                title = result.get('title', '未知标题')
                question = result.get('user_question', '')[:200]
                response = result.get('ai_response', '')[:400]
                score = result.get('score', 0)
                timestamp = result.get('timestamp', '')

                time_str = ''
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        time_str = f" [{dt.strftime('%Y-%m-%d %H:%M')}]"
                    except Exception:
                        pass

                formatted_result = (
                    f"{i}. [{score:.2f}] {title}{time_str}\n"
                    f"   问题: {question}{'...' if len(question) >= 200 else ''}\n"
                    f"   回答: {response}{'...' if len(response) >= 400 else ''}"
                )
                formatted_results.append(formatted_result)

            header = f"知识库搜索 '{query}'（共 {len(results)} 条）：\n"
            return header + "\n\n".join(formatted_results)

        except Exception as e:
            return f"知识库搜索失败: {str(e)}"

    def search_recent(self, query: str, days: int = 7, num_results: int = 5) -> str:
        return self.search(query, num_results=num_results, days=days)

    def get_document_count(self) -> int:
        return len(self._kb.documents)

    def get_statistics(self) -> str:
        try:
            stats = self._kb.get_statistics()
            lines = [
                "知识库统计信息",
                f"文档总数: {stats['total_documents']}",
                f"总字数: {stats['total_words']}",
                f"平均字数/文档: {stats['avg_words_per_doc']}",
            ]

            if stats.get('date_range'):
                dr = stats['date_range']
                lines.append(f"时间范围: {dr.get('earliest', 'N/A')} ~ {dr.get('latest', 'N/A')}")

            if stats.get('file_count_by_dir'):
                lines.append("\n目录分布:")
                for d, c in stats['file_count_by_dir'].items():
                    lines.append(f"  {d}: {c} 个文件")

            if stats.get('top_keywords'):
                lines.append("\n高频关键词:")
                for word, count in stats['top_keywords'][:10]:
                    lines.append(f"  {word}: {count} 次")

            return "\n".join(lines)
        except Exception as e:
            return f"获取统计信息失败: {str(e)}"

    def add_knowledge(self, question: str, answer: str, title: str = "") -> str:
        try:
            from datetime import datetime
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

            content = (
                f"时间: {timestamp}\n"
                f"{'='*60}\n\n"
                f"【用户问题】\n"
                f"{question}\n\n"
                f"【AI 回复】\n"
                f"{answer}\n"
            )

            safe_title = title or question[:30]
            doc_id = self._kb.add_document(content, title=safe_title)

            if doc_id:
                return f"已成功添加知识（ID: {doc_id[:8]}...）"
            return "添加失败"
        except Exception as e:
            return f"添加知识失败: {str(e)}"

    def refresh(self) -> str:
        try:
            self._kb.refresh()
            count = len(self._kb.documents)
            return f"知识库已刷新，当前共 {count} 个文档"
        except Exception as e:
            return f"刷新失败: {str(e)}"

    def find_duplicates(self) -> str:
        try:
            dups = self._kb.find_duplicates(threshold=0.85)
            if not dups:
                return "未发现高度重复的知识文档"

            lines = [f"发现 {len(dups)} 组相似文档（阈值 0.85）:\n"]
            for i, (d1, d2, sim) in enumerate(dups[:10], 1):
                lines.append(
                    f"{i}. 相似度: {sim:.2f}\n"
                    f"   A: {d1.get('filename', 'N/A')}\n"
                    f"   B: {d2.get('filename', 'N/A')}"
                )
            return "\n".join(lines)
        except Exception as e:
            return f"查找重复失败: {str(e)}"


# 全局实例
_kb_search_tool = None


def get_kb_search_tool():
    """获取知识库搜索工具实例（单例）"""
    global _kb_search_tool
    if _kb_search_tool is None:
        _kb_search_tool = KnowledgeBaseSearchTool()
    return _kb_search_tool


kb_search_tool = get_kb_search_tool()


# ========== 新式函数+元信息模式（供 ToolRegistry 自动发现） ==========

TOOL_META = {
    "name": "knowledge",
    "description": "搜索本地知识库获取历史对话和知识，用于查找项目相关历史信息、过往讨论",
    "category": "knowledge",
    "aliases": ["kb", "mem", "记忆"],
    "parameters": {
        "query": {
            "type": "str",
            "description": "搜索关键词",
            "required": True,
        },
        "num_results": {
            "type": "int",
            "description": "返回结果数量，默认5",
            "required": False,
        },
    },
    "examples": ["/knowledge 项目架构", "/kb 数据库设计"],
}


def execute(query: str, num_results: int = 5) -> str:
    """函数式入口：搜索知识库"""
    return get_kb_search_tool().search(query, num_results)
