import random


def create_matrix(N, M):
    new_matrix = [[] for n in range(N)]

    for n in range(N):
        new_matrix[n] = [random.randint(-10, 10) for m in range(M)]

    return new_matrix


def print_matrix(matrix):
    for p in matrix:
        print(p)
    print('\n')


def count_matrix(matrix):
    values = [0, 0, 0]

    for n in matrix:
        for i in n:
            if i > 0:
                values[0] += 1
            elif i < 0:
                values[1] += 1
            else:
                values[2] += 1

    return values


# matrix_1 = create_matrix(4, 4)
# print_matrix(matrix_1)
# print(count_matrix(matrix_1))
print_matrix(create_matrix(4,4))
