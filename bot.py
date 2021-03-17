from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.exceptions import BotBlocked, BadRequest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, user

import asyncio
import json
import datetime

from db_manager import Database
from config import creds_path, db_path, start_work, stop_work
from news import suggest_news_user, suggest_news, save_news


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
        except BotBlocked as e:
            print(user_id, 'blocked me') # add to table mb
        except BadRequest as e:
            print(news_id, 'bad img url')
        

async def pin_news_user(user_id):
    news = db.get_fresh_news(user_id)
    if news.empty:
        return
    await send_news(
        user_id=user_id,
        news_id=news['id'],
        title=news['title'],
        description=news['description'],
        link=news['link'],
        img_link=news['img_link']
    )

async def pin_news():
    users_df = db.get_users()
    for user_id in users_df['id']:
        await pin_news_user(user_id)


# async def check_user(user_id):
#     if not db.is_exist(user_id):
#         await bot.send_message(user_id, '''*Я тебя не знаю 😔*, давай познакомимся /start''', parse_mode='markdown')


help_msg = '''\t*Вот, что я умею*
- /help - помогу тебе
- /notify - выключить/включить меня 
- /news - пришлю новость специально для тебя'''

admin_help_msg = '''\t*Вот, что я умею*
- /help - помогу тебе
- /notify - выключить/включить меня 
- /news - пришлю новость специально для тебя
ADMIN
- /pin - пришлю всем свежую новость
- /allnews - пришлю новость всем
- /admin - сколько нас
- /remove - удалю все новые новости'''

# user commands

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

    user_id = message.from_user.id
    if db.is_admin(user_id):
        await message.answer(admin_help_msg, parse_mode='markdown')
    else:
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
    save_news()
    suggest_news_user(user_id)
    await pin_news_user(user_id)
    

# admin commands

@dp.message_handler(commands=['pin'])
async def process_all_news_command(message: types.Message):
    await process_start_command(message)
    user_id = message.from_user.id
    if db.is_admin(user_id):
        await pin_news()
        await message.answer('Send news to everybody')

@dp.message_handler(commands=['remove'])
async def process_remove_command(message: types.Message):
    await process_start_command(message)

    user_id = message.from_user.id
    if db.is_admin(user_id):
        db.set_all_news_seen()
        await message.answer('Set all news "seen"')

@dp.message_handler(commands=['allnews'])
async def process_news_command(message: types.Message):
    await process_start_command(message)
    user_id = message.from_user.id
    if db.is_admin(user_id):
        save_news()
        suggest_news()
        await pin_news()
        await message.answer('Suggest and send news')





@dp.message_handler(commands=['admin'])
async def echo_message(message: types.Message):
    await process_start_command(message)
    user_id = message.from_user.id
    if db.is_admin(user_id):
        await message.answer('ADMIN PANEL', parse_mode='markdown')
        amount_of_users = db.select_query('select count(*) from users').iloc[0][0]
        await message.answer(f'amount: {amount_of_users}', parse_mode='markdown')

# callbacks

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


# garbege

@dp.message_handler()
async def echo_message(message: types.Message):
    await process_start_command(message)
    await bot.send_message(message.from_user.id, 'Я не понимаю 😔')


async def periodic(sleep_for):
    while True:
        print('try to pin')
        if stop_work > datetime.datetime.now().time() > start_work:
            print('pinning')
            await pin_news()
        await asyncio.sleep(sleep_for)

if __name__ == '__main__':

    print('Create task')
    loop = asyncio.get_event_loop()
    loop.create_task(periodic(60))

    print('Start')
    executor.start_polling(dp)
