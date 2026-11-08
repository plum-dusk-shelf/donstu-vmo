import random


def generate_matrix(tasks, processors, min_complexity, max_complexity):
    """
    Генерирует случайную матрицу.

    Строки    — задачи.
    Столбцы   — процессоры.
    Элемент    — сложность выполнения задачи
                 на соответствующем процессоре.
    """

    matrix = []

    for _ in range(tasks):
        row = []

        for _ in range(processors):
            value = random.randint(
                min_complexity,
                max_complexity
            )

            row.append(value)

        matrix.append(row)

    return matrix


def print_matrix(matrix):
    """Вывод матрицы."""

    for i, row in enumerate(matrix):
        print(
            f"Задача {i + 1}: "
            f"{row}   сумма = {sum(row)}"
        )


def sort_matrix(matrix, sort_type):
    """
    Возвращает копию матрицы в нужном порядке.

    original — без сортировки
    asc      — по возрастанию сумм строк
    desc     — по убыванию сумм строк
    """

    matrix = [row[:] for row in matrix]

    if sort_type == "original":
        return matrix

    if sort_type == "asc":
        matrix.sort(key=sum)
        return matrix

    if sort_type == "desc":
        matrix.sort(key=sum, reverse=True)
        return matrix

    raise ValueError("Неизвестный тип сортировки")


def plotnikov_zverev(matrix, show_steps=True):
    """
    Алгоритм Плотникова-Зверева.

    Первый шаг:
        из первой строки выбирается минимальный элемент.
        Индекс элемента определяет процессор.

    Последующие шаги:
        для каждой следующей строки рассматриваются
        все её элементы.

        Для каждого элемента рассчитывается,
        какая нагрузка получится у соответствующего
        процессора после назначения задачи.

        Выбирается минимальная получившаяся нагрузка.

    Возвращает:
        loads — итоговые нагрузки процессоров
        cmax  — максимальную нагрузку
    """

    processors = len(matrix[0])

    # Текущая суммарная нагрузка процессоров
    loads = [0] * processors

    if show_steps:
        print()
        print("Начальные нагрузки:")
        print(loads)

    # ==================================================
    # ПЕРВАЯ СТРОКА
    # ==================================================

    first_row = matrix[0]

    min_value = min(first_row)
    processor = first_row.index(min_value)

    loads[processor] = min_value

    if show_steps:
        print()
        print("=" * 70)
        print("ШАГ 1 — первая строка")
        print("=" * 70)

        print(f"Строка: {first_row}")

        print(
            f"Минимальный элемент: "
            f"{min_value}"
        )

        print(
            f"Выбран процессор: "
            f"P{processor + 1}"
        )

        print(
            f"Нагрузка P{processor + 1}: "
            f"{min_value}"
        )

        print(
            f"Текущие нагрузки: "
            f"{loads}"
        )

    # ==================================================
    # ОСТАЛЬНЫЕ СТРОКИ
    # ==================================================

    for row_number in range(1, len(matrix)):

        row = matrix[row_number]

        if show_steps:
            print()
            print("=" * 70)
            print(
                f"ШАГ {row_number + 1} — "
                f"следующая строка"
            )
            print("=" * 70)

            print(f"Строка: {row}")

            print(
                f"Текущие нагрузки: "
                f"{loads}"
            )

        # --------------------------------------------------
        # Рассматриваем каждый элемент строки
        # --------------------------------------------------

        candidates = []

        for processor in range(processors):

            task_complexity = row[processor]

            new_load = (
                loads[processor]
                + task_complexity
            )

            candidates.append(
                (
                    new_load,
                    processor,
                    task_complexity
                )
            )

            if show_steps:
                print(
                    f"P{processor + 1}: "
                    f"{loads[processor]} + "
                    f"{task_complexity} = "
                    f"{new_load}"
                )

        # --------------------------------------------------
        # Выбираем минимальную итоговую нагрузку
        # --------------------------------------------------

        best_load, processor, task_complexity = min(
            candidates,
            key=lambda x: (x[0], x[1])
        )

        # --------------------------------------------------
        # Назначаем задачу
        # --------------------------------------------------

        loads[processor] = best_load

        if show_steps:
            print()
            print(
                f"Выбираем P{processor + 1}: "
                f"{loads[processor] - task_complexity} + "
                f"{task_complexity} = "
                f"{loads[processor]}"
            )

            print(
                f"Текущие нагрузки: "
                f"{loads}"
            )

    # ==================================================
    # ЗАВЕРШЕНИЕ
    # ==================================================

    cmax = max(loads)

    if show_steps:
        print()
        print("=" * 70)
        print("ЗАВЕРШЕНИЕ")
        print("=" * 70)

        print(
            f"Итоговые нагрузки: "
            f"{loads}"
        )

        print(
            f"Cmax = max{tuple(loads)} = {cmax}"
        )

    return loads, cmax


def main():

    print("АЛГОРИТМ ПЛОТНИКОВА-ЗВЕРЕВА")
    print("=" * 70)

    # ==================================================
    # Ввод параметров
    # ==================================================

    tasks = int(
        input("Количество задач: ")
    )

    processors = int(
        input("Количество процессоров: ")
    )

    min_complexity = int(
        input("Минимальная сложность задачи: ")
    )

    max_complexity = int(
        input("Максимальная сложность задачи: ")
    )

    iterations = int(
        input("Количество итераций: ")
    )

    # ==================================================
    # Проверка
    # ==================================================

    if tasks <= 0:
        raise ValueError(
            "Количество задач должно быть больше 0"
        )

    if processors <= 0:
        raise ValueError(
            "Количество процессоров должно быть больше 0"
        )

    if min_complexity > max_complexity:
        raise ValueError(
            "Минимальная сложность не может "
            "быть больше максимальной"
        )

    if iterations <= 0:
        raise ValueError(
            "Количество итераций должно быть больше 0"
        )

    # ==================================================
    # Типы сортировки
    # ==================================================

    sort_types = [
        "original",
        "asc",
        "desc"
    ]

    names = {
        "original": "Без сортировки",
        "asc": "Возрастание сумм строк",
        "desc": "Убывание сумм строк"
    }

    # Количество побед
    wins = {
        "original": 0,
        "asc": 0,
        "desc": 0
    }

    # Количество ничьих
    ties = 0

    # Суммарный Cmax
    total_cmax = {
        "original": 0,
        "asc": 0,
        "desc": 0
    }

    # ==================================================
    # Эксперимент
    # ==================================================

    for iteration in range(1, iterations + 1):

        print()
        print()
        print("#" * 70)
        print(f"ИТЕРАЦИЯ {iteration}")
        print("#" * 70)

        # --------------------------------------------------
        # Генерируем одну матрицу
        # --------------------------------------------------

        matrix = generate_matrix(
            tasks,
            processors,
            min_complexity,
            max_complexity
        )

        print()
        print("СГЕНЕРИРОВАННАЯ МАТРИЦА")
        print("-" * 70)

        print_matrix(matrix)

        results = {}

        # ==================================================
        # Три варианта порядка строк
        # ==================================================

        for sort_type in sort_types:

            print()
            print()
            print("#" * 70)
            print(
                f"ВАРИАНТ: {names[sort_type]}"
            )
            print("#" * 70)

            # --------------------------------------------------
            # Сортируем строки
            # --------------------------------------------------

            sorted_matrix = sort_matrix(
                matrix,
                sort_type
            )

            print()
            print("Матрица для обработки:")
            print("-" * 70)

            print_matrix(sorted_matrix)

            # --------------------------------------------------
            # Запускаем алгоритм
            # --------------------------------------------------

            loads, cmax = plotnikov_zverev(
                sorted_matrix,
                show_steps=True
            )

            results[sort_type] = {
                "loads": loads,
                "cmax": cmax
            }

            total_cmax[sort_type] += cmax

        # ==================================================
        # Определяем победителя
        # ==================================================

        min_cmax = min(
            results[sort_type]["cmax"]
            for sort_type in sort_types
        )

        winners = [
            sort_type
            for sort_type in sort_types
            if results[sort_type]["cmax"] == min_cmax
        ]

        print()
        print()
        print("=" * 70)
        print("РЕЗУЛЬТАТ ИТЕРАЦИИ")
        print("=" * 70)

        for sort_type in sort_types:

            loads = results[sort_type]["loads"]
            cmax = results[sort_type]["cmax"]

            print(
                f"{names[sort_type]:<30}"
                f"Cmax = {cmax:<8}"
                f"Нагрузки = {loads}"
            )

        print()

        if len(winners) == 1:

            winner = winners[0]

            wins[winner] += 1

            print(
                f"Победитель: "
                f"{names[winner]}"
            )

        else:

            ties += 1

            print("Результат: НИЧЬЯ")

    # ==================================================
    # СВОДНАЯ ТАБЛИЦА
    # ==================================================

    print()
    print()
    print("=" * 80)
    print("СВОДНАЯ ТАБЛИЦА")
    print("=" * 80)

    print(
        f"{'Способ сортировки':<30}"
        f"{'Побед':>10}"
        f"{'Средний Cmax':>20}"
    )

    print("-" * 80)

    for sort_type in sort_types:

        average_cmax = (
            total_cmax[sort_type]
            / iterations
        )

        print(
            f"{names[sort_type]:<30}"
            f"{wins[sort_type]:>10}"
            f"{average_cmax:>20.2f}"
        )

    print("-" * 80)

    print(
        f"{'Ничьи':<30}"
        f"{ties:>10}"
    )

    print("=" * 80)

    # ==================================================
    # Параметры эксперимента
    # ==================================================

    print()
    print("Параметры эксперимента:")
    print(
        f"  Задач:              {tasks}"
    )
    print(
        f"  Процессоров:        {processors}"
    )
    print(
        f"  Сложность:          "
        f"[{min_complexity}, {max_complexity}]"
    )
    print(
        f"  Итераций:           {iterations}"
    )


if __name__ == "__main__":
    main()
