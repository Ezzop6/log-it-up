import hashlib


def get_persistent_hash(value: str) -> int:
    # TODO: Change this to string hash
    return int(hashlib.sha256(value.encode()).hexdigest(), 16)
