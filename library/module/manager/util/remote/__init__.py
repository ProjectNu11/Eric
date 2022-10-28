from contextlib import suppress
from json import JSONDecodeError

from graia.saya import Channel
from pydantic import ValidationError

from library.module.manager.model.module import RemoteModule
from library.module.manager.util.remote.context import remote_modules

channel = Channel.current()


def initialize():
    try:
        modules: list[RemoteModule] = []
        with open("modules.json") as file:
            modules = RemoteModule.parse_file(file)
    except (FileNotFoundError, ValidationError, JSONDecodeError):
        pass
