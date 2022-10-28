from kayaku import create

from library.model.config.service.manager import ManagerConfig
from library.module.manager.util.remote.context import repositories


def parse_repo():
    mgr_cfg: ManagerConfig = create(ManagerConfig)
    repositories.set(sorted(list(set(mgr_cfg.parse_repo())), key=lambda r: r.__name__))
