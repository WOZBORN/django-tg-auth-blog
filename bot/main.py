import asyncio
import json
import logging
import sys
from os import getenv

import aiohttp

from aiogram import Bot, Dispatcher, html, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.handlers.callback_query import CallbackQuery

# Получаем токен бота и URL Django (можно задать напрямую)
with open("config.json", "r") as f:
    config = json.load(f)
    TOKEN = config.get("bot_token")
    DJANGO_URL = config.get("django_url")

router = Router()

async def check_user_registration(tg_id: int) -> dict:
    url = f"{DJANGO_URL}/check_user/?tg_id={tg_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
            return {}


async def register_user(tg_id: int, nickname: str) -> dict:
    url = f"{DJANGO_URL}/create-user/"
    payload = {"tg_id": str(tg_id), "nickname": nickname}
    headers = {'Content-Type': 'application/json'}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            return await resp.json()


@router.message(CommandStart())
async def cmd_start_handler(message: Message) -> None:
    tg_id = message.from_user.id
    user_info = await check_user_registration(tg_id)
    if user_info.get("status") == "ok":
        token = user_info.get("token")
        await message.answer(f"Вы уже зарегистрированы.\nВаш токен для входа: {html.bold(token)}")
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Зарегистрироваться", callback_data="register")]
        ])
        await message.answer("Вы не зарегистрированы. Нажмите кнопку для регистрации.", reply_markup=keyboard)


@router.callback_query(lambda callback: callback.data == "register")
async def callback_query_handler(callback: CallbackQuery):
    tg_id = callback.from_user.id
    nickname = callback.from_user.username or callback.from_user.full_name
    registration_info = await register_user(tg_id, nickname)
    if registration_info.get("status") == "ok":
        token = registration_info.get("token")
        await callback.message.edit_text(f"Регистрация прошла успешно!\nВаш токен: {html.bold(token)}")
    else:
        await callback.message.edit_text("Ошибка регистрации. Попробуйте позже.")
    await callback.answer()


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())