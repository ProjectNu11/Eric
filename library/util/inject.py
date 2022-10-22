import contextlib

from creart import it
from graia.ariadne.event.message import MessageEvent
from graia.broadcast import Decorator
from graia.saya import Saya
from graia.saya.builtins.broadcast import ListenerSchema


def _process(_decorator: Decorator, _inject: bool):
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
                        if isinstance(_deco, type(_decorator))
                    ),
                    None,
                )
                if deco is None:
                    if _inject:
                        decorators.append(_decorator)
                        saya.broadcast.getListener(cube.content).decorators.append(
                            _decorator
                        )
                elif not _inject:
                    with contextlib.suppress(ValueError):
                        decorators.remove(deco)
                        saya.broadcast.getListener(cube.content).decorators.remove(deco)


def inject(decorator: Decorator):
    _process(decorator, True)


def uninject(decorator: Decorator):
    _process(decorator, False)
