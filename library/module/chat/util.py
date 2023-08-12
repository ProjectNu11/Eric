from asyncio import Lock
from pathlib import Path

from creart import it
from graia.saya import Channel
from sqlalchemy import select

from library.model.openai import ChatCompletion, ChatReturn
from library.util.chat import ChatSession
from library.util.module import Modules
from library.util.orm import orm
from library.util.orm.table import ChatCompletionTable

channel = Channel.current()


shared_instance = ChatCompletion(timeout=180)
shared_instance_lock = Lock()


async def generate_recap(instance: ChatCompletion) -> ChatReturn:
    async with shared_instance_lock:
        shared_instance.flush(system=True)
        shared_instance.system = instance.system[:]
        shared_instance.nodes = instance.nodes.copy()
        shared_instance.history = instance.history.copy()
        recap = await shared_instance.send(
            """# Workflow

Generate a recap from the current conversation in English.
The recap must contain every necessary information to continue the conversation.".
""",
            role="system",
        )
        shared_instance.flush(system=True)
        return recap


async def add_recap(session: ChatSession, identifier: str, instance: ChatCompletion):
    recap = await generate_recap(instance)
    await session.update_usage(recap["response_usage"])
    identifier_to_path(f"recap.{session.field}.{identifier}")


class PresetStore:
    presets: dict[str, str]

    def __init__(self):
        self.presets = {}

    def load(self):
        base = identifier_to_path("global.preset")
        if not base.is_dir():
            return
        for file in base.iterdir():
            self.presets[file.name] = file.read_text(encoding="utf-8")


async def get_user(user: int) -> tuple[int, int]:
    return await orm.first(
        select(ChatCompletionTable.usage, ChatCompletionTable.total_tokens).where(
            ChatCompletionTable.field == user  # noqa
        )
    )


def identifier_to_path(identifier: str) -> Path:
    return Path(it(Modules).get(channel.module).data_path, *identifier.split("."))


def get_text(identifier: str, fallback: str = "") -> str:
    file = identifier_to_path(identifier)
    return file.read_text(encoding="utf-8") if file.is_file() else fallback


def get_memory(user: int, identifier: str, fallback: str = "") -> str:
    return get_text(f"memory.{user}.{identifier}", fallback)


def get_recap(user: int, identifier: str, fallback: str = "") -> str:
    return get_text(f"recap.{user}.{identifier}", fallback)


async def initialize_user(user: int, name: str):
    await orm.insert_or_update(
        ChatCompletionTable,
        [ChatCompletionTable.field == user],
        field=user,
        system_prompt=get_text("global.default").format(
            name=repr(name)[1:-1], memory=get_memory(user, "default")
        ),
    )


class TriggerStore:
    every_token: dict[int, str]

    def __init__(self):
        self.every_token = {}
        self.load_every_token()

    def load_every_token(self):
        base = identifier_to_path("global.triggers.every_token")
        if not base.is_dir():
            return
        for file in base.iterdir():
            self.every_token[int(file.name)] = file.read_text(encoding="utf-8")

    def check(self, before: int, after: int) -> list[str]:
        return [
            data.format(token=after)
            for token, data in self.every_token.items()
            if (after // token) > (before // token)
        ]


presets = PresetStore()
triggers = TriggerStore()
