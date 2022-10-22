import contextlib

from creart import it
from graia.ariadne.event.message import MessageEvent
from graia.broadcast import Decorator
from graia.saya import Saya
from graia.saya.builtins.broadcast import ListenerSchema


def inject(decorator: Decorator):
    saya: Saya = it(Saya)
    for _, channel in saya.channels.items():
        for cube in channel.content:
            if isinstance(cube.metaclass, ListenerSchema):
                if any(
                    not issubclass(event, MessageEvent)
                    for event in cube.metaclass.listening_events
                ):
                    continue
                decorators = cube.metaclass.decorators
                deco = next(
                    (
                        _deco
                        for _deco in decorators
                        if isinstance(_deco, type(decorator))
                    ),
                    None,
                )
                if deco is None:
                    decorators.append(decorator)
                    saya.broadcast.getListener(cube.content).decorators.append(
                        decorator
                    )


def uninject(decorator: Decorator):
    saya: Saya = it(Saya)
    for _, channel in saya.channels.items():
        for cube in channel.content:
            if isinstance(cube.metaclass, ListenerSchema):
                if any(
                    not issubclass(event, MessageEvent)
                    for event in cube.metaclass.listening_events
                ):
                    continue
                decorators = cube.metaclass.decorators
                deco = next(
                    (
                        _deco
                        for _deco in decorators
                        if isinstance(_deco, type(decorator))
                    ),
                    None,
                )
                if deco is not None:
                    with contextlib.suppress(ValueError):
                        decorators.remove(deco)
                        saya.broadcast.getListener(cube.content).decorators.remove(deco)
