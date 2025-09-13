# Функция для очистки прошлого сообщения бота
async def delete_previous_message(state) -> None:
    message_to_delete = await state.get_value("message_to_delete")
    if message_to_delete is None:
        pass
    else:
        try:
            await message_to_delete.delete()
        except:
            pass
        await state.update_data(message_to_delete=None)

# Функция для получения текста и раскладки клавиатуры и перезаписи в фсм как прошлый текст+клавиатура
async def get_text_kb(state, text, kb) -> None:
    old_text = await state.get_value("text")
    old_kb = await state.get_value("kb")

    await state.update_data(text=text)
    await state.update_data(kb=kb)

    await state.update_data(old_text=old_text)
    await state.update_data(old_kb=old_kb)
