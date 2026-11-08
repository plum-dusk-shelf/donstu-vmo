# app.py
import streamlit as st
import pandas as pd
from fractions import Fraction
from solver import solve_matrix_game_with_iterations

st.set_page_config(page_title="Матричная игра — симплекс", layout="wide")

st.markdown("""
<style>
.block-container {max-width: 1200px;}
</style>
""", unsafe_allow_html=True)

def frac_to_str(x):
    if isinstance(x, Fraction):
        return f"{x.numerator}/{x.denominator}" if x.denominator != 1 else str(x.numerator)
    return str(x)

def format_tableau(tableau, exact, row_lead=None, col_lead=None):
    """Преобразует таблицу в DataFrame с подсветкой ведущего элемента."""
    m = len(tableau) - 1
    # Определяем n приблизительно: число столбцов минус m минус 1 (RHS)
    n = len(tableau[0]) - m - 1
    index = [f"x{i+1}" for i in range(m)] + ["Δ"]
    columns = [f"y{j+1}" for j in range(n)] + [f"s{i+1}" for i in range(m)] + ["RHS"]
    df = pd.DataFrame(tableau, index=index, columns=columns)

    if row_lead is not None and col_lead is not None:
        # Создаём маску стиля
        styler = df.style.applymap(
            lambda v: 'background-color: red; color: white',
            subset=pd.IndexSlice[index[row_lead], columns[col_lead]]
        )
    else:
        styler = df.style

    if exact:
        styler = styler.format(frac_to_str)
    else:
        styler = styler.format("{:.6g}")
    return styler

# Интерфейс выбора размерности
c1, c2, c3, c4 = st.columns([3, 1, 0.4, 1])
with c1:
    st.write("**Размерность платежной матрицы**")
with c2:
    m = st.selectbox("", list(range(1, 21)), index=1, key="m")
with c3:
    st.write("**×**")
with c4:
    n = st.selectbox("", list(range(1, 21)), index=4, key="n")

st.write("### Матрица")

if "A" not in st.session_state or len(st.session_state.A) != m or len(st.session_state.A[0]) != n:
    default_matrix = [
        [4, 5, -3, 1, 3],
        [5, -7, 8, 6, 8]
    ]
    st.session_state.A = default_matrix
A = st.session_state.A

for i in range(m):
    cols = st.columns(n)
    for j in range(n):
        with cols[j]:
            A[i][j] = st.number_input(
                label=f"A[{i+1},{j+1}]",
                value=float(A[i][j]),
                step=1.0,
                label_visibility="collapsed",
                key=f"cell_{i}_{j}",
            )

st.session_state.A = A

cbtn1, cbtn2, cbtn3 = st.columns([1, 1, 2])
with cbtn1:
    solve_btn = st.button("Решить", use_container_width=True)
with cbtn2:
    clear_btn = st.button("Очистить", use_container_width=True)

if clear_btn:
    st.session_state.A = [[0.0 for _ in range(n)] for _ in range(m)]
    st.rerun()

exact = True
if solve_btn:
    try:
        res = solve_matrix_game_with_iterations(st.session_state.A, exact=exact)

        # 1. Проверка на седловую точку
        if res.get("saddle_point", False):
            st.info("✅ Найдена седловая точка — игра решается в чистых стратегиях.")
            st.write(f"**Седловой элемент:** A[{res['saddle_row']+1}, {res['saddle_col']+1}] = {frac_to_str(res['saddle_value'])}")
            st.write(f"**Цена игры v = {frac_to_str(res['v'])}**")
            st.write("**Оптимальная стратегия игрока I:**", [frac_to_str(x) for x in res["p"]])
            st.write("**Оптимальная стратегия игрока II:**", [frac_to_str(x) for x in res["q"]])
            # Завершаем, дальше не идём
            st.stop()

        # 2. Сообщения о доминировании
        dom_msgs = res.get("dominance_messages", [])
        if dom_msgs:
            st.subheader("Редукция по доминированию")
            for msg in dom_msgs:
                st.write("• " + msg)
            st.write("**Редуцированная матрица:**")
            red_df = pd.DataFrame(
                [[frac_to_str(x) if exact else f"{x:.6g}" for x in row] for row in res["reduced_matrix"]],
                index=[f"Строка {i+1}" for i in range(len(res['reduced_matrix']))],
                columns=[f"Столбец {j+1}" for j in range(len(res['reduced_matrix'][0]))]
            )
            st.dataframe(red_df)
        else:
            st.write("Доминирование не обнаружено.")

        # 3. Сдвиг матрицы (если был)
        if res['K'] != 0:
            st.subheader("Модифицированная матрица (после сдвига)")
            df_shifted = pd.DataFrame(
                [[frac_to_str(x) if exact else f"{x:.6g}" for x in row] for row in res['A_shifted']],
                index=[f"Строка {i+1}" for i in range(len(res['A_shifted']))],
                columns=[f"Столбец {j+1}" for j in range(len(res['A_shifted'][0]))]
            )
            st.dataframe(df_shifted)
        else:
            st.write("Сдвиг не потребовался (все элементы матрицы положительные)")

        # 4. Основные результаты
        st.subheader("Результаты")
        st.write(f"Сдвиг K: **{res['K']}**")
        st.write(f"Цена игры для сдвинутой матрицы v': **{frac_to_str(res['v_shift'])}**  (≈ {float(res['v_shift']):.6g})")
        st.write(f"Цена исходной игры v = v' - K: **{frac_to_str(res['v'])}**  (≈ {float(res['v']):.6g})")

        st.write("**Оптимальная смешанная стратегия игрока I (строки) P:**")
        st.write([frac_to_str(x) for x in res["p"]])

        st.write("**Оптимальная смешанная стратегия игрока II (столбцы) Q:**")
        st.write([frac_to_str(x) for x in res["q"]])

        # 5. Пошаговые итерации
        with st.expander("Симплекс-таблицы для игрока 1"):
            iterations = res['iterations']
            for idx, it in enumerate(iterations):
                st.markdown(f"#### Шаг {idx} ({it['method']})")
                if it['row'] is not None and it['col'] is not None:
                    st.markdown(f"Ведущий элемент: строка **{it['row']+1}** (x{it['row']+1}), столбец **{it['col']+1}**")
                styler = format_tableau(it['tableau'], exact, it['row'], it['col'])
                st.dataframe(styler, use_container_width=True)

        with st.expander("Слау для игрока 2"):
            B = res["B"]
            b_vec = res["b_vec"]
            for i in range(len(b_vec)):
                B_row = " + ".join([f'{B[i][j]} x{j}' for j in range(len(B[i]))])
                eq = f'{B_row} = {str(b_vec[i])}'
                st.markdown(eq)

        # 6. Служебные данные
        with st.expander("Показать редуцированные стратегии"):
            st.write("y:", [frac_to_str(x) for x in res["y"]])
            st.write("x:", [frac_to_str(x) for x in res["x"]])

    except Exception as e:
        st.error(f"Ошибка: {e}")