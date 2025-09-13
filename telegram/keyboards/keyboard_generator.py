import asyncio
from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, ReplyKeyboardBuilder


async def inline_keyboard_generator(buttons: dict[str], sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for key, value in buttons.items():
        keyboard.add(InlineKeyboardButton(text=key, callback_data=value))

    return keyboard.adjust(*sizes).as_markup()


async def reply_keyboard_generator(
    *buttons: str,
    placeholder: str = None,
    sizes: tuple[int] = (2,)):

    keyboard = ReplyKeyboardBuilder()

    for index, text in enumerate(buttons, start=0):
        keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
            resize_keyboard=True, input_field_placeholder=placeholder)


kb_clear = asyncio.run(inline_keyboard_generator({"Отмена": "refuse"}))