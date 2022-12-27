from graia.ariadne.model import Group

from library.model.module import Module
from library.module.manager.util.config.docs import get_docs
from library.module.manager.util.config.util import _pre_check, get_module_config
from library.util.group_config.model import ModuleGroupConfig


def _get_msg(field: Group | int, module: Module, config: ModuleGroupConfig) -> str:
    text = f"{module.name} 配置 ({int(field)})"
    for k, doc in get_docs(type(config)):
        text += f"\n - {k}: {getattr(config, k)}"
        if doc:
            text += f"\n    {doc}"
    return text


def mgr_get_module_config(field: Group | int, mod: str) -> str:
    try:
        module = _pre_check(mod)
        config = get_module_config(field, module)
        return _get_msg(field, module, config)
    except AssertionError as e:
        return e.args[0]
