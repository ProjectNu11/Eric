from graia.ariadne.model import Group

from library.model.module import Module
from library.module.manager.util.config.docs import get_docs
from library.module.manager.util.module.search import search_module
from library.util.group_config import module_create
from library.util.group_config.model import ModuleGroupConfig
from library.util.group_config.store import _store


def _pre_check(mod: str) -> Module:
    assert (module := search_module(mod)), f"Module {mod} not found."
    return module


def get_module_config(field: Group | int, module: Module) -> ModuleGroupConfig:
    field: int = int(field)
    pack = module.pack
    assert pack in _store.models, f"Module {module.name} is not registered."
    cls = _store.models[pack]
    module_create(cls, field, flush=True)
    assert pack in _store.instances, f"Module {module.name} is not initialized."
    assert (
        field in _store.instances[pack]
    ), f"Module {module.name} is not initialized for {field}."
    return _store.instances[pack][field]


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
