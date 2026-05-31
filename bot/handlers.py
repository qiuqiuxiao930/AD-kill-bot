"""Message handler: runs incoming text through the detection pipeline."""

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)
from loguru import logger

from db.database import Database
from detection.keyword_filter import KeywordFilter
from detection.ai_classifier import AIClassifier
from detection.url_checker import URLChecker
from bot.actions import ActionHandler


async def _on_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Process every non-command text message in group chats."""
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if not message or not message.text:
        return

    # Skip private chats
    if chat.type == "private":
        return

    db: Database = context.bot_data["db"]

    # Skip if disabled for this group
    if not db.is_enabled(chat.id):
        return

    # Skip whitelisted users
    if db.is_whitelisted(user.id, chat.id):
        return

    # Skip admins
    try:
        member = await chat.get_member(user.id)
        if member.status in ("administrator", "creator"):
            return
    except Exception:
        pass

    text = message.text
    kw_filter: KeywordFilter = context.bot_data["kw_filter"]
    ai_clf: AIClassifier = context.bot_data["ai_clf"]
    url_checker: URLChecker = context.bot_data["url_checker"]
    action_handler: ActionHandler = context.bot_data["action_handler"]

    # Run detection pipeline: keyword → URL → AI
    detection = kw_filter.check(text)
    if detection is None:
        detection = url_checker.check(text)
    if detection is None and ai_clf.available:
        detection = ai_clf.predict(text)

    if detection is None:
        return

    logger.info(
        "Detection in chat {}: type={} confidence={:.2f} user={}",
        chat.id,
        detection.get("type"),
        detection.get("confidence", 0),
        user.id,
    )

    await action_handler.handle(update, detection)


def setup_handlers(
    app: Application,
    db: Database,
    config: dict,
) -> None:
    """Wire detection components and the message handler into the app."""
    det_cfg = config.get("detection", {})

    kw_filter = KeywordFilter(det_cfg.get("keywords_file", "rules/keywords.txt"))
    url_checker = URLChecker()

    use_ai = det_cfg.get("use_ai_model", True)
    threshold = det_cfg.get("confidence_threshold", 0.85)
    ai_clf = AIClassifier(confidence_threshold=threshold) if use_ai else AIClassifier.__new__(AIClassifier)
    if not use_ai:
        ai_clf._pipeline = None
        ai_clf.confidence_threshold = threshold

    action_handler = ActionHandler(db, config)

    app.bot_data["kw_filter"] = kw_filter
    app.bot_data["ai_clf"] = ai_clf
    app.bot_data["url_checker"] = url_checker
    app.bot_data["action_handler"] = action_handler

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, _on_message)
    )
    logger.info("Message handler registered (AI={}, threshold={})", use_ai, threshold)
