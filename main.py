import os
from pathlib import Path

import kayaku
from creart import it
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
    saya: Saya = it(Saya)
    with saya.module_context():
        saya.require("library.module.ping")
        saya.require("library.module.system_status")

    Ariadne.launch_blocking()
