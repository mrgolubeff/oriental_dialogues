import asyncio
import os
from pathlib import Path

import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.filters.text import Text
from aiogram.fsm.storage.memory import MemoryStorage

from config_reader import load_config
from quotes import QUOTES


async def give_wisdom(m: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://swapi.dev/api/people/1') as response:
            json_response = await response.json()
            quote = json_response.get('content')
            author = json_response.get('author')

    await m.answer(
        f'\"{quote}\"\n- {author}'
    )


async def start_cmd(m: types.Message):
    kb = [  
        [
            types.KeyboardButton(text="О создателях"),
        ],
        [
            types.KeyboardButton(text="Дай мне мудрость!")
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )
    await m.answer(
        'Привет! Этот бот отправляет случайную цитату по запросу "Дай мне мудрость!"',
        reply_markup=keyboard
    )


async def about_authors(m: types.Message):
    await m.answer(
        QUOTES['about_authors']
    )


def register_handlers(dp: Dispatcher):
    dp.message.register(start_cmd, Command('start'))
    dp.message.register(give_wisdom, Text('Дай мне мудрость!'))
    dp.message.register(about_authors, Text('О создателях'))


async def startup() -> None:
    data_folder = Path('ini_source')
    file_to_open = data_folder / 'bot.ini'
    config = load_config(file_to_open)
    admin_id = config.tg_bot.admin_id
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()
    register_handlers(dp)

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(startup())
    except (KeyboardInterrupt, SystemExit):
        pass
