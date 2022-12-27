import ast
import inspect
from dataclasses import Field
from typing import cast

from library.util.group_config.model import ModuleGroupConfig


def get_docs(cls: type[ModuleGroupConfig]):
    fields: dict[str, Field] = cls.__dataclass_fields__
    node: ast.ClassDef = cast(ast.ClassDef, ast.parse(inspect.getsource(cls)).body[0])
    for i, stmt in enumerate(node.body):
        name: str | None = None
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            name = stmt.target.id
        if name in fields:
            name: str
            if (
                i + 1 < len(node.body)
                and isinstance((doc_expr := node.body[i + 1]), ast.Expr)
                and isinstance((doc_const := doc_expr.value), ast.Constant)  # noqa
                and isinstance(doc_string := doc_const.value, str)  # noqa
            ):
                yield name, inspect.cleandoc(doc_string)
            else:
                yield name, ""
