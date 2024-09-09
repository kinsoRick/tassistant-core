from logging import getLogger
from pyrogram.types import Message
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler

from tassistant_bot.i18n import I18n
from tassistant_bot.loader import ModuleLoader

_ = I18n().create_module_get("tassistant-core")
get_i18n = I18n().get
logger = getLogger(__name__)


async def clear_history(client: Client, message: Message):
    command = message.command[0]
    args = message.command[1:]

    if len(args) < 1:
        return await message.edit(_("invalid_command_clear", {
            "prefix": ModuleLoader().command_prefix,
            "command": f"{command}"
        }))

    count = int(args[0]) + 1
    messages = []
    async for old_message in client.get_chat_history(message.chat.id, limit=count):
        messages.append(old_message.id)

    await client.delete_messages(message.chat.id, messages, revoke=True)

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
        return await message.edit(get_i18n("invalid_command_get_help_module", {
            "prefix": ModuleLoader().command_prefix,
            "command": f"{command}"
        }))

    await message.edit(get_i18n(f"{module}:help_module", {
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
