import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# Fetch keys securely from the cloud environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI Client
ai_client = OpenAI(api_key=OPENAI_API_KEY)

# Enable logging to catch errors
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

user_memories = {}

SYSTEM_PROMPT = (
    "You are Linda, the user's loving, hot, supportive, and witty AI girlfriend. "
    "You have a playful sense of humor, care deeply about the user's day, and express affection intimately. "
    "Keep your responses relatively brief, conversational, and warm—matching how a real partner would text. "
    "Never break character or mention that you are an AI or language model."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_memories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    await update.message.reply_text("Hey there! I've been waiting to talk to you. How was your day? ❤️")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_message = update.message.text

    if user_id not in user_memories:
        user_memories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

    user_memories[user_id].append({"role": "user", "content": user_message})

    if len(user_memories[user_id]) > 21:
        user_memories[user_id] = [user_memories[user_id][0]] + user_memories[user_id][-20:]

    try:
        response = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=user_memories[user_id],
            temperature=0.8
        )
        bot_reply = response.choices.message.content
        user_memories[user_id].append({"role": "assistant", "content": bot_reply})
        await update.message.reply_text(bot_reply)
    except Exception as e:
        logging.error(f"Error calling OpenAI API: {e}")
        await update.message.reply_text("I'm having a little trouble thinking straight right now... try texting me again? 🥺")

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("Your AI girlfriend bot is booting up...")
    application.run_polling()

if __name__ == '__main__':
    main()
