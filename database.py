# database.py — версия на SQLite
from __future__ import annotations
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import threading
import json

# Путь к БД (папка примонтирована в docker-compose)
DATA_DIR = Path("./data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "referrals.db"

# Глобальная блокировка на запись/схему
_lock = threading.Lock()

def _connect() -> sqlite3.Connection:
    # check_same_thread=False — позволяем использовать коннект из разных потоков aiogram
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def _init_db() -> None:
    with _lock:
        conn = _connect()
        try:
            # Улучшаем параллелизм (много чтений, редкие записи)
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA foreign_keys=ON;")

            # Пользователи-справочник (для /admin_stats)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id     INTEGER PRIMARY KEY,
                    username    TEXT,
                    first_name  TEXT,
                    last_name   TEXT
                );
            """)

            # Рефералы: кто кого пригласил
            conn.execute("""
                CREATE TABLE IF NOT EXISTS referrals (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    inviter_id  INTEGER NOT NULL,
                    user_id     INTEGER NOT NULL,
                    username    TEXT,
                    first_name  TEXT,
                    last_name   TEXT,
                    joined_at   TEXT NOT NULL,
                    UNIQUE(inviter_id, user_id),
                    FOREIGN KEY(inviter_id) REFERENCES users(user_id) ON DELETE CASCADE
                );
            """)

            # Индексы для быстрых выборок
            conn.execute("CREATE INDEX IF NOT EXISTS idx_referrals_inviter ON referrals(inviter_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_referrals_user ON referrals(user_id);")
            conn.commit()
        finally:
            conn.close()

_init_db()

def save_user_info(user) -> None:
    """
    Сохраняем (или обновляем) карточку пользователя в таблице users.
    """
    with _lock:
        conn = _connect()
        try:
            conn.execute("""
                INSERT INTO users (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username=excluded.username,
                    first_name=excluded.first_name,
                    last_name=excluded.last_name;
            """, (user.id, user.username, user.first_name, user.last_name))
            conn.commit()
        finally:
            conn.close()

def add_referral(inviter_id: int, user) -> None:
    """
    Добавляем реферала (уникальность по паре (inviter_id, user_id)).
    Если уже есть — просто молча выходим (как у тебя).
    """
    with _lock:
        conn = _connect()
        try:
            # Обновим справочник users (вдруг его ещё нет)
            conn.execute("""
                INSERT INTO users (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    username=excluded.username,
                    first_name=excluded.first_name,
                    last_name=excluded.last_name;
            """, (user.id, user.username, user.first_name, user.last_name))

            # Добавляем реферала
            now_iso = datetime.now().isoformat()
            try:
                conn.execute("""
                    INSERT INTO referrals (inviter_id, user_id, username, first_name, last_name, joined_at)
                    VALUES (?, ?, ?, ?, ?, ?);
                """, (inviter_id, user.id, user.username, user.first_name, user.last_name, now_iso))
                conn.commit()
            except sqlite3.IntegrityError:
                # Дубликат пары (inviter_id, user_id) — игнорируем
                pass
        finally:
            conn.close()

def get_stats(inviter_id: int) -> List[dict]:
    """
    Возвращаем список рефералов конкретного пригласившего
    со структурой как раньше (joined_at = datetime).
    """
    conn = _connect()
    try:
        cur = conn.execute("""
            SELECT user_id, username, first_name, last_name, joined_at
            FROM referrals
            WHERE inviter_id = ?
            ORDER BY datetime(joined_at) ASC;
        """, (inviter_id,))
        rows = cur.fetchall()

        stats = []
        for r in rows:
            stats.append({
                "user_id": r["user_id"],
                "username": r["username"],
                "first_name": r["first_name"],
                "last_name": r["last_name"],
                "joined_at": datetime.fromisoformat(r["joined_at"])
            })
        return stats
    finally:
        conn.close()

def get_all_referrals():
    """
    Возвращаем (dict[int, List[dict]], dict[int, dict]) как раньше:
      - _referrals: inviter_id -> [ {user_id, username, first_name, last_name, joined_at: datetime}, ... ]
      - _user_info: user_id -> {username, first_name, last_name}
    """
    conn = _connect()
    try:
        # users
        cur = conn.execute("SELECT user_id, username, first_name, last_name FROM users;")
        user_info = {}
        for r in cur.fetchall():
            user_info[int(r["user_id"])] = {
                "username": r["username"],
                "first_name": r["first_name"],
                "last_name": r["last_name"]
            }

        # referrals
        cur = conn.execute("""
            SELECT inviter_id, user_id, username, first_name, last_name, joined_at
            FROM referrals
            ORDER BY inviter_id, datetime(joined_at) ASC;
        """)
        refs: Dict[int, List[dict]] = {}
        for r in cur.fetchall():
            item = {
                "user_id": r["user_id"],
                "username": r["username"],
                "first_name": r["first_name"],
                "last_name": r["last_name"],
                "joined_at": datetime.fromisoformat(r["joined_at"])
            }
            refs.setdefault(int(r["inviter_id"]), []).append(item)

        return refs, user_info
    finally:
        conn.close()
