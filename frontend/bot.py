from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import asyncio

from config import TOKEN, db_path
import db_manager

# import random
import datetime


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

scores = {
    -2: '😡',
    -1: '🤨',
    0: '😐',
    1: '😉',
    2: '😊'
}


async def send_news(user_id, news_id, title, description, link, img_link):
    if db_manager.is_notify(user_id):
        score_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(smile, callback_data=f'score {score} {news_id}') for score, smile in scores.items()]]
        )
        await bot.send_photo(
            user_id, 
            img_link,
            caption=f'\n*{title}*\n\n{description}\n[Продолжить]({link})',
            parse_mode='markdown',
            reply_markup=score_keyboard
        )

async def pin_news():
    users_df = db_manager.db.select_query('select id from users')
    for user_id in users_df['id']:
        news_id, title, description, link, img_link = db_manager.get_fresh_news(user_id)
        if news_id == -1:
            continue
        await send_news(
            user_id=user_id,
            news_id=news_id,
            title=title,
            description=description,
            link=link,
            img_link=img_link
        )


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    user_id = message.from_user.id
    if not db_manager.is_exist(user_id):
        await message.answer("*Добро пожаловать в NewsTHXBot!* Я буду присылать тебе новости с разных ресурсов, чтобы ты не скучал 😊", parse_mode='markdown')
        await process_help_command(message)
        db_manager.db.insert_query(f"insert into users (id) values ('{user_id}')")
    else:
        await message.answer("Я тебя уже знаю 😊", parse_mode='markdown')



@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.answer('''*Вот, что я умею*
- /notify - выключить/включить меня 
        ''', parse_mode='markdown')


@dp.message_handler(commands=['notify'])
async def process_notify_command(message: types.Message):
    user_id = message.from_user.id
    if db_manager.is_notify(user_id):
        await message.answer('Теперь я не буду присылать тебе сообщения 😔')
        db_manager.set_notify(user_id, 0)
    else:
        await message.answer('Теперь я буду всегда рядом 😊')
        db_manager.set_notify(user_id, 1)
    



@dp.message_handler(commands=['news'])
async def process_news_command(message: types.Message):
    user_id = message.from_user.id
    if db_manager.is_admin(user_id):
        await pin_news()


@dp.callback_query_handler(lambda c: c.data.split()[0] == 'score')
async def process_callback_score(callback_query: types.CallbackQuery):
    score = int(callback_query.data.split()[1])
    news_id = int(callback_query.data.split()[2])
    user_id = callback_query.from_user.id
    await bot.answer_callback_query(callback_query.id)
    db_manager.db.insert_query(f"update suggested_news set score = {score} where news_id = {news_id} and user_id = '{user_id}'")
    db_manager.db.insert_query(f"update users set rated = rated + 1 where id = '{user_id}'")
    await bot.send_message(callback_query.from_user.id, f'Запомнил {scores[score]}')

@dp.message_handler(commands=['admin'])
async def echo_message(message: types.Message):
    user_id = message.from_user.id
    if db_manager.is_admin(user_id):
        await message.answer('ADMIN PANEL', parse_mode='markdown')
        amount_of_users = db_manager.db.select_query('select count(*) from users').iloc[0][0]
        await message.answer(f'amount: {amount_of_users}', parse_mode='markdown')


@dp.message_handler()
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, 'Я не понимаю 😔')

start = datetime.time(hour=9, minute=0, second=0)
stop = datetime.time(hour=23, minute=0, second=0)

async def periodic(sleep_for):
    while True:
        if stop > datetime.datetime.now().time() > start:
            await asyncio.sleep(sleep_for)
            await pin_news()

if __name__ == '__main__':

    # print(dp.loop)
    # print('fff')
    loop = asyncio.get_event_loop()
    loop.create_task(periodic(1))
    # dp.loop.create_task(periodic)
    # dp.loop.create_task(periodic(1))
    executor.start_polling(dp)
