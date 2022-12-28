from graia.ariadne.message.parser.twilight import (
    ArgumentMatch,
    FullMatch,
    RegexMatch,
    SpacePolicy,
    UnionMatch,
    WildcardMatch,
)

CHANGE_GROUP_MODULE_STATE_CH = [
    UnionMatch("打开", "关闭") @ "action",
    FullMatch("模块"),
    WildcardMatch() @ "content",
]
CHANGE_GROUP_MODULE_STATE_EN = [
    FullMatch("manager").space(SpacePolicy.FORCE),
    UnionMatch("enable", "disable").space(SpacePolicy.FORCE) @ "action",
    WildcardMatch() @ "content",
]

REGISTER_REPOSITORY_EN = [
    FullMatch("manager").space(SpacePolicy.FORCE),
    FullMatch("register"),
]

UPDATE_EN = [
    FullMatch("manager").space(SpacePolicy.FORCE),
    FullMatch("update"),
]

UPGRADE_EN = [
    FullMatch("manager").space(SpacePolicy.FORCE),
    FullMatch("upgrade"),
    ArgumentMatch("-y", action="store_true") @ "yes",
]

INSTALL_EN = [
    FullMatch("manager").space(SpacePolicy.FORCE),
    FullMatch("install").space(SpacePolicy.FORCE),
    ArgumentMatch("-y", action="store_true") @ "yes",
    WildcardMatch() @ "content",
]

UNLOAD_EN = [
    FullMatch("manager").space(SpacePolicy.FORCE),
    FullMatch("unload").space(SpacePolicy.FORCE),
    WildcardMatch() @ "content",
]

GET_CONFIG_EN = [
    FullMatch("manager").space(SpacePolicy.FORCE),
    FullMatch("config").space(SpacePolicy.FORCE),
    FullMatch("get").space(SpacePolicy.FORCE),
    ArgumentMatch("-g", "--group", type=int, optional=True) @ "group",
    WildcardMatch() @ "content",
]

UPDATE_CONFIG_EN = [
    FullMatch("manager").space(SpacePolicy.FORCE),
    FullMatch("config").space(SpacePolicy.FORCE),
    FullMatch("set").space(SpacePolicy.FORCE),
    ArgumentMatch("-g", "--group", type=int, optional=True) @ "group",
    RegexMatch(r"""(".+?"|'.+?'|[^ "']+)""").space(SpacePolicy.FORCE) @ "mod",
    RegexMatch(r"[a-zAZ_0-9]+") @ "key",
    FullMatch("="),
    RegexMatch(r"""(".+?"|'.+?'|[^ "']+)""") @ "value",
]

LIST_CONFIG_EN = [
    FullMatch("manager").space(SpacePolicy.FORCE),
    FullMatch("config").space(SpacePolicy.FORCE),
    FullMatch("list"),
]
