import numpy as np
from scipy.optimize import minimize_scalar, approx_fprime
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def gradient_descent(f, x0, epsilon=10**(-5), max_iter=1000, h=1e-6):
    """
    Метод наискорейшего градиентного спуска с поддержкой размерностей 1-3.
    
    Параметры:
    f - функция, которую нужно минимизировать
    x0 - начальная точка (число, список или массив numpy)
    epsilon - точность (критерий остановки)
    max_iter - максимальное число итераций
    h - шаг для численного дифференцирования
    
    Возвращает:
    x - найденную точку минимума
    history - историю приближений
    """
    x = np.array(x0, dtype='float64').flatten()
    dim = len(x)
    
    if dim < 1 or dim > 3:
        raise ValueError("Размерность должна быть от 1 до 3")
    
    history = [x.copy()]
    
    for _ in range(max_iter):
        gradient = approx_fprime(x, f, h)
        
        if np.linalg.norm(gradient) < epsilon:
            break
            
        def phi(alpha):
            return f(x - alpha * gradient)
        
        res = minimize_scalar(phi, bounds=(0, 1), method='bounded')
        alpha = res.x
        
        x = x - alpha * gradient
        history.append(x.copy())
    
    return x, np.array(history)

def plot_optimization(history, f):
    """Визуализация процесса оптимизации в зависимости от размерности"""
    dim = history.shape[1]
    
    if dim == 1:
        _plot_1d(history, f)
    elif dim == 2:
        _plot_2d(history, f)
    elif dim == 3:
        _plot_3d(history, f)

def _plot_1d(history, f):
    """Визуализация для 1D случая"""
    x = np.linspace(min(history[:,0])-1, max(history[:,0])+1, 400)
    y = [f([xi]) for xi in x]
    
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, label='Функция')
    plt.scatter(history[:,0], [f([xi]) for xi in history[:,0]], 
               c='r', marker='o', label='Шаги оптимизации')
    plt.plot(history[:,0], [f([xi]) for xi in history[:,0]], 'r--')
    plt.title('Градиентный спуск (1D)')
    plt.xlabel('x')
    plt.ylabel('f(x)')
    plt.legend()
    plt.grid(True)
    plt.show()

def _plot_2d(history, f):
    """Визуализация для 2D случая"""
    x = np.linspace(min(history[:,0])-1, max(history[:,0])+1, 100)
    y = np.linspace(min(history[:,1])-1, max(history[:,1])+1, 100)
    X, Y = np.meshgrid(x, y)
    
    Z = np.zeros_like(X)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            Z[i,j] = f([X[i,j], Y[i,j]])
    
    plt.figure(figsize=(10, 6))
    plt.contour(X, Y, Z, levels=20)
    plt.plot(history[:,0], history[:,1], 'ro-', markersize=4, linewidth=1)
    plt.title('Градиентный спуск (2D)')
    plt.xlabel('x1')
    plt.ylabel('x2')
    plt.colorbar()
    plt.show()

# Примеры использования для разных размерностей
if __name__ == "__main__":
    print("=== 1D пример ===")
    def f1(x):
        return (x[0]+5)**2
        #return x[0]**4 - 3*x[0]**3 + 2
    
    x0_1d = [0.0]
    x_min, history = gradient_descent(f1, x0_1d)
    print(f"Минимум: {x_min}, значение функции: {f1(x_min):.6f}")
    plot_optimization(history, f1)
    
    print("\n=== 2D пример ===")
    def f2(x):
        return x[0]**2 + 5*x[1]**2 + 2*x[0]*x[1]
    
    x0_2d = [10.0, 10.0]
    x_min, history = gradient_descent(f2, x0_2d)
    print(f"Минимум: {x_min}, значение функции: {f2(x_min):.6f}")
    plot_optimization(history, f2)
    
    print("\n=== 3D пример ===")
    def f3(x):
        return x[0]**2 + 3*x[1]**2 + 2*x[2]**2 + x[0]*x[1] - x[1]*x[2] + 2*x[0]
    
    x0_3d = [5.0, -3.0, 2.0]
    x_min, history = gradient_descent(f3, x0_3d)
    print(f"Минимум: {x_min}, значение функции: {f3(x_min):.6f}")
    plot_optimization(history, f3)
