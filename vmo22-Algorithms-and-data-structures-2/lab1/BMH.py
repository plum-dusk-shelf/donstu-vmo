# алгоритм Бойера-Мура-Хорспулла

import random
import string

def main():

    def boyer_moore_horspool(text, pattern):
        n = len(text)
        m = len(pattern)
        if m == 0:
            return 0, 0

        # Создаем таблицу сдвигов
        shift_table = {}
        for i in range(m - 1):
            shift_table[pattern[i]] = m - i - 1

        operations = 0  # Счетчик операций
        i = 0
        while i <= n - m:
            j = m - 1
            while j >= 0 and text[i + j] == pattern[j]:
                j -= 1
                operations += 1  # Увеличиваем счетчик операций

            if j == -1:
                return i, operations  # Образец найден

            # Сдвигаем индекс i на величину из таблицы сдвигов
            shift = shift_table.get(text[i + m - 1], m)
            i += shift
            operations += 1  # Увеличиваем счетчик операций

        return -1, operations  # Образец не найден

    # Генерация случайного текста и образца
    def generate_random_string(length):
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

    # Проверка алгоритма
    def test_algorithm():
        text_length = 1000
        pattern_length = 10
        text = generate_random_string(text_length)
        pattern = generate_random_string(pattern_length)

        # Проверка соответствия количества операций ожидаемой оценке
        expected_operations = text_length * pattern_length
        print(f"Ожидаемое количество операций: {expected_operations}")

        index, operations = boyer_moore_horspool(text, pattern)
        if index != -1:
            print(f"Образец найден на позиции {index}.")
        else:
            print("Образец не найден.")
        print(f"Количество операций: {operations}")

    # Запуск теста
    test_algorithm()


if __name__ == '__main__':
    main()
