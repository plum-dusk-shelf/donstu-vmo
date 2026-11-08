import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.patches import Polygon

def nelder_mead(f, x0, bounds=None, max_iter=1000, tol=10**(-6)):
    """
    Корректная реализация метода Нелдера-Мида для функций размерности 1-3
    с исправленным расчетом минимума.
    """
    # Преобразуем x0 в 1D массив numpy
    x0 = np.array(x0, dtype=float).flatten()
    dim = x0.size
    iteration = 0
    
    if dim not in [1, 2, 3]:
        raise ValueError("Поддерживаются только функции размерности 1, 2 или 3")
    
    # Инициализация симплекса
    simplex = _initialize_simplex(x0, dim)
    
    # Основной цикл оптимизации
    for iteration in range(max_iter):
        # Вычисляем значения функции в вершинах симплекса
        f_values = np.array([f(x) for x in simplex])
        
        # Сортируем симплекс по значениям функции
        order = np.argsort(f_values)
        simplex = simplex[order]
        f_values = f_values[order]
        
        # Проверка критерия остановки (разброс значений меньше tol)
        if np.max(f_values) - np.min(f_values) < tol:
            break
            
        # Вычисляем центр тяжести (без худшей точки)
        centroid = np.mean(simplex[:-1], axis=0)
        
        # Операция отражения
        xr = centroid + 1.0 * (centroid - simplex[-1])
        fr = f(xr)
        
        if fr < f_values[0]:
            # Операция расширения
            xe = centroid + 2.0 * (xr - centroid)
            fe = f(xe)
            simplex[-1] = xe if fe < fr else xr
        elif fr < f_values[-2]:
            simplex[-1] = xr
        else:
            # Операция сжатия
            if fr < f_values[-1]:
                xc = centroid + 0.5 * (xr - centroid)
            else:
                xc = centroid + 0.5 * (simplex[-1] - centroid)
            
            fc = f(xc)
            
            if fc < f_values[-1]:
                simplex[-1] = xc
            else:
                # Операция уменьшения
                simplex[1:] = simplex[0] + 0.5 * (simplex[1:] - simplex[0])
    
    # Возвращаем лучшую точку и значение функции
    best_idx = np.argmin([f(x) for x in simplex])
    _visualize_results(f, simplex, bounds, dim)
    return simplex[best_idx], f(simplex[best_idx]), iteration

def _initialize_simplex(x0, dim):
    """Инициализация симплекса для заданной размерности"""
    m = 0.05
    
    simplex = np.zeros((dim + 1, dim))
    simplex[0] = x0

    n = dim
    sqrt_n1 = np.sqrt(n + 1)
    denominator = n * np.sqrt(2)
    
    d1 = ((sqrt_n1 - 1) / denominator) * m
    d2 = ((sqrt_n1 + n - 1) / denominator) * m

    if dim == 1:
        return np.array([[x0[0]], [x0[0] + d1]])
    
    for i in range(dim):
        point = x0.copy()
        point[i] += d1
        simplex[i+1] = point
    
    return simplex

def _visualize_results(f, simplex, bounds, dim):
    """Визуализация результатов для разных размерностей"""
    plt.figure(figsize=(10, 7))
    
    if dim == 1:
        _plot_1d(f, simplex, bounds)
    elif dim == 2:
        _plot_2d(f, simplex, bounds)
    else:
        pass
    
    plt.tight_layout()
    plt.show()

def _plot_1d(f, simplex, bounds=None, ax=None, title='1D проекция'):
    """Обновленная 1D визуализация для работы с subplots"""
    if ax is None:
        ax = plt.gca()
    
    # Определяем границы
    if bounds is None:
        x_pad = 0.3 * (np.max(simplex) - np.min(simplex)) + 0.5
        x_min = np.min(simplex) - x_pad
        x_max = np.max(simplex) + x_pad
    else:
        x_min, x_max = bounds
    
    # Данные для графика
    x = np.linspace(x_min, x_max, 500)
    y = np.array([f(np.array([xi])) for xi in x])
    simplex_x = simplex.flatten()
    simplex_y = np.array([f(np.array([x])) for x in simplex_x])
    
    # Отрисовка
    ax.plot(x, y, 'b-', linewidth=1.5, label='Функция')
    ax.fill_between(simplex_x, simplex_y, max(y), color='red', alpha=0.15)
    ax.plot(simplex_x, simplex_y, 'r-', linewidth=2)
    ax.plot(simplex_x, simplex_y, 'ro', markersize=6)
    
    # Лучшая точка
    best_idx = np.argmin([f(np.array([x])) for x in simplex])
    ax.plot(simplex[best_idx], f(np.array([simplex[best_idx]])), 
            'g*', markersize=12, label='Лучшая точка')
    
    # Оформление
    ax.set_xlabel('x', fontsize=10)
    ax.set_ylabel('f(x)', fontsize=10)
    ax.set_title(title, fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9)

def _plot_2d(f, simplex, bounds=None, title='Метод Нелдера-Мида (2D)'):
    """Улучшенная визуализация для 2D случая с четким отображением симплекса"""
    # Определяем границы графика
    if bounds is None:
        # Добавляем 20% поля вокруг симплекса
        x_pad = 0.2 * (np.max(simplex[:,0]) - np.min(simplex[:,0])) + 0.1
        y_pad = 0.2 * (np.max(simplex[:,1]) - np.min(simplex[:,1])) + 0.1
        x_bounds = (np.min(simplex[:,0])-x_pad, np.max(simplex[:,0])+x_pad)
        y_bounds = (np.min(simplex[:,1])-y_pad, np.max(simplex[:,1])+y_pad)
    else:
        x_bounds, y_bounds = bounds
    
    # Создаем сетку для линий уровня
    x = np.linspace(*x_bounds, 100)
    y = np.linspace(*y_bounds, 100)
    X, Y = np.meshgrid(x, y)
    Z = np.array([[f(np.array([x, y])) for x, y in zip(row_x, row_y)] 
                 for row_x, row_y in zip(X, Y)])
    
    # Настройка графика
    plt.figure(figsize=(10, 8))
    
    # Линии уровня
    levels = np.linspace(np.min(Z), np.max(Z), 25)
    contour = plt.contour(X, Y, Z, levels=levels, alpha=0.4, linewidths=1)
    plt.clabel(contour, inline=True, fontsize=8)
    plt.colorbar(label='Значение функции', shrink=0.8)
    
    # Визуализация симплекса (треугольника)
    # 1. Заливка симплекса
    plt.fill(simplex[:,0], simplex[:,1], 'red', alpha=0.2, label='Симплекс')
    
    # 2. Границы симплекса (толстые линии)
    plt.plot(np.append(simplex[:,0], simplex[0,0]), 
             np.append(simplex[:,1], simplex[0,1]), 
             'r-', linewidth=2)
    
    # 3. Вершины симплекса (крупные точки)
    plt.plot(simplex[:,0], simplex[:,1], 'ro', markersize=8)
    
    # Подписи к вершинам
    for i, (x, y) in enumerate(simplex):
        plt.text(x, y, f'  {i+1}', fontsize=12, color='red',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    
    # Лучшая точка (минимум)
    f_values = np.array([f(point) for point in simplex])
    best_idx = np.argmin(f_values)
    plt.plot(simplex[best_idx,0], simplex[best_idx,1], 
             'g*', markersize=20, label='Лучшая точка')
    
    # Настройки оформления
    plt.xlabel('x1', fontsize=12)
    plt.ylabel('x2', fontsize=12)
    plt.title(title, fontsize=14)
    plt.grid(True, alpha=0.3)
    
    # Улучшенная легенда
    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(handles, labels, fontsize=10, loc='upper right')

if __name__ == "__main__":
    pass
