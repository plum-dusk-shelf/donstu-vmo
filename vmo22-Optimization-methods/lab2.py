import matplotlib.pyplot as plt
import numpy
import numpy as np
import math
from scipy.interpolate import interp1d
from lab2_b import x_data, y_data

matrix_polynomial_approximation = [0]*4

def linear_approximize(x_data, y_data):
    n = len(x_data)
    sum_x = sum(x_data)
    sum_y = sum(y_data)
    sum_x2 = sum(xi ** 2 for xi in x_data)
    sum_xy = sum(xi * yi for xi, yi in zip(x_data, y_data))

    determinant = n * sum_x2 - sum_x ** 2
    if determinant == 0:
        raise ValueError("Система уравнений вырождена")

    a0 = (sum_x2 * sum_y - sum_x * sum_xy) / determinant
    a1 = (n * sum_xy - sum_x * sum_y) / determinant
    return (a0, a1)


def print_vandermonde(matrix):
    print("\nМатрица Вандермонда для интерполяции Гаусса:")
    for i, row in enumerate(matrix):
        print(f"Строка {i + 1}: [", end="")
        for j, val in enumerate(row):
            print(f"{val:8.3f}", end=" ")
        print("]")


def gauss_solve(matrix, vector):
    n = len(vector)
    # Исправлено формирование расширенной матрицы
    aug = np.array([np.append(row, vec) for row, vec in zip(matrix, vector)], dtype=float)

    # Прямой ход метода Гаусса
    for i in range(n):
        max_row = np.argmax(np.abs(aug[i:, i])) + i
        aug[[i, max_row]] = aug[[max_row, i]]

        pivot = aug[i, i]
        if pivot == 0:
            raise ValueError("Матрица вырождена")

        aug[i] /= pivot

        for k in range(i + 1, n):
            aug[k] -= aug[k, i] * aug[i]

    matrix_return = ''
    for i in range(n):
        line = numpy.array([l for l in aug[i]], dtype=numpy.int64)
        for k in line:
            matrix_return += (f' {k: 04}  ')
        matrix_return += '\n'

    # Обратный ход
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = aug[i, -1]
        for j in range(i + 1, n):
            x[i] -= aug[i, j] * x[j]


    return x, matrix_return


def gauss_interpolation_coefficients(x_data, y_data):
    n = len(x_data)
    vander = [[xi ** i for i in range(n)] for xi in x_data]
    global  matrix_gauss_interpolation
    coefficients, matrix_gauss_interpolation = gauss_solve(vander, y_data)
    return coefficients


def matrix_mult(A, B):
    """Умножение матриц A и B"""
    n = len(A)
    return [[sum(A[i][k] * B[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def power_iteration(A, iterations=100):
    """Степенные итерации для нахождения максимального собственного значения"""
    n = len(A)
    x = [1.0] * n
    for _ in range(iterations):
        Ax = [sum(A[i][j] * x[j] for j in range(n)) for i in range(n)]
        norm = math.sqrt(sum(xi ** 2 for xi in Ax))
        x = [xi / norm for xi in Ax]

    # Вычисляем соответствующее собственное значение
    Ax = [sum(A[i][j] * x[j] for j in range(n)) for i in range(n)]
    lambda_ = sum(Ax[i] * x[i] for i in range(n)) / sum(xi ** 2 for xi in x) if sum(xi ** 2 for xi in x) != 0 else 0
    return lambda_, x


def least_squares(x_data, y_data, degree):
    """
    аппроксимация методом наименьших квадратов
    """
    # Базисные функции для квадратичной аппроксимации
    if degree == 1:
        basis = [lambda x: 1, lambda x: x]
    if degree == 2:
        basis = [lambda x: 1, lambda x: x, lambda x: x ** 2]
    if degree == 3:
        basis = [lambda x: 1, lambda x: x, lambda x: x ** 2, lambda x: x ** 3]

    # Строим матрицу плана
    A = np.array([[phi(x) for phi in basis] for x in x_data])

    # Решаем нормальные уравнения
    ATA = A.T @ A
    ATy = A.T @ y_data

    global matrix_least_squares

    try:
        coefficients, matrix_least_squares = gauss_solve(ATA, ATy)
    except np.linalg.LinAlgError:
        raise ValueError("Система уравнений вырождена")

    return coefficients


def matrix_transpose(A):
    """Транспонирование матрицы"""
    return [[A[j][i] for j in range(len(A))] for i in range(len(A[0]))]


def matrix_norm_2(A):
    """Вычисление спектральной нормы матрицы"""
    A_T = matrix_transpose(A)
    ATA = matrix_mult(A_T, A)
    lambda_max, _ = power_iteration(ATA)
    return math.sqrt(abs(lambda_max))


def inverse_power_iteration(A, iterations=100):
    """Обратные итерации для нахождения минимального собственного значения"""
    n = len(A)
    x = [1.0] * n

    # Создаем копию матрицы для решения системы
    A_copy = [row.copy() for row in A]

    for _ in range(iterations):
        # Решаем систему Ax = b методом Гаусса
        # Здесь должен быть ваш метод gauss_solve()
        try:
            x, matrix_inverse_power_iteration = gauss_solve(A_copy, x)
        except:
            return float('inf'), x

        norm = math.sqrt(sum(xi ** 2 for xi in x))
        x = [xi / norm for xi in x]

    # Вычисляем соответствующее собственное значение
    Ax = [sum(A[i][j] * x[j] for j in range(n)) for i in range(n)]
    lambda_ = sum(Ax[i] * x[i] for i in range(n)) / sum(xi ** 2 for xi in x) if sum(xi ** 2 for xi in x) != 0 else 0
    return lambda_, x


def inverse_matrix_norm_2(A):
    """Вычисление нормы обратной матрицы"""
    A_T = matrix_transpose(A)
    ATA = matrix_mult(A_T, A)
    lambda_min, _ = inverse_power_iteration(ATA)
    return 1.0 / math.sqrt(abs(lambda_min)) if lambda_min != 0 else float('inf')


def condition_number(A):
    if (len(A) == len(A[0]) and len(A[0]) <= 15):
        """Вычисление числа обусловленности"""
        norm_A = matrix_norm_2(A)
        norm_inv_A = inverse_matrix_norm_2(A)
        return norm_A * norm_inv_A
    else:
        print("Value instability! Condition_number method isn't working for big dimention matrix!")
        raise ValueError


def lagrange_interpolation(x_data, y_data):
    """Генерирует интерполяционную функцию Лагранжа"""

    def interpolate(x):
        total = 0.0
        n = len(x_data)
        for i in range(n):
            term = y_data[i]
            for j in range(n):
                if j != i:
                    term *= (x - x_data[j]) / (x_data[i] - x_data[j])
            total += term
        return total

    return interpolate


def eval_polynomial(coefficients, x):
    """Вычисляет значение полинома в точке x. Коэффициенты: от старшей степени к младшей."""
    return sum(coeff * (x ** (len(coefficients) - i - 1)) for i, coeff in enumerate(coefficients))


# Модифицированная функция polynomial_approximation
def polynomial_approximation(x_data, y_data, degree):
    """Аппроксимация полиномом заданной степени методом Гаусса"""
    # Формируем матрицу Вандермонда
    A = [[xi ** j for j in range(degree + 1)] for xi in x_data]
    A_T = matrix_transpose(A)
    ATA = matrix_mult(A_T, A)
    ATy = [sum(a * y for a, y in zip(row, y_data)) for row in A_T]

    # Решение системы
    global matrix_polynomial_approximation
    try:
        coefficients, matrix_polynomial_approximation[degree] = gauss_solve(ATA, ATy)
    except ValueError as e:
        raise ValueError(f"Ошибка: {e}")

    # Переворачиваем коэффициенты для совместимости с np.polyfit
    return coefficients[::-1]


n = len(x_data)
vander_matrix = [[xi ** i for i in range(n)] for xi in x_data]

# Вычисление коэффициентов
a0, a1 = linear_approximize(x_data, y_data)
coefficients = gauss_interpolation_coefficients(x_data[:6], y_data[:6])
# Вычисление коэффициентов
coefficients_linear = polynomial_approximation(x_data, y_data, 1)
coefficients_quadratic = polynomial_approximation(x_data, y_data, 2)
coefficients_cubic = polynomial_approximation(x_data, y_data, 3)
coefficients_gauss = gauss_interpolation_coefficients(x_data, y_data)

coefficients_quadratic_mse = least_squares(x_data, y_data, degree=2)

# Генерация точек для графиков
x_plot = np.linspace(min(x_data) - 20, max(x_data) + 20, 500)
y_gauss = [eval_polynomial(coefficients, x) for x in x_plot]
lagrange_func = lagrange_interpolation(x_data[:6], y_data[:6])
y_linear = [a0 + a1 * x for x in x_plot]
y_lagrange = [lagrange_func(x) for x in x_plot]
y_linear_2 = [eval_polynomial(coefficients_linear, x) for x in x_plot]
y_quadratic = [eval_polynomial(coefficients_quadratic, x) for x in x_plot]
y_cubic = [eval_polynomial(coefficients_cubic, x) for x in x_plot]
y_quadratic_mse = [
    coefficients_quadratic_mse[0] + coefficients_quadratic_mse[1] * x + coefficients_quadratic_mse[2] * x ** 2 for x in
    x_plot]

# Идеальная линейная регрессия через numpy
ideal_linear_coeffs = np.polyfit(x_data, y_data, 1)
ideal_linear = np.poly1d(ideal_linear_coeffs)

# Идеальная интерполяция через scipy (кубический сплайн)
ideal_interp = interp1d(x_data, y_data, kind='cubic', fill_value='extrapolate')

# Точка для демонстрации (X=0.2)
X = 0.114
gauss_value = eval_polynomial(coefficients, X)
linear_value = a0 + a1 * X
ideal_linear_value = ideal_linear(X)
ideal_interp_value = ideal_interp(X)
lagrange_value = lagrange_func(X)
quadratic_mse_value = coefficients_quadratic_mse[0] + coefficients_quadratic_mse[1] * X + coefficients_quadratic_mse[
    2] * X ** 2


for m in [1,2,3]:
    print(f'\nМатрица метода полиномиальных коэффицентов {m} степени:\n{matrix_polynomial_approximation[m]}\n')


# Построение графиков
fig, ((ax3, ax7), (ax8, ax9)) = plt.subplots(2, 2, figsize=(12, 6))

# График 3: Интерполяция Лагранжем
ax3.scatter(x_data[:6], y_data[:6], color='black', s=20, label='Исходные точки', zorder=5)
ax3.plot(x_plot, ideal_interp(x_plot), 'y-', linewidth=2, label='Идеальная интерполяция (Scipy)')
ax3.plot(x_plot, y_lagrange, 'g--', linewidth=2, label=f'Лагранж (степень {len(x_data) - 1})')
ax3.scatter([X], [lagrange_value], color='purple', s=100, zorder=5, label=f'Лагранж(X={X}) = {lagrange_value:.18f}')
ax3.scatter([X], [ideal_interp_value], color='orange', s=100, zorder=5,
            label=f'Идеальная(X={X}) = {ideal_interp_value:.18f}')
ax3.set_title('Интерполяция полиномом Лагранжа', fontsize=14)
ax3.set_xlabel('x', fontsize=12)
ax3.set_ylabel('y', fontsize=12)
ax3.grid(True, alpha=0.4)
ax3.legend(loc='upper left', fontsize=7)
ax3.set_xlim(min(x_data) - 5, max(x_data) + 5)
ax3.set_ylim(min(y_data) - 5, max(y_data) + 5)

ax7.scatter(x_data, y_data, color='black', s=20, label='Исходные точки', zorder=5)
ax7.plot(x_plot, y_quadratic_mse, 'm-', linewidth=2,
         label=f'Квадратичная: y = {coefficients_quadratic_mse[0]:.2f} + {coefficients_quadratic_mse[1]:.2f}x + {coefficients_quadratic_mse[2]:.2f}x²')
ax7.set_title('Квадратичная аппроксимация', fontsize=14)
ax7.legend(loc='upper left', fontsize=7)
ax7.grid(True, alpha=0.4)
ax7.set_xlim(-10, 5)
ax7.set_ylim(-10, 20)

# График 8: Линейная аппроксимация МНК (degree=1)
# Вычисляем коэффициенты
coefficients_linear_mse = least_squares(x_data, y_data, degree=1)
y_linear_mse = [coefficients_linear_mse[0] + coefficients_linear_mse[1] * x for x in x_plot]

ax8.scatter(x_data, y_data, color='black', s=20, label='Исходные точки', zorder=5)
ax8.plot(x_plot, y_linear_mse, 'g-', linewidth=2,
         label=f'Линейная: y = {coefficients_linear_mse[0]:.2f} + {coefficients_linear_mse[1]:.2f}x')
ax8.plot(x_plot, ideal_linear(x_plot), 'c--', linewidth=2, label='Идеальная прямая (Numpy)')
ax8.set_title('Линейная аппроксимация', fontsize=12)
ax8.grid(True, alpha=0.4)
ax8.legend(loc='upper left', fontsize=8)
ax8.set_xlim(-10, 5)
ax8.set_ylim(-10, 20)

# График 9: Кубическая аппроксимация МНК (degree=3)
# Вычисляем коэффициенты
coefficients_cubic_mse = least_squares(x_data, y_data, degree=3)
y_cubic_mse = [coefficients_cubic_mse[0] + coefficients_cubic_mse[1] * x +
               coefficients_cubic_mse[2] * x ** 2 + coefficients_cubic_mse[3] * x ** 3
               for x in x_plot]

ax9.scatter(x_data, y_data, color='black', s=20, label='Исходные точки', zorder=5)
ax9.plot(x_plot, y_cubic_mse, 'm-', linewidth=2,
         label=f'Кубическая\n{coefficients_cubic_mse[0]:.2f} + {coefficients_cubic_mse[1]:.2f}x + '
               f'{coefficients_cubic_mse[2]:.2f}x² + {coefficients_cubic_mse[3]:.2f}x³')
ax9.set_title('Кубическая аппроксимация', fontsize=12)
ax9.grid(True, alpha=0.4)
ax9.legend(loc='upper left', fontsize=8)
ax9.set_xlim(-10, 5)
ax9.set_ylim(-10, 20)

plt.tight_layout()
plt.show()
