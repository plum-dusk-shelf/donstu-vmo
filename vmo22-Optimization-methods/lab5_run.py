from lab5 import *
from scipy.optimize import minimize

def one_dem():
    funcs_1d = [lambda x: (x[0]-5)**2, lambda x: 2*x[0]**2 - 0.5**x[0] - 3, lambda x: 3 * x[0]**4 + 4 *x[0]**3 - 12 *x[0]**2 - 5]
    func_1d = funcs_1d[2]

    print("1D пример:")
    x0_1d = [2]
    res1 = gradient_descent(func_1d, x0_1d)
    plot_optimization(res1[1], func_1d)
    scipy_min = minimize(func_1d, x0_1d, method='BFGS')
    print(f"Результат: {res1[0]}, значение функции: {func_1d(res1[0]):.4f}, количество итераций: {len(res1[1])} \nЗначение scipy x: {scipy_min.x} y: {scipy_min.fun}")

def two_dems():
    funcs_2d = [lambda x: x[0]**2 - x[0]*x[1] + 3*x[1]**2 - x[0],
                lambda x: x[0]**2 + 2*x[1]**2 + np.exp(x[0]+x[1])]
    func_2d = funcs_2d[0]

    print("2D пример:")
    x0_2d = [-1.5, 2.5]
    res2 = gradient_descent(func_2d, x0_2d)
    plot_optimization(res2[1], func_2d)
    scipy_min = minimize(func_2d, x0_2d, method='BFGS')
    print(f"Результат: {res2[0]}, значение функции: {func_2d(res2[0]):.4f}, количество итераций: {len(res2[1])} \nЗначение scipy x: {scipy_min.x} y: {scipy_min.fun}")

def three_dems():
    print("\n3D пример:")
    funcs_3d = [lambda x: 2*x[0]**2 + 4*x[1]**2 + 8*x[2]**2 +2*x[0]*x[1] - x[0]*x[2] + 2*x[1]*x[2] + 6*x[0] - 7*x[2],
                lambda x: x[0]**2 + x[1]**2 + x[2]**2,
                lambda x: x[0]**4 + x[1]**2 + x[2]**2 + x[0]*x[1] + x[1]*x[2]]
    func_3d = funcs_3d[2]
    x0_3d = [1.0, 2.0, -1.0]
    res3 = gradient_descent(func_3d, x0_3d)
    scipy_min = minimize(func_3d, x0_3d, method='BFGS')
    print(f"Результат: {res3[0]}, значение функции: {func_3d(res3[0]):.4f}, количество итераций: {len(res3[1])} \nЗначение scipy x: {scipy_min.x} y: {scipy_min.fun}")

def run(demo_num):
    dems = [one_dem, two_dems, three_dems]

    if demo_num in range(len(dems)):
        dems[demo_num]()
    else:
        print('Ошибка размерности')

if __name__ == '__main__':
    run(int(input('Введите размерность: '))-1)
