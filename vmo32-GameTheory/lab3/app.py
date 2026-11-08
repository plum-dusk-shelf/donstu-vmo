import io
from contextlib import redirect_stdout

import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

from solver import (
    solve_bimatrix_game,
    BimatrixGame,
    plot_graphical_solution,
    reduce_game_by_dominance,
)


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


def init_state():
    if "m" not in st.session_state:
        st.session_state.m = 2
    if "n" not in st.session_state:
        st.session_state.n = 2
    if "A" not in st.session_state:
        st.session_state.A = np.zeros((2, 2), dtype=float)
    if "B" not in st.session_state:
        st.session_state.B = np.zeros((2, 2), dtype=float)


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


def main():
    st.set_page_config(page_title="Решение биматричных игр - Лемке-Хоусен", layout="wide")
    init_state()

    st.title("Решение биматричных игр - Алгоритм Лемке-Хоусена")

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
        m = c1.number_input("Стратегии игрока A (строки)", min_value=1, max_value=10, value=int(st.session_state.m), step=1)
        n = c2.number_input("Стратегии игрока B (столбцы)", min_value=1, max_value=10, value=int(st.session_state.n), step=1)
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
        st.session_state.A = draw_matrix_editor("Матрица A (выигрыши игрока A)", st.session_state.A, "A")

    with st.container(border=True):
        st.session_state.B = draw_matrix_editor("Матрица B (выигрыши игрока B)", st.session_state.B, "B")

    solve_clicked = st.button("РЕШИТЬ ИГРУ", use_container_width=True, type="primary")

    if solve_clicked:
        output_lines = []
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
        st.text_area("Лог решения", value="\n".join(output_lines), height=800)

        if x_star is not None and y_star is not None:
            st.success("Решение получено")
            st.write("x*:", np.array(x_star))
            st.write("y*:", np.array(y_star))

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
                    can_plot = (st.session_state.A.shape == (2, 2) and st.session_state.B.shape == (2, 2))
                    plot_A, plot_B = st.session_state.A, st.session_state.B
                else:
                    can_plot = (A_reduced.shape == (2, 2) and B_reduced.shape == (2, 2))
                    plot_A, plot_B = A_reduced, B_reduced

                if can_plot:
                    game = BimatrixGame(plot_A, plot_B)
                    fig = plot_graphical_solution(game)
                    st.pyplot(fig)


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
        print("Это Streamlit-приложение. Запуск: streamlit run app_lemke.py")
