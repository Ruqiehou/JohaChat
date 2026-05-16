"""
消息处理器 v2.0 - 处理群消息
支持上下文感知和群组状态追踪
集成消息队列进行智能合并
"""
from ncatbot.core import GroupMessage
from joha.core.service import message_service
from joha.core.commands import command_handler, normalize_fallback_command
from joha.core.runtime_context import runtime_context
from joha.core.message_queue import message_queue_manager
from joha.config.logger import johalog_logger, tprint
from joha.decision.group_state import group_state_manager


def _image_to_data_url(img) -> str:
    """将 ncatbot Image 转换为 base64 data URL（供 Qwen 多模态使用）"""
    try:
        raw = img.get_base64()
        if raw and raw.startswith("base64://"):
            return "data:image/jpeg;base64," + raw[len("base64://"):]
        return ""
    except Exception:
        return ""


class MessageProcessor:
    """消息处理器"""

    @staticmethod
    async def process_group_message(msg: GroupMessage, bot_api):
        """
        处理群消息（集成消息队列）

        Args:
            msg: 群消息对象
            bot_api: Bot API对象
        """
        # 提取文本消息
        xiaoxi = "".join(seg.text for seg in msg.message.filter_text())
        userid = msg.user_id
        actual_message = xiaoxi.strip()
        group_id = str(msg.group_id)

        # 提取图片
        images_raw = msg.message.filter_image()
        image_urls = [_image_to_data_url(img) for img in images_raw]
        image_urls = [u for u in image_urls if u]  # 过滤掉转换失败的

        # 既没有文字也没有图片，直接跳过
        if not actual_message and not image_urls:
            return

        # 记录群消息到状态追踪器（用于决策模型）
        group_state_manager.record_message(
            group_id=group_id,
            user_id=str(userid),
            text=actual_message or "[图片]",
            is_bot=False
        )

        fallback_command = normalize_fallback_command(actual_message)
        if fallback_command:
            handled = await command_handler.handle_command(fallback_command, str(userid), msg.group_id, bot_api)
            if handled is not None or actual_message.startswith("/"):
                return

        # 提取消息元数据
        is_at_bot = False
        reply_to_bot = False
        is_pure_sticker_or_image = (len(image_urls) > 0 and not actual_message)

        # 检查是否@机器人
        if hasattr(msg, 'at') and msg.at:
            is_at_bot = any(int(at) == runtime_context.bot_uin for at in msg.at)

        # 检查是否回复机器人消息
        if hasattr(msg, 'reply') and msg.reply:
            reply_msg = msg.reply
            if hasattr(reply_msg, 'sender') and hasattr(reply_msg.sender, 'user_id'):
                reply_to_bot = (int(reply_msg.sender.user_id) == runtime_context.bot_uin)

        # 使用消息队列处理（智能合并）
        merged_msg = await message_queue_manager.add_message(
            user_id=str(userid),
            group_id=group_id,
            message=actual_message,
            images=image_urls,
            is_at_bot=is_at_bot,
            reply_to_bot=reply_to_bot,
            is_pure_sticker_or_image=is_pure_sticker_or_image,
        )
        
        # 如果返回了合并消息，则处理；否则等待更多消息
        if merged_msg:
            response = await message_service.process_message(
                userid=merged_msg.user_id,
                message=merged_msg.merged_text,
                group_id=merged_msg.group_id,
                is_at_bot=merged_msg.is_at_bot,
                reply_to_bot=merged_msg.reply_to_bot,
                is_pure_sticker_or_image=merged_msg.is_pure_sticker_or_image,
                images=merged_msg.images,
            )

            # 发送回复
            if response:
                try:
                    await bot_api.post_group_msg(group_id=msg.group_id, text=response)
                    # 记录机器人回复到群组状态
                    group_state_manager.record_bot_reply(group_id=group_id, text=response)
                except Exception as e:
                    tprint("error", f"发送消息失败: {e}")


# 全局处理器实例
message_processor = MessageProcessor()
