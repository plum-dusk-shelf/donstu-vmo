import matplotlib.pyplot as plt
import numpy as np
import math
from scipy.interpolate import interp1d

def calculate_r_squared(y_real, y_pred):
    """Вычисление коэффициента детерминации R²"""
    y_mean = np.mean(y_real)
    ss_total = sum((yi - y_mean)**2 for yi in y_real)
    ss_res = sum((yi - yj)**2 for yi, yj in zip(y_real, y_pred))
    return 1 - (ss_res / ss_total) if ss_total != 0 else 0

def linear_approximize(x_data, y_data):
    n = len(x_data)
    sum_x = sum(x_data)
    sum_y = sum(y_data)
    sum_x2 = sum(xi**2 for xi in x_data)
    sum_xy = sum(xi*yi for xi, yi in zip(x_data, y_data))

    determinant = n * sum_x2 - sum_x**2
    if determinant == 0:
        raise ValueError("Система уравнений вырождена")

    a0 = (sum_x2 * sum_y - sum_x * sum_xy) / determinant
    a1 = (n * sum_xy - sum_x * sum_y) / determinant
    print("\nЛинейная аппроксимация:")
    print(format_polynomial([a1, a0]))
    return (a0, a1)

def print_vandermonde(matrix):
    print("\nМатрица Вандермонда для интерполяции Гаусса:")
    for i, row in enumerate(matrix):
        print(f"Строка {i+1}: [", end="")
        for j, val in enumerate(row):
            print(f"{val:8.3f}", end=" ")
        print("]")

def gauss_solve(matrix, vector):
    n = len(vector)
    aug = np.array([np.append(row, vec) for row, vec in zip(matrix, vector)], dtype=float)
    
    # Прямой ход
    for i in range(n):
        max_row = np.argmax(np.abs(aug[i:, i])) + i
        aug[[i, max_row]] = aug[[max_row, i]]
        
        pivot = aug[i, i]
        if pivot == 0:
            raise ValueError("Матрица вырождена")
        
        aug[i] /= pivot
        
        for k in range(i+1, n):
            aug[k] -= aug[k, i] * aug[i]
    
    # Обратный ход
    x = np.zeros(n)
    for i in range(n-1, -1, -1):
        x[i] = aug[i, -1]
        for j in range(i+1, n):
            x[i] -= aug[i, j] * x[j]
    
    return x

def gauss_interpolation_coefficients(x_data, y_data):
    n = len(x_data)
    vander = [[xi**i for i in range(n)] for xi in x_data]
    coefficients = gauss_solve(vander, y_data)
    return coefficients

def least_squares(x_data, y_data, degree):
    """Аппроксимация методом наименьших квадратов"""
    if degree == 1:
        basis = [lambda x: 1, lambda x: x]
    elif degree == 2:
        basis = [lambda x: 1, lambda x: x, lambda x: x**2]
    elif degree == 3:
        basis = [lambda x: 1, lambda x: x, lambda x: x**2, lambda x: x**3]
    
    A = np.array([[phi(x) for phi in basis] for x in x_data])
    ATA = A.T @ A
    ATy = A.T @ y_data
    
    try:
        coefficients = gauss_solve(ATA, ATy)
    except np.linalg.LinAlgError:
        raise ValueError("Система уравнений вырождена")
        
    # Коэффициенты через numpy.polyfit (для сравнения)
    np_coeffs = np.polyfit(x_data, y_data, degree)[::-1]  # Реверс порядка
    
    print(f"\nМНК аппроксимация степени {degree}:")
    print("Вычисленные коэффициенты:   ", format_polynomial(coefficients))
    print("Коэффициенты NumPy:  ", format_polynomial(np_coeffs))
    
    return coefficients

def matrix_mult(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(A))) for j in range(len(B[0]))] for i in range(len(A))]

def matrix_transpose(A):
    return [[A[j][i] for j in range(len(A))] for i in range(len(A[0]))]

def power_iteration(A, iterations=100):
    n = len(A)
    x = [1.0] * n
    for _ in range(iterations):
        Ax = [sum(A[i][j] * x[j] for j in range(n)) for i in range(n)]
        norm = math.sqrt(sum(xi**2 for xi in Ax))
        x = [xi / norm for xi in Ax]
    
    Ax = [sum(A[i][j] * x[j] for j in range(n)) for i in range(n)]
    lambda_ = sum(Ax[i] * x[i] for i in range(n)) / sum(xi**2 for xi in x) if sum(xi**2 for xi in x) != 0 else 0
    return lambda_, x

def format_polynomial(coefficients, decimals=6):
    """Форматирует коэффициенты в строку полинома"""
    terms = []
    for power, coeff in enumerate(reversed(coefficients)):
        if abs(coeff) < 1e-10:  # Пропускаем нулевые коэффициенты
            continue
            
        coeff_rounded = round(coeff, decimals)
        
        # Форматируем степень
        if power == 0:
            term = f"{coeff_rounded:.{decimals}f}"
        elif power == 1:
            term = f"{coeff_rounded:.{decimals}f}x"
        else:
            term = f"{coeff_rounded:.{decimals}f}x^{power}"
            
        # Убираем лишние символы
        term = term.replace("+ -", "- ").replace(" 1x", " x")
        terms.append(term)
    
    # Собираем все термины
    poly_str = " + ".join(terms)
    
    # Корректируем знаки
    poly_str = poly_str.replace("+ -", "- ")
    if poly_str.startswith("- "):
        poly_str = "-" + poly_str[2:]
    
    return f"P(x) = {poly_str}"

def matrix_norm_2(A):
    A_T = matrix_transpose(A)
    ATA = matrix_mult(A_T, A)
    lambda_max, _ = power_iteration(ATA)
    return math.sqrt(abs(lambda_max))

def inverse_power_iteration(A, iterations=100):
    n = len(A)
    x = [1.0] * n
    A_copy = [row.copy() for row in A]
    
    for _ in range(iterations):
        try:
            x = gauss_solve(A_copy, x)
        except:
            return float('inf'), x
        
        norm = math.sqrt(sum(xi**2 for xi in x))
        x = [xi / norm for xi in x]
    
    Ax = [sum(A[i][j] * x[j] for j in range(n)) for i in range(n)]
    lambda_ = sum(Ax[i] * x[i] for i in range(n)) / sum(xi**2 for xi in x) if sum(xi**2 for xi in x) != 0 else 0
    return lambda_, x

def inverse_matrix_norm_2(A):
    A_T = matrix_transpose(A)
    ATA = matrix_mult(A_T, A)
    lambda_min, _ = inverse_power_iteration(ATA)
    return 1.0 / math.sqrt(abs(lambda_min)) if lambda_min != 0 else float('inf')

def condition_number(A):
    if len(A) == len(A[0]) and len(A[0]) <= 15:
        norm_A = matrix_norm_2(A)
        norm_inv_A = inverse_matrix_norm_2(A)
        return norm_A * norm_inv_A
    else:
        print("Метод condition_number не работает для больших матриц!")
        raise ValueError

def lagrange_interpolation(x_data, y_data):
    """Генерирует и выводит полином в канонической форме"""
    n = len(x_data)
    
    # Решение системы Вандермонда для получения коэффициентов
    vander = [[xi**i for i in reversed(range(n))] for xi in x_data]
    coefficients = gauss_solve(vander, y_data)
    
    print(format_polynomial(coefficients))
    
    
    def interpolate(x):
        return sum(coeff * x**power for coeff, power in zip(coefficients, reversed(range(n))))
    
    return interpolate

def eval_polynomial(coefficients, x):
    return sum(coeff * (x ** (len(coefficients) - i - 1)) for i, coeff in enumerate(coefficients))

def polynomial_approximation(x_data, y_data, degree):
    A = [[xi ** j for j in range(degree + 1)] for xi in x_data]
    A_T = matrix_transpose(A)
    ATA = matrix_mult(A_T, A)
    ATy = [sum(a * y for a, y in zip(row, y_data)) for row in A_T]
    
    try:
        coefficients = gauss_solve(ATA, ATy)
    except ValueError as e:
        raise ValueError(f"Ошибка: {e}")
    print(f"\nПолиномиальная аппроксимация степени {degree}:")
    print(format_polynomial(coefficients))

    return coefficients[::-1]

def mean(values):
    return sum(values) / len(values)

def standard_deviation(values, mean_value):
    variance = sum((x - mean_value) ** 2 for x in values) / (len(values) - 1)
    return variance ** 0.5

def covariance(x, y, mean_x, mean_y):
    cov = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y)) / (len(x) - 1)
    return cov

def corrcoef(y_data, y_pred):
    if len(y_data) != len(y_pred):
        raise ValueError("Длины наборов данных должны совпадать")
    mean_y_data = mean(y_data)
    mean_y_pred = mean(y_pred)
    std_y_data = standard_deviation(y_data, mean_y_data)
    std_y_pred = standard_deviation(y_pred, mean_y_pred)
    cov = covariance(y_data, y_pred, mean_y_data, mean_y_pred)
    return cov / (std_y_data * std_y_pred)


# Данные
x_data = [-2.45, -1.94, -1.43, -0.92, -0.41, 0.1, 0.61, 1.12]
y_data = [0.87, 1.19, 1.68, 2.23, 3.04, 4.15, 5.66, 7.72]

n = len(x_data)
vander_matrix = [[xi**i for i in range(n)] for xi in x_data]
print_vandermonde(vander_matrix)
print(f"\nЧисло обусловленности: {condition_number(vander_matrix):.2f}")

# Вычисление коэффициентов
a0, a1 = linear_approximize(x_data, y_data)
coefficients_linear = polynomial_approximation(x_data, y_data, 1)
coefficients_quadratic = polynomial_approximation(x_data, y_data, 2)
coefficients_cubic = polynomial_approximation(x_data, y_data, 3)
coefficients_gauss = gauss_interpolation_coefficients(x_data, y_data)
coefficients_quadratic_mse = least_squares(x_data, y_data, degree=3)

# Генерация точек для графиков
x_plot = np.linspace(min(x_data), max(x_data), 500)
lagrange_func = lagrange_interpolation(x_data[:6], y_data[:6])

# Предсказания для R²
y_pred_lagrange = [lagrange_func(x) for x in x_data]
y_pred_linear = [a0 + a1*x for x in x_data]
y_pred_quadratic = [eval_polynomial(coefficients_quadratic, x) for x in x_data]
y_pred_cubic = [eval_polynomial(coefficients_cubic, x) for x in x_data]

# Вычисление R²
r2_lagrange = calculate_r_squared(y_data, y_pred_lagrange)
r2_linear = calculate_r_squared(y_data, y_pred_linear)
r2_quadratic = calculate_r_squared(y_data, y_pred_quadratic)
r2_cubic = calculate_r_squared(y_data, y_pred_cubic)

corr_lagrange = corrcoef(y_data, y_pred_lagrange)
corr_linear = corrcoef(y_data, y_pred_linear)
corr_quadratic = corrcoef(y_data, y_pred_quadratic)
corr_cubic = corrcoef(y_data, y_pred_cubic)
print(f'\nКорреляция метода Лагранжа {corr_lagrange}')
print(f'Корреляция линейной аппроксимации {corr_linear}')
print(f'Корреляция квадратичной аппроксимации {corr_quadratic}')
print(f'Корреляция кубической аппроксимации {corr_cubic}')
