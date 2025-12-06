from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from config import load_config
from database import add_referral, get_stats, get_all_referrals, save_user_info
import logging

router = Router()
config = load_config()
logger = logging.getLogger(__name__)

BOT_USERNAME = "sibirskoe_bot"

join_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Подать заявку на вступление", url=config.invite_link)]
    ]
)

async def send_long_message(message: Message, text: str, parse_mode: str = None):
    """
    Отправляет длинное сообщение, разбивая его на части, 
    чтобы не превысить лимит Telegram (4096 символов).
    Разбиение происходит по строкам, чтобы не разорвать HTML-теги.
    """
    chunk_size = 4000
    current_chunk = ""
    
    # Разбиваем весь текст на отдельные строки
    lines = text.split('\n')
    
    for line in lines:
        new_chunk = current_chunk + line + '\n'
        
        if len(new_chunk) > chunk_size:
            # Если добавление новой строки превысит лимит, отправляем текущий chunk
            if current_chunk: # Отправляем, только если chunk не пуст
                await message.answer(current_chunk, parse_mode=parse_mode)
            
            # Начинаем новый chunk с текущей строки
            current_chunk = line + '\n'
        else:
            # Добавляем строку в текущий chunk
            current_chunk = new_chunk

    # Отправляем оставшуюся часть
    if current_chunk.strip():
        await message.answer(current_chunk, parse_mode=parse_mode)

@router.message(CommandStart())
async def start_handler(message: Message, command: CommandStart):
    if message.from_user is None:
        return

    save_user_info(message.from_user)

    user_id = message.from_user.id
    args = command.args

    logger.info(f"/start from {user_id} with args: {args}")

    if args:
        try:
            ref_id = int(args)
            if ref_id != user_id:
                add_referral(ref_id, message.from_user)
                await message.answer(
                    "Ты пришёл по реферальной ссылке!\nНажми кнопку ниже, чтобы подать заявку на вступление:",
                    reply_markup=join_keyboard
                )
                return
        except ValueError:
            pass

    await message.answer(
        "Привет! Нажми кнопку ниже, чтобы подать заявку на вступление:",
        reply_markup=join_keyboard
    )

@router.message(Command("link"))
async def referral_link(message: Message):
    if message.from_user is None:
        return

    save_user_info(message.from_user)

    user_id = message.from_user.id
    link = f"https://t.me/{BOT_USERNAME}?start={user_id}"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="📨 Поделиться ссылкой", url=link)]]
    )

    await message.answer(
        f"🔗 *Ваша реферальная ссылка:*\n\n`{link}`",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@router.message(Command("stats"))
async def stats(message: Message):
    if message.from_user is None:
        return

    save_user_info(message.from_user)

    inviter_id = message.from_user.id
    stats = get_stats(inviter_id)

    if not stats:
        await message.answer("У тебя пока нет рефералов.")
        return

    lines = [f"📊 Рефералы ({len(stats)}):"]
    for i, ref in enumerate(stats, start=1):
        dt = ref["joined_at"].strftime("%Y-%m-%d %H:%M")
        username = f"@{ref['username']}" if ref.get("username") else ""
        first = ref.get("first_name") or ""
        last = ref.get("last_name") or ""
        full_name = f"{first} {last}".strip()
        lines.append(f"{i}. {full_name} {username} (ID: <code>{ref['user_id']}</code>) — {dt}")

    await send_long_message(message, "\n".join(lines), parse_mode="HTML") 

@router.message(Command("admin_stats"))
async def admin_stats(message: Message):
    logger.info(f"/admin_stats called by {message.from_user.id}")

    if message.from_user is None or message.from_user.id not in config.admin_ids:
        await message.answer("⛔️ У тебя нет доступа к этой команде.")
        return

    save_user_info(message.from_user)

    all_refs, user_info = get_all_referrals()
    if not all_refs:
        await message.answer("Пока нет рефералов.")
        return

    lines = ["👑 Полная статистика рефералов:\n"]
    for inviter_id, refs in all_refs.items():
        inviter_data = user_info.get(inviter_id, {})
        inviter_username = f"@{inviter_data.get('username')}" if inviter_data.get("username") else ""
        inviter_first = inviter_data.get("first_name") or ""
        inviter_last = inviter_data.get("last_name") or ""
        inviter_full_name = f"{inviter_first} {inviter_last}".strip()

        lines.append(f"👤 {inviter_full_name} {inviter_username} (ID: <code>{inviter_id}</code>) пригласил {len(refs)} чел:")

        for ref in refs:
            dt = ref["joined_at"].strftime("%Y-%m-%d %H:%M")
            username = f"@{ref['username']}" if ref.get("username") else ""
            first = ref.get("first_name") or ""
            last = ref.get("last_name") or ""
            full_name = f"{first} {last}".strip()

            lines.append(f"  └ {full_name} {username} (ID: <code>{ref['user_id']}</code>) — {dt}")

    await send_long_message(message, "\n".join(lines), parse_mode="HTML") 
