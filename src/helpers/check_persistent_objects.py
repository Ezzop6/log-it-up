def check_persistent_objects(obj, depth=0):
    indent = "  " * depth

    if isinstance(obj, (type(None), int, float, str, bool)):
        return True

    if hasattr(obj, '_p_jar'):
        print(f"{indent}✓ {type(obj)} is Persistent")
        return True

    if isinstance(obj, dict):
        print(f"{indent}Checking dictionary:")
        for k, v in obj.items():
            print(f"{indent}  Key: {k}")
            is_persistent = check_persistent_objects(v, depth + 1)
            if not is_persistent:
                print(f"{indent}  ✗ Non-persistent value found for key: {k}")
                return False
        return True

    if isinstance(obj, list):
        print(f"{indent}Checking list:")
        for i, item in enumerate(obj):
            is_persistent = check_persistent_objects(item, depth + 1)
            if not is_persistent:
                print(f"{indent}  ✗ Non-persistent item found at index {i}")
                return False
        return True

    if isinstance(obj, set):
        print(f"{indent}Checking set:")
        for item in obj:
            is_persistent = check_persistent_objects(item, depth + 1)
            if not is_persistent:
                print(f"{indent}  ✗ Non-persistent item found in set")
                return False
        return True

    print(f"{indent}✗ Non-persistent object: {type(obj)}")
    return False
