import os

from dotenv import load_dotenv

load_dotenv()


BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN не задан. Скопируй .env.example в .env и впиши туда токен, "
        "либо задай переменную окружения BOT_TOKEN вручную."
    )


# Для Украины: OLX_BASE_URL = "https://www.olx.ua", OLX_SEARCH_PATH = "uk/list", CURRENCY_LABEL = "грн"
# Для Польши:  OLX_BASE_URL = "https://www.olx.pl", OLX_SEARCH_PATH = "oferty",  CURRENCY_LABEL = "zł"
OLX_BASE_URL = "https://www.olx.ua"
OLX_SEARCH_PATH = "uk/list"
CURRENCY_LABEL = "грн"
ACCEPT_LANGUAGE = "uk-UA,uk;q=0.9,ru;q=0.8,en;q=0.7"


SEARCH_QUERIES = {
    "iphone 13": 5000,
    "материнська плата": 1500,
    "оперативна пам'ять": 300,
}


CHECK_INTERVAL_SECONDS = 300


MIN_SAMPLES_FOR_AVERAGE = 3


ACCESSORY_KEYWORDS = [
    "чохол", "чехол", "дисплей", "скло", "стекло", "батарея", "акб",
    "модуль", "плівка", "плёнка", "запчаст", "ремонт", "корпус",
    "коробка", "упаковка", "шлейф", "радіатор", "кулер",
]

# Порог "выгодной цены" в процентах ниже средней
DISCOUNT_THRESHOLD_PERCENT = 15