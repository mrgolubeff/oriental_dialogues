import asyncio
import os
from pathlib import Path

import aiohttp
from aiogram import F
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters.state import StatesGroup, State
from aiogram.types import ContentType, CallbackQuery

from aiogram_dialog import Window, Dialog, DialogManager, setup_dialogs, StartMode
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput

from config_reader import load_config
from quotes import QUOTES


POST_ADRESS = 'http://127.0.0.1:8000/quotes/'
GET_ADRESS = 'http://127.0.0.1:8000/quotes/random'


async def get_data(dialog_manager: DialogManager, **kwargs):
    author = dialog_manager.dialog_data.get('author', None)
    quote = dialog_manager.dialog_data.get('quote', None)
    return {
        "author": author,
        "quote": quote,
    }

class AddQuote(StatesGroup):
    add_author = State()
    add_quote = State()
    confirm_quote = State()
    add_more_quote = State()

def render_quote(quote: str, author: str) -> str:
    return f'\"{quote}\"\n- {author}'


async def author_handler(message: types.Message, message_input: MessageInput,
                       manager: DialogManager):
    manager.dialog_data['author'] = message.text
    await manager.next()


async def quote_handler(message: types.Message, message_input: MessageInput,
                        manager: DialogManager):
    manager.dialog_data['quote'] = message.text
    await manager.switch_to(AddQuote.confirm_quote)


async def on_cancel(callback: CallbackQuery, button: Button, manager: DialogManager):
    await callback.message.answer('Отменено. Чтобы добавить еще цитату, нажмите /add')
    await manager.done()


async def on_add(callback: CallbackQuery, button: Button, manager: DialogManager):
    async with aiohttp.ClientSession() as session:
        params = {
            'author': manager.dialog_data['author'],
            'text': manager.dialog_data['quote'],
        }
        async with session.post(POST_ADRESS, params=params) as response:
            print(response.status)
    await manager.switch_to(AddQuote.add_more_quote)


cancel_button = Button(Const('Отмена'), id='cancel', on_click=on_cancel)

author_window = Window(
    Const('Введите автора:'),
    cancel_button,
    MessageInput(author_handler, content_types=[ContentType.TEXT]),
    state=AddQuote.add_author,
)
quote_window = Window(
    Format('Автор:\n{author}\n\nВведите цитату:'),
    cancel_button,
    MessageInput(quote_handler, content_types=[ContentType.TEXT]),
    state=AddQuote.add_quote,
    getter=get_data,
)
confirm_window = Window(
    Format('Автор:\n{author}\n\nЦитата:\n{quote}'),
    cancel_button,
    SwitchTo(Const('Исправить цитату'), id='rewrite', state=AddQuote.add_quote),
    Button(Const('Добавить'), id='add_quote', on_click=on_add),
    getter=get_data,
    state=AddQuote.confirm_quote,
)
more_quote_window = Window(
    Format('Цитата добавлена. Можно добавить еще цитату того же автора.\n\nАвтор:\n{author}\n\nВведите цитату:'),
    cancel_button,
    MessageInput(quote_handler, content_types=[ContentType.TEXT]),
    state=AddQuote.add_more_quote,
    getter=get_data,
)


dialog = Dialog(
    author_window,
    quote_window,
    confirm_window,
    more_quote_window,
)


async def give_wisdom(m: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(GET_ADRESS) as response:
            json_response = await response.json()
            quote = json_response.get('quote')
            author = json_response.get('author')

    await m.answer(
        render_quote(quote, author)
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




async def add_quote(m: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(AddQuote.add_author, mode=StartMode.RESET_STACK)




def register_handlers(dp: Dispatcher):
    dp.message.register(start_cmd, Command('start'))
    dp.message.register(give_wisdom, F.text == 'Дай мне мудрость!')
    dp.message.register(about_authors, F.text == 'О создателях')
    dp.message.register(add_quote, Command('add'))


async def startup() -> None:
    data_folder = Path('ini_source')
    file_to_open = data_folder / 'bot.ini'
    config = load_config(file_to_open)
    admin_id = config.tg_bot.admin_id
    storage = MemoryStorage()
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()
    register_handlers(dp)
    dp.include_router(dialog)
    setup_dialogs(dp)

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(startup())
    except (KeyboardInterrupt, SystemExit):
        pass
