from aiogram import Bot
from aiogram.utils.exceptions import MessageCantBeEdited,\
    MessageToEditNotFound, MessageNotModified, MessageToDeleteNotFound

class InfoBar:

    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def update(self, text: str, user_id, message_id):

        try:
            await self.bot.edit_message_text(text=text, chat_id=user_id, message_id=message_id)
        except (MessageCantBeEdited, MessageToEditNotFound, MessageToDeleteNotFound):
            message_id = await self.create(user_id)
            message_id = await self.update(text, user_id, message_id)
        except MessageNotModified:
            pass

        return message_id
    

    async def create(self, user_id, text, not_delete_msg='Не удаляй это сообщение 👇'):

        await self.bot.send_message(chat_id=user_id, text=not_delete_msg)
        message = await self.bot.send_message(chat_id=user_id, text=text)
        await self.pin(user_id, message.message_id)

        return message.message_id


    async def pin(self, user_id, message_id):
        await self.bot.unpin_all_chat_messages(chat_id=user_id)
        await self.bot.pin_chat_message(chat_id=user_id, message_id=message_id)
        await self.bot.delete_message(chat_id=user_id, message_id=message_id + 1)