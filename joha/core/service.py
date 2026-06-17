"""
消息处理服务
学习和回复是两套独立的流程
"""
import time
import asyncio
from typing import Optional, Dict, Any
from joha.ai.generator import generator
from joha.core.message_builder import message_builder
from joha.ai.bot import get_chat_engine
from joha.core.tool_registry import get_tool_registry, tool_registry
from joha.managers.history_manager import history_manager
from joha.managers.style_learner import style_learner
from joha.config.logger import johalog_logger, ai_logger, tprint
from joha.config.config_manager import config
from joha.config.group_mode_config import group_mode_config
from joha.decision import get_decision_engine


# ==================== 多模态能力检测 ====================

MULTIMODAL_MODEL_PREFIXES = (
    "gpt-4o", "gpt-4-vision", "gpt-4-turbo",
    "claude-3", "claude-3.5", "claude-3.7",
    "gemini-1.5", "gemini-2", "gemini-2.5",
    "qwen-vl", "qwen2-vl", "qwen2.5-vl", "qwen3-vl",
    "qwen-omni", "qwen3.5-omni",
    "glm-4v", "cogvlm", "cogagent",
    "yi-vision", "yi-vl",
    "internvl", "internlm-xcomposer",
    "llava", "bakllava", "llama3.2-vision", "llama-3.2-vision",
    "pixtral", "deepseek-vl",
)


def supports_multimodal(model_name: str) -> bool:
    model_lower = model_name.lower()
    return any(model_lower.startswith(prefix.lower()) for prefix in MULTIMODAL_MODEL_PREFIXES)


class MessageService:
   
    
    def __init__(self):
        self.mode = config.get('bot.mode', 'passive')
        self.started_at = time.time()
        self.total_messages = 0
        self.learned_messages = 0
        self.reply_decisions = 0
        self.skipped_replies = 0
        self.generated_replies = 0
        self.failed_replies = 0
        
        # 初始化 Tool Registry（自动发现工具）
        self.tool_registry = tool_registry
        discovered = self.tool_registry.auto_discover()
        message_builder.tool_registry = self.tool_registry
        johalog_logger.info(f"ToolRegistry 已加载 {discovered} 个工具")
        
        # 初始化决策引擎
        self.decision_engine = get_decision_engine()
        
        self.group_modes: Dict[str, str] = group_mode_config.get_all_modes()
        johalog_logger.info(f"已初始化 {len(self.group_modes)} 个群组模式")

    async def process_message(
        self,
        userid: str,
        message: str,
        group_id: Optional[str] = None,
        force_reply: bool = False,
        is_at_bot: bool = False,
        reply_to_bot: bool = False,
        is_pure_sticker_or_image: bool = False,
        images: list = None,
    ) -> Optional[str]:
        userid_str = str(userid)
        message = message.strip()
        images = images or []
        
        if not message and not images:
            return None
        
        self.total_messages += 1
        log_msg = message if message else f"[图片 x{len(images)}]"
        ai_logger.info(f"收到消息", extra={"userid": userid_str, "msg_content": log_msg})
        tprint("info", f"[消息] 群{group_id} | 用户{userid_str}: {log_msg}")
        
        group_mode = self.get_group_mode(group_id) if group_id else self.get_global_mode()
        learn_msg = message if message else f"[用户发送了一张图片]"
        
        # 1. 先学习所有消息（无论是否回复）
        self._learn_message(userid_str, learn_msg, group_id)
        
        # 2. 检查群组模式
        should_generate_reply = group_mode == "active" or force_reply
        
        if not should_generate_reply:
            return None
        
        # 3. 主动模式：通过决策引擎进行完整决策
        result = self.decision_engine.process(
            text=log_msg,
            user_id=userid_str,
            group_id=group_id or "",
            is_at_bot=is_at_bot,
            reply_to_bot=reply_to_bot,
            is_pure_media=is_pure_sticker_or_image,
            group_mode=group_mode,
            force_reply=force_reply,
        )
        self.reply_decisions += 1
        
        if not result.should_reply:
            self.skipped_replies += 1
            return None
        
        # 4. 工具直接回复（引擎已执行）
        if result.reply_text:
            history_manager.add_message(userid_str, message or "[图片]", group_id=group_id)
            self.generated_replies += 1
            return result.reply_text
        
        # 5. 生成完整回复
        return await self._handle_active_mode(userid_str, message, images, group_id)
    
    def _learn_message(self, userid_str: str, message: str, group_id: Optional[str] = None) -> None:
        try:
            history_manager.add_message(userid_str, message, group_id=group_id)
            style_learner.learn_from_message(userid_str, message)
            self.learned_messages += 1
            
            johalog_logger.debug(f"[学习] 记录用户 {userid_str} 的消息并学习风格")
        except Exception as e:
            johalog_logger.error(f"学习失败：{e}")
    
    async def _handle_active_mode(
        self,
        userid_str: str,
        message: str,
        images: list = None,
        group_id: Optional[str] = None,
    ) -> Optional[str]:
        try:
            images = images or []

            if images:
                current_model = getattr(get_chat_engine(), 'model', generator.current_model)
                if not supports_multimodal(current_model):
                    tprint("warning", f"[多模态] 模型 {current_model} 不支持图片，已跳过 {len(images)} 张图片")
                    johalog_logger.warning(f"模型 {current_model} 不支持多模态，已跳过图片")
                    images = []
            # 获取历史记录
            history = history_manager.load_history(userid_str, group_id=group_id)

            # 使用统一消息构建器
            context_messages = message_builder.build(
                user_id=userid_str,
                message=message,
                images=images,
                persona_name="joha",
                history=history,
                include_style=True,
                include_rag=False,
                group_id=group_id,
            )

            # 调用LLM生成回复
            log_msg = message[:30] if message else f"[图片]"
            tprint("info", f"[AI] 请求中... | 用户{userid_str} | 消息: {log_msg}{'...' if len(message) > 30 else ''}")
            
            response = None
            try:
                engine = get_chat_engine()
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: engine.chat(message, temperature=0.7)
                )
            except Exception as bot_err:
                tprint("warning", f"[ChatEngine] 失败，回退到生成器: {bot_err}")
                response = await generator.chat(
                    messages=context_messages,
                    temperature=0.7,
                    max_tokens=1024,
                )
            if not response:
                self.failed_replies += 1
                tprint("warning", f"[AI] 未生成回复，已跳过发送到群 | 用户{userid_str} | 消息: {log_msg}")
                johalog_logger.warning(
                    f"[回复生成失败] 用户:{userid_str}, 消息:{log_msg[:20]}..., 已跳过群发送"
                )
                return None

            tprint("info", f"[AI] 回复: {response}")
            
            johalog_logger.info(
                f"[回复生成] 用户:{userid_str}, 消息:{log_msg[:20]}..., 回复:{response[:20]}..."
            )
            
            # 记录回复到历史
            history_manager.add_message(userid_str, message or "[图片]", group_id=group_id)
            
            self.generated_replies += 1
            return response
        
        except Exception as e:
            self.failed_replies += 1
            johalog_logger.error(f"生成回复失败：{e}", exc_info=True)
            tprint("error", f"[AI] 生成回复失败，已跳过发送到群：{e}")
            return None
    
    def get_global_mode(self) -> str:
        config.load()
        mode = config.get('bot.mode', self.mode)
        if mode not in ["active", "passive"]:
            return self.mode
        self.mode = mode
        return mode

    def set_global_mode(self, mode: str) -> None:
        if mode not in ["active", "passive"]:
            raise ValueError(f"无效的模式: {mode}")
        config.load()
        config.set('bot.mode', mode)
        config.save()
        self.mode = mode

    def get_group_mode(self, group_id: str) -> str:
        return group_mode_config.get_mode(group_id, self.get_global_mode())
    
    def set_group_mode(self, group_id: str, mode: str) -> None:
        if mode not in ["active", "passive"]:
            raise ValueError(f"无效的模式: {mode}")
        
        group_mode_config.set_mode(group_id, mode)
        self.group_modes = group_mode_config.get_all_modes()
    
    def get_stats(self) -> Dict[str, Any]:
        uptime = int(time.time() - self.started_at)
        from joha.decision.group_state import group_state_manager
        gs = group_state_manager.get_stats()
        return {
            "uptime": uptime,
            "total_messages": self.total_messages,
            "learned_messages": self.learned_messages,
            "reply_decisions": self.reply_decisions,
            "skipped_replies": self.skipped_replies,
            "generated_replies": self.generated_replies,
            "failed_replies": self.failed_replies,
            "active_groups": len([g for g, m in self.group_modes.items() if m == "active"]),
            "passive_groups": len([g for g, m in self.group_modes.items() if m == "passive"]),
            "tracked_groups": gs["total_groups"],
            "group_total_messages": gs["total_messages"],
            "group_bot_replies": gs["total_bot_replies"],
            "avg_msg_per_min": round(gs["avg_msg_per_min"], 1),
        }
    
    def get_stats_str(self) -> str:
        stats = self.get_stats()
        return (
            f"=== Joha 服务统计 ===\n"
            f"运行时间: {stats['uptime']} 秒\n"
            f"收到消息: {stats['total_messages']}\n"
            f"学习消息: {stats['learned_messages']}\n"
            f"回复决策: {stats['reply_decisions']}\n"
            f"生成回复: {stats['generated_replies']}\n"
            f"跳过回复: {stats['skipped_replies']}\n"
            f"失败回复: {stats['failed_replies']}\n"
            f"活跃群组: {stats['active_groups']}\n"
            f"被动群组: {stats['passive_groups']}\n"
            f"追踪群组: {stats['tracked_groups']}\n"
            f"群总消息: {stats['group_total_messages']}\n"
            f"=================="
        )


# 全局服务实例
message_service = MessageService()
