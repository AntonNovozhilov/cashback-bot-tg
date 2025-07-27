import asyncio

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.database import async_session
from sqlalchemy import select
from db.models import User

newses = Router()


async def count_users_tg_id_list():
    '''Вывод всех телеграм айди.'''
    async with async_session() as session:
        result = await session.scalars(select(User.telegram_id))
        return result.all()
    
class NewsPost(StatesGroup):
    '''Пост для рассылки.'''

    text = State()
    confirm = State()


@newses.message(F.text == 'Сделать рассылку')
async def news_to_subscriber(message: types.Message, state: FSMContext):
    """Запуск рассылки: ждем текст или пересланное сообщение."""
    await state.set_state(NewsPost.text)
    await message.answer("✉ Введите текст или перешлите сообщение для рассылки", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_send")]
        ]
    ))

@newses.message(NewsPost.text)
async def news_post_preview(message: types.Message, state: FSMContext):
    """Превью рассылки: сохраняем текст или пересланное сообщение."""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅ Подтвердить', callback_data='confirm_send')],
        [InlineKeyboardButton(text='❌ Отменить', callback_data='cancel_send')]
    ])

    if message.forward_from_chat or message.forward_from or message.forward_signature:
        await state.update_data(
            forward_message_id=message.message_id,
            forward_chat_id=message.chat.id
        )
        await message.answer("🔁 Сообщение принято. Подтвердите рассылку:", reply_markup=kb)
    elif message.text:
        await state.update_data(text=message.text)
        await message.answer(
            f"📢 Сообщение для рассылки:\n\n{message.text}",
            reply_markup=kb
        )
    else:
        await message.answer("❗ Отправьте текст или пересланное сообщение.")
        return

    await state.set_state(NewsPost.confirm)

@newses.callback_query(F.data == 'cancel_send', NewsPost.confirm)
async def cancel_newsletter(call: types.CallbackQuery, state: FSMContext):
    """Отмена рассылки."""
    await call.message.edit_reply_markup()
    await call.message.answer("❌ Рассылка отменена.")
    await state.clear()

@newses.callback_query(F.data == 'confirm_send', NewsPost.confirm)
async def send_newsletter(call: types.CallbackQuery, state: FSMContext):
    """Отправка рассылки."""
    await call.message.edit_reply_markup()
    data = await state.get_data()
    users_list = await count_users_tg_id_list()

    success, failed = 0, 0

    if 'forward_message_id' in data:
        # Пересылаем оригинальное сообщение
        for user in users_list:
            try:
                await call.bot.copy_message(
                    chat_id=user,
                    from_chat_id=data['forward_chat_id'],
                    message_id=data['forward_message_id']
                )
                success += 1
            except Exception as e:
                failed += 1
                print(f'Ошибка при пересылке: {e}')
            await asyncio.sleep(1)
    else:
        # Обычное текстовое сообщение
        for user in users_list:
            try:
                await call.bot.send_message(chat_id=user, text=data['text'])
                success += 1
            except Exception as e:
                failed += 1
                print(f'Ошибка при отправке: {e}')
            await asyncio.sleep(1)

    await call.message.answer(f"✅ Рассылка завершена.\nУспешно: {success}\nОшибок: {failed}")
    await state.clear()