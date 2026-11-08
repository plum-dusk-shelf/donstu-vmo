import random
import string


def main():

    def linear_search(text, pattern):
        n = len(text)
        m = len(pattern)
        operations = 0  # Счетчик основных операций

        for i in range(n - m + 1):
            j = 0
            while j < m:
                operations += 1  # Увеличиваем счетчик операций
                if text[i + j] != pattern[j]:
                    break
                j += 1
            if j == m:
                return i, operations  # Образец найден, возвращаем позицию и количество операций

        return -1, operations  # Образец не найден, возвращаем -1 и количество операций

    def generate_random_string(length):
        return ''.join(random.choice(string.ascii_letters) for _ in range(length))

    # Генерация случайного текста и образца
    text_length = 1000
    pattern_length = 10
    text = generate_random_string(text_length)
    pattern = generate_random_string(pattern_length)

    # Поиск образца в тексте
    position, operations = linear_search(text, pattern)

    if position != -1:
        print(f"Образец найден на позиции {position}.")
    else:
        print("Образец не найден в тексте.")

    print(f"Количество выполненных операций: {operations}")

    # Проверка соответствия количества операций ожидаемой оценке
    expected_operations = text_length * pattern_length
    print(f"Ожидаемое количество операций: {expected_operations}")

    if operations <= expected_operations:
        print("Количество операций соответствует ожидаемой оценке.")
    else:
        print("Количество операций превышает ожидаемую оценку.")


if __name__ == '__main__':
    main()
