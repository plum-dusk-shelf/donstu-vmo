M = 10
N = 10
matrix = []
compositions = []

for m in range(M):
    matrix.append([])
    for n in range(N):
        matrix[m].append(10 * m)

for row in matrix:
    print(row)

for i in range(len(matrix)):
    compositions.append(1)
    for j in matrix[i]:
        compositions[i] *= j

for row_comp in compositions:
    print(row_comp)

side_diagonal_sum = 0

for row in range(len(matrix)):
    side_diagonal_sum += matrix[row][N - row - 1]

print(side_diagonal_sum)
