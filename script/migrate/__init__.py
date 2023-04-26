from pkgutil import walk_packages

from packaging.version import Version

from script.migrate.base import BaseMigrator


def _get_all_migrators() -> list[BaseMigrator]:
    migrators: list[BaseMigrator] = []

    for importer, modname, is_pkg in walk_packages(__path__):
        if modname == "base":
            continue
        module = importer.find_module(modname).load_module(modname)
        if hasattr(module, "Migrator"):
            migrators.append(module.Migrator())

    return sorted(migrators, key=lambda x: Version(x.dest_version))


def get_migrators(version: Version) -> list[BaseMigrator]:
    migrators = _get_all_migrators()
    return [
        migrator for migrator in migrators if version < Version(migrator.dest_version)
    ]


def need_migrate(version: Version) -> bool:
    return bool(get_migrators(version))


def run_migrators(version: Version):
    for migrator in get_migrators(version):
        migrator.log_and_run()
