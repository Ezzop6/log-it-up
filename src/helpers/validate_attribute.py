from typing import Any


def validate_attribute(obj: object, atribut: str, type: Any) -> Any:
    if hasattr(obj, atribut) and isinstance(getattr(obj, atribut), type):
        return getattr(obj, atribut)
    raise AttributeError(f"Object {obj} does not have attribute {atribut} of type {type}")
