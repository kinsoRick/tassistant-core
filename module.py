from logging import getLogger

from tassistant.loader import Module


_ = getLogger(__name__)

class CoreModule(Module):
    class Meta:
        name = "Core Module"
        description = "Core Module of Tassistant"

    def __init__(self, base_path):
        super().__init__(base_path)