import re

import requests
from bs4 import BeautifulSoup

import config

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": config.ACCEPT_LANGUAGE,
}


def build_search_url(query: str) -> str:
    query_encoded = query.strip().replace(" ", "-")
    return f"{config.OLX_BASE_URL}/{config.OLX_SEARCH_PATH}/q-{query_encoded}/"


def parse_price(raw_price: str):
    digits = re.sub(r"[^\d]", "", raw_price)
    if not digits:
        return None
    return float(digits)


def fetch_listings(query: str, min_price: float = 0, limit: int = 20):
    """
    Возвращает список словарей: olx_id, title, price, url.

    min_price — объявления дешевле этой суммы (обычно аксессуары/запчасти)
    пропускаются.

    ВАЖНО: OLX регулярно меняет вёрстку и css-классы. Если парсер вдруг
    перестанет находить объявления — открой страницу поиска в браузере,
    нажми "Просмотр кода" на карточке объявления и обнови селекторы ниже
    (сейчас используются актуальные на момент написания data-cy/data-testid
    атрибуты, они меняются реже, чем классы).
    """
    url = build_search_url(query)
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    cards = soup.select('div[data-cy="l-card"]')[:limit]

    for card in cards:
        link_tag = card.select_one("a")
        title_tag = card.select_one("h4, h6")
        price_tag = card.select_one('p[data-testid="ad-price"]')

        if not (link_tag and title_tag and price_tag):
            continue

        href = link_tag.get("href", "")
        full_url = href if href.startswith("http") else f"{config.OLX_BASE_URL}{href}"

        olx_id_match = re.search(r"ID(\w+)\.html", href)
        olx_id = olx_id_match.group(1) if olx_id_match else full_url

        price = parse_price(price_tag.get_text())
        if price is None:
            continue

        title_text = title_tag.get_text(strip=True)

        if price < min_price:
            continue

        if any(keyword.lower() in title_text.lower() for keyword in config.ACCESSORY_KEYWORDS):
            continue

        results.append({
            "olx_id": olx_id,
            "title": title_text,
            "price": price,
            "url": full_url,
        })

    return results