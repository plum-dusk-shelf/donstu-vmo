from __future__ import annotations
from fractions import Fraction
from typing import Any, Dict, List, Sequence, Union, Optional, Tuple
import copy

Number = Union[int, float, Fraction]


def _to_number(x: Number, exact: bool) -> Union[Fraction, float]:
    return Fraction(str(x)) if exact else float(x)


def find_saddle_point(
    A: List[List[Number]],
    exact: bool,
    float_eps: float = 1e-9,
) -> Tuple[bool, Optional[Number], Optional[int], Optional[int]]:
    """
    Ищет седловую точку в матрице A.
    Возвращает (найдена ли, значение, индекс строки, индекс столбца).

    Исправление: в float-режиме сравнение через == ненадёжно из-за
    погрешностей вычислений. Используем допуск float_eps.
    """
    m, n = len(A), len(A[0])
    row_mins = [min(row) for row in A]
    col_maxs = [max(A[i][j] for i in range(m)) for j in range(n)]

    for i in range(m):
        for j in range(n):
            if exact:
                # Точный режим: Fraction поддерживает ==  без погрешностей
                is_row_min = A[i][j] == row_mins[i]
                is_col_max = A[i][j] == col_maxs[j]
            else:
                # Float-режим: сравниваем с допуском
                is_row_min = abs(float(A[i][j]) - float(row_mins[i])) <= float_eps
                is_col_max = abs(float(A[i][j]) - float(col_maxs[j])) <= float_eps

            if is_row_min and is_col_max:
                return True, A[i][j], i, j

    return False, None, None, None


def reduce_by_dominance(
    A: List[List[Number]],
    exact: bool,
) -> Tuple[List[List[Number]], List[int], List[int], List[str]]:
    """
    Удаляет доминируемые строки и столбцы итеративно.
    Возвращает:
        - редуцированную матрицу,
        - список индексов удалённых строк (в исходной нумерации),
        - список индексов удалённых столбцов,
        - список сообщений о каждом удалении.
    """
    m, n = len(A), len(A[0])
    A_num = [[_to_number(A[i][j], exact) for j in range(n)] for i in range(m)]

    current_rows = list(range(m))
    current_cols = list(range(n))
    removed_rows = []
    removed_cols = []
    messages = []

    changed = True
    while changed:
        changed = False

        # Удаление доминируемых строк
        i = 0
        while i < len(A_num):
            dominator_row: Optional[int] = None   # исправление: сохраняем индекс явно
            for k in range(len(A_num)):
                if k == i:
                    continue
                if all(A_num[k][j] >= A_num[i][j] for j in range(len(A_num[0]))):
                    dominator_row = k
                    break  # нашли первый доминант — достаточно

            if dominator_row is not None:
                orig_idx = current_rows[i]
                orig_dom = current_rows[dominator_row]
                removed_rows.append(orig_idx)
                messages.append(
                    f"Строка {orig_idx + 1} (текущий индекс {i}) удалена, "
                    f"так как она доминируется строкой {orig_dom + 1}."
                )
                del A_num[i]
                del current_rows[i]
                changed = True
                # i не увеличиваем — после удаления следующий элемент
                # занял позицию i
            else:
                i += 1

        # Удаление доминируемых столбцов
        j = 0
        while j < len(A_num[0]):
            dominator_col: Optional[int] = None   # исправление: сохраняем индекс явно
            for l in range(len(A_num[0])):
                if l == j:
                    continue
                if all(A_num[i][l] <= A_num[i][j] for i in range(len(A_num))):
                    dominator_col = l
                    break  # нашли первый доминант — достаточно

            if dominator_col is not None:
                orig_idx = current_cols[j]
                orig_dom = current_cols[dominator_col]
                removed_cols.append(orig_idx)
                messages.append(
                    f"Столбец {orig_idx + 1} (текущий индекс {j}) удалён, "
                    f"так как он доминируется столбцом {orig_dom + 1}."
                )
                for row in A_num:
                    del row[j]
                del current_cols[j]
                changed = True
                # j не увеличиваем по той же причине
            else:
                j += 1

    return A_num, removed_rows, removed_cols, messages


def solve_matrix_game_with_iterations(
    A: Sequence[Sequence[Number]],
    exact: bool = True,
    eps: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Решает матричную игру с предварительным анализом (седловая точка, доминирование).
    Возвращает результаты и список итераций.
    """
    if not A or not A[0]:
        raise ValueError("Матрица пустая")

    m, n = len(A), len(A[0])
    for row in A:
        if len(row) != n:
            raise ValueError("Все строки матрицы должны иметь одинаковую длину")

    A_orig = [list(row) for row in A]

    # 1. Поиск седловой точки
    saddle_found, saddle_value, saddle_i, saddle_j = find_saddle_point(A_orig, exact)
    if saddle_found:
        p = [Fraction(0) if exact else 0.0 for _ in range(m)]
        q = [Fraction(0) if exact else 0.0 for _ in range(n)]
        p[saddle_i] = Fraction(1) if exact else 1.0
        q[saddle_j] = Fraction(1) if exact else 1.0
        return {
            "m": m,
            "n": n,
            "saddle_point": True,
            "saddle_value": saddle_value,
            "saddle_row": saddle_i,
            "saddle_col": saddle_j,
            "p": p,
            "q": q,
            "v": saddle_value,
            "K": 0,
            "A_shifted": A_orig,
            "x": [0] * m, "y": [0] * n, "v_shift": saddle_value,
            "tableau": [], "basis": [],
            "iterations": [],
            "removed_rows": [],
            "removed_cols": [],
            "dominance_messages": [],
        }

    # 2. Редукция по доминированию
    reduced_A, removed_rows, removed_cols, dom_messages = reduce_by_dominance(A_orig, exact)

    m_red = len(reduced_A)
    n_red = len(reduced_A[0]) if reduced_A else 0
    if m_red == 0 or n_red == 0:
        raise ValueError("После удаления доминируемых строк/столбцов матрица пуста")

    # 3. Сдвиг матрицы
    amin_raw = min(min(row) for row in reduced_A)
    amin = _to_number(amin_raw, exact)
    K = _to_number(0, exact)
    if amin <= 0:
        K = _to_number(1, exact) - amin

    A_shifted = [
        [_to_number(reduced_A[i][j], exact) + K for j in range(n_red)]
        for i in range(m_red)
    ]

    # 4. Построение начальной симплекс-таблицы
    cols = n_red + m_red + 1
    T = [[_to_number(0, exact)] * cols for _ in range(m_red + 1)]

    for i in range(m_red):
        for j in range(n_red):
            T[i][j] = A_shifted[i][j]
        T[i][n_red + i] = _to_number(1, exact)
        T[i][-1] = _to_number(1, exact)

    for j in range(n_red):
        T[m_red][j] = _to_number(-1, exact)

    basis = [n_red + i for i in range(m_red)]

    local_eps = 0 if exact else (eps if eps is not None else 1e-12)

    def is_neg(x):
        return x < -local_eps

    def is_pos(x):
        return x > local_eps

    def is_nonneg(x):
        return x >= -local_eps

    iterations = []
    iterations.append({
        "tableau": copy.deepcopy(T),
        "row": None,
        "col": None,
        "method": "initial",
        "basis": basis.copy(),
    })

    # 5. Симплекс-метод (прямой + двойственный)
    while True:
        delta = T[m_red]

        all_delta_nonneg = all(not is_neg(delta[j]) for j in range(n_red + m_red))

        neg_rhs_index = None
        for i in range(m_red):
            if is_neg(T[i][-1]):
                neg_rhs_index = i
                break

        if all_delta_nonneg and neg_rhs_index is not None:
            # Двойственный симплекс
            method = "dual"
            leave = neg_rhs_index
            min_rhs = T[leave][-1]
            for i in range(m_red):
                if is_neg(T[i][-1]) and T[i][-1] < min_rhs:
                    min_rhs = T[i][-1]
                    leave = i

            enter = None
            best_ratio = None
            for j in range(n_red + m_red):
                a = T[leave][j]
                if is_neg(a):
                    ratio = delta[j] / a
                    if enter is None or ratio > best_ratio:
                        best_ratio = ratio
                        enter = j
            if enter is None:
                raise ValueError("Двойственный симплекс: нет отрицательных элементов в ведущей строке")

        elif any(is_neg(delta[j]) for j in range(n_red + m_red)):
            # Прямой симплекс
            method = "primal"
            enter = None
            for j in range(n_red + m_red):
                if is_neg(delta[j]):
                    enter = j
                    break
            leave = None
            best_ratio = None
            for i in range(m_red):
                a = T[i][enter]
                if is_pos(a):
                    ratio = T[i][-1] / a
                    if is_nonneg(ratio):
                        if leave is None or ratio < best_ratio or (
                            ratio == best_ratio and i < leave
                        ):
                            best_ratio = ratio
                            leave = i
            if leave is None:
                raise ValueError("Прямой симплекс: нет положительных элементов в ведущем столбце")
        else:
            break

        # Жорданово исключение
        piv = T[leave][enter]
        for j in range(cols):
            T[leave][j] = T[leave][j] / piv

        for i in range(m_red + 1):
            if i == leave:
                continue
            factor = T[i][enter]
            if factor != 0:
                for j in range(cols):
                    T[i][j] = T[i][j] - factor * T[leave][j]

        basis[leave] = enter

        iterations.append({
            "tableau": copy.deepcopy(T),
            "row": leave,
            "col": enter,
            "method": method,
            "basis": basis.copy(),
        })

    y_red = [_to_number(0, exact) for _ in range(n_red)]
    for i in range(m_red):
        bj = basis[i]
        if bj < n_red:
            y_red[bj] = T[i][-1]

    Z = sum(y_red)
    if Z == 0:
        raise ValueError("Не удалось получить Z>0 (проверь матрицу/сдвиг)")

    v_shift = _to_number(1, exact) / Z
    q_red = [v_shift * yj for yj in y_red]

    #x_red = [T[m_red][n_red + i] for i in range(m_red)]
    B = []
    for i in range(m_red):
        col_idx = basis[i]
        col = []
        for r in range(m_red):
            if col_idx < n_red:
                col.append(A_shifted[r][col_idx])
            else:
                col.append(1 if (col_idx - n_red) == r else 0)
        B.append(col)

    B_T = B# list(map(list, zip(*B)))

    b_vec = [_to_number(1, exact) for _ in range(m_red)]

    def gauss(A, b):
        A = [row[:] for row in A]
        b = b[:]
        n = len(A)

        for i in range(n):
            pivot = A[i][i]
            for j in range(n):
                A[i][j] /= pivot
            b[i] /= pivot

            for k in range(n):
                if k != i:
                    factor = A[k][i]
                    for j in range(n):
                        A[k][j] -= factor * A[i][j]
                    b[k] -= factor * b[i]

        return b

    x_red = gauss(B_T, b_vec)
    p_red = [v_shift * xi for xi in x_red]

    v = v_shift - K

    p_full = [_to_number(0, exact) for _ in range(m)]
    q_full = [_to_number(0, exact) for _ in range(n)]

    kept_rows = [i for i in range(m) if i not in removed_rows]
    kept_cols = [j for j in range(n) if j not in removed_cols]

    for idx_in_red, orig_row in enumerate(kept_rows):
        p_full[orig_row] = p_red[idx_in_red]
    for idx_in_red, orig_col in enumerate(kept_cols):
        q_full[orig_col] = q_red[idx_in_red]

    if not exact:
        p_full = [0.0 if abs(pi) < 1e-12 else float(pi) for pi in p_full]
        q_full = [0.0 if abs(qj) < 1e-12 else float(qj) for qj in q_full]
        p_red  = [0.0 if abs(pi) < 1e-12 else float(pi) for pi in p_red]
        q_red  = [0.0 if abs(qj) < 1e-12 else float(qj) for qj in q_red]

    return {
        "m": m,
        "n": n,
        "saddle_point": False,
        "removed_rows": removed_rows,
        "removed_cols": removed_cols,
        "dominance_messages": dom_messages,
        "reduced_matrix": reduced_A,
        "K": K,
        "A_shifted": A_shifted,
        "B": B,
        "b_vec": b_vec,
        "x": x_red,
        "y": y_red,
        "p": p_full,
        "q": q_full,
        "v_shift": v_shift,
        "v": v,
        "tableau": T,
        "basis": basis,
        "iterations": iterations,
    }