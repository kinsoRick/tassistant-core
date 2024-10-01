import asyncio
import re

from collections import Counter
from time import sleep
from logging import getLogger

from pyt2s.services import stream_elements
from pyrogram.types import Message
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.handlers import MessageHandler
from pyrogram import filters, Client

from tassistant_bot.i18n import I18n
from tassistant_bot.loader import ModuleLoader

_ = I18n('ru').create_module_get("tassistant-core")
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
        _("MESSAGES_PERCENT_CHAT", {
            "user": user,
            "percent": f"{float(count / messages_count * 100):.2f}"
        }) for user, count in people.items()
    ]

    msg_rows.append(
        f"\n{_('MESSAGES_TOTAL', {'count': str(messages_count)})}"
    )

    await client.send_message(chat, "\n".join(msg_rows), disable_notification=True)


percent_messages_handler = MessageHandler(
    percent_messages,
    filters.command("процент", prefixes=ModuleLoader().get_command_prefix())
    & filters.me
)


async def eminem(client: Client, message: Message):
    await message.delete()
    chat = message.chat.id
    messages = [
        "Uh, summa-lumma, dooma-lumma,", "you assumin' I'm a human", "What I gotta do", "to get it through", "to you",
        "I'm superhuman?", "Innovative", "and I'm made of rubber", "so that anything", "You say is ricochetin' off",
        "of me", "and it'll glue", "to you", "and I'm devastating", "more than ever", "demonstrating", "How to give",
        "a motherfuckin' audience",
        "a feeling like", "it's levitating", "Never fading", "and I know", "the haters are", "forever waiting",
        "For the day",
        "that they can say", "I fell off", "they'll be celebrating", "'Cause I know the way to get", "'em motivated",
        "I make elevating music",
        "you make elevator music"
    ]

    for message in messages:
        try:
            await client.send_message(chat, message, disable_notification=True)
            sleep(0.1)
        except FloodWait as e:
            sleep(e.x)
        except MessageNotModified as e:
            logger.warning(f"| Message not modified |")


eminem_message_handler = MessageHandler(
    eminem,
    filters.command("эминем", prefixes=ModuleLoader().get_command_prefix())
    & filters.me
)


async def tts(client: Client, message: Message):
    await message.delete()
    command = message.command[0]
    text = " ".join(message.command[1:])

    data = stream_elements.requestTTS(text, stream_elements.Voice.ru_RU_Wavenet_A.value)

    with open('output.ogg', '+wb') as file:
        file.write(data)

    await client.send_voice(message.chat.id, "output.ogg")


tts_handler = MessageHandler(
    tts,
    filters.command("tts", prefixes=ModuleLoader().get_command_prefix())
    & filters.me
)


async def typing(client: Client, message: Message):
    command = message.command[0]
    args = message.command[1:]

    if len(args) < 1:
        await message.edit(_("INVALID_COMMAND_TYPING", {
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

    await message.edit(_("SEARCH_CURSE_WORDS"))

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
    common_bad_words_history,
    tts_handler,
    eminem_message_handler
]
