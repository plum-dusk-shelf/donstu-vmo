from random import randint


def MaxInt(A: list, N=None):
    if not N: N = len(A)
    if N < 1 or N > 10:
        return 0
    if N == 1:
        return A[0]
    if A[0] < A[1]:
        return MaxInt(A[1:], len(A[1:]))
    else:
        return MaxInt(A, len(A))


list_A = [x for x in range(1, 10)]
list_B = [x for x in range(9, 0, -1)]
list_C = [randint(-10, -1) for i in range(0, 10)]

print(list_A, MaxInt(list_A, len(list_A)))
print(list_B, MaxInt(list_B, len(list_B)))
print(list_C, MaxInt(list_C, len(list_C)))
