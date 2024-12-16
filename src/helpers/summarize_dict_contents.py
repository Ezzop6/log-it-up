def summarize_dict_contents(dict) -> str:
    keys_count = len(dict.keys())
    item_count = sum([len(i) for i in [i for i in dict.values()]])
    return f"Total keys: {keys_count}, Total items: {item_count}"
