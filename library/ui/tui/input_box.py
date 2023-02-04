from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Container
from textual.demo import Notification
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Input, Static


class FrozenInput(Static):
    DEFAULT_CSS = """
    FrozenInput {
        background: $boost;
        color: $text;
        padding: 0 2;
        border: tall $background;
        width: 100%;
        height: 1;
        min-height: 1;
    }
    """


class InputPair(Container):
    DEFAULT_CSS = """
    InputPair {
        height: auto;
        layout: grid;
        grid-size: 2;
        grid-rows: 4;
        grid-columns: 12 1fr;
    }

    InputPair .label {
        padding: 1 2;
        text-align: right;
    }
    """


class InputField(Container):
    DEFAULT_CSS = """
    InputField {
        height: auto;
        margin: 0 2;
        padding: 1 2;
        background: $boost;
        border: wide $background;
    }

    InputField .description {
        margin: 1 0 0 0;
        text-align: center;
    }
    """

    data: str

    def __init__(
        self, classes: str, label: str, placeholder: str, description: str | Text = None
    ):
        super().__init__(classes=classes)
        self._field_label = label
        self._field_placeholder = placeholder
        self._field_description = description

    def compose(self) -> ComposeResult:
        container = [
            InputPair(
                Static(self._field_label, classes="label"),
                Input(placeholder=self._field_placeholder),
            )
        ]
        if self._field_description:
            container.append(Static(self._field_description, classes="description"))
        yield from container

    def on_input_changed(self, message: Input.Changed) -> None:
        self.data = message.value


class MutableInputPair(Container):
    DEFAULT_CSS = """
    MutableInputPair {
        height: auto;
        layout: grid;
        grid-size: 3;
        grid-rows: 4;
        grid-columns: 12 1fr 5;
    }

    MutableInputPair .label {
        padding: 1 2;
        text-align: right;
    }
    """


class MutableInputField(Container):
    DEFAULT_CSS = """
    MutableInputField {
        height: auto;
        margin: 0 2;
        padding: 1 2;
        background: $boost;
        border: wide $background;
    }

    MutableInputField .description {
        margin: 1 0 0 0;
        text-align: center;
    }
    """

    data: list[str]
    _widgets: reactive[dict[str, Widget]] = reactive({}, layout=True)
    _input: str

    @property
    def button_id_prefix(self):
        return f"{self._field_classes}"

    def __init__(
        self, classes: str, label: str, placeholder: str, description: str | Text = None
    ):
        super().__init__(classes=classes)
        self._field_classes = classes
        self._field_label = label
        self._field_placeholder = placeholder
        self._field_description = description
        self.data = []
        self._input = ""

    def compose(self) -> ComposeResult:
        container = [
            MutableInputPair(
                Static(self._field_label, classes="label"),
                Input(
                    placeholder=self._field_placeholder,
                    classes=f"{self.button_id_prefix}_input",
                ),
                Button("+", id=f"{self.button_id_prefix}_add", variant="primary"),
            )
        ]
        if self._field_description:
            container.append(Static(self._field_description, classes="description"))
        yield from container

    def on_input_changed(self, message: Input.Changed) -> None:
        self._input = message.value

    def on_button_pressed(self, event: Button.Pressed):
        if not event.button.id or not event.button.id.startswith(self.button_id_prefix):
            return
        if event.button.id.startswith(f"{self.button_id_prefix}_remove"):
            index = event.button.id.split("_")[-1]
            if index in self._widgets:
                self._widgets[index].remove()
                del self._widgets[index]
            return
        if not self._input:
            self.screen.mount(Notification("输入不能为空"))
            return
        index = len(self.data) + 1
        self.mount(
            pair := MutableInputPair(
                Static("", classes="label"),
                FrozenInput(self._input),
                Button(
                    "-", id=f"{self.button_id_prefix}_remove_{index}", variant="error"
                ),
                classes=f"{self._field_classes}_data_{index} _margin-top",
            )
        )
        self.data.append(self._input)
        self._widgets[str(index)] = pair
        self._input = ""
        box = self.query_one(f".{self.button_id_prefix}_input")
        box.value = ""
        return
