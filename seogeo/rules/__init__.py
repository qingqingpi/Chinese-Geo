"""import 即注册：导入 seogeo.rules 时触发所有规则模块自注册到全局 REGISTRY。

新增一条检查 = 在本包下写一个 @register 装饰的函数文件，并加进下面的 import。
"""
from seogeo.rules import (  # noqa: F401  （触发自注册）
    bytespider,
    content,
    discovery,
    domestic_bots,
    overseas_bots,
    rendering,
    structure,
    technical,
)
