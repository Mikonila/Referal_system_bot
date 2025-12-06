from aiogram import Router, Bot
from aiogram.types import ChatJoinRequest, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from config import load_config

router = Router()
config = load_config()

# --- когда кто-то подаёт заявку ---
@router.chat_join_request()
async def on_join_request(event: ChatJoinRequest):
    user = event.from_user
    if not user:
        return

    text = (
        f"📥 Новый запрос на вступление в группу:\n\n"
        f"👤 {user.first_name or ''} {user.last_name or ''}\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"🔗 @{user.username or '—'}"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve:{user.id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"decline:{user.id}")
            ]
        ]
    )

    # Отправляем всем админам уведомление
    for admin_id in config.admin_ids:
        try:
            await event.bot.send_message(admin_id, text, reply_markup=keyboard, parse_mode="HTML")
        except Exception as e:
            print(f"Не удалось отправить админу {admin_id}: {e}")


# --- когда админ нажимает кнопку ---
@router.callback_query()
async def handle_approval(callback: CallbackQuery, bot: Bot):
    data = callback.data
    if not data:
        return

    if data.startswith("approve:"):
        user_id = int(data.split(":")[1])
        try:
            await bot.approve_chat_join_request(config.group_chat_id, user_id)
            await callback.message.edit_text(f"✅ Пользователь {user_id} одобрен.")
            # теперь уведомляем пользователя лично
            await bot.send_message(user_id, "🎉 Ваша заявка одобрена, добро пожаловать в группу!")
        except Exception as e:
            await callback.answer(f"Ошибка при одобрении: {e}", show_alert=True)

    elif data.startswith("decline:"):
        user_id = int(data.split(":")[1])
        try:
            await bot.decline_chat_join_request(config.group_chat_id, user_id)
            await callback.message.edit_text(f"❌ Пользователь {user_id} отклонён.")
            await bot.send_message(user_id, "🚫 Ваша заявка отклонена администратором.")
        except Exception as e:
            await callback.answer(f"Ошибка при отклонении: {e}", show_alert=True)


# --- для удаления уведомлений о вступлении/выходе (на случай ручного добавления) ---
@router.message()
async def delete_join_leave_messages(message: Message):
    if message.new_chat_members or message.left_chat_member:
        try:
            await message.delete()
        except Exception:
            pass
