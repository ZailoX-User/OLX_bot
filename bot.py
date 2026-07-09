import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

import config
import database
from parser import fetch_listings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def format_message(item: dict, avg_price):
    message = (
        "📦 <b>Новое объявление!</b>\n"
        f"📌 Название: {item['title']}\n"
        f"💰 Цена: {item['price']:.0f} {config.CURRENCY_LABEL}\n"
        f"🔗 {item['url']}"
    )

    if avg_price:
        diff_percent = (avg_price - item["price"]) / avg_price * 100
        if diff_percent >= config.DISCOUNT_THRESHOLD_PERCENT:
            message += (
                f"\n\n🔥 <b>ВЫГОДНАЯ ЦЕНА! На {diff_percent:.0f}% ниже рынка!</b>"
            )

    return message


async def broadcast(app: Application, text: str):
    for chat_id in database.get_all_subscribers():
        try:
            await app.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="HTML",
                disable_web_page_preview=False,
            )
        except Exception as e:
            logger.warning("Не удалось отправить сообщение %s: %s", chat_id, e)


async def check_query(app: Application, query: str, min_price: float):
    try:
        listings = fetch_listings(query, min_price=min_price)
    except Exception as e:
        logger.error("Ошибка парсинга запроса '%s': %s", query, e)
        return

    # Считаем среднюю цену ДО добавления новых объявлений этого прохода,
    # чтобы новая партия не искажала сама себя.
    for item in listings:
        if database.listing_exists(item["olx_id"]):
            continue

        avg_price = database.get_average_price(query, config.MIN_SAMPLES_FOR_AVERAGE)
        message = format_message(item, avg_price)

        database.save_listing(query, item["olx_id"], item["title"], item["price"], item["url"])
        await broadcast(app, message)
        logger.info("Новое объявление по '%s': %s (%.0f %s)", query, item["title"], item["price"], config.CURRENCY_LABEL)


async def scheduled_job(context: ContextTypes.DEFAULT_TYPE):
    for query, min_price in config.SEARCH_QUERIES.items():
        await check_query(context.application, query, min_price)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat is None or update.message is None:
        return
    database.add_subscriber(update.effective_chat.id)
    await update.message.reply_text(
        "Привет! Теперь ты будешь получать уведомления о новых объявлениях OLX, "
        "особенно о тех, что дешевле рынка 🔥\n\n"
        "Чтобы отписаться — /stop"
    )


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat is None or update.message is None:
        return
    database.remove_subscriber(update.effective_chat.id)
    await update.message.reply_text("Ты отписан от рассылки. Вернуться можно командой /start")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Необработанная ошибка: %s", context.error, exc_info=context.error)


def main():
    database.init_db()

    app = Application.builder().token(config.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_error_handler(error_handler)

    app.job_queue.run_repeating(
        scheduled_job, interval=config.CHECK_INTERVAL_SECONDS, first=5
    )

    logger.info("Бот запущен, начинаю мониторинг OLX...")
    app.run_polling()


if __name__ == "__main__":
    main()