import re
import asyncio
import datetime

from aiogram import types, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from telegram.handlers.commands import Order
from telegram.keyboards.keyboard_generator import inline_keyboard_generator, reply_keyboard_generator, kb_clear
from Database import Database

router_new_order = Router()

MONTHS = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}


back_deny = {"Назад": "back", "Отмена": "deny"}
kb_back_deny = asyncio.run(inline_keyboard_generator(back_deny, (1, 1)))
kb_apply_back_deny = asyncio.run(inline_keyboard_generator(
    {
        "Подтвердить": "approve",
        "Назад": "back",
        "Отмена": "deny"
    },
    (1, 1, 1))
)


# Старт фсм для создания записи. Выбор дня
@router_new_order.callback_query(F.data == "order")
@router_new_order.callback_query(Order.service, F.data == "back")
async def start_new_order(callback: types.CallbackQuery, state: FSMContext) -> None:
    kb_day = await inline_keyboard_generator({"Сегодня": "today", "Завтра": "tomorrow", "Отмена": "deny"})

    text = f"На какой день запишемся?"
    await callback.message.edit_text(text, reply_markup=kb_day)
    await state.set_state(Order.day)


# Выбор услуги
@router_new_order.callback_query(Order.day, F.data.in_(("today", "tomorrow")))
@router_new_order.callback_query(Order.approved, F.data == "back")
async def choose_service(callback: types.CallbackQuery, state: FSMContext) -> None:
    if callback.data == "back":
        day = await state.get_value("day")
    else:
        day = callback.data

    date = datetime.date.today()

    if day == "today" or day == "сегодня":
        day = "сегодня"
    elif day == "tomorrow" or day == "завтра":
        day = "завтра"
        date = date + datetime.timedelta(days=1)

    for key, value in MONTHS.items():
        if value == date.month:
            month = key

    date = f"{date.day} {month} {date.year}"
    await state.update_data(day=day)
    await state.update_data(date=date)

    list_of_services = await Database.get_services()
    if not list_of_services:
        text = f"Нет услуг на данный момент"
        await callback.message.edit_text(
            text,
            reply_markup=kb_back_deny
        )
        await state.set_state(Order.service)
        return

    dict_of_services = {i[0]: [i[1], i[2]] for i in list_of_services}
    for key, value in dict_of_services.items():
        if int(value[1]) > 60:
            value[1] = f"{int(value[1]) // 60}ч{int(value[1]) % 60}мин"
        else:
            value[1] = f"{int(value[1])}мин"
    await state.update_data(dict_of_services=dict_of_services)

    dict_kb = {v[0]: v[0] for k, v in dict_of_services.items()} | back_deny

    twos = len(dict_of_services) // 2
    ones = len(dict_of_services) % 2

    sizes = (2,) * twos + (1,) * ones + (1, 1)

    kb_services = await inline_keyboard_generator(dict_kb, sizes)

    text = (
        f"Запись на {day} ({date})\n"
        f"Выберите желаемую услугу:"
    )
    await callback.message.edit_text(
        text,
        reply_markup=kb_services

    )
    await state.set_state(Order.service)


# Вывод записи и ожидание подтверждения
@router_new_order.callback_query(Order.service, F.data)
@router_new_order.callback_query(Order.ok, F.data == "back")
async def show_appointment(callback: types.CallbackQuery, state: FSMContext) -> None:
    dict_of_services = await state.get_value("dict_of_services")
    if dict_of_services:
        if callback.data == "back":
            service = await state.get_value("service")
        else:
            service = callback.data

        service_id = next((k for k, v in dict_of_services.items() if service in v), None)
        if service_id is not None:
            duration = dict_of_services[service_id][1]
            day = await state.get_value("day")
            date = await state.get_value("date")

            text = (
                f"Запись на {day} ({date})\n"
                f"Услуга: {service}\n"
                f"Длительность: {duration}\n"
                f"Стоимость: от 1200\n\n"

                f"Номер мастера для уточнения: 89999999999"
            )
            await callback.message.edit_text(
                text,
                reply_markup=kb_apply_back_deny
            )
            await state.update_data(service_id=service_id)
            await state.update_data(service=service)
            await state.update_data(duration=duration)
            await state.set_state(Order.approved)
    return None


# Вывод подтвержденной записи
@router_new_order.callback_query(Order.approved, F.data == "approve")
async def approved_appointment(callback: types.CallbackQuery, state: FSMContext) -> None:
    dict_of_services = await state.get_value("dict_of_services")
    if dict_of_services:
        service_id = await state.get_value("service_id")
        service = await state.get_value("service")
        duration = await state.get_value("duration")
        date = await state.get_value("date")

        await Database.insert_appointment(
            callback.from_user.id,
            service_id,
            date,
            "0",
            duration
        )

        text = (
            f"Вы успешно записаны на {service.lower()} на {date}\n"
            f"Длительность: {duration}\n"
            f"Стоимость: от 1200\n"
            f"Адрес: г.Уфа, ул. Маршала Жукова, дом 15, квартира 1\n\n"

            f"Номер мастера: 89999999999"
        )
        await callback.message.edit_text(
            text,
            reply_markup=kb_apply_back_deny
        )
        await state.set_state(Order.ok)