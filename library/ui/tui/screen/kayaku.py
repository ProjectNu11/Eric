import dataclasses
from dataclasses import _MISSING_TYPE  # noqa
from typing import cast

import typing_extensions
from kayaku.schema_gen import ConfigModel
from rich.text import Text
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Footer, Header, Static
from typing_extensions import Self

from library.ui.tui.widget import Body, ContainerTitle, InputField, MutableInputField


class KayakuScreen(Screen):
    components: tuple[Widget, ...]

    def __init__(self, model: ConfigModel, *components: Widget):
        super().__init__()
        self._model = model
        self.components = components

    def compose(self) -> ComposeResult:
        yield from self.components

    @staticmethod
    def is_required_field(field: dataclasses.Field) -> bool:
        return isinstance(field.default, _MISSING_TYPE) and isinstance(
            field.default_factory, _MISSING_TYPE
        )

    @staticmethod
    def assemble_description(required: bool, docs: str, hint: str) -> Text:
        if not required and not docs:
            return Text(hint, style="bold green")
        require_prefix = ("*必填 ", "bold red") if required else ""
        return Text.assemble(
            require_prefix, docs, "\n\n", "@type: ", (hint, "bold green")
        )

    @classmethod
    def from_model(cls, model: type) -> Self:
        model = cast(ConfigModel, model)
        components: list[Widget] = [
            ContainerTitle(Static(model.__name__, classes="kayaku-model-name"))
        ]
        type_hints = typing_extensions.get_type_hints(model, include_extras=True)
        for field in dataclasses.fields(model):  # noqa
            typ = type_hints[field.name]
            hint = (
                f"{typ!r}"
                if (typ_origin := typing_extensions.get_origin(typ))
                else f"{typ.__name__}"
            )
            docs = field.metadata.get("description", "")
            desc = cls.assemble_description(cls.is_required_field(field), docs, hint)
            if field.default == "":
                default = "<未设置>"
            elif isinstance(field.default, _MISSING_TYPE):
                default = ""
            else:
                default = field.default
            input_field = MutableInputField if typ_origin == list else InputField
            components.append(
                input_field(model.__name__, f"{field.name}", str(default), desc)
            )
        # TODO Implement QuickAccess
        return cls(model, Header(), Body(*components), Footer())
