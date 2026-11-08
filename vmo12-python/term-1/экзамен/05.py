import random


def double_max(list_: list):
    len_list = len(list_)
    maximum = -100000
    count = 0
    for i in list_:
        if i >= maximum:
            maximum = i
    for j in range(len_list):
        if list_[j] == maximum:
            list_[j] = maximum * 2
            count += 1
    return list_, count


example_list = [random.randint(1, 100) for i in range(10)]
print(example_list)
print(double_max(example_list))
