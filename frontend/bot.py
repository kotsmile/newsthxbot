from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import asyncio

from config import TOKEN, db_path
from db_manager import Database

# import random
import datetime


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
db = Database(db_path)

scores = {
    -2: '😡',
    -1: '🤨',
    0: '😐',
    1: '😉',
    2: '😊'
}




def is_notify(user_id):
    is_notify_df = db.select_query(f"select * from users where id = '{user_id}' and notify = 1")
    return not is_notify_df.empty

def is_exist(user_id):
    is_exist_df = db.select_query(f"select * from users where id = '{user_id}'")
    return not is_exist_df.empty

def is_admin(user_id):
    is_admin_df = db.select_query(f"select * from users where id = '{user_id}' and is_admin = 1")
    return not is_admin_df.empty

def set_notify(user_id, notify):
    db.insert_query(f"update users set notify = {notify} where id = '{user_id}'")

async def send_news(user_id, news_id, title, description, link, img_link):
    if is_notify(user_id):
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
    users_df = db.select_query('select id from users')
    for user_id in users_df['id']:
        news_for_user_q = f"select news_id from suggested_news  where user_id = '{user_id}' and seen = 0 order by timestamp desc limit 1 "
        news_for_user = db.select_query(news_for_user_q)
        if not news_for_user.empty:
            news_id = news_for_user.iloc[0][0]
            get_news_q = f"select id, title, description, link, img_link from news where id = {news_id}"
            news_data = db.select_query(get_news_q)
            if not news_data.empty:
                news_data = news_data.iloc[0]
                db.insert_query(f"update suggested_news set seen = 1 where user_id = '{user_id}' and news_id = {news_data['id']}")
                await send_news(
                    user_id=user_id,
                    news_id=news_data['id'],
                    title=news_data['title'],
                    description=news_data['description'],
                    link=news_data['link'],
                    img_link=news_data['img_link']
                )



@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    user_id = message.from_user.id
    if not is_exist(user_id):
        await message.answer("*Добро пожаловать в NewsTHXBot!* Я буду присылать тебе новости с разных ресурсов, чтобы ты не скучал 😊", parse_mode='markdown')
        await process_help_command(message)
        db.insert_query(f"insert into users (id) values ('{user_id}')")
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
    if is_notify(user_id):
        await message.answer('Теперь я не буду присылать тебе сообщения 😔')
        set_notify(user_id, 0)
    else:
        await message.answer('Теперь я буду всегда рядом 😊')
        set_notify(user_id, 1)
    



@dp.message_handler(commands=['news'])
async def process_news_command(message: types.Message):
    user_id = message.from_user.id
    if is_admin(user_id):
        await pin_news()


@dp.callback_query_handler(lambda c: c.data.split()[0] == 'score')
async def process_callback_score(callback_query: types.CallbackQuery):
    score = int(callback_query.data.split()[1])
    news_id = int(callback_query.data.split()[2])
    user_id = callback_query.from_user.id
    await bot.answer_callback_query(callback_query.id)
    db.insert_query(f"update suggested_news set score = {score} where news_id = {news_id} and user_id = '{user_id}'")
    db.insert_query(f"update users set rated = rated + 1 where id = '{user_id}'")
    await bot.send_message(callback_query.from_user.id, f'Запомнил {scores[score]}')

@dp.message_handler(commands=['admin'])
async def echo_message(message: types.Message):
    user_id = message.from_user.id
    if is_admin(user_id):
        await message.answer('ADMIN PANEL', parse_mode='markdown')
        amount_of_users = db.select_query('select count(*) from users').iloc[0][0]
        await message.answer(f'amount: {amount_of_users}', parse_mode='markdown')


@dp.message_handler()
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, 'Я не понимаю 😔')

start = datetime.time(hour=9, minute=0, second=0)
stop = datetime.time(hour=21, minute=0, second=0)

async def periodic(sleep_for):
    while True:
        if stop > datetime.datetime.now().time() > start:
            await asyncio.sleep(sleep_for)
            await pin_news()

if __name__ == '__main__':

    # print(dp.loop)
    loop = asyncio.get_event_loop()
    loop.create_task(periodic(1))
    # dp.loop.create_task(periodic)
    # dp.loop.create_task(periodic(1))
    executor.start_polling(dp)
