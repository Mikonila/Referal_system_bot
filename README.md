# Psychology Referral Bot

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![aiogram](https://img.shields.io/badge/aiogram-3.4.1-2CA5E0?logo=telegram&logoColor=white)
![Database](https://img.shields.io/badge/SQLite-referral%20stats-003B57)
![License](https://img.shields.io/badge/Usage-private%20project-informational)

Telegram bot for running a **referral funnel** into a private group:  
users share their personal invite link, admins approve join requests in one tap,  
and everyone sees how many people they’ve invited.

---

## ✨ Key features

- Personal referral link for every user (`/link`):contentReference[oaicite:0]{index=0}  
- Automatic tracking of who invited whom (referral tree in SQLite):contentReference[oaicite:1]{index=1}  
- User’s own referral stats via `/stats`:contentReference[oaicite:2]{index=2}  
- Full referral statistics for admins via `/admin_stats`:contentReference[oaicite:3]{index=3}  
- Join requests go to admins as interactive messages with **Approve / Decline** buttons:contentReference[oaicite:4]{index=4}  
- When approved/declined, the user gets a DM notification:contentReference[oaicite:5]{index=5}  
- All data stored locally in `./data/referrals.db` (SQLite with WAL mode & indexes):contentReference[oaicite:6]{index=6}  
- Long messages are auto-split to fit Telegram’s limits (no broken HTML):contentReference[oaicite:7]{index=7}  

---

## ⚙ Tech stack

- **Language:** Python 3.10+
- **Framework:** [aiogram 3.4.1](https://docs.aiogram.dev/) :contentReference[oaicite:8]{index=8}  
- **Config:** `python-dotenv` + custom `config.py` loader:contentReference[oaicite:9]{index=9}  
- **Database:** SQLite (`./data/referrals.db`) with WAL & indices:contentReference[oaicite:10]{index=10}  
- **Architecture:** `main.py` + separate routers for private and group handlers:contentReference[oaicite:11]{index=11}  



# Психологический реферальный бот

![Python](https://img.shields.io/badge/Язык-Python_3.10%2B-3776AB?logo=python&logoColor=white)
![aiogram](https://img.shields.io/badge/Фреймворк-aiogram_3.x-2CA5E0?logo=telegram&logoColor=white)
![Database](https://img.shields.io/badge/База-SQLite_referrals-003B57)
![Status](https://img.shields.io/badge/Статус-private_project-informational)

Телеграм-бот для **реферальной воронки** в закрытую группу:
каждый пользователь получает личную ссылку-приглашение,
админы одобряют заявки в один клик,
а все приглашения фиксируются в локальной базе SQLite.

---

## ✨ Основные возможности

- Личная реферальная ссылка (`/link`) для каждого пользователя  
- Автоматический учёт: кто кого пригласил (реферальное дерево в SQLite)  
- Просмотр своей статистики приглашений через `/stats`  
- Общая статистика по всем приглашениям для админов (`/admin_stats`)  
- Удобное одобрение заявок в группу через inline-кнопки «✅ Одобрить / ❌ Отклонить»  
- Личные уведомления пользователю о том, что его заявку приняли или отклонили  
- Все данные хранятся локально в `./data/referrals.db`  
- Длинные сообщения автоматически дробятся, чтобы не упираться в лимиты Telegram и не ломать разметку  

---

## ⚙ Стек технологий

- **Язык:** Python 3.10+
- **Фреймворк:** aiogram 3.x
- **Конфигурация:** `config.py` + переменные окружения (по желанию `.env`)
- **База данных:** SQLite (`./data/referrals.db`) с включённым WAL и индексами
- **Архитектура:** отдельные модули для приватных команд и групповых событий
