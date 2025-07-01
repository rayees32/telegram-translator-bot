import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
from googletrans import Translator

TOKEN = os.getenv("BOT_TOKEN")
translator = Translator()

CHOOSING_LANGUAGE, TRANSLATING = range(2)
user_lang_direction = {}

lang_options = [
    ["فارسی ➜ انگلیسی", "انگلیسی ➜ فارسی"],
    ["فارسی ➜ پشتو", "پشتو ➜ فارسی"]
]

lang_map = {
    "فارسی ➜ انگلیسی": ("fa", "en"),
    "انگلیسی ➜ فارسی": ("en", "fa"),
    "فارسی ➜ پشتو": ("fa", "ps"),
    "پشتو ➜ فارسی": ("ps", "fa"),
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "لطفاً زبان مورد نظر را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(lang_options, resize_keyboard=True, one_time_keyboard=True)
    )
    return CHOOSING_LANGUAGE

async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice in lang_map:
        user_lang_direction[update.effective_user.id] = lang_map[choice]
        await update.message.reply_text("حالا متنت را بفرست تا ترجمه کنم.")
        return TRANSLATING
    else:
        await update.message.reply_text("لطفاً یک گزینه معتبر انتخاب کنید.")
        return CHOOSING_LANGUAGE

async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in user_lang_direction:
        await update.message.reply_text("اول زبان را انتخاب کن. /start را بزن.")
        return CHOOSING_LANGUAGE

    src, dest = user_lang_direction[uid]
    text = update.message.text

    try:
        translated = translator.translate(text, src=src, dest=dest)
        await update.message.reply_text(f"🔄 ترجمه:
{translated.text}")
    except Exception as e:
        await update.message.reply_text("❌ خطا در ترجمه. لطفاً دوباره امتحان کن.")

    return TRANSLATING

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("گفتگو پایان یافت. /start برای شروع دوباره.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_language)],
            TRANSLATING: [MessageHandler(filters.TEXT & ~filters.COMMAND, translate_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    print("🤖 Bot is running on Railway...")
    app.run_polling()

if __name__ == "__main__":
    main()
