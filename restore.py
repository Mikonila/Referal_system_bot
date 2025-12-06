import sqlite3
from datetime import datetime

DB_PATH = "data/referrals.db"

data = [
    # inviter_id, inviter_username, user_id, username, first_name, joined_at
    (375778984, "Lil_LittleR", 8324911816, None, "Андрэ", "2025-10-11 16:09"),
    (375778984, "Lil_LittleR", 5833949867, None, "Елена", "2025-10-12 18:28"),
    (375778984, "Lil_LittleR", 1727288106, "NordARH7", "VASILII", "2025-10-14 18:21"),
    (375778984, "Lil_LittleR", 653630638, "dmitrii_iy", "Дмитрий", "2025-10-15 04:01"),

    (1024803917, "TaisyaTihomirova", 6617875797, "eamishar", "Еа", "2025-10-16 23:17"),
    (6617875797, "eamishar", 245772847, "annaurmans", "Anna", "2025-10-16 23:28"),
    (6617875797, "eamishar", 5119552772, None, "наташа", "2025-10-17 04:08"),
    (6617875797, "eamishar", 597768123, None, "Г Г", "2025-10-17 04:15"),
    (6617875797, "eamishar", 522701067, None, "Алёна", "2025-10-17 06:10"),
    (6617875797, "eamishar", 847480871, None, "Марина", "2025-10-17 06:19"),
    (6617875797, "eamishar", 1578961610, None, "Вадим", "2025-10-17 09:34"),
]

conn = sqlite3.connect(DB_PATH)

# создаём таблицу, если её нет
conn.execute("""
CREATE TABLE IF NOT EXISTS referrals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inviter_id INTEGER,
    user_id INTEGER,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    joined_at TEXT
)
""")

# вставляем всех рефералов
for inviter_id, inviter_username, user_id, username, first_name, joined_at in data:
    try:
        conn.execute("""
        INSERT INTO referrals (inviter_id, user_id, username, first_name, joined_at)
        VALUES (?, ?, ?, ?, ?)
        """, (inviter_id, user_id, username, first_name, joined_at))
    except sqlite3.IntegrityError:
        print(f"⏩ Уже есть: {first_name}")

conn.commit()
conn.close()

print("✅ Все рефералы восстановлены!")
