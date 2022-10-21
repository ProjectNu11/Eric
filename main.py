import os
from pathlib import Path

import kayaku
from creart import create
from graia.ariadne import Ariadne
from graia.saya import Saya

if __name__ == "__main__":
    if Path.cwd() != Path(__file__).parent:
        os.chdir(Path(__file__).parent)

    kayaku.initialize({"{**}": "./config/{**}"})

    from library.service.stage import initialize

    initialize()
    kayaku.bootstrap()
    kayaku.save_all()

    # TODO Placeholder for actual module requiring
    saya: Saya = create(Saya)
    with saya.module_context():
        saya.require("library.module.ping")

    Ariadne.launch_blocking()
