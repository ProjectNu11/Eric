import os
from pathlib import Path

import kayaku
from graia.ariadne import Ariadne

if __name__ == "__main__":
    if Path.cwd() != Path(__file__).parent:
        os.chdir(Path(__file__).parent)

    kayaku.initialize({"{**}": "./config/{**}"})

    from library.service.stage import initialize

    initialize()
    kayaku.bootstrap()
    kayaku.save_all()

    Ariadne.launch_blocking()
