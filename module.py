from tassistant_bot.loader import Module
from tassistant_bot.helpers import I18n
from logging import getLogger
from pyrogram import Client

logger = getLogger(__name__)
_ = I18n().create_module_get("tassistant-core")


class CoreModule(Module):
    class Meta:
        name = "Core Module"
        description = "Core Module of Tassistant"
        module_name = "tassistant-core"

    def __init__(self, base_path):
        super().__init__(base_path)

    async def client_ready(self, client: Client) -> None:
        logger.debug(f"| {self.Meta.name} | overriding client ready")
        await super().client_ready(client)
        await client.send_message("me", _("WELCOME_MESSAGE"))
