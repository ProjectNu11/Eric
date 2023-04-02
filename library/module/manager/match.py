from arclet.alconna import Alconna, AllParam, Arg, Args, Option, Subcommand, store_true
from graia.ariadne.message.parser.twilight import (
    ArgumentMatch,
    FullMatch,
    RegexMatch,
    SpacePolicy,
    UnionMatch,
    WildcardMatch,
)
from kayaku import create

from library.model.config import FunctionConfig

_FUNC_CONFIG: FunctionConfig = create(FunctionConfig)

SUBCOMMANDS: dict[str, str] = {
    "enable": "打开模块",
    "disable": "关闭模块",
    "register": "注册模块仓库",
    "update": "更新模块仓库",
    "upgrade": "更新模块",
    "install": "安装模块",
    "unload": "卸载模块",
    "config": "配置模块",
}

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
    ArgumentMatch("-y", "--yes", action="store_true") @ "yes",
]

INSTALL_EN = [
    FullMatch("manager").space(SpacePolicy.FORCE),
    FullMatch("install").space(SpacePolicy.FORCE),
    ArgumentMatch("-y", "--yes", action="store_true") @ "yes",
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

MANAGER_ALC = Alconna(
    _FUNC_CONFIG.prefix,
    "manager",
    Subcommand(
        "enable",
        Arg("modules", AllParam),
    ),
    Subcommand(
        "disable",
        Arg("modules", AllParam),
    ),
    Subcommand("register"),
    Subcommand("update"),
    Subcommand(
        "upgrade",
        Option("--yes", alias=["-y"], action=store_true),
    ),
    Subcommand(
        "install",
        Option("--yes", alias=["-y"], action=store_true),
        Arg("modules", AllParam),
    ),
    Subcommand(
        "unload",
        Arg("modules", AllParam),
    ),
    Subcommand(
        "config",
        Subcommand(
            "get",
            Option("--group", alias=["-g"], args=Args["group", int]),
            Arg("content", AllParam),
        ),
        Subcommand(
            "set",
            Option("--group", alias=["-g"], args=Args["group", int]),
            Arg("content", AllParam),
        ),
        Subcommand("list"),
    ),
    Subcommand("stop"),
)
