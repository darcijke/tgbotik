import os
import asyncio
import aiosqlite

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import FSInputFile

TOKEN = os.getenv("BOT_API_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_API_TOKEN не задан")

ADMIN_ID = 547379929

bot = Bot(token=TOKEN)
dp = Dispatcher()

# =====================
# БАЗА
# =====================

async def init_db():
    async with aiosqlite.connect("users.db") as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY
        )
        """)
        await db.commit()

# =====================
# /START
# =====================

@dp.message(Command("start"))
async def start(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Accetta l'invito", callback_data="tyk")]
    ])
    await message.answer("La Dolce Vita si avvicina", reply_markup=kb)

# =====================
# КНОПКА ТЫК
# =====================

@dp.callback_query(F.data == "tyk")
async def tyk(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍷 L'Italia è già vicina...", callback_data="sub")]
    ])

    await bot.send_photo(
        chat_id=callback.from_user.id,
        photo = FSInputFile("images.png"),
        caption="🍋 До итальянского вечера осталось несколько дней. Готовь светлый outfit, хорошее настроение и любовь к красивым вечерам.",
        reply_markup=kb
    )

    await callback.answer()

# =====================
# ПОДПИСКА
# =====================

@dp.callback_query(F.data == "sub")
async def subscribe(callback: CallbackQuery):
    async with aiosqlite.connect("users.db") as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
            (callback.from_user.id,)
        )
        await db.commit()

    await callback.answer("🍋 Benvenuto alla Dolce Vita 🍋", show_alert=True)

# =====================
# РАССЫЛКА
# =====================

async def send_to_all(text=None, photo=None):
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            users = await cursor.fetchall()

    for (user_id,) in users:
        try:
            if photo:
                await bot.send_photo(user_id, photo=photo, caption=text)
            else:
                await bot.send_message(user_id, text)
        except:
            pass

# =====================
# АДМИН
# =====================

@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="11.06", callback_data="a11")],
        [InlineKeyboardButton(text="12.06", callback_data="a12")],
        [InlineKeyboardButton(text="13.06 🎉", callback_data="a13")]
    ])

    await message.answer("Админ-панель", reply_markup=kb)

# =====================
# АДМИН КНОПКИ
# =====================

@dp.callback_query(F.data.in_(["a11", "a12", "a13"]))
async def admin_actions(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа", show_alert=True)
        return

    if callback.data == "a11":
        await send_to_all("🥂 Почти как лето в Италии… Через 2 дня встречаемся на вечере La Dolce Vita 🥂")

    elif callback.data == "a12":
        await send_to_all("Итальянский вечер становится всё ближе. Всего 1 день до празднования. Музыка, лимоны и атмосфера итальянского лета ☀️")

    elif callback.data == "a13":
        await send_to_all(
            text="Сегодня собираемся на итальянский день рождения. Буду очень ждать. Dress code, настроение и немного Италии — всё, что нужно ✨\nНапоминаем о месте проведения: Петра Дубрава, Вишнёвая улица, 139А, а также координаты на Яндекс Картах для поиска: 53.301014, 50.376039",
        ),

    await callback.answer("Отправлено ✅")

# =====================
# MAIN (СТАБИЛЬНЫЙ)
# =====================

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await init_db()

    while True:
        try:
            await dp.start_polling(bot)
        except Exception as e:
            print(f"Bot crashed: {e}")
            await asyncio.sleep(3)

# =====================
# START
# =====================

if __name__ == "__main__":
    asyncio.run(main())