import random
from math import inf

INF = inf


def generate_tasks(processors, task_count, min_time, max_time,
                   forbidden_probability, rng):
    """Матрица: строки — работы, столбцы — процессоры."""
    tasks = []
    for _ in range(task_count):
        row = [
            INF if rng.random() < forbidden_probability
            else rng.randint(min_time, max_time)
            for _ in range(processors)
        ]
        # У каждой работы должен быть хотя бы один допустимый процессор.
        if all(value == INF for value in row):
            row[rng.randrange(processors)] = rng.randint(min_time, max_time)
        tasks.append(row)
    return tasks


def task_weight(row):
    """Вес работы — сумма длительностей на доступных процессорах."""
    return sum(value for value in row if value != INF)

def sort_task_indexes(tasks, mode, rng):
    indexes = list(range(len(tasks)))

    if mode == "original":
        # 1. Исходный порядок строк, без сортировки.
        pass

    elif mode == "infinities":
        # 2. Больше бесконечностей — выше.
        indexes.sort(
            key=lambda i: sum(value == INF for value in tasks[i]),
            reverse=True
        )

    elif mode == "infinities_and_sum":
        # 3. Сначала больше бесконечностей,
        # затем большая сумма конечных элементов.
        indexes.sort(
            key=lambda i: (
                sum(value == INF for value in tasks[i]),
                task_weight(tasks[i])
            ),
            reverse=True
        )

    else:
        raise ValueError("Неизвестный способ сортировки")

    return indexes

def format_value(value):
    return "∞" if value == INF else str(value)


def print_matrix(tasks, title):
    print(f"\n{title}")
    if not tasks:
        print("(пустая матрица)")
        return
    width = max(4, max(len(format_value(x)) for row in tasks for x in row))
    print("Работа | " + " ".join(f"П{j + 1:>{width}}" for j in range(len(tasks[0]))))
    print("-" * (9 + (width + 3) * len(tasks[0])))
    for i, row in enumerate(tasks, 1):
        print(f"{i:>6} | " + " ".join(f"{format_value(x):>{width}}" for x in row))


def run_schedule(tasks, processors, order, show_steps=True):
    """Жадное назначение работ доступному процессору с минимальной загрузкой."""
    loads = [0] * processors
    schedule = []

    if show_steps:
        print("Начальная загрузка процессоров:", loads)

    for step, task_index in enumerate(order, 1):
        row = tasks[task_index]
        candidates = [p for p in range(processors) if row[p] != INF]
        if not candidates:
            raise ValueError(f"У работы {task_index + 1} нет доступного процессора")

        chosen = min(candidates, key=lambda p: (loads[p], p))
        start = loads[chosen]
        duration = row[chosen]
        finish = start + duration
        loads[chosen] = finish

        schedule.append((task_index, chosen, start, finish))

        if show_steps:
            print(
                f"Шаг {step}: работа {task_index + 1}, "
                f"длительности = [{', '.join(format_value(x) for x in row)}]"
            )
            print(
                f"  Назначена процессору {chosen + 1}: "
                f"{start} + {duration} = {finish}"
            )
            print("  Текущие загрузки:", loads)

    return max(loads, default=0), loads, schedule


def main():
    print("Лабораторная работа: сравнение порядка работ в теории расписаний")

    processors = int(input("Количество процессоров n: "))
    task_count = int(input("Количество работ m: "))
    min_time = int(input("Минимальная длительность работы: "))
    max_time = int(input("Максимальная длительность работы: "))
    forbidden_probability = float(
        input("Вероятность недоступности процессора (0..1, например 0.15): ")
    )
    iterations = int(input("Количество запусков алгоритма: "))
    seed_text = input("Seed генератора (Enter — случайный): ").strip()

    if processors < 1 or task_count < 1:
        raise ValueError("Количество процессоров и работ должно быть положительным.")
    if min_time < 1 or max_time < min_time:
        raise ValueError("Неверный диапазон длительностей.")
    if not 0 <= forbidden_probability < 1:
        raise ValueError("Вероятность должна быть в диапазоне [0, 1).")
    if iterations < 1:
        raise ValueError("Количество запусков должно быть положительным.")

    base_seed = int(seed_text) if seed_text else None
    modes = [
        ("Исходный порядок", "original"),
        ("По количеству бесконечностей", "infinities"),
        ("По количеству бесконечностей и сумме", "infinities_and_sum"),
    ]
    wins = {title: 0 for title, _ in modes}
    ties = 0

    for iteration in range(1, iterations + 1):
        print("\n" + "=" * 88)
        print(f"ИТЕРАЦИЯ {iteration} ИЗ {iterations}")
        print("=" * 88)

        # Для каждой итерации создаётся новая матрица, одинаковая для всех
        # трёх способов упорядочивания в рамках этой итерации.
        seed = None if base_seed is None else base_seed + iteration
        data_rng = random.Random(seed)
        tasks = generate_tasks(
            processors, task_count, min_time, max_time,
            forbidden_probability, data_rng
        )
        print_matrix(tasks, "Исходная матрица длительностей")

        results = []
        for title, mode in modes:
            print("\n" + "-" * 88)
            print(f"Вариант: {title}")
            sort_rng = random.Random(
                None if seed is None else seed + 10_000
            )
            order = sort_task_indexes(tasks, mode, sort_rng)
            ordered_tasks = [tasks[i] for i in order]

            print("Порядок исходных номеров работ:",
                  [i + 1 for i in order])
            print_matrix(ordered_tasks, "Матрица после сортировки")

            makespan, loads, schedule = run_schedule(
                tasks, processors, order, show_steps=True
            )
            print("Итоговая загрузка процессоров:", loads)
            print("Cmax =", makespan)

            results.append({
                "title": title,
                "makespan": makespan,
                "loads": loads,
                "order": order,
                "schedule": schedule,
            })

        best_value = min(result["makespan"] for result in results)
        winners = [
            result["title"] for result in results
            if result["makespan"] == best_value
        ]
        if len(winners) == 1:
            wins[winners[0]] += 1
            print(f"\nПобедитель итерации: {winners[0]} (Cmax = {best_value})")
        else:
            ties += 1
            print(
                f"\nНичья: {', '.join(winners)} "
                f"(Cmax = {best_value}); победа засчитана как ничья"
            )

    print("\n" + "=" * 88)
    print("ИТОГОВОЕ КОЛИЧЕСТВО ПОБЕД")
    print("=" * 88)
    for title, _ in modes:
        print(f"{title}: {wins[title]}")
    print("Количество ничьих:", ties)
    print("Всего итераций:", iterations)
    print(
        "\nПобедителем итерации считается единственный вариант с минимальным Cmax. "
        "Если несколько вариантов дают одинаковый минимум, это ничья и она "
        "не добавляется в счёт побед ни одному варианту."
    )


if __name__ == "__main__":
    main()
