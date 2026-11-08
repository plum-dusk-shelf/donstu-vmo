import random
from statistics import mean


# ------------------------------------------------------------
# Вспомогательные функции
# ------------------------------------------------------------
def encode_chromosome(assignments, processor_count):
    chromosome = []

    for processor in assignments:
        value = processor * 64 + random.randint(0, 63)
        bits = format(value, '08b')
        chromosome.extend(int(bit) for bit in bits)

    return chromosome

def decode_chromosome(chromosome, processor_count):
    assignments = []

    for i in range(0, len(chromosome), 8):
        gene = chromosome[i:i + 8]
        value = int(''.join(map(str, gene)), 2)

        processor = min(value // 64, processor_count - 1)
        assignments.append(processor)

    return assignments

def print_individual(individual, times, processor_count, title):
    assignments = decode_chromosome(individual, processor_count)
    value = makespan(individual, times, processor_count)

    print(f"\n{title}")
    print("Хромосома:", " ".join(
        "".join(map(str, individual[i:i + 8]))
        for i in range(0, len(individual), 8)
    ))
    print(f"Распределение заданий: {assignments}")
    print(f"Целевая функция (makespan): {value}")

def print_population(population, times, processor_count, generation):
    print(f"\n{'=' * 60}")
    print(f"Поколение {generation}")
    print(f"{'=' * 60}")

    for i, individual in enumerate(population):
        value = makespan(individual, times, processor_count)
        assignments = decode_chromosome(individual, processor_count)

        print(f"\nОсобь {i + 1}")
        print(f"Хромосома: {''.join(map(str, individual))}")
        print(f"Распределение: {assignments}")
        print(f"Время выполнения: {value}")

def print_selection(
    parent_index,
    candidate_a,
    candidate_b,
    partner_index,
    fitness
):
    print("\n" + "-" * 60)
    print("ВЫБОР РОДИТЕЛЕЙ")
    print("-" * 60)

    print(f"Первый родитель: особь {parent_index + 1}")
    print(f"  Целевая функция: {fitness[parent_index]}")

    print("\nКандидаты на второго родителя:")

    print(
        f"  Особь {candidate_a + 1}: "
        f"makespan = {fitness[candidate_a]}"
    )

    print(
        f"  Особь {candidate_b + 1}: "
        f"makespan = {fitness[candidate_b]}"
    )

    print(f"\nПобедитель турнира: особь {partner_index + 1}")

def print_population(population, times, processor_count, generation):
    print("\n" + "=" * 68)
    print(f"ПОКОЛЕНИЕ {generation}")
    print("=" * 68)

    values = []

    for i, individual in enumerate(population):
        value = makespan(individual, times, processor_count)
        values.append(value)

        print_individual(
            individual,
            times,
            processor_count,
            f"Особь {i + 1}"
        )

    print("\nСтатистика поколения:")
    print(f"Лучшее значение: {min(values)}")
    print(f"Среднее значение: {mean(values):.2f}")
    print(f"Худшее значение: {max(values)}")

def makespan(chromosome, times, processor_count):
    """Максимальная суммарная загрузка одного процессора."""

    assignments = decode_chromosome(chromosome, processor_count)

    loads = [0] * processor_count

    for job_index, processor in enumerate(assignments):
        loads[processor] += times[job_index]

    return max(loads)

def print_schedule(chromosome, times, processor_count):
    """Печать распределения заданий и загрузки процессоров."""

    assignments = decode_chromosome(chromosome, processor_count)

    jobs_by_processor = [[] for _ in range(processor_count)]
    loads = [0] * processor_count

    for job_index, processor in enumerate(assignments):
        jobs_by_processor[processor].append(job_index + 1)
        loads[processor] += times[job_index]

    for p in range(processor_count):
        jobs = jobs_by_processor[p]

        print(
            f"  Процессор {p + 1}: задания {jobs}; "
            f"загрузка = {loads[p]}"
        )

    print(f"  Время завершения расписания (makespan): {max(loads)}")

# ------------------------------------------------------------
# Инициализация первого поколения
# ------------------------------------------------------------

def monte_carlo_individual(times, processor_count):
    """Случайно назначает каждое задание на один из процессоров."""
    assignments = [
        random.randrange(processor_count)
        for _ in times
    ]

    return encode_chromosome(assignments, processor_count)


def cpm_individual(times, processor_count, mode):
    """
    Эвристическое распределение:
    очередное задание назначается на наименее загруженный процессор.

    mode:
      ascending  - задания по возрастанию длительности;
      descending - задания по убыванию длительности;
      random     - случайный порядок заданий.
    """
    job_indices = list(range(len(times)))

    if mode == "ascending":
        # При одинаковой длительности порядок дополнительно перемешивается.
        random.shuffle(job_indices)
        job_indices.sort(key=lambda i: times[i])

    elif mode == "descending":
        random.shuffle(job_indices)
        job_indices.sort(key=lambda i: times[i], reverse=True)

    elif mode == "random":
        random.shuffle(job_indices)

    else:
        raise ValueError("Неизвестный режим CPM")

    loads = [0] * processor_count
    chromosome = [-1] * len(times)

    for job_index in job_indices:
        min_load = min(loads)

        # При равной загрузке выбираем случайный процессор.
        candidates = [
            p for p in range(processor_count)
            if loads[p] == min_load
        ]
        processor = random.choice(candidates)

        chromosome[job_index] = processor
        loads[processor] += times[job_index]
    
    return encode_chromosome(chromosome, processor_count)

def create_population(times, processor_count, population_size, init_mode):
    """Создает первое поколение выбранным способом."""
    population = []

    for _ in range(population_size):
        if init_mode == "monte_carlo":
            individual = monte_carlo_individual(times, processor_count)
        else:
            individual = cpm_individual(
                times, processor_count, init_mode
            )

        population.append(individual)

    return population


# ------------------------------------------------------------
# Генетические операторы
# ------------------------------------------------------------

def crossover(parent, partner):
    gene_count = len(parent) // 8

    if gene_count < 2:
        return parent.copy(), None

    # Точка скрещивания выбирается между целыми генами.
    point = random.randint(1, gene_count - 1) * 8

    child = parent[:point] + partner[point:]

    return child, point


def mutation(individual):
    mutated = individual.copy()

    gene_count = len(mutated) // 8

    gene_index = random.randrange(gene_count)
    bit_index = random.randrange(8)

    index = gene_index * 8 + bit_index

    old_bit = mutated[index]
    mutated[index] = 1 - mutated[index]

    return mutated, gene_index, bit_index, old_bit

# ------------------------------------------------------------
# Генетический алгоритм
# ------------------------------------------------------------

def genetic_algorithm(
    times,
    processor_count,
    population_size,
    crossover_probability,
    mutation_probability,
    stagnation_limit,
    init_mode
):
    population = create_population(
        times,
        processor_count,
        population_size,
        init_mode
    )

    # ==========================================
    # ПОКОЛЕНИЕ 0
    # ==========================================

    print_population(
        population,
        times,
        processor_count,
        0
    )

    fitness = [
        makespan(ind, times, processor_count)
        for ind in population
    ]

    best_index = min(
        range(population_size),
        key=lambda i: fitness[i]
    )

    best_individual = population[best_index].copy()
    best_value = fitness[best_index]

    generations_without_improvement = 0
    generation = 0

    # ==========================================
    # ГЕНЕТИЧЕСКИЙ АЛГОРИТМ
    # ==========================================

    while generations_without_improvement < stagnation_limit:

        # Подробная печать только при формировании поколения 1.
        debug = (generation == 0)

        if debug:
            print("\n" + "#" * 68)
            print("ФОРМИРОВАНИЕ ПОКОЛЕНИЯ 1")
            print("#" * 68)

        new_population = []
        improved = False

        for i in range(population_size):

            parent = population[i]
            parent_value = fitness[i]

            if debug:
                print("\n" + "=" * 60)
                print(f"ОБРАБОТКА ОСОБИ {i + 1}")
                print("=" * 60)

                print_individual(
                    parent,
                    times,
                    processor_count,
                    "ПЕРВЫЙ РОДИТЕЛЬ"
                )

            # ----------------------------------
            # 1. Выбор второго родителя
            # ----------------------------------

            candidates = [
                j for j in range(population_size)
                if j != i
            ]

            candidate_a, candidate_b = random.sample(candidates, 2)

            if fitness[candidate_a] <= fitness[candidate_b]:
                partner_index = candidate_a
            else:
                partner_index = candidate_b

            partner = population[partner_index]

            if debug:
                print_selection(
                    i,
                    candidate_a,
                    candidate_b,
                    partner_index,
                    fitness
                )

                print_individual(
                    partner,
                    times,
                    processor_count,
                    "ВТОРОЙ РОДИТЕЛЬ"
                )

            # ----------------------------------
            # 2. Кроссовер
            # ----------------------------------

            crossover_happened = (
                random.random() < crossover_probability
            )

            if crossover_happened:
                child, point = crossover(parent, partner)

                if debug:
                    print("\nКРОССОВЕР ВЫПОЛНЕН")
                    print(f"Точка разрыва: {point}")

            else:
                child = parent.copy()

                if debug:
                    print("\nКРОССОВЕР НЕ ВЫПОЛНЕН")
                    print("Потомок скопирован из первого родителя.")

            if debug:
                print_individual(
                    child,
                    times,
                    processor_count,
                    "ПОТОМОК ПОСЛЕ КРОССОВЕРА"
                )

            # ----------------------------------
            # 3. Мутация
            # ----------------------------------

            mutation_happened = (
                random.random() < mutation_probability
            )

            if mutation_happened:
                child, gene_index, bit_index, old_bit = mutation(child)

                if debug:
                    print("\nМУТАЦИЯ ВЫПОЛНЕНА")
                    print(f"Изменён ген: {gene_index + 1}")
                    print(f"Изменён бит: {bit_index + 1}")
                    print(f"Значение бита: {old_bit} -> {1 - old_bit}")

            elif debug:
                print("\nМУТАЦИЯ НЕ ВЫПОЛНЕНА")

            if debug:
                print_individual(
                    child,
                    times,
                    processor_count,
                    "ПОТОМОК ПОСЛЕ МУТАЦИИ"
                )

            # ----------------------------------
            # 4. Сравнение родителя и потомка
            # ----------------------------------

            child_value = makespan(
                child,
                times,
                processor_count
            )

            if debug:
                print("\nСРАВНЕНИЕ РОДИТЕЛЯ И ПОТОМКА")
                print(f"Родитель: {parent_value}")
                print(f"Потомок: {child_value}")

            # ----------------------------------
            # 5. Выбор лучшей особи
            # ----------------------------------

            if child_value <= parent_value:
                selected = child
                selected_value = child_value
                reason = "Потомок выбран"
            else:
                selected = parent.copy()
                selected_value = parent_value
                reason = "Сохранён родитель"

            new_population.append(selected)

            if debug:
                print(f"\nРЕЗУЛЬТАТ: {reason}")

                print_individual(
                    selected,
                    times,
                    processor_count,
                    "ОСОБЬ НОВОГО ПОКОЛЕНИЯ"
                )

            # ----------------------------------
            # 6. Обновление глобального минимума
            # ----------------------------------

            if selected_value < best_value:
                best_value = selected_value
                best_individual = selected.copy()
                improved = True

        # ======================================
        # ЗАВЕРШЕНИЕ ПОКОЛЕНИЯ
        # ======================================

        population = new_population
        generation += 1

        fitness = [
            makespan(ind, times, processor_count)
            for ind in population
        ]

        if debug:
            print("\n" + "#" * 68)
            print("ИТОГОВАЯ ПОПУЛЯЦИЯ ПОКОЛЕНИЯ 1")
            print("#" * 68)

            print_population(
                population,
                times,
                processor_count,
                generation
            )

        if improved:
            generations_without_improvement = 0
        else:
            generations_without_improvement += 1

    return best_individual, best_value, generation

# ------------------------------------------------------------
# Сравнение способов инициализации
# ------------------------------------------------------------

def compare_initializations(
    job_count,
    min_time,
    max_time,
    processor_count,
    population_size,
    crossover_probability,
    mutation_probability,
    stagnation_limit,
    runs
):
    methods = [
        ("Монте-Карло", "monte_carlo"),
        ("CPM по возрастанию", "ascending"),
        ("CPM по убыванию", "descending"),
        ("CPM в случайном порядке", "random"),
    ]

    results = {
        name: {
            "wins": 0,
            "values": []
        }
        for name, _ in methods
    }

    total_draws = 0

    print("\n" + "=" * 68)
    print("СРАВНЕНИЕ СПОСОБОВ ИНИЦИАЛИЗАЦИИ")
    print("=" * 68)

    for run in range(1, runs + 1):

        # Генерация нового набора заданий.
        times = [
            random.randint(min_time, max_time)
            for _ in range(job_count)
        ]

        print(f"\nНабор заданий {run}/{runs}: {times}")

        run_results = {}

        # Запуск каждого метода на одном наборе заданий.
        for method_name, init_mode in methods:

            individual, value, generations = genetic_algorithm(
                times=times,
                processor_count=processor_count,
                population_size=population_size,
                crossover_probability=crossover_probability,
                mutation_probability=mutation_probability,
                stagnation_limit=stagnation_limit,
                init_mode=init_mode
            )

            run_results[method_name] = value
            results[method_name]["values"].append(value)

            print(
                f"  {method_name}: makespan = {value}, "
                f"поколений = {generations}"
            )

        # Определение победителей ТЕКУЩЕГО набора.
        best_value = min(run_results.values())

        winners = [
            name
            for name, value in run_results.items()
            if value == best_value
        ]

        if len(winners) == 1:
            results[winners[0]]["wins"] += 1
            print(f"  Победитель: {winners[0]}")

        else:
            total_draws += 1
            print(f"  Ничья между: {', '.join(winners)}")

    # Итоговое сравнение всех наборов.
    print("\n" + "=" * 68)
    print("ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
    print("=" * 68)

    for method_name, _ in methods:
        print(
            f"{method_name}: "
            f"побед = {results[method_name]['wins']}"
        )

    print(f"\nОбщее количество ничьих: {total_draws}")

    print(f"\nВсего наборов заданий: {runs}")
    print(
        f"Проверено наборов: "
        f"{sum(r['wins'] for r in results.values()) + total_draws}"
    )

    max_wins = max(
        result["wins"]
        for result in results.values()
    )

    best_methods = [
        name
        for name, result in results.items()
        if result["wins"] == max_wins
    ]

    print("\n" + "=" * 68)

    if len(best_methods) == 1:
        print(f"ЛУЧШИЙ МЕТОД: {best_methods[0]}")
    else:
        print(f"ЛИДИРУЮЩИЕ МЕТОДЫ: {', '.join(best_methods)}")

    print("=" * 68)

def read_int(prompt, minimum):
    while True:
        try:
            value = int(input(prompt))
            if value < minimum:
                print(f"Введите целое число не меньше {minimum}.")
                continue
            return value
        except ValueError:
            print("Ошибка: необходимо ввести целое число.")


def read_probability(prompt):
    while True:
        try:
            value = float(input(prompt).replace(",", "."))
            if not 0.0 <= value <= 1.0:
                print("Вероятность должна находиться в диапазоне [0; 1].")
                continue
            return value
        except ValueError:
            print("Ошибка: введите число.")


def main():
    print("=" * 68)
    print("ГЕНЕТИЧЕСКИЙ АЛГОРИТМ ДЛЯ ЗАДАЧИ РАСПРЕДЕЛЕНИЯ ЗАДАНИЙ")
    print("=" * 68)

    processor_count = read_int(
        "Введите количество процессоров n: ", 1
    )

    job_count = read_int(
        "Введите количество заданий m: ", 1
    )

    print("\nЗадайте диапазон случайной генерации длительностей:")
    while True:
        min_time = read_int("Минимальная длительность задания: ", 1)
        max_time = read_int("Максимальная длительность задания: ", 1)

        if min_time <= max_time:
            break

        print("Ошибка: минимум не может быть больше максимума.")

    print("\nПараметры генетического алгоритма:")

    population_size = read_int(
        "Размер популяции (не менее 3): ", 3
    )

    crossover_probability = read_probability(
        "Вероятность кроссовера Pc (0..1): "
    )

    mutation_probability = read_probability(
        "Вероятность мутации Pm (0..1): "
    )

    stagnation_limit = read_int(
        "Количество поколений без улучшения (условие останова): ", 1
    )

    runs = read_int(
        "Количество повторных запусков для каждого метода: ", 1
    )

    print("\nИсходные данные:")
    print(f"Количество процессоров: {processor_count}")
    print(f"Количество заданий: {job_count}")
    print(f"Диапазон длительностей: [{min_time}, {max_time}]")
    print(f"Размер популяции: {population_size}")
    print(f"Pc = {crossover_probability}")
    print(f"Pm = {mutation_probability}")
    print(f"Условие останова: {stagnation_limit}")
    print(f"Повторных запусков: {runs}")

    compare_initializations(
        job_count=job_count,
        min_time=min_time,
        max_time=max_time,
        processor_count=processor_count,
        population_size=population_size,
        crossover_probability=crossover_probability,
        mutation_probability=mutation_probability,
        stagnation_limit=stagnation_limit,
        runs=runs
    )


if __name__ == "__main__":
    main()
