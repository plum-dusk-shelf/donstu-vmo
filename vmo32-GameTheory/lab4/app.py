import io
from contextlib import redirect_stdout
import itertools

import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

from solver import (
    solve_bimatrix_game,
    BimatrixGame,
    plot_graphical_solution,
    reduce_game_by_dominance,
    ThreePlayerCooperativeGame,
)

# ======================== ПРИМЕРЫ ДЛЯ БИМАТРИЧНЫХ ИГР ========================
EXAMPLES = {
    "Пример 1: 3×4": (
        np.array([[6, 3, 2, 8], [4, 9, 7, 2], [8, 2, 3, 6]], dtype=float),
        np.array([[2, 7, 8, 1], [9, 2, 4, 4], [4, 8, 3, 5]], dtype=float),
    ),
    "Пример 2: 4×4": (
        np.array([[7, 0, 14, 3], [10, 1, 8, 6], [2, 9, 5, 11], [4, 6, 9, 0]], dtype=float),
        np.array([[13, 9, 7, 3], [5, 10, 6, 11], [7, 3, 5, 4], [11, 12, 0, 9]], dtype=float),
    ),
    "Пример 3: 2×2 (отрицательные)": (
        np.array([[-10, 2], [1, -1]], dtype=float),
        np.array([[5, -2], [-1, 1]], dtype=float),
    ),
    "Пример 4: 3×3": (
        np.array([[4, 5, 6], [7, 8, 3], [8, 0, 5]], dtype=float),
        np.array([[7, 6, 2], [8, 4, 3], [2, 1, 5]], dtype=float),
    ),
    "Пример 5: 2×2 (A=[1,4;6,3], B=[5,4;2,5])": (
        np.array([[1, 4], [6, 3]], dtype=float),
        np.array([[5, 4], [2, 5]], dtype=float),
    ),
    "Пример 6: 2×2 (A=[4,8;6,3], B=[7,1;5,8])": (
        np.array([[4, 8], [6, 3]], dtype=float),
        np.array([[7, 1], [5, 8]], dtype=float),
    ),
}

# ======================== ВСТРОЕННЫЙ ПРИМЕР ДЛЯ КООПЕРАТИВНОЙ ИГРЫ ========================
BUILTIN_COOP_MATS = {
    (1, 2): (
        np.array([[-2.25, -2.75], [-2.50, -3.00]], dtype=float),   # A12
        np.array([[-3.75, -4], [-8.75, -9.00]], dtype=float),   # A21
    ),
    (1, 3): (
        np.array([[0.25, -0.75], [0.00, -1.00]], dtype=float),     # A13
        np.array([[-1.00, -0.75], [-2.25, -2.00]], dtype=float),   # A31
    ),
    (2, 3): (
        np.array([[2.50, -3.75], [-2.75, -4.00]], dtype=float),    # A23
        np.array([[1.75, 2.00], [0.75, 1.00]], dtype=float),       # A32
    ),
}

# ======================== УПРАВЛЕНИЕ СОСТОЯНИЕМ ========================
def init_state():
    if "m" not in st.session_state:
        st.session_state.m = 2
    if "n" not in st.session_state:
        st.session_state.n = 2
    if "A" not in st.session_state:
        st.session_state.A = np.zeros((2, 2), dtype=float)
    if "B" not in st.session_state:
        st.session_state.B = np.zeros((2, 2), dtype=float)

    # Состояния для кооперативной игры
    for pair in [(1, 2), (1, 3), (2, 3)]:
        for mat_name in [f"A{pair[0]}{pair[1]}", f"A{pair[1]}{pair[0]}"]:
            if mat_name not in st.session_state:
                st.session_state[mat_name] = np.zeros((2, 2), dtype=float)

    # Флаг автоматической загрузки встроенного кооперативного примера
    if "coop_loaded" not in st.session_state:
        st.session_state.coop_loaded = False

    # Автоматическая загрузка примера при первом входе в кооперативный режим
    if not st.session_state.coop_loaded:
        for pair, (A_ij, A_ji) in BUILTIN_COOP_MATS.items():
            st.session_state[f"A{pair[0]}{pair[1]}"] = A_ij.copy()
            st.session_state[f"A{pair[1]}{pair[0]}"] = A_ji.copy()
        st.session_state.coop_loaded = True

    if "coop_mode" not in st.session_state:
        st.session_state.coop_mode = False


# ======================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ========================
def resize_matrices(m: int, n: int):
    old_A = st.session_state.A
    old_B = st.session_state.B
    new_A = np.zeros((m, n), dtype=float)
    new_B = np.zeros((m, n), dtype=float)

    rows = min(m, old_A.shape[0])
    cols = min(n, old_A.shape[1])
    new_A[:rows, :cols] = old_A[:rows, :cols]
    new_B[:rows, :cols] = old_B[:rows, :cols]

    st.session_state.A = new_A
    st.session_state.B = new_B
    st.session_state.m = m
    st.session_state.n = n
    for i in range(m):
        for j in range(n):
            st.session_state[f"A_{i}_{j}"] = float(new_A[i, j])
            st.session_state[f"B_{i}_{j}"] = float(new_B[i, j])


def set_matrix_values(A: np.ndarray, B: np.ndarray):
    st.session_state.A = A.copy()
    st.session_state.B = B.copy()
    st.session_state.m, st.session_state.n = A.shape
    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            st.session_state[f"A_{i}_{j}"] = float(A[i, j])
            st.session_state[f"B_{i}_{j}"] = float(B[i, j])


def draw_matrix_editor(name: str, matrix: np.ndarray, key_prefix: str):
    st.markdown(f"#### {name}")
    for i in range(matrix.shape[0]):
        cols = st.columns(matrix.shape[1])
        for j in range(matrix.shape[1]):
            val = cols[j].number_input(
                label=f"{name}[{i+1},{j+1}]",
                value=float(matrix[i, j]),
                step=1.0,
                label_visibility="collapsed",
                key=f"{key_prefix}_{i}_{j}",
            )
            matrix[i, j] = val
    return matrix


def draw_2x2_editor(label: str, matrix: np.ndarray, key_prefix: str):
    """Компактный редактор 2×2 матрицы с заголовком."""
    st.markdown(f"**{label}**")
    m = matrix.copy()
    for i in range(2):
        cols = st.columns(2)
        for j in range(2):
            m[i, j] = cols[j].number_input(
                label=f"{label}[{i+1},{j+1}]",
                value=float(matrix[i, j]),
                step=0.25,          # удобный шаг для вашего примера
                format="%.2f",
                label_visibility="collapsed",
                key=f"{key_prefix}_{i}_{j}",
            )
    return m


# ======================== Streamlit-интерфейс ========================
def main():
    st.set_page_config(page_title="Решение биматричных игр - Лемке-Хаусен", layout="wide")
    init_state()

    st.title("Решение биматричных игр - Алгоритм Лемке-Хаусена")

    # Выбор режима
    mode = st.radio(
        "Режим",
        ["Биматричная игра", "Кооперативная игра (3 игрока)"],
        horizontal=True,
        index=0 if not st.session_state.coop_mode else 1,
    )

    # ==================== БИМАТРИЧНАЯ ИГРА ====================
    if mode == "Биматричная игра":
        st.session_state.coop_mode = False

        mode_labels = {
            "Автовыбор": "auto",
            "Всегда Лемке": "always_lemke",
            "Графически для 2×2 после редукции": "reduced_2x2_graphical",
        }
        selected_mode_label = st.selectbox(
            "Режим выбора метода",
            options=list(mode_labels.keys()),
            index=0,
        )
        method_mode = mode_labels[selected_mode_label]
        apply_dominance = st.checkbox("Применять упрощение по доминированию", value=True)

        with st.container(border=True):
            st.subheader("Размерность игры")
            c1, c2, c3 = st.columns([1, 1, 1])
            m = c1.number_input(
                "Стратегии игрока A (строки)",
                min_value=1, max_value=10,
                value=int(st.session_state.m), step=1,
            )
            n = c2.number_input(
                "Стратегии игрока B (столбцы)",
                min_value=1, max_value=10,
                value=int(st.session_state.n), step=1,
            )
            if c3.button("Обновить матрицы", use_container_width=True):
                resize_matrices(int(m), int(n))
                st.rerun()

        with st.container(border=True):
            st.subheader("Быстрая вставка примеров")
            labels = list(EXAMPLES.keys())
            for row in range(2):
                cols = st.columns(3)
                for col in range(3):
                    idx = row * 3 + col
                    if cols[col].button(labels[idx], use_container_width=True):
                        A, B = EXAMPLES[labels[idx]]
                        set_matrix_values(A, B)
                        st.rerun()

        with st.container(border=True):
            st.session_state.A = draw_matrix_editor(
                "Матрица A (выигрыши игрока A)", st.session_state.A, "A"
            )
        with st.container(border=True):
            st.session_state.B = draw_matrix_editor(
                "Матрица B (выигрыши игрока B)", st.session_state.B, "B"
            )

        solve_clicked = st.button("РЕШИТЬ ИГРУ", use_container_width=True, type="primary")

        if solve_clicked:
            log_buffer = io.StringIO()
            old_show = plt.show
            plt.show = lambda *args, **kwargs: None
            try:
                with redirect_stdout(log_buffer):
                    x_star, y_star = solve_bimatrix_game(
                        st.session_state.A.copy(),
                        st.session_state.B.copy(),
                        output_callback=print,
                        method_mode=method_mode,
                        apply_dominance=apply_dominance,
                    )
            except Exception as exc:
                st.error(f"Ошибка при решении: {exc}")
                x_star, y_star = None, None
            finally:
                plt.show = old_show

            output_lines = log_buffer.getvalue().splitlines()
            st.markdown("### Результаты")
            st.text_area("Лог решения", value="\n".join(output_lines), height=420)

            if x_star is not None and y_star is not None:
                st.success("Решение получено")
                st.write("x*:", np.array(x_star))
                st.write("y*:", np.array(y_star))

                # График только для 2×2 в разрешённом режиме
                if method_mode != "always_lemke":
                    if apply_dominance:
                        A_reduced, B_reduced = reduce_game_by_dominance(
                            st.session_state.A.copy(),
                            st.session_state.B.copy(),
                            max_reduce_to=2,
                        )
                    else:
                        A_reduced, B_reduced = st.session_state.A.copy(), st.session_state.B.copy()

                    if method_mode == "auto":
                        can_plot = (
                            st.session_state.A.shape == (2, 2)
                            and st.session_state.B.shape == (2, 2)
                        )
                        plot_A, plot_B = st.session_state.A, st.session_state.B
                    else:
                        can_plot = (
                            A_reduced.shape == (2, 2)
                            and B_reduced.shape == (2, 2)
                        )
                        plot_A, plot_B = A_reduced, B_reduced

                    if can_plot:
                        game = BimatrixGame(plot_A, plot_B)
                        fig = plot_graphical_solution(game)
                        st.pyplot(fig)

    # ==================== КООПЕРАТИВНАЯ ИГРА (3 игрока) ====================
    else:
        st.session_state.coop_mode = True
        st.markdown("## Кооперативная игра трёх игроков")
        st.info("Автоматически загружен встроенный пример. Вы можете изменить матрицы.")

        # Кнопка восстановления примера
        if st.button("🔄 Восстановить встроенный пример", use_container_width=True):
            for pair, (A_ij, A_ji) in BUILTIN_COOP_MATS.items():
                st.session_state[f"A{pair[0]}{pair[1]}"] = A_ij.copy()
                st.session_state[f"A{pair[1]}{pair[0]}"] = A_ji.copy()
            st.rerun()

        pairs = [(1, 2), (1, 3), (2, 3)]
        col1, col2, col3 = st.columns(3)
        for idx, (i, j) in enumerate(pairs):
            with [col1, col2, col3][idx]:
                st.markdown(f"#### Игра {i} против {j}")
                A_ij = st.session_state[f"A{i}{j}"]
                A_ji = st.session_state[f"A{j}{i}"]
                st.session_state[f"A{i}{j}"] = draw_2x2_editor(
                    f"Матрица A{i}{j} (выигрыш {i})", A_ij, f"A{i}{j}"
                )
                st.session_state[f"A{j}{i}"] = draw_2x2_editor(
                    f"Матрица A{j}{i} (выигрыш {j})", A_ji, f"A{j}{i}"
                )

        if st.button("Найти устойчивые коалиции", use_container_width=True, type="primary"):
            # Собираем матрицы
            pair_matrices = {}
            for (i, j) in pairs:
                A_ij = st.session_state[f"A{i}{j}"]
                A_ji = st.session_state[f"A{j}{i}"]
                pair_matrices[(i, j)] = (A_ij.copy(), A_ji.copy())

            try:
                game = ThreePlayerCooperativeGame(pair_matrices)
            except Exception as e:
                st.error(f"Ошибка при построении игры: {e}")
                st.stop()

            # ==================== ПОДРОБНЫЙ ВЫВОД ПО ЭТАПАМ ====================
            st.markdown("---")
            st.markdown("## 🔍 Подробный анализ по этапам")

            # ---------- ЭТАП 1 ----------
            st.markdown("### Этап 1: Некооперативные выигрыши (исходные взаимодействия)")
            st.markdown(
                "Решаются попарные биматричные игры 2×2 методом Лемке–Хаусона. "
                "Для каждого игрока его индивидуальный выигрыш вычисляется как среднее арифметическое по двум партнёрам."
            )
            d1, d2, d3 = game.d[1], game.d[2], game.d[3]
            st.markdown(f"- Игрок 1: $d_1 = {d1:.4f}$")
            st.markdown(f"- Игрок 2: $d_2 = {d2:.4f}$")
            st.markdown(f"- Игрок 3: $d_3 = {d3:.4f}$")

            # ---------- ЭТАП 2 ----------
            st.markdown("### Этап 2: Характеристическая функция $v(S)$ (коалиционные возможности)")
            st.markdown(
                "Для каждой коалиции $S$ строится антагонистическая игра $S$ против $N \\setminus S$. "
                "Значение $v(S)$ — гарантированный суммарный выигрыш коалиции (максимин)."
            )
            for size in [1, 2, 3]:
                for S in itertools.combinations([1, 2, 3], size):
                    key = frozenset(S)
                    st.markdown(f"- $v(\\{{{','.join(map(str, S))}\\}}) = {game.v[key]:.4f}$")

            vN = game.v[frozenset({1, 2, 3})]

            # ---------- ЭТАП 3 ----------
            st.markdown("### Этап 3: Устойчивая коалиционная структура (ядро большой коалиции)")
            st.markdown(
                f"Проверяется, можно ли распределить $v(\\{{1,2,3\\}}) = {vN:.4f}$ так, "
                "чтобы никакой подгруппе не было выгодно отделиться. "
                "Если такое распределение существует — большая коалиция устойчива (ядро непусто)."
            )

            # Получаем точку ядра, ближайшую к некооперативным выигрышам
            core_exists, x_core = game.core_allocation()
            if not core_exists:
                st.markdown("**❌ Ядро большой коалиции пусто.** Поиск устойчивого разбиения...")
                part, x_part = game.find_stable_partition()
                if part:
                    st.markdown(f"Найдена устойчивая коалиционная структура: {part}")
                    for i in [1, 2, 3]:
                        st.markdown(f"- $x_{i} = {x_part[i]:.4f}$")
                else:
                    st.markdown("Устойчивой структуры не найдено (в рамках модели).")
                st.stop()

            st.markdown("**✅ Ядро большой коалиции непусто.** Большая коалиция $\\{1,2,3\\}$ экономически устойчива в смысле кооперативной теории.")

            # ---------- ЭТАП 4 ----------
            st.markdown("### Этап 4: Дележ и проверка условий устойчивости")
            st.markdown("Внутри большой коалиции выигрыш делится между участниками. Рассматриваются два принципа дележа:")

            shap = game.shapley_values()
            st.markdown("#### 4a. Вектор Шепли (по вкладам каждого участника)")
            st.markdown(f"- $\\varphi_1 = {shap[1]:.4f}$")
            st.markdown(f"- $\\varphi_2 = {shap[2]:.4f}$")
            st.markdown(f"- $\\varphi_3 = {shap[3]:.4f}$")

            st.markdown("#### 4b. Дележ, ближайший к некооперативным выигрышам (евклидово расстояние)")
            x1, x2, x3 = x_core[1], x_core[2], x_core[3]
            st.markdown(f"- $x_1^* = {x1:.4f}$")
            st.markdown(f"- $x_2^* = {x2:.4f}$")
            st.markdown(f"- $x_3^* = {x3:.4f}$")

            # ---------- Проверка всех условий ядра ----------
            st.markdown("#### Проверка кооперативной рациональности (все условия ядра):")

            core_conditions_ok = True

            # Эффективность
            sum_x = x1 + x2 + x3
            ok_sum = abs(sum_x - vN) < 1e-8
            core_conditions_ok = core_conditions_ok and ok_sum
            st.markdown(
                f"- **Эффективность:** $x_1+x_2+x_3 = {sum_x:.4f} = v(N) = {vN:.4f}$ → {'✅' if ok_sum else '❌'}"
            )

            # Индивидуальная рациональность
            for i in [1, 2, 3]:
                vi = game.v[frozenset({i})]
                xi = x_core[i]
                ok_i = xi >= vi - 1e-8
                core_conditions_ok = core_conditions_ok and ok_i
                st.markdown(
                    f"- **Игрок {i}:** $x_{{{i}}} = {xi:.4f} \\ge v(\\{{{i}\\}}) = {vi:.4f}$ → {'✅' if ok_i else '❌'}"
                )

            # Коалиционная рациональность для пар
            for pair in [(1, 2), (1, 3), (2, 3)]:
                S_key = frozenset(pair)
                sum_pair = sum(x_core[i] for i in pair)
                v_pair = game.v[S_key]
                ok_pair = sum_pair >= v_pair - 1e-8
                core_conditions_ok = core_conditions_ok and ok_pair

                # Красивое форматирование: {1,2} вместо (1,2)
                pair_str = "\\{" + ",".join(map(str, pair)) + "\\}"
                st.markdown(
                    f"- **Коалиция {pair_str}:** "
                    f"$x_{{{pair[0]}}}+x_{{{pair[1]}}} = {sum_pair:.4f} \\ge "
                    f"v({pair_str}) = {v_pair:.4f}$ → {'✅' if ok_pair else '❌'}"
                )

            if core_conditions_ok:
                st.markdown("**Все условия ядра выполнены — данный дележ принадлежит ядру.**")
            else:
                st.markdown("**Некоторые условия ядра нарушены — данный дележ не принадлежит ядру.**")

            # ---------- Сравнение с некооперативным статус-кво ----------
            st.markdown("#### Сравнение с некооперативным статус-кво ($x_i \\ge d_i$):")
            st.markdown("Проверяем, получает ли каждый игрок в коалиции не меньше своего некооперативного выигрыша.")
            for i in [1, 2, 3]:
                xi = x_core[i]
                di = game.d[i]
                ok_d = xi >= di - 1e-8
                st.markdown(f"- Игрок {i}: $x_{{{i}}} = {xi:.4f}$, $d_{{{i}}} = {di:.4f}$ → {'✅ выгодно' if ok_d else '❌ невыгодно'}")

            # Универсальный вывод (без жёстко заданных чисел)
            if x1 < d1 - 1e-8:
                st.markdown(
                    f"**Вывод:** Для игрока 1 условие $x_1 \\ge d_1$ не выполняется "
                    f"(${x1:.4f} < {d1:.4f}$). "
                    "Однако это не нарушает устойчивость в смысле ядра, так как ядро определяется "
                    "характеристической функцией $v(S)$ и коалиционными ограничениями. "
                    f"Из ограничения для коалиции $\\{{2,3\\}}$ следует "
                    f"$x_1 \\le v(N)-v(\\{{2,3\\}}) = {vN:.4f} - {game.v[frozenset({2,3})]:.4f} = {vN - game.v[frozenset({2,3})]:.4f}$. "
                    "Поэтому в данной игре невозможно одновременно выполнить условия ядра и "
                    "$x_1 \\ge d_1$. Если некооперативный выигрыш рассматривается как обязательный "
                    "минимальный уровень, то устойчивого дележа в ядре с такими требованиями не существует."
                )
            else:
                st.markdown(
                    "**Вывод:** Найденный дележ принадлежит ядру и одновременно не хуже "
                    "некооперативного статус-кво для всех игроков."
                )

            st.markdown("---")
            st.success("Анализ завершён. Ядро непусто, большая коалиция устойчива (в смысле теоретико-игрового ядра).")

            with st.expander("📐 Подробные вычисления кооперативного анализа"):
                st.text(game.get_detailed_log())

            # Получаем логи парных игр (сохранены в game.pair_logs)
            if game.pair_logs:
                with st.expander("Подробные логи решений Лемке-Хаусена (парные игры)", expanded=False):
                    for (i, j, log) in game.pair_logs:
                        st.markdown(f"#### Игра {i} против {j}")
                        st.text(log)

def _is_streamlit_context() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False


if __name__ == "__main__":
    if _is_streamlit_context():
        main()
    else:
        print("Это Streamlit-приложение. Запуск: streamlit run app.py")