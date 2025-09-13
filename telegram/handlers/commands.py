import asyncio

from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from telegram.keyboards.keyboard_generator import inline_keyboard_generator


router_commands = Router()

class Order(StatesGroup):
    day = State()
    service = State()
    approved = State()
    ok = State()


# Вызов главного меню
@router_commands.message(Command("start"))
@router_commands.callback_query(F.data == "deny")
@router_commands.callback_query(Order.ok, F.data == "approve")
async def start(update: types.Message | types.CallbackQuery, state: FSMContext) -> None:
    if not await state.get_state() is None:
        await state.clear()

    kb_order = await inline_keyboard_generator({"Записаться": "order"})

    if type(update) is types.CallbackQuery:
        if update.data == "approve":
            seconds = 5
            while seconds > 0:
                await update.message.edit_text(
                    f"<b>Успешно</b>\n\n"
                    f"<i>Возврат в гл.меню через</i> <code>{seconds}</code> <i>с.</i>")
                await asyncio.sleep(1)
                seconds -= 1
        await update.message.edit_text(f"Привет!\nЭто бот для записи к мастеру салона красоту 'Мадина'!", reply_markup=kb_order)
    elif type(update) is types.Message:
        await update.delete()
        await update.answer(f"Привет!\nЭто бот для записи к мастеру салона красоту 'Мадина'!", reply_markup=kb_order)

