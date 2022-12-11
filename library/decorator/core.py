from creart import it
from graia.broadcast import Decorator, DecoratorInterface, ExecutionStop

from library.model.core import EricCore


class CoreInitCheck(Decorator):
    pre = True

    @staticmethod
    async def target(_: DecoratorInterface):
        core: EricCore = it(EricCore)
        if not core.initialized:
            raise ExecutionStop()
