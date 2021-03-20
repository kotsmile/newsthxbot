from aiogram.utils.exceptions import MessageCantBeEdited,\
    MessageToEditNotFound, MessageNotModified, MessageToDeleteNotFound
from aiogram import Bot
import traceback

class InfoBar:

    def __init__(self, info_func, bot, set, get):
        self.info_func = info_func
        self.bot: Bot = bot
        self.get = get
        self.set = set
    
    async def update(self, *users_id):
        print('update')
        for user_id in users_id:
            message_id = self.get(key=user_id)

            info_str = self.info_func(user_id=user_id)
            try:
                await self.bot.edit_message_text(text=info_str, chat_id=user_id, message_id=message_id)
            except (MessageCantBeEdited, MessageToEditNotFound, MessageToDeleteNotFound):
                traceback.print_exc()
                await self.create(user_id)
                await self.update(user_id)
            except MessageNotModified:
                pass
    

    async def create(self, user_id):
        print('create')
        info_str = self.info_func(user_id=user_id)
        await self.bot.send_message(chat_id=user_id, text='Не удаляй это сообщение 👇')
        message = await self.bot.send_message(chat_id=user_id, text=info_str)
        self.set(key=user_id, value=message.message_id)
        await self.pin(user_id, message.message_id)


    async def pin(self, user_id, message_id):
        await self.bot.unpin_all_chat_messages(chat_id=user_id)
        await self.bot.pin_chat_message(chat_id=user_id, message_id=message_id)
        await self.bot.delete_message(chat_id=user_id, message_id=message_id + 1)