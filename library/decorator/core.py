from creart import it
from graia.broadcast import Decorator, DecoratorInterface, ExecutionStop

from library.model.core import EricCore


class CoreInitCheck(Decorator):
    """核心初始化检查装饰器"""

    pre = True

    @staticmethod
    async def target(_: DecoratorInterface):
        core: EricCore = it(EricCore)
        if not core.initialized:
            raise ExecutionStop
