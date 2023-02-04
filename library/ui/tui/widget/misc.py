from textual.containers import Container


class Body(Container):
    DEFAULT_CSS = """
    Body {
        height: 100%;
        overflow-y: scroll;
        width: 100%;
        background: $surface;
    }
    """


class ContainerTitle(Container):
    DEFAULT_CSS = """
    ContainerTitle {
        margin: 1 0 0 0;
        height: auto;
        width: 100%;
    }
    """
