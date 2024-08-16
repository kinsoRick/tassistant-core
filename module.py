from logging import getLogger

from tassistant_bot.loader import Module

logger = getLogger(__name__)


class CoreModule(Module):
    class Meta:
        name = "Core Module"
        description = "Core Module of Tassistant"
        module_name = "tassistant-core"

    def __init__(self, base_path):
        super().__init__(base_path)
