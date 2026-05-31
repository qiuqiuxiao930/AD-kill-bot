"""Admin command handlers for /scamguard, /whitelist, /warn, /unban."""

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from telegram.error import TelegramError
from loguru import logger

from db.database import Database


async def _is_admin(update: Update) -> bool:
    """Check whether the user is a group admin or creator."""
    user = update.effective_user
    chat = update.effective_chat
    if chat.type == "private":
        return True
    try:
        member = await chat.get_member(user.id)
        return member.status in ("administrator", "creator")
    except TelegramError:
        return False


# ── /scamguard ────────────────────────────────────────────────

async def scamguard_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if not await _is_admin(update):
        await update.message.reply_text("⛔ 仅管理员可使用此命令。")
        return

    db: Database = context.bot_data["db"]
    chat_id = update.effective_chat.id
    args = context.args or []

    if not args:
        await update.message.reply_text(
            "用法：/scamguard <on|off|status>"
        )
        return

    sub = args[0].lower()
    if sub == "on":
        db.set_enabled(chat_id, True)
        await update.message.reply_text("🛡️ ScamGuard 已启用。")
    elif sub == "off":
        db.set_enabled(chat_id, False)
        await update.message.reply_text("🛡️ ScamGuard 已停用。")
    elif sub == "status":
        enabled = db.is_enabled(chat_id)
        stats = db.get_stats(chat_id)
        status_text = "启用" if enabled else "停用"
        lines = [
            f"🛡️ ScamGuard 状态：{status_text}",
            f"总检测次数：{stats['total_detections']}",
        ]
        if stats["by_type"]:
            lines.append("按类型统计：")
            for t, c in stats["by_type"].items():
                lines.append(f"  - {t}: {c}")
        await update.message.reply_text("\n".join(lines))
    else:
        await update.message.reply_text("用法：/scamguard <on|off|status>")


# ── /whitelist ────────────────────────────────────────────────

async def whitelist_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if not await _is_admin(update):
        await update.message.reply_text("⛔ 仅管理员可使用此命令。")
        return

    db: Database = context.bot_data["db"]
    chat_id = update.effective_chat.id
    args = context.args or []

    if len(args) < 2:
        await update.message.reply_text("用法：/whitelist <add|remove> @user")
        return

    action = args[0].lower()
    # Try to resolve the user from the reply or mentioned entities
    target_user = _resolve_user(update, args[1])
    if target_user is None:
        await update.message.reply_text("❌ 无法识别目标用户，请回复该用户的消息或使用 @用户名。")
        return

    if action == "add":
        db.add_to_whitelist(target_user, chat_id)
        await update.message.reply_text(f"✅ 用户 {target_user} 已加入白名单。")
    elif action == "remove":
        db.remove_from_whitelist(target_user, chat_id)
        await update.message.reply_text(f"✅ 用户 {target_user} 已移出白名单。")
    else:
        await update.message.reply_text("用法：/whitelist <add|remove> @user")


# ── /warn ─────────────────────────────────────────────────────

async def warn_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if not await _is_admin(update):
        await update.message.reply_text("⛔ 仅管理员可使用此命令。")
        return

    db: Database = context.bot_data["db"]
    chat_id = update.effective_chat.id
    args = context.args or []

    target_user = None
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user.id
    elif args:
        target_user = _resolve_user(update, args[0])

    if target_user is None:
        await update.message.reply_text("用法：/warn @user 或回复消息使用 /warn")
        return

    count = db.add_warning(target_user, chat_id)
    max_w = context.bot_data.get("config", {}).get(
        "actions", {}
    ).get("on_detect", {}).get("max_warnings", 3)

    await update.message.reply_text(
        f"⚠️ 用户 {target_user} 已被警告（{count}/{max_w}）"
    )

    if count >= max_w:
        try:
            await update.effective_chat.ban_member(target_user)
            await update.message.reply_text(
                f"🚫 用户 {target_user} 已达到最大警告次数，已被封禁。"
            )
        except TelegramError as exc:
            logger.error("Failed to ban user {}: {}", target_user, exc)


# ── /unban ────────────────────────────────────────────────────

async def unban_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if not await _is_admin(update):
        await update.message.reply_text("⛔ 仅管理员可使用此命令。")
        return

    db: Database = context.bot_data["db"]
    chat_id = update.effective_chat.id
    args = context.args or []

    target_user = _resolve_user(update, args[0]) if args else None
    if target_user is None:
        await update.message.reply_text("用法：/unban @user")
        return

    db.reset_warnings(target_user, chat_id)
    try:
        await update.effective_chat.unban_member(target_user)
        await update.message.reply_text(f"✅ 用户 {target_user} 已被解除封禁，警告已清零。")
    except TelegramError as exc:
        logger.error("Failed to unban user {}: {}", target_user, exc)
        await update.message.reply_text(f"❌ 解封失败：{exc}")


# ── helpers ───────────────────────────────────────────────────

def _resolve_user(update: Update, arg: str) -> int | None:
    """Try to extract a user ID from a command argument or message entities."""
    # Numeric user ID
    try:
        return int(arg)
    except ValueError:
        pass

    # @username mention in entities
    if update.message and update.message.entities:
        for entity in update.message.entities:
            if entity.type == "text_mention" and entity.user:
                return entity.user.id
            if entity.type == "mention":
                pass  # cannot resolve username→id without extra API call
    return None


def register_commands(app: Application, db: Database, config: dict) -> None:
    """Register all admin commands on the Application."""
    app.bot_data["db"] = db
    app.bot_data["config"] = config

    app.add_handler(CommandHandler("scamguard", scamguard_command))
    app.add_handler(CommandHandler("whitelist", whitelist_command))
    app.add_handler(CommandHandler("warn", warn_command))
    app.add_handler(CommandHandler("unban", unban_command))

    logger.info("Admin commands registered")
