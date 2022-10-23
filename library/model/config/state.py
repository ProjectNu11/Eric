from dataclasses import field
from pathlib import Path

from kayaku import config, create


@config("library.state")
class ModuleState:
    loaded: dict[str, bool] = field(default_factory=dict)
    """已加载模块，不建议直接修改"""

    def load(self, module: str):
        self.loaded[module] = True

    def unload(self, module: str):
        self.loaded[module] = False

    def initialize(self):
        from library.model.config.path import PathConfig
        from library.util.module.get_all import iter_metadata

        _path_config: PathConfig = create(PathConfig)
        for path in [Path("library/module"), Path(_path_config.module)]:
            for module in iter_metadata(path):
                if module.pack in self.loaded:
                    continue
                self.load(module.pack)
