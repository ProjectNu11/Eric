import inspect
from typing import Callable, Coroutine

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button, Static


class MessageBox(Container):
    DEFAULT_CSS = """
    MessageBox {
        background: $boost;
        height: auto;
        max-width: 100;
        min-width: 40;
        border: wide $primary;
        padding: 1 2;
        margin: 1 2;
        box-sizing: border-box;
    }

    MessageBox Button {
        width: 100%;
        margin-top: 1;
    }
    """

    def __init__(
        self,
        static: Static,
        button: Button | None = None,
        button_callback: Callable[[], None | Coroutine] = None,
        classes: str = "",
    ):
        super().__init__(classes=classes)
        self._static = static
        self._button = button
        self._button_callback = button_callback

    def compose(self) -> ComposeResult:
        yield self._static
        if self._button:
            yield self._button

    async def on_button_pressed(self, event: Button.Pressed):
        if not self._button:
            return
        if event.button.id == self._button.id and self._button_callback:
            obj = self._button_callback()
            while inspect.isawaitable(obj):
                obj = await obj
