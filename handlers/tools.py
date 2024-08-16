from logging import getLogger
from pyrogram.types import Message
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler

from tassistant.helpers import I18n
from tassistant.loader import ModuleLoader

_ = I18n()
logger = getLogger(__name__)


# Реализуем асинхронный каллбек
async def clear_history(client: Client, message: Message):
    # Получаем команды и аргументы
    command = message.command[0]
    args = message.command[1:]

    if len(args) < 1:
        return await message.edit(_.get_and_set("invalid_command_clear", {
            "prefix": ModuleLoader().command_prefix,
            "command": f"{command}"
        }))

    count = int(args[0]) + 1
    messages = []
    async for old_message in client.get_chat_history(message.chat.id, limit=count):
        messages.append(old_message.id)

    await client.delete_messages(message.chat.id, messages, revoke=True)

# реализуем хэндлер
clear_history_handler = MessageHandler(
    clear_history,
    filters.command("почистить", prefixes=ModuleLoader().command_prefix)
    & filters.me
)


async def get_help_module(client: Client, message: Message):
    command = message.command[0]
    try:
        module = message.command[1]
    except IndexError:
        return await message.edit(_.get_and_set("invalid_command_get_help_module", {
            "prefix": ModuleLoader().command_prefix,
            "command": f"{command}"
        }))

    await message.edit(_.get_and_set(f"{module}:help_module", {
        "prefix": ModuleLoader().command_prefix,
    }))

help_module_handler = MessageHandler(
    get_help_module,
    filters.command("помощь", prefixes=ModuleLoader().command_prefix)
    & filters.me
)

all_handlers = [
    clear_history_handler,
    help_module_handler
]
