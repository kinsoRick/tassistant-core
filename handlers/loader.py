import asyncio
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from tassistant_bot.i18n import I18n
from tassistant_bot.loader import extract_repo_name, ModuleLoader


_ = I18n('ru').create_module_get("tassistant-core")


async def download_module_repo(client: Client, message: Message):
    loader = ModuleLoader()
    if len(message.command) < 2:
        await message.edit(
            _("INVALID_COMMAND_MODULE_DOWNLOAD", {
                "prefix": loader.command_prefix,
                "command": message.command[0],
            })
        )
        await asyncio.sleep(10)
        return await message.delete()

    repo_url = message.command[1]
    repo_name = extract_repo_name(repo_url)
    try:
        loader.download_module(repo_url, repo_name)
    except Exception as e:
        return await message.edit(_("MODULE_DOWNLOAD_ERROR", {
            "repo_name": repo_name,
        }))

    loader.load_modules(repo_name)

    await message.edit(f"{repo_name} | Loaded")

download_handler = MessageHandler(
    download_module_repo,
    filters.me
    & filters.command("скачать", ModuleLoader().command_prefix)
)

all_handlers = [
    download_handler,
]