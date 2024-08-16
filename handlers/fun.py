import asyncio
import re

from collections import Counter
from time import sleep
from logging import getLogger

from pyrogram.types import Message
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.handlers import MessageHandler
from pyrogram import filters, Client

from tassistant.helpers import I18n
from tassistant.loader import ModuleLoader

_ = I18n('ru')
logger = getLogger(__name__)

async def percent_messages(client: Client, message: Message):
    chat = message.chat.id
    people = Counter()

    await message.delete()

    messages_count = 0
    async for msg in client.get_chat_history(chat):
        messages_count += 1
        if msg.from_user and not msg.from_user.is_bot:
            people[msg.from_user.username] += 1

    msg_rows = [
        _.get_and_set("MESSAGES_PERCENT_CHAT", {
            "user": user,
            "percent": f"{float(count / messages_count * 100):.2f}"
        }) for user, count in people.items()
    ]

    msg_rows.append(
        f"\n{_.get_and_set('MESSAGES_TOTAL', {'count': str(messages_count)})}"
    )

    await client.send_message(chat, "\n".join(msg_rows), disable_notification=True)


percent_messages_handler = MessageHandler(
    percent_messages,
    filters.command("процент", prefixes=ModuleLoader().get_command_prefix())
    & filters.me
)


async def typing(client: Client, message: Message):
    command = message.command[0]
    args = message.command[1:]

    if len(args) < 1:
        await message.edit(_.get_and_set("INVALID_COMMAND_TYPING", {
            "prefix": ModuleLoader().command_prefix,
            "command": command
        }))
        await asyncio.sleep(10)
        return await message.delete()

    orig_text = " ".join(args)
    text = orig_text
    tbp = ""
    typing_symbol = "▒"

    while tbp != orig_text:
        try:
            await message.edit(tbp + typing_symbol)
            sleep(0.1)

            tbp = tbp + text[0]
            text = text[1:]

            await message.edit(tbp)
            sleep(0.1)

        except FloodWait as e:
            sleep(e.x)
        except MessageNotModified as e:
            logger.warning(f"| Message not modified |")


typing_handler = MessageHandler(
    typing,
    filters.command("напечатать", prefixes=ModuleLoader().command_prefix)
    & filters.me
)


async def common_bad_words(client: Client, message: Message):
    command = message.command[0]

    messages = {

    }
    regex_te = ("(?iux)(?<![а-яё])(?:(?:(?:у|[нз]а|(?:хитро|не)?вз?[ыьъ]|с[ьъ]|(?:и|ра)[зс]ъ?|(?:о[тб]|п[оа]д)[ьъ]?|("
                "?:\S(?=[а-яё]))+?[оаеи-])-?)?(?:[её](?:б(?!о[рй]|рач)|п[уа](?:ц|тс))|и[пб][ае][тцд][ьъ]).*?|(?:(?:н["
                "иеа]|ра[зс]|[зд]?[ао](?:т|дн[оа])?|с(?:м[еи])?|а[пб]ч)-?)?ху(?:[яйиеёю]|л+и(?!ган)).*?|бл(?:["
                "эя]|еа?)(?:[дт][ьъ]?)?|\S*?(?:п(?:[иеё]зд|ид[аое]?р|ед(?:р(?!о)|[аое]р|ик)|охую)|бля(?:[дбц]|тс)|["
                "ое]ху[яйиеё]|хуйн).*?|(?:о[тб]?|про|на|вы)?м(?:анд(?:[ауеыи](?:л(?:и[сзщ])?[ауеиы])?|ой|[ао]в.*?|юк("
                "?:ов|[ауи])?|е[нт]ь|ища)|уд(?:[яаиое].+?|е?н(?:[ьюия]|ей))|[ао]л[ао]ф[ьъ](?:[яиюе]|[еёо]й))|елд["
                "ауые].*?|ля[тд]ь|(?:[нз]а|по)х)(?![а-яё])")

    async for old_message in client.get_chat_history(message.chat.id):
        try:
            if old_message.text is None:
                continue

            username = old_message.from_user.username
            if username not in messages:
                messages[username] = []

            words = old_message.text.split(" ")
            words = [word for word in words if re.match(regex_te, word)]

            messages[username] += words
        except Exception as e:
            logger.error(e)

    answer = ""
    for username, words in messages.items():
        counter = Counter(words)
        formatted_counter = ", ".join([
            f"{word} - {count}" for word, count in counter.most_common(10)
        ])
        answer += f"@{username}: {formatted_counter}\n\n"

    await message.edit(answer)


common_bad_words_history = MessageHandler(
    common_bad_words,
    filters.command("мат", prefixes=ModuleLoader().command_prefix)
    & filters.me
)

all_handlers = [
    typing_handler,
    percent_messages_handler,
    common_bad_words_history
]