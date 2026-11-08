import numpy as np
from fractions import Fraction
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import scrolledtext
import sys
import io
from itertools import combinations, product
from scipy.optimize import linprog
from itertools import permutations
from scipy.optimize import linprog, minimize
# ============================================================
# Класс LemkeHowson и связанные функции (ваш исходный код)
# ============================================================
class LemkeHowson:
    def __init__(self, A, B):
        self.A = np.array(A, dtype=float)
        self.B = np.array(B, dtype=float)
        self.m, self.n = self.A.shape
        self.pivot_row_A = None
        self.pivot_col_A = None
        self.pivot_row_B = None
        self.pivot_col_B = None

    def _to_frac(self, x):
        if abs(x) < 1e-10:
            return "0"
        frac = Fraction(x).limit_denominator(100)
        if abs(float(frac) - x) < 1e-8:
            return str(frac)
        return f"{x:.4f}"

    def _find_pivot_in_row(self, row, start_col=0, end_col=None):
        if end_col is None:
            end_col = len(row)
        min_positive = None
        min_col = -1
        for j in range(start_col, end_col):
            if row[j] > 0:
                if min_positive is None or row[j] < min_positive:
                    min_positive = row[j]
                    min_col = j
        return min_col, min_positive

    def _generate_col_names_A(self):
        names = []
        for i in range(self.m):
            names.append(f'a{i + 1}')
        for i in range(self.n):
            names.append(f'e{i + 1}')
        return names

    def _generate_col_names_B(self):
        names = []
        for i in range(self.n):
            names.append(f'b{i + 1}')
        for i in range(self.m):
            names.append(f'f{i + 1}')
        return names

    def _print_tableau(self, title, tableau, col_names, extra_col=None, extra_name=None, bottom_row=None):
        print(f"\n{title}:")
        if extra_col is not None:
            header = "     " + "  ".join(f"{name:>6}" for name in col_names) + f"  {extra_name:>6}"
        else:
            header = "     " + "  ".join(f"{name:>6}" for name in col_names)
        print(header)
        print("    " + "-" * (7 + 7 * len(col_names) + (7 if extra_col is not None else 0)))
        for i, row in enumerate(tableau):
            if extra_col is not None:
                row_str = f"стр{i + 1} " + "  ".join(
                    f"{self._to_frac(val):>6}" for val in row) + f"  {self._to_frac(extra_col[i]):>6}"
            else:
                row_str = f"стр{i + 1} " + "  ".join(f"{self._to_frac(val):>6}" for val in row)
            print(row_str)

        if bottom_row is not None:
            row_str = "q    " + "  ".join(f"{self._to_frac(val):>6}" for val in bottom_row)
            print(row_str)

    def _simplex_step(self, tableau, pivot_row, pivot_col):
        tableau = tableau.copy()
        pivot = tableau[pivot_row, pivot_col]
        tableau[pivot_row, :] /= pivot
        for i in range(tableau.shape[0]):
            if i != pivot_row:
                factor = tableau[i, pivot_col]
                tableau[i, :] -= factor * tableau[pivot_row, :]
        return tableau

    def _compute_lambdas_with_print(self, table, xi, y0, q_row, name):
        size = table.shape[0]
        lambdas = []

        for j in range(size):
            print(f"\n{'-' * 60}")
            print(f"j = {j + 1}:")
            row = table[j, :]
            print(f"  Строка {j + 1}: {[self._to_frac(x) for x in row]}")
            print(f"  Строка q:     {[self._to_frac(x) for x in q_row]}")

            lambda_star_vals = []
            lambda_star_star_vals = []
            lambda_star_details = []
            lambda_star_star_details = []

            for col, alpha in enumerate(row):
                if abs(alpha) < 1e-10:
                    print(f"  α[{col + 1}] = 0 → пропускаем")
                    continue

                if (name == "A" and col < self.m) or (name == "B" and col < self.n):
                    value = -(xi[col] - 1) / alpha
                    formula = f"-({self._to_frac(xi[col])} - 1)/{self._to_frac(alpha)}"
                    val_str = f"{formula} = {self._to_frac(value)}"
                else:
                    q_val = q_row[col]
                    if abs(q_val) < 1e-10:
                        print(f"  α[{col + 1}] = {self._to_frac(alpha)}, q = 0 → пропускаем")
                        continue
                    r = col - self.m if name == "A" else col - self.n
                    value = -y0[r] / alpha
                    formula = f"-({self._to_frac(y0[r])})/{self._to_frac(alpha)}"
                    val_str = f"{formula} = {self._to_frac(value)}"

                if alpha < 0:
                    lambda_star_vals.append(value)
                    lambda_star_details.append(f"    α={self._to_frac(alpha)} < 0 → λ* = {val_str}")
                    print(f"  α[{col + 1}] = {self._to_frac(alpha)} < 0 → λ* = {val_str}")
                else:
                    lambda_star_star_vals.append(value)
                    lambda_star_star_details.append(f"    α={self._to_frac(alpha)} > 0 → λ** = {val_str}")
                    print(f"  α[{col + 1}] = {self._to_frac(alpha)} > 0 → λ** = {val_str}")

            lambda_val = 0
            print(f"\n  --- Результат для j={j + 1} ---")

            if lambda_star_vals:
                positive_vals = [v for v in lambda_star_vals if v > 1e-10]
                if positive_vals:
                    lambda_val = min(positive_vals)
                    print(f"  λ* (для α<0): {', '.join(self._to_frac(v) for v in positive_vals)}")
                    print(
                        f"  λ* = min({', '.join(self._to_frac(v) for v in positive_vals)}) = {self._to_frac(lambda_val)}")
                else:
                    print(f"  λ*: нет положительных значений (все ≤ 0)")
            else:
                print(f"  λ*: нет значений с α<0")

            if lambda_star_star_vals:
                lambda_val_star_star = max(lambda_star_star_vals)
                print(f"  λ** (для α>0): {', '.join(self._to_frac(v) for v in lambda_star_star_vals)}")
                print(
                    f"  λ** = max({', '.join(self._to_frac(v) for v in lambda_star_star_vals)}) = {self._to_frac(lambda_val_star_star)}")
                if not lambda_star_vals:
                    lambda_val = lambda_val_star_star
            else:
                print(f"  λ**: нет значений с α>0")

            print(f"  → Итоговое λ_{j + 1} = {self._to_frac(lambda_val)}")
            lambdas.append(lambda_val)

        return lambdas

    def solve(self):
        print("=" * 70)
        print("МАТРИЦА A (игрок A):")
        print(self.A)
        print("\nМАТРИЦА B (игрок B):")
        print(self.B)

        # Шаг 1
        max_val = max(np.max(self.A), np.max(self.B))
        d = max_val + 1
        print(f"\n{'=' * 70}")
        print(f"ШАГ 1: Вычисление d = max(A,B) + 1")
        print(f"max(A,B) = {max_val} → d = max(A,B) + 1 = {d}")
        print(f"{'=' * 70}")

        # Шаг 2 
        A1 = d - self.A
        B1 = d - self.B
        print(f"\nШАГ 2: Преобразование матриц A1 = d·1 - A, B1 = d·1 - B")
        print(f"A1 = {d} - A:")
        print(A1)
        print(f"\nB1 = {d} - B:")
        print(B1)

        # Шаг 3 y^0
        print(f"\n{'=' * 70}")
        print("ШАГ 3: Выбор начальной точки y⁰")
        print(f"{'=' * 70}")
        first_col = A1[:, 0]
        min_val = np.min(first_col)
        min_row = np.argmin(first_col)
        y0 = np.zeros(self.n)
        y0[0] = 1 / min_val
        print(f"Первый столбец A1: {[self._to_frac(x) for x in first_col]}")
        print(f"Минимальный элемент = {min_val} (строка {min_row + 1})")
        print(f"y⁰[1] = 1/{min_val} = {self._to_frac(y0[0])}")
        print(f"y⁰ = {[self._to_frac(x) for x in y0]}")

        # Шаг 4 x^0
        print(f"\n{'=' * 70}")
        print("ШАГ 4: Выбор начальной точки x⁰")
        print(f"{'=' * 70}")
        row_B1 = B1[min_row, :]
        min_val_B = np.min(row_B1)
        min_col_B = np.argmin(row_B1)
        x0 = np.zeros(self.m)
        x0[min_row] = 1 / min_val_B
        print(f"Строка {min_row + 1} из B1: {[self._to_frac(x) for x in row_B1]}")
        print(f"Минимальный элемент = {min_val_B} (столбец {min_col_B + 1})")
        print(f"x⁰[{min_row + 1}] = 1/{min_val_B} = {self._to_frac(x0[min_row])}")
        print(f"x⁰ = {[self._to_frac(x) for x in x0]}")

        # Шаг 5: Проверка равновесия
        print(f"\n{'=' * 70}")
        print("ШАГ 5: Проверка условий равновесия для (x⁰, y⁰)")
        print(f"{'=' * 70}")
        print("Условие: (eⱼᵀ·y⁰)·(bⱼᵀ·x⁰ − 1) = 0 для всех j")

        is_nash = True
        for j in range(self.n):
            bj = B1[:, j]
            bjTx0 = np.dot(bj, x0)
            y0j = y0[j]
            product = y0j * (bjTx0 - 1)

            print(f"\n  j = {j + 1}:")
            print(f"    y⁰[{j + 1}] = {self._to_frac(y0j)}")
            print(f"    b_{j + 1}ᵀ·x⁰ = {self._to_frac(bjTx0)}")
            print(f"    (b_{j + 1}ᵀ·x⁰ - 1) = {self._to_frac(bjTx0 - 1)}")
            print(f"    Произведение = {self._to_frac(y0j)} × {self._to_frac(bjTx0 - 1)} = {self._to_frac(product)}")

            if abs(product) > 1e-8:
                is_nash = False
                print(f"    ✗ {self._to_frac(product)} ≠ 0 → НАРУШЕНИЕ!")
                break
            else:
                print(f"    ✓ {self._to_frac(product)} = 0 → выполняется")

        if is_nash:
            # нормировка стратегий
            sum_x = np.sum(x0)
            sum_y = np.sum(y0)
            if abs(sum_x - 1) > 1e-10 or abs(sum_y - 1) > 1e-10:
                x0 = x0 / sum_x
                y0 = y0 / sum_y
            print("\n✓ РАВНОВЕСИЕ НАЙДЕНО!")
            return x0, y0
        print("\n✗ Равновесие не найдено, производим замену базиса")

        # Шаг 6
        print(f"\n{'=' * 70}")
        print("ШАГ 6: Построение симплекс-таблиц A₀ и B₀")
        print(f"{'=' * 70}")
        A1T = A1.T
        I_n = np.eye(self.n)
        A0 = np.hstack([A1T, I_n])
        col_names_A = self._generate_col_names_A()
        self._print_tableau(f"A₀ = (A₁ᵀ | I_{self.n})", A0, col_names_A)

        I_m = np.eye(self.m)
        B0 = np.hstack([B1, I_m])
        col_names_B = self._generate_col_names_B()
        self._print_tableau(f"B₀ = (B₁ | I_{self.m})", B0, col_names_B)

        # Шаг 7
        print(f"\n{'=' * 70}")
        print("ШАГ 7: Замена базиса (первая итерация)")
        print(f"{'=' * 70}")

        print("\nДля таблицы A:")
        pivot_row_A = -1
        for i in range(self.n):
            if y0[i] > 0:
                pivot_row_A = i
                break
        self.pivot_row_A = pivot_row_A
        print(f"  Выводим e{pivot_row_A + 1} (строка {pivot_row_A + 1})")

        row_A = A0[pivot_row_A, :self.m]
        pivot_col_A, pivot_A = self._find_pivot_in_row(row_A, 0, self.m)
        self.pivot_col_A = pivot_col_A
        print(f"  Наименьший положительный в строке: {self._to_frac(pivot_A)} (столбец a{pivot_col_A + 1})")
        print(f"  Вводим a{pivot_col_A + 1}")

        A1_star = self._simplex_step(A0, pivot_row_A, pivot_col_A)
        self._print_tableau("A₁*", A1_star, col_names_A)

        print("\nДля таблицы B:")
        pivot_row_B = -1
        for i in range(self.m):
            if x0[i] > 0:
                pivot_row_B = i
                break
        self.pivot_row_B = pivot_row_B
        print(f"  Выводим f{pivot_row_B + 1} (строка {pivot_row_B + 1})")

        row_B = B0[pivot_row_B, :self.n]
        pivot_col_B, pivot_B = self._find_pivot_in_row(row_B, 0, self.n)
        self.pivot_col_B = pivot_col_B
        print(f"  Наименьший положительный в строке: {self._to_frac(pivot_B)} (столбец b{pivot_col_B + 1})")
        print(f"  Вводим b{pivot_col_B + 1}")

        B1_star = self._simplex_step(B0, pivot_row_B, pivot_col_B)
        self._print_tableau("B₁*", B1_star, col_names_B)

        # Шаг 8
        print(f"\n{'=' * 70}")
        print("ШАГ 8: Вычисление векторов ξ и η")
        print(f"{'=' * 70}")
        xi = [np.dot(A1[i, :], y0) for i in range(self.m)]
        print(f"ξ = (A1·y⁰) = ({', '.join(self._to_frac(x) for x in xi)})")

        eta = [np.dot(B1[:, j], x0) for j in range(self.n)]
        print(f"η = (B1ᵀ·x⁰) = ({', '.join(self._to_frac(x) for x in eta)})")

        # Шаг 9
        print(f"\n{'=' * 70}")
        print("ШАГ 9: Формирование строк q для таблиц")
        print(f"{'=' * 70}")
        xi_minus_1 = [x - 1 for x in xi]
        q_row_A = xi_minus_1 + list(y0)
        print(f"q_A = (ξ-1, y⁰) = ({', '.join(self._to_frac(x) for x in q_row_A)})")

        eta_minus_1 = [x - 1 for x in eta]
        q_row_B = eta_minus_1 + list(x0)
        print(f"q_B = (η-1, x⁰) = ({', '.join(self._to_frac(x) for x in q_row_B)})")

        # Шаг 10: Вычисление λ
        print(f"\n{'=' * 70}")
        print("ШАГ 10: Вычисление λ для таблицы A")
        print("=" * 70)
        print("Формулы:")
        print("  Для a-столбцов: λ = -(ξₖ - 1)/α")
        print("  Для e-столбцов: λ = -y_r⁰/α")
        print("  λ* = min{λ для α < 0} (только положительные)")
        print("  λ** = max{λ для α > 0} (если нет λ*, то λ = λ**)")
        print("=" * 70)

        lambdas = self._compute_lambdas_with_print(A1_star, xi, y0, q_row_A, "A")
        print(f"\nИТОГОВЫЕ λ = ({', '.join(self._to_frac(x) for x in lambdas)})")

        # Шаг 10b: Вычисление μ
        print(f"\n{'=' * 70}")
        print("ШАГ 10b: Вычисление μ для таблицы B")
        print("=" * 70)
        print("Формулы:")
        print("  Для b-столбцов: μ = -(ηₗ - 1)/β")
        print("  Для f-столбцов: μ = -x_s⁰/β")
        print("  μ* = min{μ для β < 0} (только положительные)")
        print("  μ** = max{μ для β > 0} (если нет μ*, то μ = μ**)")
        print("=" * 70)

        mus = self._compute_lambdas_with_print(B1_star, eta, x0, q_row_B, "B")
        print(f"\nИТОГОВЫЕ μ = ({', '.join(self._to_frac(x) for x in mus)})")

        # Шаг 11
        print(f"\n{'=' * 70}")
        print("ШАГ 11: Таблицы с добавленными столбцами λ и μ")
        print(f"{'=' * 70}")
        self._print_tableau("A₁* с добавленным столбцом λ", A1_star, col_names_A, lambdas, "λ", q_row_A)
        self._print_tableau("B₁* с добавленным столбцом μ", B1_star, col_names_B, mus, "μ", q_row_B)

        # Шаг 12: Построение новых y_i
        print(f"\n{'=' * 70}")
        print("ШАГ 12: Построение новых векторов yᵢ")
        print("=" * 70)
        print("Формула: yᵢ = y⁰ + λᵢ · (строка i из e-столбцов)")
        print("-" * 50)

        e_indices = [i for i, name in enumerate(col_names_A) if name.startswith('e')]

        y_vectors = []
        for i, lam in enumerate(lambdas):
            e_row = [A1_star[i, idx] for idx in e_indices]
            print(f"\n  y{i + 1} = y⁰ + λ_{i + 1}·(строка {i + 1} из e-столбцов)")
            print(f"    y⁰ = ({', '.join(self._to_frac(v) for v in y0)})")
            print(f"    λ_{i + 1} = {self._to_frac(lam)}")
            print(f"    e-строка {i + 1} = ({', '.join(self._to_frac(v) for v in e_row)})")
            print(f"    λ·e-строка = ({', '.join(self._to_frac(lam * v) for v in e_row)})")
            y_new = y0 + lam * np.array(e_row)
            y_new = np.maximum(y_new, 0)
            print(f"    y{i + 1} = ({', '.join(self._to_frac(v) for v in y_new)})")
            y_vectors.append(y_new)

        # Шаг 12b: Построение новых x_i
        print(f"\n{'=' * 70}")
        print("ШАГ 12b: Построение новых векторов xᵢ")
        print("=" * 70)
        print("Формула: xᵢ = x⁰ + μᵢ · (строка i из f-столбцов)")
        print("-" * 50)

        f_indices = [i for i, name in enumerate(col_names_B) if name.startswith('f')]

        x_vectors = []
        for i, mu in enumerate(mus):
            f_row = [B1_star[i, idx] for idx in f_indices]
            print(f"\n  x{i + 1} = x⁰ + μ_{i + 1}·(строка {i + 1} из f-столбцов)")
            print(f"    x⁰ = ({', '.join(self._to_frac(v) for v in x0)})")
            print(f"    μ_{i + 1} = {self._to_frac(mu)}")
            print(f"    f-строка {i + 1} = ({', '.join(self._to_frac(v) for v in f_row)})")
            print(f"    μ·f-строка = ({', '.join(self._to_frac(mu * v) for v in f_row)})")
            x_new = x0 + mu * np.array(f_row[:self.m])
            x_new = np.maximum(x_new, 0)
            print(f"    x{i + 1} = ({', '.join(self._to_frac(v) for v in x_new)})")
            x_vectors.append(x_new)

        # ШАГ 13: Матрицы в новом базисе
        print(f"\n{'=' * 70}")
        print("ШАГ 13: Матрицы в новом базисе после замены")
        print("=" * 70)

        new_basis_A = []
        for i in range(self.n):
            if i == self.pivot_row_A:
                new_basis_A.append(f'a{self.pivot_col_A + 1}')
            else:
                new_basis_A.append(f'e{i + 1}')

        print(f"\nНовый базис Q(y) = {{{', '.join(new_basis_A)}}}")
        print(f"\nМатрица A в новом базисе (диагональная матрица λ):")
        print("         " + "  ".join(f"{name:>6}" for name in new_basis_A))
        print("    " + "-" * (7 + 7 * len(new_basis_A)))

        diag_matrix_A = np.zeros((self.n, self.n))
        for i in range(self.n):
            diag_matrix_A[i, i] = lambdas[i]

        for i in range(self.n):
            row_str = f"стр{i + 1} "
            for j in range(self.n):
                row_str += f"  {self._to_frac(diag_matrix_A[i, j]):>6}"
            print(row_str)

        new_basis_B = []
        for i in range(self.m):
            if i == self.pivot_row_B:
                new_basis_B.append(f'b{self.pivot_col_B + 1}')
            else:
                new_basis_B.append(f'f{i + 1}')

        print(f"\nНовый базис P(x) = {{{', '.join(new_basis_B)}}}")
        print(f"\nМатрица B в новом базисе (диагональная матрица μ):")
        print("         " + "  ".join(f"{name:>6}" for name in new_basis_B))
        print("    " + "-" * (7 + 7 * len(new_basis_B)))

        diag_matrix_B = np.zeros((self.m, self.m))
        for i in range(self.m):
            diag_matrix_B[i, i] = mus[i]

        for i in range(self.m):
            row_str = f"стр{i + 1} "
            for j in range(self.m):
                row_str += f"  {self._to_frac(diag_matrix_B[i, j]):>6}"
            print(row_str)

        print(f"\nЗначения λ (диагональ матрицы A): {[self._to_frac(x) for x in lambdas]}")
        print(f"Значения μ (диагональ матрицы B): {[self._to_frac(x) for x in mus]}")

        # ШАГ 14: Поиск равновесия
        print(f"\n{'=' * 70}")
        print("ШАГ 14: Поиск равновесной ситуации")
        print("=" * 70)

        a_indices = [int(var[1:]) - 1 for var in new_basis_A if var.startswith('a')]
        b_indices = [int(var[1:]) - 1 for var in new_basis_B if var.startswith('b')]

        print(f"\nАктивные стратегии A (индексы a в Q(y)): {[i + 1 for i in a_indices]}")
        print(f"Активные стратегии B (индексы b в P(x)): {[i + 1 for i in b_indices]}")

        print("\nВекторы xᵢ:")
        for i, x in enumerate(x_vectors):
            x_pos = [idx for idx, val in enumerate(x) if val > 1e-10]
            print(
                f"  x{i + 1} = {[self._to_frac(v) for v in x]} → положительные компоненты: {[idx + 1 for idx in x_pos]}")

        print("\nВекторы yⱼ:")
        for j, y in enumerate(y_vectors):
            y_pos = [idx for idx, val in enumerate(y) if val > 1e-10]
            print(
                f"  y{j + 1} = {[self._to_frac(v) for v in y]} → положительные компоненты: {[idx + 1 for idx in y_pos]}")

        # Поиск равновесия
        best_x = None
        best_y = None
        best_x_idx = -1
        best_y_idx = -1

        print("\nПроверка условий равновесия (дополняющая нежесткость):")
        print("  Условие 1: если x[k] > 0, то (A1[k,:]·y - 1) = 0")
        print("  Условие 2: если y[l] > 0, то (B1[:,l]·x - 1) = 0")

        for i, x in enumerate(x_vectors):
            for j, y in enumerate(y_vectors):
                condition1 = True
                condition2 = True

                for k in range(self.m):
                    val = np.dot(A1[k, :], y) - 1
                    if x[k] > 1e-10 and abs(val) > 1e-8:
                        condition1 = False
                        break

                for l in range(self.n):
                    val = np.dot(B1[:, l], x) - 1
                    if y[l] > 1e-10 and abs(val) > 1e-8:
                        condition2 = False
                        break

                if condition1 and condition2 and np.sum(x) > 1e-10 and np.sum(y) > 1e-10:
                    best_x = x
                    best_y = y
                    best_x_idx = i
                    best_y_idx = j
                    print(f"\n  ✓ Найдена равновесная пара (x{best_x_idx + 1}, y{best_y_idx + 1})")
                    print(f"    x = {[self._to_frac(v) for v in x]}")
                    print(f"    y = {[self._to_frac(v) for v in y]}")
                    break
            if best_x is not None:
                break

        if best_x is None:
            print("\n  ✗ Не найдено пар по условиям равновесия")
            best_x = x_vectors[0]
            best_y = y_vectors[0]
            best_x_idx = 0
            best_y_idx = 0
            print(f"  Используем (x1, y1)")

        x_eq = best_x
        y_eq = best_y

        print(f"\nВыбрана равновесная ситуация:")
        print(f"  X̃ = x{best_x_idx + 1} = {[self._to_frac(v) for v in x_eq]}")
        print(f"  Ỹ = y{best_y_idx + 1} = {[self._to_frac(v) for v in y_eq]}")

        # ШАГ 15: Нормировка
        print(f"\n{'=' * 70}")
        print("ШАГ 15: Нормировка")
        print("=" * 70)
        print("Формулы: x* = X̃ / ΣX̃, y* = Ỹ / ΣỸ")
        print("-" * 50)

        sum_x = np.sum(x_eq)
        sum_y = np.sum(y_eq)

        # Динамическое формирование строки для x_eq
        x_eq_str = ' + '.join(self._to_frac(v) for v in x_eq)
        print(f"ΣX̃ = {x_eq_str} = {self._to_frac(sum_x)}")

        # Динамическое формирование строки для y_eq
        y_eq_str = ' + '.join(self._to_frac(v) for v in y_eq)
        print(f"ΣỸ = {y_eq_str} = {self._to_frac(sum_y)}")

        x_star = x_eq / sum_x
        y_star = y_eq / sum_y

        print(
            f"\nx* = X̃ / ΣX̃ = ({', '.join(self._to_frac(v) for v in x_eq)}) / {self._to_frac(sum_x)} = ({', '.join(self._to_frac(v) for v in x_star)})")
        print(
            f"y* = Ỹ / ΣỸ = ({', '.join(self._to_frac(v) for v in y_eq)}) / {self._to_frac(sum_y)} = ({', '.join(self._to_frac(v) for v in y_star)})")

        # ШАГ 16: Цены игры
        print(f"\n{'=' * 70}")
        print("ШАГ 16: Вычисление выигрышей")
        print("=" * 70)
        print(f"Формулы: H_A = d - 1/ΣỸ, H_B = d - 1/ΣX̃")
        print("-" * 50)

        H_A = d - 1 / sum_y
        H_B = d - 1 / sum_x

        print(
            f"H_A = {d} - 1/{self._to_frac(sum_y)} = {d} - {self._to_frac(1 / sum_y)} = {self._to_frac(H_A)} = {float(H_A):.4f}")
        print(
            f"H_B = {d} - 1/{self._to_frac(sum_x)} = {d} - {self._to_frac(1 / sum_x)} = {self._to_frac(H_B)} = {float(H_B):.4f}")

        # ИТОГОВЫЙ ОТВЕТ
        print("\n" + "=" * 70)
        print("ИТОГОВЫЙ ОТВЕТ")
        print("=" * 70)
        print(f"x* = ({', '.join(self._to_frac(v) for v in x_star)})")
        print(f"y* = ({', '.join(self._to_frac(v) for v in y_star)})")
        print(f"H_A = {self._to_frac(H_A)}")
        print(f"H_B = {self._to_frac(H_B)}")

        print(f"\nФинальный результат:")
        print(f"{' '.join(self._to_frac(v) for v in x_star)} x*")
        print(f"{' '.join(self._to_frac(v) for v in y_star)} y*")
        print(f"Ha = {self._to_frac(H_A)} Hb = {self._to_frac(H_B)}")

        return x_star, y_star


class BimatrixGame:
    def __init__(self, A, B):
        self.A = np.array(A, dtype=float)
        self.B = np.array(B, dtype=float)
        self.m, self.n = self.A.shape

    def find_mixed_nash_2x2(self):
        a11, a12 = self.A[0, 0], self.A[0, 1]
        a21, a22 = self.A[1, 0], self.A[1, 1]
        b11, b12 = self.B[0, 0], self.B[0, 1]
        b21, b22 = self.B[1, 0], self.B[1, 1]

        a1 = a11 - a12 - a21 + a22
        a2 = a22 - a12
        b1 = b11 - b12 - b21 + b22
        b2 = b22 - b21

        if abs(a1) > 1e-10 and abs(b1) > 1e-10:
            x_star = b2 / b1
            y_star = a2 / a1
            if 0 <= x_star <= 1 and 0 <= y_star <= 1:
                x_frac = Fraction(int(b2), int(b1)).limit_denominator()
                y_frac = Fraction(int(a2), int(a1)).limit_denominator()
            else:
                x_star, y_star = None, None
                x_frac, y_frac = None, None
        else:
            x_star, y_star = None, None
            x_frac, y_frac = None, None

        return x_star, y_star, x_frac, y_frac, a1, a2, b1, b2


def check_dominance_rows(A):
    m = A.shape[0]
    dominated = []
    for i in range(m):
        for j in range(m):
            if i != j and np.all(A[i] <= A[j]) and np.any(A[i] < A[j]):
                if i not in dominated:
                    dominated.append(i)
    return dominated


def check_dominance_cols(B):
    n = B.shape[1]
    dominated = []
    for i in range(n):
        for j in range(n):
            if i != j and np.all(B[:, i] <= B[:, j]) and np.any(B[:, i] < B[:, j]):
                if i not in dominated:
                    dominated.append(i)
    return dominated


def reduce_game_by_dominance(A, B, max_reduce_to=2):
    A_reduced = A.copy()
    B_reduced = B.copy()

    changed = True
    iteration = 0
    max_iter = 10

    while changed and iteration < max_iter:
        changed = False
        iteration += 1

        if A_reduced.shape[0] > max_reduce_to:
            dominated_rows = check_dominance_rows(A_reduced)
            if dominated_rows:
                rows_to_keep = [i for i in range(A_reduced.shape[0]) if i not in dominated_rows]
                if len(rows_to_keep) >= max_reduce_to:
                    A_reduced = A_reduced[rows_to_keep]
                    B_reduced = B_reduced[rows_to_keep]
                    print(f"Удалены доминируемые строки (A): {[r + 1 for r in dominated_rows]}")
                    changed = True

        if B_reduced.shape[1] > max_reduce_to:
            dominated_cols = check_dominance_cols(B_reduced)
            if dominated_cols:
                cols_to_keep = [i for i in range(B_reduced.shape[1]) if i not in dominated_cols]
                if len(cols_to_keep) >= max_reduce_to:
                    A_reduced = A_reduced[:, cols_to_keep]
                    B_reduced = B_reduced[:, cols_to_keep]
                    print(f"Удалены доминируемые столбцы (B): {[c + 1 for c in dominated_cols]}")
                    changed = True

    return A_reduced, B_reduced


def solve_bimatrix_game(A, B, output_callback=print, method_mode="auto", apply_dominance=True):
    output_callback("=" * 70)
    output_callback("РЕШЕНИЕ БИМАТРИЧНОЙ ИГРЫ")
    output_callback("=" * 70)

    output_callback("\nИсходные матрицы:")
    output_callback("Матрица A (игрок A):")
    output_callback(str(A))
    output_callback("\nМатрица B (игрок B):")
    output_callback(str(B))

    A_current = A.copy()
    B_current = B.copy()
    original_is_2x2 = (A.shape == (2, 2) and B.shape == (2, 2))

    # Упрощение доминированием (опционально)
    output_callback("\n" + "=" * 70)
    output_callback("ЭТАП 1: УПРОЩЕНИЕ ДОМИНИРОВАНИЕМ")
    output_callback("=" * 70)
    if apply_dominance:
        A_reduced, B_reduced = reduce_game_by_dominance(A_current, B_current, max_reduce_to=2)
        if A_reduced.shape != A_current.shape or B_reduced.shape != B_current.shape:
            output_callback(f"\nРазмер после упрощения: {A_reduced.shape[0]}x{A_reduced.shape[1]}")
            A_current, B_current = A_reduced, B_reduced
        else:
            output_callback("\nДоминируемых стратегий не найдено")
    else:
        output_callback("\nУпрощение отключено пользователем")

    # Выбор метода решения
    output_callback("\n" + "=" * 70)
    output_callback("ЭТАП 2: ВЫБОР МЕТОДА РЕШЕНИЯ")
    output_callback("=" * 70)

    output_callback(f"\nРазмер после упрощения: {A_current.shape[0]}x{A_current.shape[1]}")

    reduced_is_2x2 = (A_current.shape == (2, 2) and B_current.shape == (2, 2))

    use_graphical = False
    if method_mode == "always_lemke":
        use_graphical = False
        output_callback("→ Режим: ВСЕГДА ЛЕМКЕ-ХАУСЕН")
    elif method_mode == "reduced_2x2_graphical":
        use_graphical = reduced_is_2x2
        output_callback("→ Режим: ГРАФИЧЕСКИЙ ДЛЯ 2×2 ПОСЛЕ РЕДУКЦИИ")
    else:
        # auto: графический только для исходной 2×2
        use_graphical = original_is_2x2 and reduced_is_2x2
        output_callback("→ Режим: АВТОВЫБОР")

    if use_graphical:
        output_callback("→ Используем ГРАФИЧЕСКИЙ МЕТОД")
        output_callback("=" * 70)

        game = BimatrixGame(A_current, B_current)
        x_star, y_star, x_frac, y_frac, a1, a2, b1, b2 = game.find_mixed_nash_2x2()

        if x_star is not None and y_star is not None:
            x_frac2 = Fraction(1, 1) - x_frac
            y_frac2 = Fraction(1, 1) - y_frac

            output_callback("\n" + "=" * 70)
            output_callback("РЕШЕНИЕ БИМАТРИЧНОЙ ИГРЫ 2x2")
            output_callback("=" * 70)

            output_callback("\nИсходные данные:")
            output_callback("Матрица A :")
            output_callback(str(game.A))
            output_callback("\nМатрица B :")
            output_callback(str(game.B))

            output_callback("\n" + "=" * 70)
            output_callback("ВЫЧИСЛЕНИЕ КОЭФФИЦИЕНТОВ")
            output_callback("=" * 70)

            a11, a12 = game.A[0, 0], game.A[0, 1]
            a21, a22 = game.A[1, 0], game.A[1, 1]
            b11, b12 = game.B[0, 0], game.B[0, 1]
            b21, b22 = game.B[1, 0], game.B[1, 1]

            output_callback(f"\nДля игрока A:")
            output_callback(f"a₁₁ = {a11:.0f}, a₁₂ = {a12:.0f}, a₂₁ = {a21:.0f}, a₂₂ = {a22:.0f}")
            output_callback(f"a₁ = a₁₁ - a₁₂ - a₂₁ + a₂₂ = {a11:.0f} - {a12:.0f} - {a21:.0f} + {a22:.0f} = {a1:.2f}")
            output_callback(f"a₂ = a₂₂ - a₁₂ = {a22:.0f} - {a12:.0f} = {a2:.2f}")
            output_callback(f"α = a₂/a₁ = {a2:.2f}/{a1:.2f} = {y_star:.4f} = {y_frac}")

            output_callback(f"\nДля игрока B:")
            output_callback(f"b₁₁ = {b11:.0f}, b₁₂ = {b12:.0f}, b₂₁ = {b21:.0f}, b₂₂ = {b22:.0f}")
            output_callback(f"b₁ = b₁₁ - b₁₂ - b₂₁ + b₂₂ = {b11:.0f} - {b12:.0f} - {b21:.0f} + {b22:.0f} = {b1:.2f}")
            output_callback(f"b₂ = b₂₂ - b₂₁ = {b22:.0f} - {b21:.0f} = {b2:.2f}")
            output_callback(f"β = b₂/b₁ = {b2:.2f}/{b1:.2f} = {x_star:.4f} = {x_frac}")

            output_callback("\n" + "=" * 70)
            output_callback("АНАЛИЗ ЛИНИЙ ОТКЛИКА (ДЛЯ ГРАФИКА)")
            output_callback("=" * 70)

            # Анализ линии отклика игрока A
            output_callback("\n--- ЛИНИЯ ОТКЛИКА ИГРОКА A ---")
            output_callback(
                f"Ожидаемый выигрыш A при выборе стратегии A₁: E₁ = a₁₁·y + a₁₂·(1-y) = {a11:.0f}·y + {a12:.0f}·(1-y)")
            output_callback(
                f"Ожидаемый выигрыш A при выборе стратегии A₂: E₂ = a₂₁·y + a₂₂·(1-y) = {a21:.0f}·y + {a22:.0f}·(1-y)")
            output_callback(f"Разность: ΔE = E₁ - E₂ = ({a11:.0f} - {a21:.0f})·y + ({a12:.0f} - {a22:.0f})·(1-y)")

            diff_a = (a11 - a21) - (a12 - a22)
            const_a = a12 - a22
            output_callback(f"ΔE = {diff_a:.0f}·y + {const_a:.0f}")

            # Находим точку пересечения
            if diff_a != 0:
                y_cross = -const_a / diff_a
                output_callback(f"Точка пересечения (ΔE = 0): y = {-const_a:.0f}/{diff_a:.0f} = {y_cross:.4f}")

                if diff_a > 0:
                    output_callback(f"\nИнтервалы для y:")
                    output_callback(f"  y ∈ [0; {y_cross:.4f}): ΔE < 0 → A выбирает A₂")
                    output_callback(f"  y = {y_cross:.4f}: ΔE = 0 → A безразличен")
                    output_callback(f"  y ∈ ({y_cross:.4f}; 1]: ΔE > 0 → A выбирает A₁")
                else:
                    output_callback(f"\nИнтервалы для y:")
                    output_callback(f"  y ∈ [0; {y_cross:.4f}): ΔE > 0 → A выбирает A₁")
                    output_callback(f"  y = {y_cross:.4f}: ΔE = 0 → A безразличен")
                    output_callback(f"  y ∈ ({y_cross:.4f}; 1]: ΔE < 0 → A выбирает A₂")

            # Анализ линии отклика игрока B
            output_callback("\n--- ЛИНИЯ ОТКЛИКА ИГРОКА B ---")
            output_callback(
                f"Ожидаемый выигрыш B при выборе стратегии B₁: F₁ = b₁₁·x + b₂₁·(1-x) = {b11:.0f}·x + {b21:.0f}·(1-x)")
            output_callback(
                f"Ожидаемый выигрыш B при выборе стратегии B₂: F₂ = b₁₂·x + b₂₂·(1-x) = {b12:.0f}·x + {b22:.0f}·(1-x)")
            output_callback(f"Разность: ΔF = F₁ - F₂ = ({b11:.0f} - {b12:.0f})·x + ({b21:.0f} - {b22:.0f})·(1-x)")

            diff_b = (b11 - b12) - (b21 - b22)
            const_b = b21 - b22
            output_callback(f"ΔF = {diff_b:.0f}·x + {const_b:.0f}")

            # Находим точку пересечения
            if diff_b != 0:
                x_cross = -const_b / diff_b
                output_callback(f"Точка пересечения (ΔF = 0): x = {-const_b:.0f}/{diff_b:.0f} = {x_cross:.4f}")

                if diff_b > 0:
                    output_callback(f"\nИнтервалы для x:")
                    output_callback(f"  x ∈ [0; {x_cross:.4f}): ΔF < 0 → B выбирает B₂")
                    output_callback(f"  x = {x_cross:.4f}: ΔF = 0 → B безразличен")
                    output_callback(f"  x ∈ ({x_cross:.4f}; 1]: ΔF > 0 → B выбирает B₁")
                else:
                    output_callback(f"\nИнтервалы для x:")
                    output_callback(f"  x ∈ [0; {x_cross:.4f}): ΔF > 0 → B выбирает B₁")
                    output_callback(f"  x = {x_cross:.4f}: ΔF = 0 → B безразличен")
                    output_callback(f"  x ∈ ({x_cross:.4f}; 1]: ΔF < 0 → B выбирает B₂")

            output_callback("\n" + "=" * 70)
            output_callback("РАВНОВЕСИЕ НЭША")
            output_callback("=" * 70)

            output_callback(f"\nx* (A₁) = {x_star:.4f} = {x_frac}")
            output_callback(f"1 - x* (A₂) = {1 - x_star:.4f} = {x_frac2}")
            output_callback(f"\ny* (B₁) = {y_star:.4f} = {y_frac}")
            output_callback(f"1 - y* (B₂) = {1 - y_star:.4f} = {y_frac2}")

            # Подробное вычисление выигрышей
            output_callback("\n" + "=" * 70)
            output_callback("ВЫЧИСЛЕНИЕ ВЫИГРЫШЕЙ")
            output_callback("=" * 70)

            output_callback("\nДля игрока A:")
            output_callback(f"H_A = x·A·yᵀ = [x, 1-x] · [{a11:.0f} {a12:.0f}; {a21:.0f} {a22:.0f}] · [y; 1-y]")
            output_callback(f"H_A = x·y·a₁₁ + x·(1-y)·a₁₂ + (1-x)·y·a₂₁ + (1-x)·(1-y)·a₂₂")
            output_callback(
                f"    = {x_star:.4f}·{y_star:.4f}·{a11:.0f} + {x_star:.4f}·{1 - y_star:.4f}·{a12:.0f} + {1 - x_star:.4f}·{y_star:.4f}·{a21:.0f} + {1 - x_star:.4f}·{1 - y_star:.4f}·{a22:.0f}")

            term1 = x_star * y_star * a11
            term2 = x_star * (1 - y_star) * a12
            term3 = (1 - x_star) * y_star * a21
            term4 = (1 - x_star) * (1 - y_star) * a22

            output_callback(f"    = {term1:.4f} + {term2:.4f} + {term3:.4f} + {term4:.4f}")

            H_A = term1 + term2 + term3 + term4
            H_A_frac = Fraction(H_A).limit_denominator()
            output_callback(f"    = {H_A:.4f} = {H_A_frac}")

            output_callback("\nДля игрока B:")
            output_callback(f"H_B = x·B·yᵀ = [x, 1-x] · [{b11:.0f} {b12:.0f}; {b21:.0f} {b22:.0f}] · [y; 1-y]")
            output_callback(f"H_B = x·y·b₁₁ + x·(1-y)·b₁₂ + (1-x)·y·b₂₁ + (1-x)·(1-y)·b₂₂")
            output_callback(
                f"    = {x_star:.4f}·{y_star:.4f}·{b11:.0f} + {x_star:.4f}·{1 - y_star:.4f}·{b12:.0f} + {1 - x_star:.4f}·{y_star:.4f}·{b21:.0f} + {1 - x_star:.4f}·{1 - y_star:.4f}·{b22:.0f}")

            term1b = x_star * y_star * b11
            term2b = x_star * (1 - y_star) * b12
            term3b = (1 - x_star) * y_star * b21
            term4b = (1 - x_star) * (1 - y_star) * b22

            output_callback(f"    = {term1b:.4f} + {term2b:.4f} + {term3b:.4f} + {term4b:.4f}")

            H_B = term1b + term2b + term3b + term4b
            H_B_frac = Fraction(H_B).limit_denominator()
            output_callback(f"    = {H_B:.4f} = {H_B_frac}")

            output_callback("\n" + "=" * 70)
            output_callback("ИТОГОВЫЙ ОТВЕТ")
            output_callback("=" * 70)

            output_callback(f"\nРавновесие Нэша в смешанных стратегиях:")
            output_callback(f"  Стратегия A(x*): (A₁: {x_frac}, A₂: {x_frac2})")
            output_callback(f"  Стратегия B(y*): (B₁: {y_frac}, B₂: {y_frac2})")
            output_callback(f"  H_A = {H_A_frac} = {float(H_A):.4f}")
            output_callback(f"  H_B = {H_B_frac} = {float(H_B):.4f}")

            try:
                fig = plot_graphical_solution(game)
                plt.show(block=False)
                output_callback("\nГрафик решения открыт в отдельном окне")
            except Exception as e:
                output_callback(f"\n(График не может быть отображен: {e})")

            return np.array([float(x_frac), float(x_frac2)]), np.array([float(y_frac), float(y_frac2)])

    if method_mode == "auto" and not original_is_2x2 and reduced_is_2x2:
        output_callback("→ После доминирования получили 2×2, но в режиме АВТО")
        output_callback("  для исходной не-2×2 игры продолжаем методом Лемке-Хаусена.")

    output_callback(f"→ Используем АЛГОРИТМ ЛЕМКЕ-ХАУСЕНА ({A_current.shape[0]}×{A_current.shape[1]})")
    output_callback("=" * 70)

    solver = LemkeHowson(A_current, B_current)
    x_star, y_star = solver.solve()

    return x_star, y_star


def plot_graphical_solution(game):
    x_star, y_star, x_frac, y_frac, a1, a2, b1, b2 = game.find_mixed_nash_2x2()

    fig, ax = plt.subplots(figsize=(10, 10))
    square = Rectangle((0, 0), 1, 1, fill=False, edgecolor='black', linewidth=2.5)
    ax.add_patch(square)

    if y_star is not None and 0 <= y_star <= 1:
        if a1 > 0:
            ax.fill_between([0, 1], y_star, 1, alpha=0.2, color='red', label='A выбирает A₁')
            ax.fill_between([0, 1], 0, y_star, alpha=0.2, color='blue', label='A выбирает A₂')
            ax.plot([0, 0], [0, y_star], color='red', linewidth=2.5)
            ax.plot([0, 1], [y_star, y_star], color='red', linewidth=2.5)
            ax.plot([1, 1], [y_star, 1], color='red', linewidth=2.5)
        else:
            ax.fill_between([0, 1], y_star, 1, alpha=0.2, color='blue')
            ax.fill_between([0, 1], 0, y_star, alpha=0.2, color='red')
            ax.plot([0, 0], [y_star, 1], color='red', linewidth=2.5)
            ax.plot([0, 1], [y_star, y_star], color='red', linewidth=2.5)
            ax.plot([1, 1], [0, y_star], color='red', linewidth=2.5)

        ax.text(0.5, y_star + 0.04, f'y* = {y_star:.3f}', color='red', ha='center', fontsize=12,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    if x_star is not None and 0 <= x_star <= 1:
        if b1 > 0:
            ax.fill_betweenx([0, 1], x_star, 1, alpha=0.15, color='lightgreen', label='B выбирает B₁')
            ax.fill_betweenx([0, 1], 0, x_star, alpha=0.15, color='yellow', label='B выбирает B₂')
            ax.plot([1, x_star], [0, 0], color='green', linewidth=2.5)
            ax.plot([x_star, x_star], [0, 1], color='green', linewidth=2.5)
            ax.plot([x_star, 0], [1, 1], color='green', linewidth=2.5)
        else:
            ax.fill_betweenx([0, 1], x_star, 1, alpha=0.15, color='yellow')
            ax.fill_betweenx([0, 1], 0, x_star, alpha=0.15, color='lightgreen')
            ax.plot([0, x_star], [0, 0], color='green', linewidth=2.5)
            ax.plot([x_star, x_star], [0, 1], color='green', linewidth=2.5)
            ax.plot([x_star, 1], [1, 1], color='green', linewidth=2.5)

        ax.text(x_star + 0.04, 0.5, f'x* = {x_star:.3f}', color='green', va='center', fontsize=12,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    if x_star is not None and y_star is not None and 0 <= x_star <= 1 and 0 <= y_star <= 1:
        ax.plot(x_star, y_star, 'ko', markersize=14, label='Равновесие Нэша')
        ax.plot(x_star, y_star, 'wo', markersize=6)

    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlabel('Вероятность x (стратегия A₁)', fontsize=14)
    ax.set_ylabel('Вероятность y (стратегия B₁)', fontsize=14)
    ax.set_title('Графическое решение биматричной игры 2×2', fontsize=16)
    ax.grid(True, alpha=0.2)

    ax.text(-0.04, -0.04, '(0,0)\nA₂,B₂', fontsize=10, ha='right', va='top')
    ax.text(1.04, -0.04, '(1,0)\nA₁,B₂', fontsize=10, ha='left', va='top')
    ax.text(-0.04, 1.04, '(0,1)\nA₂,B₁', fontsize=10, ha='right', va='bottom')
    ax.text(1.04, 1.04, '(1,1)\nA₁,B₁', fontsize=10, ha='left', va='bottom')

    legend_elements = [
        Patch(facecolor='red', alpha=0.3, label='A выбирает A₁'),
        Patch(facecolor='blue', alpha=0.3, label='A выбирает A₂'),
        Patch(facecolor='lightgreen', alpha=0.3, label='B выбирает B₁'),
        Patch(facecolor='yellow', alpha=0.3, label='B выбирает B₂'),
        plt.Line2D([0], [0], color='red', linewidth=2.5, label='Линия отклика A'),
        plt.Line2D([0], [0], color='green', linewidth=2.5, label='Линия отклика B'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=9)

    info_text = (f"Матрица A:\n{game.A[0, 0]:.0f} {game.A[0, 1]:.0f}\n{game.A[1, 0]:.0f} {game.A[1, 1]:.0f}\n\n"
                 f"Матрица B:\n{game.B[0, 0]:.0f} {game.B[0, 1]:.0f}\n{game.B[1, 0]:.0f} {game.B[1, 1]:.0f}")
    ax.text(1.05, 0.5, info_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))

    plt.tight_layout()
    return fig


class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()

    def flush(self):
        pass


class BimatrixGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Решение биматричных игр - Алгоритм Лемке-Хаусена")
        self.root.geometry("1100x950")

        self.m = tk.IntVar(value=2)
        self.n = tk.IntVar(value=2)

        self.A_frame = None
        self.B_frame = None
        self.A_entries = []
        self.B_entries = []

        self.create_widgets()

    def create_widgets(self):
        main_canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)

        scrollable_frame.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))

        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)

        dim_frame = ttk.LabelFrame(scrollable_frame, text="Размерность игры", padding=10)
        dim_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(dim_frame, text="Стратегии игрока A (строки):").grid(row=0, column=0, padx=5, pady=5)
        m_spinbox = ttk.Spinbox(dim_frame, from_=1, to=10, textvariable=self.m, width=5, command=self.update_dimensions)
        m_spinbox.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(dim_frame, text="Стратегии игрока B (столбцы):").grid(row=0, column=2, padx=5, pady=5)
        n_spinbox = ttk.Spinbox(dim_frame, from_=1, to=10, textvariable=self.n, width=5, command=self.update_dimensions)
        n_spinbox.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(dim_frame, text="Обновить матрицы", command=self.update_dimensions).grid(row=0, column=4, padx=10,
                                                                                            pady=5)

        examples_frame = ttk.LabelFrame(scrollable_frame, text="Быстрая вставка примеров", padding=10)
        examples_frame.pack(fill="x", padx=10, pady=5)

        examples = [
            ("Пример 1: 3×4", self.load_example_3x4),
            ("Пример 2: 4×4", self.load_example_4x4),
            ("Пример 3: 2×2 (отрицательные)", self.load_example_2x2_neg),
            ("Пример 4: 3×3", self.load_example_3x3),
            ("Пример 5: 2×2 (A=[1,4;6,3], B=[5,4;2,5])", self.load_example_2x2_1),
            ("Пример 6: 2×2 (A=[4,8;6,3], B=[7,1;5,8])", self.load_example_2x2_2),
        ]

        for i, (text, command) in enumerate(examples):
            btn = ttk.Button(examples_frame, text=text, command=command)
            btn.grid(row=i // 3, column=i % 3, padx=5, pady=5, sticky="ew")

        examples_frame.columnconfigure(0, weight=1)
        examples_frame.columnconfigure(1, weight=1)
        examples_frame.columnconfigure(2, weight=1)

        self.A_frame = ttk.LabelFrame(scrollable_frame, text="Матрица A (выигрыши игрока A)", padding=10)
        self.A_frame.pack(fill="x", padx=10, pady=5)

        self.B_frame = ttk.LabelFrame(scrollable_frame, text="Матрица B (выигрыши игрока B)", padding=10)
        self.B_frame.pack(fill="x", padx=10, pady=5)

        solve_btn = ttk.Button(scrollable_frame, text="РЕШИТЬ ИГРУ", command=self.solve_game)
        solve_btn.pack(pady=10)

        # Кнопка для открытия окна кооперативной игры
        coop_btn = ttk.Button(scrollable_frame, text="Кооперативная игра (3 игрока)",
                              command=self.open_cooperative_window)
        coop_btn.pack(pady=5)

        output_frame = ttk.LabelFrame(scrollable_frame, text="Результаты", padding=10)
        output_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.output_text = scrolledtext.ScrolledText(output_frame, height=25, width=90, wrap=tk.WORD)
        self.output_text.pack(fill="both", expand=True)

        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.update_dimensions()

    def update_dimensions(self):
        m = self.m.get()
        n = self.n.get()

        for widget in self.A_frame.winfo_children():
            widget.destroy()
        for widget in self.B_frame.winfo_children():
            widget.destroy()

        self.A_entries = []
        self.B_entries = []

        for i in range(m):
            row_entries = []
            for j in range(n):
                entry = ttk.Entry(self.A_frame, width=8, justify="center")
                entry.grid(row=i, column=j, padx=2, pady=2)
                entry.insert(0, "0")
                row_entries.append(entry)
            self.A_entries.append(row_entries)

        for i in range(m):
            row_entries = []
            for j in range(n):
                entry = ttk.Entry(self.B_frame, width=8, justify="center")
                entry.grid(row=i, column=j, padx=2, pady=2)
                entry.insert(0, "0")
                row_entries.append(entry)
            self.B_entries.append(row_entries)

    def set_matrix_values(self, A, B):
        m, n = A.shape
        self.m.set(m)
        self.n.set(n)
        self.update_dimensions()

        for i in range(m):
            for j in range(n):
                self.A_entries[i][j].delete(0, tk.END)
                self.A_entries[i][j].insert(0, str(int(A[i][j]) if A[i][j] == int(A[i][j]) else str(A[i][j])))
                self.B_entries[i][j].delete(0, tk.END)
                self.B_entries[i][j].insert(0, str(int(B[i][j]) if B[i][j] == int(B[i][j]) else str(B[i][j])))

    def load_example_3x4(self):
        A = np.array([[6, 3, 2, 8], [4, 9, 7, 2], [8, 2, 3, 6]])
        B = np.array([[2, 7, 8, 1], [9, 2, 4, 4], [4, 8, 3, 5]])
        self.set_matrix_values(A, B)
        messagebox.showinfo("Загрузка", "Загружен пример 3×4")

    def load_example_4x4(self):
        A = np.array([[7, 0, 14, 3], [10, 1, 8, 6], [2, 9, 5, 11], [4, 6, 9, 0]])
        B = np.array([[13, 9, 7, 3], [5, 10, 6, 11], [7, 3, 5, 4], [11, 12, 0, 9]])
        self.set_matrix_values(A, B)
        messagebox.showinfo("Загрузка", "Загружен пример 4×4")

    def load_example_2x2_neg(self):
        A = np.array([[-10, 2], [1, -1]])
        B = np.array([[5, -2], [-1, 1]])
        self.set_matrix_values(A, B)
        messagebox.showinfo("Загрузка", "Загружен пример 2×2 (с отрицательными числами)")

    def load_example_3x3(self):
        A = np.array([[4, 5, 6], [7, 8, 3], [8, 0, 5]])
        B = np.array([[7, 6, 2], [8, 4, 3], [2, 1, 5]])
        self.set_matrix_values(A, B)
        messagebox.showinfo("Загрузка", "Загружен пример 3×3")

    def load_example_2x2_1(self):
        A = np.array([[1, 4], [6, 3]])
        B = np.array([[5, 4], [2, 5]])
        self.set_matrix_values(A, B)
        messagebox.showinfo("Загрузка", "Загружен пример 2×2 №1")

    def load_example_2x2_2(self):
        A = np.array([[4, 8], [6, 3]])
        B = np.array([[7, 1], [5, 8]])
        self.set_matrix_values(A, B)
        messagebox.showinfo("Загрузка", "Загружен пример 2×2 №2")

    def get_matrices(self):
        m = self.m.get()
        n = self.n.get()

        A = []
        B = []

        for i in range(m):
            row_A = []
            row_B = []
            for j in range(n):
                try:
                    val_A = float(self.A_entries[i][j].get())
                    val_B = float(self.B_entries[i][j].get())
                except ValueError:
                    val_A = 0.0
                    val_B = 0.0
                row_A.append(val_A)
                row_B.append(val_B)
            A.append(row_A)
            B.append(row_B)

        return np.array(A), np.array(B)

    def solve_game(self):
        self.output_text.delete(1.0, tk.END)

        A, B = self.get_matrices()

        old_stdout = sys.stdout
        sys.stdout = TextRedirector(self.output_text)

        try:
            solve_bimatrix_game(A, B, output_callback=print)
        except Exception as e:
            print(f"\nОшибка при решении: {e}")
            import traceback
            traceback.print_exc()

        sys.stdout = old_stdout

    def open_cooperative_window(self):
        CooperativeGameWindow(tk.Toplevel(self.root))


# ============================================================
# НОВЫЙ БЛОК: алгоритм кооперативной игры трёх лиц
# ============================================================
def solve_zero_sum_game(payoff_matrix):
    """Решает антагонистическую игру: максимизирующий игрок (строки) против минимизирующего (столбцы).
       Возвращает цену игры для максимизирующего игрока."""
    m, n = payoff_matrix.shape
    c = np.zeros(m + 1)
    c[0] = -1.0  # min -v  <=> max v
    A_ub = np.hstack([np.ones((n, 1)), -payoff_matrix.T])
    b_ub = np.zeros(n)
    A_eq = np.array([np.hstack([0, np.ones(m)])])
    b_eq = np.array([1.0])
    bounds = [(None, None)] + [(0, None) for _ in range(m)]
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    if res.success:
        return -res.fun
    else:
        # fallback: полный перебор для маленьких игр
        val = -np.inf
        for row in payoff_matrix:
            val = max(val, min(row))
        return val


class ThreePlayerCooperativeGame:
    def __init__(self, pair_matrices):
        """
        pair_matrices: словарь {(i,j): (A_ij, A_ji)} для i<j, каждая матрица 2x2.
        """
        self.N = 3
        self.payoff = pair_matrices
        self.pair_logs = []   # будет хранить кортежи (i, j, log_text)
        self.coop_logs = []   # для хранения подробностей кооперативных вычислений
        self.d = self._compute_noncooperative_payoffs()
        self.v = {}
        self._compute_characteristic_function()

    def _solve_pair_with_log(self, i, j):
        """Возвращает (payoff_i, payoff_j, log_text) для пары (i,j)."""
        A_ij, A_ji = self.payoff[(min(i, j), max(i, j))]
        if i < j:
            A_i, A_j = A_ij, A_ji
        else:
            A_i, A_j = A_ji.T, A_ij.T

        log_buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = log_buffer
        try:
            solver = LemkeHowson(A_i, A_j)
            x, y = solver.solve()
        except Exception:
            x, y = np.ones(2)/2, np.ones(2)/2
        finally:
            sys.stdout = old_stdout

        payoff_i = x @ A_i @ y
        payoff_j = x @ A_j @ y
        log_text = log_buffer.getvalue()
        return payoff_i, payoff_j, log_text

    def _compute_noncooperative_payoffs(self):
        d = {}
        for i in [1, 2, 3]:
            pays = []
            for j in [1, 2, 3]:
                if j == i:
                    continue
                pi, pj, log_text = self._solve_pair_with_log(i, j)
                pays.append(pi)
                # сохраним лог только для i<j, чтобы не дублировать
                if i < j:
                    self.pair_logs.append((i, j, log_text))
            print(f'Pays: {pays}')
            d[i] = np.mean(pays)
        return d

    def _total_payoffs_profile(self, s):
        """Суммарный выигрыш игроков для профиля s=(a1,a2,a3), ai in {0,1}."""
        a1, a2, a3 = s
        (A12, A21) = self.payoff[(1,2)]
        (A13, A31) = self.payoff[(1,3)]
        (A23, A32) = self.payoff[(2,3)]
        u1 = A12[a1, a2] + A13[a1, a3]
        u2 = A21[a2, a1] + A23[a2, a3]
        u3 = A31[a3, a1] + A32[a3, a2]
        return u1, u2, u3

    def _compute_characteristic_function(self):
        players = [1, 2, 3]
        self.coop_logs.append("=" * 50)
        self.coop_logs.append("ВЫЧИСЛЕНИЕ ХАРАКТЕРИСТИЧЕСКОЙ ФУНКЦИИ v(S)")
        self.coop_logs.append("=" * 50)

        # --- Большая коалиция {1,2,3} ---
        self.coop_logs.append("\n--- Коалиция {1,2,3} (полный перебор профилей) ---")
        max_sum = -np.inf
        best_profile = None
        for a1, a2, a3 in product([0, 1], repeat=3):
            u1, u2, u3 = self._total_payoffs_profile((a1, a2, a3))
            total = u1 + u2 + u3
            self.coop_logs.append(
                f"Профиль (a1={a1}, a2={a2}, a3={a3}): "
                f"u1={u1:.4f}, u2={u2:.4f}, u3={u3:.4f}, сумма={total:.4f}"
            )
            if total > max_sum:
                max_sum = total
                best_profile = (a1, a2, a3)
        self.coop_logs.append(
            f"Максимальная сумма = {max_sum:.4f} (профиль {best_profile})"
        )
        self.v[frozenset(players)] = max_sum

        # --- Коалиции размера 1 и 2 ---
        for size in [1, 2]:
            for S in combinations(players, size):
                S_set = set(S)
                T_set = set(players) - S_set
                S_list = sorted(S_set)
                T_list = sorted(T_set)

                strategies_S = list(product([0, 1], repeat=len(S_list)))
                strategies_T = list(product([0, 1], repeat=len(T_list)))

                self.coop_logs.append(
                    f"\n--- Коалиция S = {S_set} против T = {T_set} ---"
                )
                self.coop_logs.append(
                    f"Стратегии S: {strategies_S} (первый индекс соответствует {S_list})"
                )
                self.coop_logs.append(
                    f"Стратегии T: {strategies_T} (первый индекс соответствует {T_list})"
                )

                payoff_matrix = np.zeros((len(strategies_S), len(strategies_T)))

                # Подробный перебор
                for idx_S, s_S in enumerate(strategies_S):
                    for idx_T, s_T in enumerate(strategies_T):
                        profile = {}
                        for i, val in zip(S_list, s_S):
                            profile[i] = val
                        for j, val in zip(T_list, s_T):
                            profile[j] = val
                        a1, a2, a3 = profile[1], profile[2], profile[3]
                        u1, u2, u3 = self._total_payoffs_profile((a1, a2, a3))
                        payoff_S = sum(u for i, u in zip([1, 2, 3], [u1, u2, u3]) if i in S_set)
                        payoff_matrix[idx_S, idx_T] = payoff_S
                        self.coop_logs.append(
                            f"  s_S={s_S} (S={S_list}), s_T={s_T} (T={T_list}) -> "
                            f"u=({u1:.4f},{u2:.4f},{u3:.4f}), выигрыш S = {payoff_S:.4f}"
                        )

                self.coop_logs.append("Матрица выплат коалиции S (строки - стратегии S, столбцы - T):")
                self.coop_logs.append(str(payoff_matrix))

                # Решаем антагонистическую игру
                v_S = solve_zero_sum_game(payoff_matrix)
                self.coop_logs.append(f"Цена антагонистической игры (максимин) = {v_S:.4f}")
                self.v[frozenset(S_set)] = v_S

    def shapley_values(self):
        N = [1,2,3]
        shap = {i:0.0 for i in N}
        for perm in permutations(N):
            cur_coalition = set()
            for i in perm:
                before = frozenset(cur_coalition)
                cur_coalition.add(i)
                after = frozenset(cur_coalition)
                shap[i] += self.v[after] - self.v.get(before, 0)
        for i in N:
            shap[i] /= 6.0
        return shap

    def core_allocation(self):
        self.coop_logs.append("\n" + "=" * 50)
        self.coop_logs.append("ПРОВЕРКА ЯДРА БОЛЬШОЙ КОАЛИЦИИ")
        self.coop_logs.append("=" * 50)

        v = self.v
        N = [1, 2, 3]
        grand = frozenset(N)

        # Формирование ограничений для ЛП
        self.coop_logs.append("\nОграничения задачи ЛП (проверка существования ядра):")
        self.coop_logs.append("  x1 + x2 + x3 = v({{1,2,3}}) = {:.4f}".format(v[grand]))
        for S in combinations(N, 1):
            self.coop_logs.append(
                "  x{} >= v({{{}}}) = {:.4f}".format(S[0], S[0], v[frozenset(S)])
            )
        for S in combinations(N, 2):
            self.coop_logs.append(
                "  x{} + x{} >= v({{{},{}}}) = {:.4f}".format(
                    S[0], S[1], S[0], S[1], v[frozenset(S)]
                )
            )

        # Решаем ЛП
        c = np.zeros(3)
        A_ub = []
        b_ub = []
        for S in combinations(N, 1):
            a = np.zeros(3)
            for i in S:
                a[i - 1] = -1.0
            A_ub.append(a)
            b_ub.append(-v[frozenset(S)])
        for S in combinations(N, 2):
            a = np.zeros(3)
            for i in S:
                a[i - 1] = -1.0
            A_ub.append(a)
            b_ub.append(-v[frozenset(S)])
        A_eq = [np.ones(3)]
        b_eq = [v[grand]]
        A_ub = np.array(A_ub)
        b_ub = np.array(b_ub)

        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                      bounds=[(None, None)] * 3, method='highs')

        self.coop_logs.append("\nРезультат ЛП: " + ("допустимо" if res.success else "недопустимо"))
        if not res.success:
            self.coop_logs.append("Ядро пусто.")
            return False, None

        # Поиск ближайшей к d точки ядра
        d_vec = np.array([self.d[i] for i in N])
        self.coop_logs.append("\nПоиск ближайшего к некооперативным выигрышам дележа:")
        self.coop_logs.append(f"  d = ({d_vec[0]:.4f}, {d_vec[1]:.4f}, {d_vec[2]:.4f})")
        self.coop_logs.append("Минимизируем (x1-d1)^2 + (x2-d2)^2 + (x3-d3)^2")
        self.coop_logs.append("при ограничениях ядра.")

        # Используем minimize
        def objective(x):
            return np.sum((x - d_vec) ** 2)

        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - v[grand]}]
        for S in combinations(N, 1):
            constraints.append(
                {'type': 'ineq', 'fun': lambda x, S=S: sum(x[i - 1] for i in S) - v[frozenset(S)]}
            )
        for S in combinations(N, 2):
            constraints.append(
                {'type': 'ineq', 'fun': lambda x, S=S: sum(x[i - 1] for i in S) - v[frozenset(S)]}
            )

        res2 = minimize(objective, d_vec, constraints=constraints, method='SLSQP',
                        options={'ftol': 1e-12, 'maxiter': 2000})

        if res2.success:
            x_opt = res2.x
            self.coop_logs.append("Найден оптимальный дележ:")
            self.coop_logs.append(f"  x1 = {x_opt[0]:.4f}")
            self.coop_logs.append(f"  x2 = {x_opt[1]:.4f}")
            self.coop_logs.append(f"  x3 = {x_opt[2]:.4f}")
            return True, {1: x_opt[0], 2: x_opt[1], 3: x_opt[2]}
        else:
            # fallback – угол ядра
            self.coop_logs.append("Не удалось найти ближайший дележ (используем d).")
            return True, {1: d_vec[0], 2: d_vec[1], 3: d_vec[2]}

    def get_detailed_log(self):
        return "\n".join(self.coop_logs)

    def find_stable_partition(self):
        """Ищет устойчивое разбиение и дележ, если ядро большой коалиции пусто."""
        v = self.v
        N = [1,2,3]
        partitions = [
            [{1},{2},{3}],
            [{1,2},{3}],
            [{1,3},{2}],
            [{2,3},{1}],
        ]
        for part in partitions:
            # Проверяем существование дележа, удовлетворяющего сумме v(S) и ядру внутри каждой S
            # Здесь используем общее ЛП для всего x с ограничениями по коалициям разбиения и по всем S
            # Условия: для каждой S в part: sum_{i in S} x_i = v[frozenset(S)]
            # и для всех коалиций T (любых) sum_{i in T} x_i >= v(T)
            # Решаем ЛП с целевой функцией 0
            A_eq = []
            b_eq = []
            for S in part:
                a = np.zeros(3)
                for i in S: a[i-1] = 1.0
                A_eq.append(a)
                b_eq.append(v[frozenset(S)])
            A_eq = np.array(A_eq)
            b_eq = np.array(b_eq)
            # Ограничения ядра
            A_ub = []
            b_ub = []
            for T in combinations(N,1):
                a = np.zeros(3)
                for i in T: a[i-1] = -1.0
                A_ub.append(a)
                b_ub.append(-v[frozenset(T)])
            for T in combinations(N,2):
                a = np.zeros(3)
                for i in T: a[i-1] = -1.0
                A_ub.append(a)
                b_ub.append(-v[frozenset(T)])
            A_ub = np.array(A_ub)
            b_ub = np.array(b_ub)
            res = linprog(np.zeros(3), A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                          bounds=[(None,None)]*3, method='highs')
            if res.success:
                x = {i: res.x[i-1] for i in N}
                return part, x
        return None, None


class CooperativeGameWindow:
    def __init__(self, parent):
        self.window = parent
        self.window.title("Кооперативная игра трёх игроков")
        self.window.geometry("1000x800")

        self.entries = {}  # (i,j): (матрица A_ij, A_ji)

        self.create_widgets()
        self.load_default_example()

    def create_widgets(self):
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Заголовок
        ttk.Label(main_frame, text="Задайте матрицы попарных биматричных игр (все 2×2)",
                  font=("Arial", 12, "bold")).pack(pady=5)

        frames = {}
        pairs = [(1,2), (1,3), (2,3)]
        for (i,j) in pairs:
            grp = ttk.LabelFrame(main_frame, text=f"Игра {i} против {j}", padding=5)
            grp.pack(fill="x", pady=5)
            ttk.Label(grp, text=f"Матрица A{i}{j} (выигрыш {i})").grid(row=0, column=0, padx=5)
            ttk.Label(grp, text=f"Матрица A{j}{i} (выигрыш {j})").grid(row=0, column=1, padx=5)

            A_ij_entries = []
            A_ji_entries = []
            for r in range(2):
                row_ij = []
                row_ji = []
                for c in range(2):
                    e1 = ttk.Entry(grp, width=6, justify='center')
                    e1.grid(row=r+1, column=0, padx=2, pady=2)
                    row_ij.append(e1)
                    e2 = ttk.Entry(grp, width=6, justify='center')
                    e2.grid(row=r+1, column=1, padx=2, pady=2)
                    row_ji.append(e2)
                A_ij_entries.append(row_ij)
                A_ji_entries.append(row_ji)
            self.entries[(i,j)] = (A_ij_entries, A_ji_entries)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Решить и найти устойчивые коалиции",
                   command=self.solve_cooperative).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Загрузить пример", command=self.load_default_example).pack(side="left", padx=5)

        self.output = scrolledtext.ScrolledText(main_frame, height=20, width=110, wrap=tk.WORD)
        self.output.pack(fill="both", expand=True, pady=5)

    def load_default_example(self):
        # Пример: игра "Дилемма заключённого" с разными вариациями
        data = {
            (1,2): (np.array([[3,0],[5,1]]), np.array([[3,5],[0,1]])),
            (1,3): (np.array([[2,4],[1,3]]), np.array([[2,1],[4,3]])),
            (2,3): (np.array([[4,2],[0,5]]), np.array([[4,0],[2,5]]))
        }
        for (i,j), (A_ij, A_ji) in data.items():
            entry_A, entry_B = self.entries[(i,j)]
            for r in range(2):
                for c in range(2):
                    entry_A[r][c].delete(0, tk.END)
                    entry_A[r][c].insert(0, str(int(A_ij[r,c])))
                    entry_B[r][c].delete(0, tk.END)
                    entry_B[r][c].insert(0, str(int(A_ji[r,c])))

    def solve_cooperative(self):
        self.output.delete(1.0, tk.END)
        old_stdout = sys.stdout
        sys.stdout = TextRedirector(self.output)

        try:
            # Считываем матрицы
            pair_matrices = {}
            for (i,j), (A_entries, B_entries) in self.entries.items():
                A_ij = np.zeros((2,2))
                A_ji = np.zeros((2,2))
                for r in range(2):
                    for c in range(2):
                        A_ij[r,c] = float(A_entries[r][c].get())
                        A_ji[r,c] = float(B_entries[r][c].get())
                pair_matrices[(i,j)] = (A_ij, A_ji)

            print("Построение кооперативной игры...\n")
            game = ThreePlayerCooperativeGame(pair_matrices)

            print("1. Индивидуальные некооперативные выигрыши (среднее по партнёрам):")
            for i in [1,2,3]:
                print(f"   d_{i} = {game.d[i]:.4f}")

            print("\n2. Характеристическая функция v(S):")
            for size in [1,2,3]:
                for S in combinations([1,2,3], size):
                    if size == 3:
                        print(f"   v({{1,2,3}}) = {game.v[frozenset(S)]:.4f}")
                    else:
                        print(f"   v({{{ ','.join(map(str,S)) }}}) = {game.v[frozenset(S)]:.4f}")

            shap = game.shapley_values()
            print("\n3. Вектор Шепли:")
            for i in [1,2,3]:
                print(f"   φ_{i} = {shap[i]:.4f}")

            print("\n4. Проверка ядра большой коалиции:")
            core_exists, x_core = game.core_allocation()
            if core_exists:
                print("   Ядро НЕПУСТО.")
                print(f"   Дележ, ближайший к некооперативным выигрышам:")
                for i in [1,2,3]:
                    print(f"      x_{i} = {x_core[i]:.4f}")
                in_core = all(sum(x_core[i] for i in S) >= game.v[frozenset(S)] - 1e-8 for S in combinations([1,2,3], 1))
                in_core &= all(sum(x_core[i] for i in S) >= game.v[frozenset(S)] - 1e-8 for S in combinations([1,2,3], 2))
                print(f"   Принадлежность ядру: {'да' if in_core else 'нет'}")
            else:
                print("   Ядро ПУСТО. Поиск устойчивой коалиционной структуры...")
                part, x_part = game.find_stable_partition()
                if part:
                    print(f"   Найдена устойчивая структура: {part}")
                    print("   Соответствующий дележ:")
                    for i in [1,2,3]:
                        print(f"      x_{i} = {x_part[i]:.4f}")
                else:
                    print("   Устойчивой структуры не найдено (в рамках модели).")

            print("\nАнализ завершён.")

        except Exception as e:
            print(f"Ошибка: {e}")
            import traceback
            traceback.print_exc()
        finally:
            sys.stdout = old_stdout


# ============================================================
# Главный запуск
# ============================================================
def main():
    root = tk.Tk()
    app = BimatrixGameGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()