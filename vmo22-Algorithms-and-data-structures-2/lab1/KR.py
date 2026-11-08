import sys
from math import log2


def karp_rabin_hash(S, m):
    if len(S) < m:
        raise ValueError("Длина строки S должна быть не меньше m")

    alphabet_size = 1114112  # Максимальное значение кода символа в Unicode (0x10FFFF)

    power = alphabet_size ** (m - 1)

    current_hash = 0
    for i in range(m):
        current_hash = current_hash * alphabet_size + ord(S[i])

    return current_hash


def karp_rabin_hash_with_slick(S, m, pos = 0, k = None, value = None):

    if len(S) < pos + m:
        raise ValueError("Длина строки S недостаточна для выбора подстроки")

    alphabet_size = 1114112  # Размер алфавита (Unicode)

    if pos == 0:
        current_hash = 0
        for i in range(m):
            current_hash = current_hash * alphabet_size + ord(S[i])
    else:
        if value is None:
            raise ValueError("Для pos > 0 требуется предыдущее значение хеша (value)")

        power = alphabet_size ** (m - 1)

        old_char = ord(S[pos - 1])
        new_char = ord(S[pos + m - 1])
        current_hash = (value - old_char * power) * alphabet_size + new_char

    if k is not None:
        return current_hash % k
    return current_hash


def karp_rabin_search(text: str, pattern: str) -> list[int]:
    n = len(text)
    m = len(pattern)
    if m == 0 or n < m:
        return []

    pattern_hash = karp_rabin_hash(pattern, m)
    window_hash = karp_rabin_hash(text, m)

    p = 1114112
    power = p ** (m - 1)

    matches = []

    if window_hash == pattern_hash and text[:m] == pattern:
        matches.append(0)

    for i in range(1, n - m + 1):
        old_char = ord(text[i - 1])
        new_char = ord(text[i + m - 1])
        window_hash = (window_hash - old_char * power) * p + new_char

        if window_hash == pattern_hash and text[i:i + m] == pattern:
            matches.append(i)

    return matches


if __name__ == "__main__":
    S = "abracadabra"
    m = 3
    print(f"Хеш первых {m} символов строки '{S}': {karp_rabin_hash(S, m)}")

    k = 1000

    hash1 = karp_rabin_hash_with_slick(S, m, pos=0, k=k)
    print(f"Хеш подстроки '{S[0:3]}': {hash1}")

    hash2 = karp_rabin_hash_with_slick(S, m, pos=1, k=k, value=hash1)
    print(f"Хеш подстроки '{S[1:4]}': {hash2}")

    text = "abracadabra"
    pattern = "cad"
    print(f"Поиск '{pattern}' в '{text}': {karp_rabin_search(text, pattern)}")

