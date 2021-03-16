from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.exceptions import BotBlocked
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, user

import asyncio
import json
import datetime

from db_manager import Database
from config import creds_path, db_path, start_work, stop_work


def load_json(path):
    with open(path, 'r') as file:
        return json.load(file)

TOKEN = load_json(creds_path)['TOKEN']
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
db = Database(db_path)

scores = {
    1: '😡',
    2: '🤨',
    3: '😐',
    4: '😉',
    5: '😊'
}




async def send_news(user_id, news_id, title, description, link, img_link, reply_keyboard=True):
    if db.is_notify(user_id):
        score_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(smile, callback_data=f'score {score} {news_id}') for score, smile in scores.items()]]
        )
        
        try:
            msg = await bot.send_photo(
                user_id, 
                img_link,
                caption=f'\n*{title}*\n\n{description}\n\n[продолжить]({link})',
                parse_mode='markdown',
                reply_markup=score_keyboard
            )
            # print(msg.)
        except BotBlocked as e:
            return


async def pin_news():
    users_df = db.get_users()
    for user_id in users_df['id']:
        news = db.get_fresh_news(user_id)
        if news.empty:
            continue
        await send_news(
            user_id=user_id,
            news_id=news['id'],
            title=news['title'],
            description=news['description'],
            link=news['link'],
            img_link=news['img_link']
        )

# async def check_user(user_id):
#     if not db.is_exist(user_id):
#         await bot.send_message(user_id, '''*Я тебя не знаю 😔*, давай познакомимся /start''', parse_mode='markdown')


help_msg = '''\t*Вот, что я умею*
- /notify - выключить/включить меня '''


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    user_id = message.from_user.id
    if not db.is_exist(user_id):
        print(f'New user!! {user_id}')
        await message.answer(f'*Добро пожаловать {message.from_user.first_name} в NewsTHXBot!*\nЯ буду присылать тебе новости с разных ресурсов, чтобы ты не скучал 😊', parse_mode='markdown')
        await message.answer(help_msg, parse_mode='markdown')
        db.add_user(
            user_id=user_id, 
            username=message.from_user.username, 
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )

@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await process_start_command(message)
    await message.answer(help_msg, parse_mode='markdown')


@dp.message_handler(commands=['notify'])
async def process_notify_command(message: types.Message):
    await process_start_command(message)
    user_id = message.from_user.id
    if db.is_notify(user_id):
        await message.answer('Теперь я не буду присылать тебе сообщения 😔')
        db.set_notify(user_id, 0)
    elif db.is_exist(user_id):
        await message.answer('Теперь я буду всегда рядом 😊')
        db.set_notify(user_id, 1)
    



@dp.message_handler(commands=['news'])
async def process_news_command(message: types.Message):
    await process_start_command(message)
    user_id = message.from_user.id
    if db.is_admin(user_id):
        print(message.from_user.username)
        print(message.from_user.first_name)
        print(message.from_user.last_name)
        await pin_news()


@dp.callback_query_handler(lambda c: c.data.split()[0] == 'score')
async def process_callback_score(callback_query: types.CallbackQuery):
    score = int(callback_query.data.split()[1])
    news_id = int(callback_query.data.split()[2])
    user_id = callback_query.from_user.id

    await bot.edit_message_reply_markup(user_id, callback_query.message.message_id)

    if not db.is_scored(user_id, news_id):
        print(callback_query.data)
    db.update_score(user_id, news_id, score)

    await bot.answer_callback_query(callback_query.id)

@dp.message_handler(commands=['admin'])
async def echo_message(message: types.Message):
    await process_start_command(message)
    user_id = message.from_user.id
    if db.is_admin(user_id):
        await message.answer('ADMIN PANEL', parse_mode='markdown')
        amount_of_users = db.select_query('select count(*) from users').iloc[0][0]
        await message.answer(f'amount: {amount_of_users}', parse_mode='markdown')


@dp.message_handler()
async def echo_message(message: types.Message):
    await process_start_command(message)
    await bot.send_message(message.from_user.id, 'Я не понимаю 😔')


async def periodic(sleep_for):
    while True:
        if stop_work > datetime.datetime.now().time() > start_work:
            await asyncio.sleep(sleep_for)
            await pin_news()

if __name__ == '__main__':

    print('Create task')
    loop = asyncio.get_event_loop()
    loop.create_task(periodic(60))

    print('Start')
    executor.start_polling(dp)
