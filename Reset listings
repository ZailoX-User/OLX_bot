import database

database.init_db()

with database.get_connection() as conn:
    count = conn.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
    conn.execute("DELETE FROM listings")

print(f"Удалено объявлений: {count}. Подписчики не тронуты.")