if __name__ == "__main__":
    import kayaku

    kayaku.initialize({"{**}": "./config/{**}"})

    from graia.ariadne import Ariadne
    from library.service.stage import initialize as initialize

    initialize()
    kayaku.bootstrap()
    kayaku.save_all()

    Ariadne.launch_blocking()
