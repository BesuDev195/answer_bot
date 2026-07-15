"""
bot.py

Telegram Smart FAQ Assistant Bot - main entry point.

Implements:
  FR-01: Mention detection - only responds when mentioned.
  FR-02: Question processing - strip mention, normalize.
  FR-03/FR-04: FAQ matching + automatic reply (via faq_matcher.py).
  FR-05: Default reply for unknown questions.
  FR-07: Logging of questions, matches, and misses.
"""

import os
import re
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatType
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from faq_manager import FAQManager
from faq_matcher import find_best_match, normalize
from logger_config import setup_logger

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DEFAULT_REPLY = (
    "Sorry, I couldn't find an answer to your question. "
    "Please contact an administrator."
)

logger = setup_logger()
faq_manager = FAQManager(filepath="data/faqs.json")


def extract_question(text: str, bot_username: str) -> str:
    """
    FR-02: Remove the bot mention (@BotUsername) from the message text,
    leaving only the actual question.
    """
    pattern = re.compile(rf"@{re.escape(bot_username)}", re.IGNORECASE)
    cleaned = pattern.sub("", text)
    return cleaned.strip()


def is_bot_mentioned(update: Update, bot_username: str) -> bool:
    """
    FR-01: Detect whether the bot was mentioned in this message.

    Checks both the raw text (covers @username mentions) and message
    entities (covers the case where Telegram tags it as a 'mention' entity),
    plus replies directly to one of the bot's own messages.
    """
    message = update.message
    if message is None or message.text is None:
        return False

    text_lower = message.text.lower()
    if f"@{bot_username.lower()}" in text_lower:
        return True

    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                mentioned_text = message.text[entity.offset: entity.offset + entity.length]
                if mentioned_text.lower() == f"@{bot_username.lower()}":
                    return True

    if message.reply_to_message and message.reply_to_message.from_user:
        if message.reply_to_message.from_user.username == bot_username:
            return True

    return False


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if message is None or message.text is None:
        return

    bot_username = context.bot.username

    # FR-01: only respond in groups when mentioned. Private chats: always respond.
    if message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        if not is_bot_mentioned(update, bot_username):
            return

    raw_text = message.text
    question = extract_question(raw_text, bot_username)
    normalized_question = normalize(question)

    if not normalized_question:
        # Bot was mentioned with no actual question attached.
        await message.reply_text(
            "Hi! Ask me a question and I'll try to help — for example: "
            f"\"@{bot_username} how do I register?\""
        )
        return

    faqs = faq_manager.get_all()
    match = find_best_match(normalized_question, faqs)

    user = message.from_user
    username = user.username or user.full_name or str(user.id)

    if match:
        await message.reply_text(match["answer"])
        logger.info(
            "MATCHED | user=%s | question=%r | matched_faq=%r | category=%s",
            username, normalized_question, match["question"], match.get("category", "")
        )
    else:
        await message.reply_text(DEFAULT_REPLY)
        logger.info(
            "UNANSWERED | user=%s | question=%r",
            username, normalized_question
        )


def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN not found. Create a .env file (see .env.example) "
            "and set BOT_TOKEN=your_token_here"
        )

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot starting up...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
