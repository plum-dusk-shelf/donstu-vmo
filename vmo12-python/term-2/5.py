import numpy as np
import random


def first():
    array = np.array([random.randint(0, 5) for i in range(10)])
    print(f'{array} → {array.nonzero()[0]}')


def second():
    one_matrix = np.eye(3, 3)
    print(one_matrix)


def third():
    matrix = np.random.rand(3, 3, 3)
    print(matrix)


# 4.
def fourth(n=5):
    zero = np.zeros(n)
    print(zero)
    return zero


def fifth():
    zeros = fourth(7)
    zeros[4] = 1
    print(zeros)


def sixth(n=0, m=10):
    arr = np.arange(n, m)
    print(arr)
    return arr


def seventh():
    arr = sixth()
    print(arr[::-1])


def eights():
    matr = np.zeros((5, 5))
    print(matr)
    matr[0] = 1
    matr[-1] = 1
    matr[:, 0] = 1
    matr[:, -1] = 1
    print(matr)


def ninth(n=5):
    matr = np.diag(range(1, n), -1)
    print(matr)
    return matr


def tenth(n=8):
    matr = np.zeros((n, n), dtype='int')
    matr[n % 2::2, ::2] = 1
    matr[(n + 1) % 2::2, 1::2] = 1
    print(matr)


def eleventh(n=5, m=5):
    arr = np.random.randint(-10, 10, (n, m), dtype='int')
    maxim = arr.argmax()
    new_arr = arr.copy().reshape(m * n)
    new_arr[maxim] = 0
    print(arr, maxim, new_arr.reshape(n, m), sep='\n')


def twelfth(n=5, m=5):
    arr = np.random.randint(-10, 10, (n, m), dtype='int')
    target = 6
    arr_new = np.abs(arr.copy() - target)
    closer = arr_new.argmin()
    print(arr, arr_new, closer, sep='\n')


def thirteenth(n=5):
    arr = np.random.randint(-10, 10, [n for i in range(4)], dtype='int')
    print(arr.sum(2), arr.sum(2))


def fourteenth():
    arr = np.random.randint(-10, 10, (5, 5), dtype='int')
    print(arr)
    print(0 in arr.sum(0))
    arr[:, -1] = 0
    print(arr)
    print(0 in arr.sum(0))


def fifteenth():
    arr = np.random.randint(-10, 10, (5, 5), dtype='int')
    median = arr.mean()
    print(arr, median, arr - median, sep='\n')


if __name__ == '__main__':
    number = int(input())
    match number:
        case 1:
            first()
        case 2:
            second()
        case 3:
            third()
        case 4:
            fourth()
        case 5:
            fifth()
        case 6:
            sixth()
        case 7:
            seventh()
        case 8:
            eights()
        case 9:
            ninth()
        case 10:
            tenth()
        case 11:
            eleventh()
        case 12:
            twelfth()
        case 13:
            thirteenth()
        case 14:
            fourteenth()
        case 15:
            fifteenth()
