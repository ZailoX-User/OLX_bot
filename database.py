import sqlite3
from contextlib import contextmanager

DB_PATH = "olx_bot.db"


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                olx_id TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                price REAL NOT NULL,
                url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                chat_id INTEGER PRIMARY KEY,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def listing_exists(olx_id: str) -> bool:
    with get_connection() as conn:
        cur = conn.execute("SELECT 1 FROM listings WHERE olx_id = ?", (olx_id,))
        return cur.fetchone() is not None


def get_average_price(query: str, min_samples: int = 3):
    """Средняя цена по всем уже сохранённым объявлениям этого запроса.
    Возвращает None, если объявлений ещё недостаточно для надёжного среднего."""
    with get_connection() as conn:
        cur = conn.execute("SELECT price FROM listings WHERE query = ?", (query,))
        prices = [row["price"] for row in cur.fetchall()]

    if len(prices) < min_samples:
        return None
    return sum(prices) / len(prices)


def save_listing(query: str, olx_id: str, title: str, price: float, url: str):
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO listings (query, olx_id, title, price, url) "
            "VALUES (?, ?, ?, ?, ?)",
            (query, olx_id, title, price, url),
        )


def add_subscriber(chat_id: int):
    with get_connection() as conn:
        conn.execute("INSERT OR IGNORE INTO subscribers (chat_id) VALUES (?)", (chat_id,))


def remove_subscriber(chat_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM subscribers WHERE chat_id = ?", (chat_id,))


def get_all_subscribers():
    with get_connection() as conn:
        cur = conn.execute("SELECT chat_id FROM subscribers")
        return [row["chat_id"] for row in cur.fetchall()]
