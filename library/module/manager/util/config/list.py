from library.module.manager.util.module.search import search_module
from library.util.group_config.store import _store


def mgr_list_module_configs() -> str:
    modules = [search_module(m) for m in list(_store.models.keys())]
    modules = [m for m in modules if m is not None]
    if not modules:
        return "没有找到任何支持群组配置的模块"
    text = "支持群组配置的模块有："
    for m in modules:
        text += f"\n - {m.name} ({m.pack})"
    return text
