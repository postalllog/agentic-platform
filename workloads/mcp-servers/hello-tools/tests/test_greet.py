import ast
from pathlib import Path


def test_greet():
    source = (Path(__file__).resolve().parents[1] / 'main.py').read_text()
    tree = ast.parse(source)
    method = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'greet')
    method.decorator_list = []
    namespace = {}
    exec(compile(ast.Module(body=[method], type_ignores=[]), 'mcp_greet', 'exec'), namespace)
    assert namespace['greet']('developer') == 'Hello, developer!'
    assert namespace['greet']() == 'Hello, world!'
