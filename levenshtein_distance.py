"""
Levenshtein Distance also known as Edit Distance.
Difference between two strings in terms of operations (insertion, deletion, substitution) required to get second string from first string.
"""


def cache_calls(func):
    cache = {}

    def cached_call(*args, **kwargs):
        key = str(args) + str(**kwargs)
        if key in cache:
            return cache[key]
        # Reduce Space Complexity by limiting cache
        # if len(key) < 12:
        # Control Space Complexity by clearing cache
        # if sys.getsizeof(cache) >= 1024 * 1024 * 128: # 128 MB
        #     cache.clear()
        cache[key] = func(*args, **kwargs)
        return cache[key]

    return cached_call


@cache_calls
def get_levenshtein_distance(first_string: str, second_string: str):
    if first_string == "":
        return len(second_string)
    if second_string == "":
        return len(first_string)
    cost = 0 if first_string[-1] == second_string[-1] else 1

    distance = min(
        [
            get_levenshtein_distance(first_string[:-1], second_string) + 1,
            get_levenshtein_distance(first_string, second_string[:-1]) + 1,
            get_levenshtein_distance(first_string[:-1], second_string[:-1]) + cost,
        ]
    )

    return distance


def get_simple_distance(first_string: str, second_string: str):
    first_string_symbols = dict.fromkeys(first_string, 0)
    second_string_symbols = dict.fromkeys(second_string, 0)

    for symbol in first_string:
        first_string_symbols[symbol] += 1

    for symbol in second_string:
        second_string_symbols[symbol] += 1

    distance = 0
    for symbol, amount in first_string_symbols.items():
        if symbol in second_string_symbols:
            distance += abs(second_string_symbols[symbol] - amount)
        else:
            distance += amount

    for symbol, amount in second_string_symbols.items():
        if symbol not in first_string_symbols:
            distance += amount

    return distance


def is_similar(tested_item, similar_item, similarity_percent):
    min_allowed_distance = len(tested_item) - round(
        len(tested_item) * similarity_percent
    )

    if tested_item is similar_item:
        return True

    if get_simple_distance(tested_item, similar_item) >= min_allowed_distance:
        return False

    if get_levenshtein_distance(tested_item, similar_item) >= min_allowed_distance:
        return False

    return True


def get_similar_items(items, similarity_percent):
    similar_items = []

    for tested_item_index, tested_item in enumerate(items):
        for similar_item_index, similar_item in enumerate(items):
            if tested_item_index == similar_item_index:
                continue

            if is_similar(tested_item, similar_item, similarity_percent):
                similar_items.append((tested_item, similar_item))

    return similar_items
