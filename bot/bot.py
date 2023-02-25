import asyncio
import os

import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.filters.text import Text
from aiogram.fsm.storage.memory import MemoryStorage

from config_reader import load_config
from quotes import QUOTES


async def give_wisdom(m: types.Message):
    response = requests.get('https://api.quotable.io/random').json()
    quote = response.get('content')
    author = response.get('author')

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
    config = load_config('bot.ini')
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
