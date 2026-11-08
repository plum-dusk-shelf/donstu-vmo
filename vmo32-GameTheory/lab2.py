import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Критерии принятия решений", layout="wide")

st.title("Анализ платёжной матрицы")

st.markdown("Введите матрицу (строки через Enter, элементы через пробел):")

matrix_input = st.text_area("Матрица", "10 5 8\n7 9 6\n3 4 2")

st.markdown("Введите вероятности для столбцов (через пробел):")
prob_input = st.text_input("Вероятности", "0.3 0.4 0.3")

alpha = st.slider("Параметр Гурвица (α)", 0.0, 1.0, 0.5)


def parse_matrix(text):
    return np.array([list(map(float, row.split())) for row in text.strip().split("\n")])


def parse_probs(text):
    return np.array(list(map(float, text.strip().split())))


if st.button("Рассчитать"):
    try:
        A = parse_matrix(matrix_input)
        probs = parse_probs(prob_input)

        if A.shape[1] != len(probs):
            st.error("Количество вероятностей должно совпадать с числом столбцов")
        else:
            st.subheader("Исходная матрица")
            st.dataframe(pd.DataFrame(A))

            # Матрица сожалений
            max_cols = A.max(axis=0)
            regret = max_cols - A

            st.subheader("Матрица сожалений")
            st.dataframe(pd.DataFrame(regret))

            # Критерий Вальда (максимин)
            wald_values = A.min(axis=1)
            wald_choice = np.argmax(wald_values)

            # Критерий Сэвиджа (минимакс сожалений)
            savage_values = regret.max(axis=1)
            savage_choice = np.argmin(savage_values)

            # Критерий Гурвица
            min_vals = A.min(axis=1)
            max_vals = A.max(axis=1)
            hurwicz_values = alpha * min_vals + (1 - alpha) * min_vals
            hurwicz_choice = np.argmax(hurwicz_values)

            # Условия определенности (матожидание)
            expected_values = A @ probs
            expected_choice = np.argmax(expected_values)

            st.subheader("Результаты")

            result_df = pd.DataFrame({
                "Вальд": wald_values,
                "Сэвидж": savage_values,
                "Гурвиц": hurwicz_values,
                "Мат. ожидание": expected_values
            })

            st.dataframe(result_df)

            st.markdown(f"**Выбор по Вальду:** {wald_choice}")
            st.markdown(f"**Выбор по Сэвиджу:** {savage_choice}")
            st.markdown(f"**Выбор по Гурвицу:** {hurwicz_choice}")
            st.markdown(f"**Выбор по мат. ожиданию:** {expected_choice}")

    except Exception as e:
        st.error(f"Ошибка: {e}")

