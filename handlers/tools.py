from logging import getLogger
from pyrogram.types import Message
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler

from tassistant.helpers import I18n

_ = I18n('ru')
logger = getLogger(__name__)


async def clear_history(client: Client, message: Message):
    command = message.command[0]
    args = message.command[1:]

    if len(args) < 1:
        return await message.edit(_.get_and_set("invalid_command_clear", {
            "prefix": "/",
            "command": f"{command}"
        }))

    count = int(args[0]) + 1
    messages = []
    async for old_message in client.get_chat_history(message.chat.id, limit=count):
        messages.append(old_message.id)

    await client.delete_messages(message.chat.id, messages, revoke=True)


clear_history_handler = MessageHandler(
    clear_history,
    filters.command("почистить", prefixes="/")
    & filters.me
)

all_handlers = [
    clear_history_handler,
]
