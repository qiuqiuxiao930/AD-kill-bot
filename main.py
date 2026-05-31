"""TG-ScamGuard entry point."""

import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv
from loguru import logger
from telegram.ext import Application

from bot.commands import register_commands
from bot.handlers import setup_handlers
from db.database import Database

# ── configuration ─────────────────────────────────────────────

def load_config(path: str = "config.yml") -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def configure_logging(config: dict) -> None:
    log_cfg = config.get("logging", {})
    logger.remove()  # remove default stderr handler
    logger.add(sys.stderr, level="INFO")
    if log_cfg.get("save_to_file", False):
        log_path = log_cfg.get("log_path", "logs/scamguard.log")
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        logger.add(log_path, rotation="10 MB", retention="30 days", level="DEBUG")


# ── main ──────────────────────────────────────────────────────

def main() -> None:
    load_dotenv()

    import os

    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        logger.error("BOT_TOKEN is not set. Please configure .env")
        sys.exit(1)

    config = load_config()
    configure_logging(config)

    logger.info("Starting TG-ScamGuard...")

    db = Database()
    app = Application.builder().token(bot_token).build()

    register_commands(app, db, config)
    setup_handlers(app, db, config)

    logger.info("Bot is running. Press Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
