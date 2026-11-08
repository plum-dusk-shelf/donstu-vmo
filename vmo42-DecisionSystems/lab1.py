import random
import numpy as np

def cpm(tasks, n, s):
    if s == 0:
        tasks = sorted(tasks, reverse=True)
    if s == 1:
        tasks = sorted(tasks, reverse=False)

    schedule = [[] for _ in range(n)]
    loads = [0] * n

    print(tasks)
    for i in range(len(tasks)):
        task = tasks[i]
        processor = min(range(n), key=lambda i: loads[i])

        schedule[processor].append(task)
        loads[processor] += task

#        print(f'Шаг {i}')
#        for j in range(len(loads)):
#            print(f'{loads[j]:4} | {schedule[j]}')

    return schedule, loads

def hdmt(tasks, n):
    if n < 2 or n % 2 != 0:
        raise ValueError("количество процессоров должно быть чётным")

    tasks = sorted(tasks, reverse=True)

    groups = [[], []]
    loads = [0, 0]

    for task in tasks:
        group = min(range(2), key=lambda i: loads[i])
        groups[group].append(task)
        loads[group] += task

    schedule = [[] for _ in range(n)]
    final_loads = [0] * n

    processors_per_group = n // 2

    for group_index, group in enumerate(groups):

        group_schedule, group_loads = cpm(
            group,
            processors_per_group,
            0
        )

        start_processor = group_index * processors_per_group

        for i in range(processors_per_group):
            processor = start_processor + i

            schedule[processor] = group_schedule[i]
            final_loads[processor] = group_loads[i]

    return schedule, final_loads


def ofmt(tasks, n):
    if (n < 1 or (n & (n - 1)) != 0):
        raise ValueError("количество процессоров должно быть степенью двойки")
    tasks = sorted(tasks, reverse=True)
    schedule = [[] for _ in range(n)]
    loads = [0] * n
    
    def divide(current_tasks, processors):
        if len(processors) == 1:
            processor = processors[0]

            schedule[processor].extend(current_tasks)
            loads[processor] += sum(current_tasks)

            return

        groups = [[], []]
        group_loads = [0, 0]

        for task in current_tasks:
            group = min(
                range(2),
                key=lambda i: group_loads[i]
            )

            groups[group].append(task)
            group_loads[group] += task

        middle = len(processors) // 2

        left_processors = processors[:middle]
        right_processors = processors[middle:]

        divide(
            groups[0],
            left_processors
        )

        divide(
            groups[1],
            right_processors
        )

    divide(tasks, list(range(n)))

    return schedule, loads

def my_print(schedule, loads):
    print("Load | Schedule")
    for i in range(len(loads)):
        print(f'{loads[i]:4} | {schedule[i]}')
    print('Cmax =', max(loads))

list_ = np.zeros((100,4))
m = input('M: ')
n = input('N: ')
a = input('A: ')
b = input('B: ')
num = int(input('Количество: '))
for i in range(num):
    if n == '' and m == '' and a == '' and b == '':
        n = 2
        m = random.choice(range(20, 26))
        a = 10
        b = 30
    m = int(m)
    n = int(n)
    a = int(a)
    b = int(b)
    tasks = [random.choice(range(a,b)) for _ in range(m)]

    print('\n'*3, f'Попытка номер {i}')
    for j in range(n):
        print(tasks)

    schedule, loads = cpm(tasks, n, 0)
    print("\n\nCPM")
    list_[i,0]=(max(loads))
    my_print(schedule, loads)

    schedule, loads = cpm(tasks, n, 1)
    print("\n\nCPM по возрастанию")
    list_[i,1]=(max(loads))
    my_print(schedule, loads)

    schedule, loads = hdmt(tasks, n)
    print("\n\nHDMT")
    list_[i,2]=(max(loads))
    my_print(schedule, loads)

    schedule, loads = cpm(tasks, n, 2)
    print("\n\nCPM случайный")
    list_[i,3]=(max(loads))
    my_print(schedule, loads)

cpm_wins = 0
cpm1_wins = 0
hdmt_wins = 0
ofmt_wins = 0
ties = 0

for i in range(100):
    cpm_val = list_[i][0]
    cpm1_val = list_[i][1]
    hdmt_val = list_[i][2]
    ofmt_val = list_[i][3]

    min_val = min(cpm_val, cpm1_val, hdmt_val, ofmt_val)

    winners = []
    if cpm_val == min_val:
        winners.append('CPM')
    if cpm1_val == min_val:
        winners.append('CPM 1')
    if hdmt_val == min_val:
        winners.append('HDMT')
    if ofmt_val == min_val:
        winners.append('OFMT')

    if len(winners) == 1:
        if winners[0] == 'CPM':
            cpm_wins += 1
        elif winners[0] == 'CPM 1':
            cpm1_wins += 1
        elif winners[0] == 'HDMT':
            hdmt_wins += 1
        elif winners[0] == 'OFMT':
            ofmt_wins += 1
    else:
        ties += 1


print("\n\nРЕЗУЛЬТАТЫ СОРЕВНОВАНИЯ АЛГОРИТМОВ")
print(f"CPM  побед: {cpm_wins}")
print(f"CPM по возрастанию  побед: {cpm_wins}")
print(f"HDMT побед: {hdmt_wins}")
print(f"CPM случайный побед: {ofmt_wins}")
print(f"Ничьих (несколько алгоритмов с одинаковым минимумом): {ties}")

avg_cpm = np.mean(list_[:, 0])
avg_cpm1 = np.mean(list_[:, 1])
avg_hdmt = np.mean(list_[:, 2])
avg_ofmt = np.mean(list_[:, 3])

print(f"Средний Cmax CPM:  {avg_cpm:.2f}")
print(f"Средний Cmax CPM по возрастанию:  {avg_cpm1:.2f}")
print(f"Средний Cmax HDMT: {avg_hdmt:.2f}")
print(f"Средний Cmax CPM случайный: {avg_ofmt:.2f}")
