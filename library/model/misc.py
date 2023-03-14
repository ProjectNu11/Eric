class Hashable:
    def __repr__(self):
        return (
            f"<{self.__class__.__name__} "
            f"{' '.join(f'{k}={v}' for k, v in self.__dict__.items())}>"
        )

    def __hash__(self):
        return hash(self.__repr__())
