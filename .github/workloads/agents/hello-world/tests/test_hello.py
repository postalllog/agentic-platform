import importlib.util
from pathlib import Path


def test_hello_world():
    path = Path(__file__).resolve().parents[1] / 'main.py'
    source = path.read_text()
    # Read function and test with runtime dependency stub so unit test does not need AWS SDK
    import ast
    tree = ast.parse(source)
    method = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'hello')
    mod = ast.Module(body=[method], type_ignores=[])
    namespace = {}
    exec(compile(mod, str(path), 'exec'), namespace)
    assert namespace['hello']({'name': 'Postalllog'}) == {'message': 'Hello, Postalllog!'}
    assert namespace['hello']({}) == {'message': 'Hello, world!'}
