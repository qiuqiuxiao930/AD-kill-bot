"""Enforcement actions: delete, warn, mute, ban."""

from telegram import Update
from telegram.error import TelegramError
from loguru import logger

from db.database import Database


class ActionHandler:
    """Execute enforcement actions based on detection results and config."""

    def __init__(self, db: Database, config: dict) -> None:
        self.db = db
        self.cfg = config.get("actions", {}).get("on_detect", {})
        self.max_warnings: int = self.cfg.get("max_warnings", 3)
        self.delete_message: bool = self.cfg.get("delete_message", True)
        self.warn_user: bool = self.cfg.get("warn_user", True)
        self.ban_on_max: bool = self.cfg.get("ban_on_max_warnings", True)

    async def handle(
        self,
        update: Update,
        detection: dict,
    ) -> str:
        """Apply configured actions. Returns a summary string of what was done."""
        message = update.effective_message
        user = update.effective_user
        chat_id = update.effective_chat.id
        user_id = user.id
        actions_taken: list[str] = []

        # 1. Delete
        if self.delete_message:
            try:
                await message.delete()
                actions_taken.append("删除消息")
            except TelegramError as exc:
                logger.error("Failed to delete message: {}", exc)

        # 2. Warn
        if self.warn_user:
            count = self.db.add_warning(user_id, chat_id)
            actions_taken.append(f"警告 ({count}/{self.max_warnings})")

            if self.ban_on_max and count >= self.max_warnings:
                await self._ban_user(update, user_id, chat_id)
                actions_taken.append("封禁用户")
            else:
                await self._send_warning(update, detection, count)

        # 3. Log
        self.db.log_detection(
            chat_id=chat_id,
            user_id=user_id,
            message_text=message.text or "",
            detection_type=detection.get("type", "unknown"),
            confidence=detection.get("confidence", 0.0),
            action_taken=", ".join(actions_taken),
        )

        return ", ".join(actions_taken)

    async def _send_warning(
        self, update: Update, detection: dict, count: int
    ) -> None:
        user = update.effective_user
        det_type = detection.get("type", "违规内容")
        text = (
            f"⚠️ 检测到可疑消息，已自动删除。\n"
            f"类型：{det_type}\n"
            f"用户 {user.mention_html()} 已被警告（{count}/{self.max_warnings}）"
        )
        try:
            await update.effective_chat.send_message(text, parse_mode="HTML")
        except TelegramError as exc:
            logger.error("Failed to send warning: {}", exc)

    async def _ban_user(
        self, update: Update, user_id: int, chat_id: int
    ) -> None:
        try:
            await update.effective_chat.ban_member(user_id)
            await update.effective_chat.send_message(
                f"🚫 用户 {user_id} 已达到最大警告次数，已被封禁。"
            )
            logger.info("Banned user {} in chat {}", user_id, chat_id)
        except TelegramError as exc:
            logger.error("Failed to ban user {}: {}", user_id, exc)
