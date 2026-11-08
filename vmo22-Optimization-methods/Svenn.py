import numpy as np
import matplotlib.pyplot as plt
import math


# метод Пауэла (квадратичное интерполяции)
# 2*x**2 - 0.5**x - 3

def f(x, func_str):
    try:
        return eval(func_str, {"x": x, "np": np})
    except Exception as e:
        print(f"Ошибка при вычислении функции: {e}")
        return None


def algorithm(x0, h, func_str, max_iterations=100):
    k = 0
    # Шаг 1
    f0 = f(x0, func_str)
    f_left = f(x0 - h, func_str)

    # Шаг 2
    f_right = f(x0 + h, func_str)

    # Шаг 3
    if f_left >= f0 <= f_right:
        return (x0 - h, x0 + h, 0)

    # Шаг 4
    elif f_left <= f0 >= f_right:
        print("Ошибка, функция не является унимодальной.")
        return None

    # Шаг 5
    elif f_left >= f0 >= f_right:
        t = h
        a = x0
        x1 = x0 + h

    # Шаг 6
    else:
        t = -h
        b = x0
        x1 = x0 - h

    k = 1
    while k < max_iterations:

        # Шаг 7
        x_next = x1 + (2 ** k) * t
        f_next = f(x_next, func_str)

        # Шаг 8
        if f_next < f(x1, func_str):
            if t > 0:
                a = x1
            else:
                b = x1

        # Шаг 9
        else:
            if t > 0:
                b = x_next
            else:
                a = x_next
            break

        x1 = x_next
        k += 1

    return (a, b, k)


def quadratic_interpolation(search_interval, func_str, tol=10**(-10), max_iter=100):

    a, b = search_interval
    x1 = a
    x3 = b
    x2 = (a + b) / 2  # средняя точка
    count = 0

    f = lambda x: eval(func_str)

    for _ in range(max_iter):
        count += 1
        f1, f2, f3 = f(x1), f(x2), f(x3)

        # Коэффициенты квадратичного полинома P(x) = A*x^2 + B*x + C
        A = ((f3 - f1) / (x3 - x1) - (f2 - f1) / (x2 - x1)) / (x3 - x2)
        B = (f2 - f1) / (x2 - x1) - A * (x1 + x2)
        # C = f1 - A * x1 ** 2 - B * x1

        # Находим вершину параболы (минимум)
        x_min_quad = -B / (2 * A) if A != 0 else x2

        # Проверяем, находится ли x_min_quad внутри интервала
        if x_min_quad < x1 or x_min_quad > x3:
            x_min_quad = x2

        f_min_quad = f(x_min_quad)

        # Критерий остановки
        if abs(x_min_quad - x2) < tol:
            return x_min_quad, f_min_quad, count

        # Обновляем точки для следующей итерации
        if x_min_quad < x2:
            if f_min_quad < f2:
                x3, f3 = x2, f2
                x2, f2 = x_min_quad, f_min_quad
            else:
                x1, f1 = x_min_quad, f_min_quad
        else:
            if f_min_quad < f2:
                x1, f1 = x2, f2
                x2, f2 = x_min_quad, f_min_quad
            else:
                x3, f3 = x_min_quad, f_min_quad

    # Если достигнуто максимальное число итераций
    return x2, f2

'''
x0 = float(input("x0 = "))
h = float(input("h = "))
'''

func_str = input("f(x) = ")

vals = [(1,1), (1,0.5), (2,1), (5,3), (-1,1)]

intervals = [algorithm(v[0], v[1], func_str) for v in vals]
for interval in intervals:
    a, b, iterations = interval
    print(f"Найденный интервал минимума: [{a:.4f}, {b:.4f}]")
    print(f"Количество итераций: {iterations}")

    x_values = np.linspace(a, b, 1000)
    f_values = [f(x, func_str) for x in x_values]
    # min_x = x_values[np.argmin(f_values)]
    # min_y = min

    min_x, min_y, iterations2 = quadratic_interpolation((a,b), func_str)

    print(f"\nМинимум функции: x = {min_x:.10f}, f(x) = {min_y:.10f}")
    print(f"Количество итераций: {iterations2}\n\n")

    plt.plot(x_values, f_values, label=f"f(x) = {func_str}", color="blue")
    plt.scatter(min_x, min_y, color="red", zorder=3, label=f"Minimum at x = {min_x:.4f}")
    plt.fill_between(x_values, f_values, where=((x_values >= a) & (x_values <= b)), color='yellow', alpha=0.3)
    plt.axhline(0, color='black', lw=0.5)
    plt.axvline(min_x, color='red', linestyle='--')
    plt.xlabel("x")
    plt.ylabel("f(x)")
    plt.legend()
    plt.grid()
    plt.show()

