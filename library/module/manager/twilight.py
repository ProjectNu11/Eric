from graia.ariadne.message.element import At
from graia.ariadne.message.parser.twilight import (
    ArgumentMatch,
    ElementMatch,
    FullMatch,
    SpacePolicy,
    Twilight,
    UnionMatch,
    WildcardMatch,
)

from library.util.dispatcher import PrefixMatch

CHANGE_GROUP_MODULE_STATE_CH = Twilight(
    ElementMatch(At, optional=True),
    PrefixMatch(optional=True),
    UnionMatch("打开", "关闭") @ "action",
    FullMatch("模块"),
    WildcardMatch() @ "content",
)
CHANGE_GROUP_MODULE_STATE_EN = Twilight(
    PrefixMatch(),
    FullMatch("manager"),
    UnionMatch("enable", "disable") @ "action",
    WildcardMatch() @ "content",
)

REGISTER_REPOSITORY_EN = Twilight(
    ElementMatch(At, optional=True),
    PrefixMatch(),
    FullMatch("manager").space(SpacePolicy.FORCE),
    FullMatch("register"),
)

UPDATE_EN = Twilight(
    ElementMatch(At, optional=True),
    PrefixMatch(),
    FullMatch("manager").space(SpacePolicy.FORCE),
    FullMatch("update"),
)

UPGRADE_EN = Twilight(
    ElementMatch(At, optional=True),
    PrefixMatch(),
    FullMatch("manager").space(SpacePolicy.FORCE),
    FullMatch("upgrade"),
    ArgumentMatch("-y", action="store_true") @ "yes",
)

INSTALL_EN = Twilight(
    ElementMatch(At, optional=True),
    PrefixMatch(),
    FullMatch("manager").space(SpacePolicy.FORCE),
    FullMatch("install"),
    ArgumentMatch("-y", action="store_true") @ "yes",
    WildcardMatch() @ "content",
)

UNLOAD_EN = Twilight(
    ElementMatch(At, optional=True),
    PrefixMatch(),
    FullMatch("manager").space(SpacePolicy.FORCE),
    FullMatch("unload"),
    WildcardMatch() @ "content",
)
