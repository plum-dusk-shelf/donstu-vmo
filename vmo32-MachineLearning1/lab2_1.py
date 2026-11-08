import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split


def load_and_prepare_data(data, test_size=0.1, random_state=42):
    # data = pd.read_csv(filename)

    numeric_columns = data.select_dtypes(include=[np.number]).columns
    class_column = None

    for col in data.columns:
        if data[col].dtype == 'object' or data[col].nunique() < 20:
            class_column = col
            break

    if class_column is None:
        raise ValueError("Не найден категориальный столбец для определения классов")

    unique_classes = data[class_column].unique()
    print(f"Найдены классы: {unique_classes}")

    if len(unique_classes) > 2:
        print(f"Внимание: найдено {len(unique_classes)} классов. Используем первые два: {unique_classes[:2]}")
        class1, class2 = unique_classes[:2]
        data = data[data[class_column].isin([class1, class2])]
    else:
        class1, class2 = unique_classes

    X = data[numeric_columns].values
    y = data[class_column].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    X_1_train = X_train[y_train == class1]
    X_2_train = X_train[y_train == class2]
    X_1_test = X_test[y_test == class1]
    X_2_test = X_test[y_test == class2]

    return {
        'class1_name': class1,
        'class2_name': class2,
        'X_1_train': X_1_train.tolist(),
        'X_2_train': X_2_train.tolist(),
        'X_1_test': X_1_test.tolist(),
        'X_2_test': X_2_test.tolist(),
        'feature_names': numeric_columns.tolist(),
        'class_column': class_column
    }


def calculate_discriminant_function(X_1, X_2):
    """
    Вычисление дискриминантной функции для двух классов
    """
    n1 = len(X_1)
    n2 = len(X_2)
    X_1_ar = np.array(X_1)
    X_2_ar = np.array(X_2)

    X_11 = np.mean(X_1_ar, axis=0)
    X_12 = np.mean(X_2_ar, axis=0)

    s1 = np.zeros((X_1_ar.shape[1], X_1_ar.shape[1]))
    s2 = np.zeros((X_2_ar.shape[1], X_2_ar.shape[1]))

    for j in range(X_1_ar.shape[1]):
        for l in range(X_1_ar.shape[1]):
            sum_cov_1 = sum((X_1_ar[i][j] - X_11[j]) * (X_1_ar[i][l] - X_11[l]) for i in range(n1))
            s1[j][l] = sum_cov_1 / n1

    for j in range(X_2_ar.shape[1]):
        for l in range(X_2_ar.shape[1]):
            sum_cov_2 = sum((X_2_ar[i][j] - X_12[j]) * (X_2_ar[i][l] - X_12[l]) for i in range(n2))
            s2[j][l] = sum_cov_2 / n2

    so = (1 / (n1 + n2 - 2)) * (n1 * s1 + n2 * s2)
    regularization_param = 1e-6
    so_reg = so + regularization_param * np.eye(so.shape[0])
    so_obrat = np.linalg.inv(so_reg)
    a = so_obrat @ (X_11 - X_12)

    return a, X_11, X_12


def main():
    try:
        df1 = pd.read_csv('Credit_card.csv')
        df2 = pd.read_csv('Credit_card_label.csv')
        my_dict = pd.merge(df2, df1, on='Ind_ID').drop(columns=['Mobile_phone','Work_Phone','Phone','EMAIL_ID','Type_Occupation'])
        print(my_dict.head(5))
        data_dict = load_and_prepare_data(my_dict)
        # data_dict = load_and_prepare_data(pd.read_csv('Discriminate_Analize_DataSet_1.csv'), test_size=0.3)

        class1_name = data_dict['class1_name']
        class2_name = data_dict['class2_name']
        X_1_train = data_dict['X_1_train']
        X_2_train = data_dict['X_2_train']
        X_1_test = data_dict ['X_1_test']
        X_2_test = data_dict['X_2_test']

        print(f"Используемые классы: {class1_name} и {class2_name}")
        print(f"Признаки: {data_dict['feature_names']}")

    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return

    A, X_11, X_12 = calculate_discriminant_function(X_1_train, X_2_train)

    X_1_ar_train = np.array(X_1_train)
    X_2_ar_train = np.array(X_2_train)

    F_1_train = np.sum(A * X_1_ar_train, axis=1)
    F_2_train = np.sum(A * X_2_ar_train, axis=1)

    F_1_mean = F_1_train.mean()
    F_2_mean = F_2_train.mean()
    F_all = (F_1_mean + F_2_mean) / 2

    F_1_centered = F_1_train - F_all
    F_2_centered = F_2_train - F_all

    X_1_ar_test = np.array(X_1_test)
    X_2_ar_test = np.array(X_2_test)

    F_1_test = np.sum(A * X_1_ar_test, axis=1)
    F_2_test = np.sum(A * X_2_ar_test, axis=1)

    F_1_test_centered = F_1_test - F_all
    F_2_test_centered = F_2_test - F_all

    plt.figure(figsize=(15, 6))

    plt.subplot(1, 2, 1)
    plt.plot(range(1, len(F_1_centered) + 1), F_1_centered, 'bo',
             label=class1_name, markersize=8)
    plt.plot(range(len(F_1_centered) + 1, len(F_1_centered) + len(F_2_centered) + 1),
             F_2_centered, 'ro', label=class2_name, markersize=8)

    plt.axhline(y=0, color='black', linestyle='--', linewidth=2,
                label='граница классификации')

    plt.xlabel('номер объекта')
    plt.ylabel('дискриминантная функция')
    plt.title(f'Тренировочные данные\n{class1_name} vs {class2_name}')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.subplot(1, 2, 2)
    plt.plot(range(1, len(F_1_test_centered) + 1), F_1_test_centered, 'bo',
             label=class1_name, markersize=8)
    plt.plot(range(len(F_1_test_centered) + 1,
                   len(F_1_test_centered) + len(F_2_test_centered) + 1),
             F_2_test_centered, 'ro', label=class2_name, markersize=8)

    plt.axhline(y=0, color='black', linestyle='--', linewidth=2,
                label='граница классификации')

    plt.xlabel('номер объекта')
    plt.ylabel('дискриминантная функция')
    plt.title(f'Тестовые данные\n{class1_name} vs {class2_name}')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    print(f"\nстатистика данных:")
    print(f"тренировочные данные:")
    print(f"  {class1_name}: {len(F_1_centered)} объектов")
    print(f"  {class2_name}: {len(F_2_centered)} объектов")

    print(f"\nтестовые данные:")
    print(f"  {class1_name}: {len(F_1_test_centered)} объектов")
    print(f"  {class2_name}: {len(F_2_test_centered)} объектов")

    correct_1 = np.sum(F_1_test_centered > 0)
    correct_2 = np.sum(F_2_test_centered < 0)
    total_correct = correct_1 + correct_2
    total_test = len(F_1_test_centered) + len(F_2_test_centered)
    accuracy = total_correct / total_test

    print(f"\nточность классификации на тестовых данных: {accuracy:.4f}")
    print(f"  {class1_name}: {correct_1}/{len(F_1_test_centered)} правильно классифицированы")
    print(f"  {class2_name}: {correct_2}/{len(F_2_test_centered)} правильно классифицированы")


if __name__ == "__main__":
    main()