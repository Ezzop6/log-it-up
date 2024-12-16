
from pathlib import Path


def load_function_from_file(file_path: Path, function_name: str):
    import importlib.util

    module_name = file_path.stem
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if not spec:
        raise FileNotFoundError(f"File '{file_path}' not found.")
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise ImportError(f"Cannot load module from {file_path}")
    spec.loader.exec_module(module)

    if not hasattr(module, function_name):
        raise AttributeError(f"The file '{file_path}' must contain a function named '{function_name}'.")

    return getattr(module, function_name)
