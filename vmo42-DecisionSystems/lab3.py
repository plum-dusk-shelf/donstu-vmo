import random


def print_matrix(assignment, times, N, title=""):
    """Вывод матрицы распределения заданий и загрузок процессоров."""
    if title:
        print(f"\n{title}")
    print("-" * 70)
    loads = []
    for j in range(N):
        tasks = assignment[j]
        load = sum(times[i] for i in tasks)
        loads.append(load)
        task_str = ", ".join(f"t{i+1}({times[i]})" for i in tasks) if tasks else "-"
        print(f"  P{j+1}: {task_str:<50} | load = {load}")
    print(f"  {'Max load:':<53} {max(loads)}")
    print("-" * 70)
    return loads


def kron_refinement(assignment, times, N, verbose=True):
    """
    Второй этап алгоритма Крона — уточнение распределения.
    Обмен заданиями между наиболее и наименее загруженными процессорами.
    На каждом шаге выводится текущая матрица распределения.
    """
    step = 0

    # Показываем матрицу перед началом уточнения
    if verbose:
        print_matrix(assignment, times, N,
                     f"ШАГ {step} (начальное состояние перед уточнением):")

    while True:
        loads = [sum(times[i] for i in assignment[j]) for j in range(N)]
        max_load = max(loads)
        min_load = min(loads)
        max_proc = loads.index(max_load)
        min_proc = loads.index(min_load)

        delta = max_load - min_load

        if delta == 0:
            if verbose:
                print(f"  Все процессоры сбалансированы (Δ=0). Останов.")
            break

        if verbose:
            print(f"\n  Анализ: Max = P{max_proc+1} (загрузка={max_load}), "
                  f"Min = P{min_proc+1} (загрузка={min_load}), Δ = {delta}")

        found = False
        for i in list(assignment[max_proc]):
            for j in list(assignment[min_proc]):
                if times[i] > times[j] and times[i] - times[j] < delta:
                    # Обмен заданиями
                    assignment[max_proc].remove(i)
                    assignment[min_proc].remove(j)
                    assignment[max_proc].append(j)
                    assignment[min_proc].append(i)
                    found = True
                    step += 1
                    if verbose:
                        print(f"  Обмен: t{i+1}({times[i]}) с P{max_proc+1} "
                              f"<-> t{j+1}({times[j]}) с P{min_proc+1}")
                        print_matrix(assignment, times, N,
                                     f"ШАГ {step} (после обмена):")
                    break
            if found:
                break

        if not found:
            if verbose:
                print(f"  Улучшающий обмен не найден. Алгоритм завершён.")
                print_matrix(assignment, times, N,
                             f"ШАГ {step} (финальное состояние — улучшений нет):")
            break

    return assignment

def format_task_list(task_indices, times, max_width=60, indent="      "):
    """
    Форматирует список заданий в несколько строк для читаемого вывода.
    Каждому заданию предшествует его порядковый номер в очереди.
    """
    items = [f"[{k+1}] t{i+1}({times[i]})" for k, i in enumerate(task_indices)]
    lines = []
    current = ""
    for item in items:
        candidate = f"{current}  {item}" if current else item
        if current and len(indent) + len(candidate) > max_width:
            lines.append(current)
            current = item
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def initial_random(times, N):
    """Случайное начальное распределение (классический 1-й этап Крона)."""
    M = len(times)
    assignment = [[] for _ in range(N)]
    for i in range(M):
        proc = random.randint(0, N - 1)
        assignment[proc].append(i)
        print_matrix(assignment, times, N,
                     f"  [Случайный] Назначение t{i+1}({times[i]}) -> P{proc+1}:")
    return assignment


def initial_cpm_ascending(times, N):
    """Критический путь по возрастанию."""
    M = len(times)
    assignment = [[] for _ in range(N)]
    sorted_indices = sorted(range(M), key=lambda i: times[i])

    print(f"  [Крит. путь ↑] Отсортированные задания по возрастанию:")
    for line in format_task_list(sorted_indices, times):
        print(line)

    loads = [0] * N
    for i in sorted_indices:
        min_proc = loads.index(min(loads))
        assignment[min_proc].append(i)
        loads[min_proc] += times[i]
        print_matrix(assignment, times, N,
                     f"  [Крит. путь ↑] Назначение t{i+1}({times[i]}) -> P{min_proc+1}:")
    return assignment


def initial_cpm_descending(times, N):
    """Критический путь по убыванию (LPT-эвристика)."""
    M = len(times)
    assignment = [[] for _ in range(N)]
    sorted_indices = sorted(range(M), key=lambda i: times[i], reverse=True)

    print(f"  [Крит. путь ↓] Отсортированные задания по убыванию:")
    for line in format_task_list(sorted_indices, times):
        print(line)

    loads = [0] * N
    for i in sorted_indices:
        min_proc = loads.index(min(loads))
        assignment[min_proc].append(i)
        loads[min_proc] += times[i]
        print_matrix(assignment, times, N,
                     f"  [Крит. путь ↓] Назначение t{i+1}({times[i]}) -> P{min_proc+1}:")
    return assignment

def run_experiment(N, M, min_time, max_time, num_iterations):
    """Запуск сравнительного эксперимента с определением победителя."""
    methods = [
        ("Случайный порядок", initial_random),
        ("Крит. путь (возр.)", initial_cpm_ascending),
        ("Крит. путь (убыв.)", initial_cpm_descending),
    ]

    method_names = [name for name, _ in methods]
    wins = {name: 0 for name in method_names}
    draws_per_method = {name: 0 for name in method_names}
    total_draws = 0
    all_results = {name: [] for name in method_names}

    for iteration in range(1, num_iterations + 1):
        print(f"\n{'=' * 70}")
        print(f"ИТЕРАЦИЯ {iteration}")
        print(f"{'=' * 70}")

        # Генерация случайных времён выполнения заданий
        times = [random.randint(min_time, max_time) for _ in range(M)]
        print(f"\nВремена заданий: {times}")
        print(f"Суммарное время: {sum(times)}")
        print(f"Нижняя граница (сумма/N): {sum(times) / N:.2f}")

        iteration_loads = {}

        for method_name, init_func in methods:
            print(f"\n{'#' * 70}")
            print(f"Метод: {method_name}")
            print(f"{'#' * 70}")

            # Начальное распределение (с пошаговым отображением)
            print(f"\n--- Этап 1: начальное распределение ---")
            assignment = init_func(times, N)

            # Этап уточнения (с пошаговым отображением)
            print(f"\n--- Этап 2: уточнение ---")
            assignment = kron_refinement(assignment, times, N, verbose=True)

            # Итоговый результат
            loads = [sum(times[i] for i in assignment[j]) for j in range(N)]
            max_load = max(loads)
            iteration_loads[method_name] = max_load
            all_results[method_name].append(max_load)

            print(f"\n>>> Итоговая максимальная загрузка метода '{method_name}': {max_load}")

        # ---- Определение победителя итерации ----
        best_load = min(iteration_loads.values())
        winners = [name for name, load in iteration_loads.items() if load == best_load]

        print(f"\n{'~' * 70}")
        print(f"РЕЗУЛЬТАТ ИТЕРАЦИИ {iteration}:")
        for name in method_names:
            print(f"  {name}: {iteration_loads[name]}")
        if len(winners) == 1:
            print(f"  Победитель: {winners[0]} (загрузка {best_load})")
            wins[winners[0]] += 1
        else:
            print(f"  Ничья между: {', '.join(winners)} (загрузка {best_load})")
            total_draws += 1
            for name in winners:
                draws_per_method[name] += 1
        print(f"{'~' * 70}")

    # ---- Итоговая таблица ----
    print(f"\n{'=' * 70}")
    print("ИТОГОВАЯ ТАБЛИЦА")
    print(f"{'=' * 70}")
    header = f"{'Метод':<25} {'Победы':>8} {'Ничьи':>8} {'Ср. макс. загрузка':>20}"
    print(header)
    print("-" * 70)
    for name in method_names:
        avg = sum(all_results[name]) / len(all_results[name]) if all_results[name] else 0
        print(f"{name:<25} {wins[name]:>8} {draws_per_method[name]:>8} {avg:>20.2f}")
    print("-" * 70)
    print(f"Всего итераций: {num_iterations}")
    print(f"Итераций с ничьей: {total_draws}")
    print(f"Итераций с единственным победителем: {num_iterations - total_draws}")

import sys


class Tee:
    """Пишет данные одновременно в несколько потоков (консоль + файл)."""
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            s.write(data)

    def flush(self):
        for s in self.streams:
            s.flush()


def main():
    print("=" * 60)
    print("Сравнение модификаций алгоритма Крона")
    print("=" * 60)

    try:
        N = int(input("Введите количество процессоров (N): "))
        M = int(input("Введите количество заданий (M): "))
        min_time = int(input("Введите минимальную сложность задания: "))
        max_time = int(input("Введите максимальную сложность задания: "))
        num_iterations = int(input("Введите количество итераций: "))

        if N <= 0 or M <= 0 or min_time <= 0 or max_time <= 0 or num_iterations <= 0:
            print("Ошибка: все значения должны быть положительными целыми числами.")
            return
        if min_time > max_time:
            print("Ошибка: минимальная сложность не может превышать максимальную.")
            return

        # ---- Дублирование вывода: консоль + файл ----
        output_filename = "result.txt"
        original_stdout = sys.stdout

        with open(output_filename, "w", encoding="utf-8") as f:
            sys.stdout = Tee(original_stdout, f)
            try:
                run_experiment(N, M, min_time, max_time, num_iterations)
            finally:
                sys.stdout = original_stdout

        print(f"\nРезультаты сохранены в файл: {output_filename}")

    except ValueError:
        print("Ошибка: пожалуйста, введите корректные целые числа.")


if __name__ == "__main__":
    main()
