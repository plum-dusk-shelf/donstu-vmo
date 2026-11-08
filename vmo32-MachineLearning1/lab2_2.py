import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

from lab2_1 import prepare_universal_data


def load_credit_card_data(features_file, target_file, test_size=0.3, random_state=42):
    """
    Загружает данные кредитных карт из двух файлов: признаки и целевая переменная.
    Объединяет их и подготавливает для дискриминантного анализа.
    """
    # Загрузка данных
    features_df = pd.read_csv(features_file)
    target_df = pd.read_csv(target_file)

    # Объединение данных по индексу или общему столбцу (предполагается, что строки соответствуют друг другу)
    # Если в данных есть явный идентификатор, укажите его в параметре 'on', например: on='id'
    data = pd.concat([features_df, target_df], axis=1)

    # Автоматическое определение имени целевого столбца
    # Предполагается, что целевой столбец называется 'Class', 'Target' или находится в единственном числе в target_df
    potential_target_cols = target_df.columns
    if len(potential_target_cols) == 1:
        target_column = potential_target_cols[0]
    else:
        # Эвристика: ищем столбец с бинарными значениями или с именем, содержащим 'class', 'target'
        for col in potential_target_cols:
            if data[col].nunique() == 2 or any(keyword in col.lower() for keyword in ['class', 'target', 'approval']):
                target_column = col
                break
        else:
            # Если не нашли, используем первый столбец из target_df
            target_column = potential_target_cols[0]
            print(
                f"Целевой столбец автоматически определен как: {target_column}. Если это неверно, задайте его вручную.")

    # Автоматическое определение числовых признаков
    numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
    # Удаляем целевой столбец из признаков, если он там есть
    if target_column in numeric_columns:
        numeric_columns.remove(target_column)

    # Определяем уникальные классы
    unique_classes = data[target_column].unique()
    print(f"Найдены классы: {unique_classes}")

    # Если классов больше 2, берем первые два
    if len(unique_classes) > 2:
        print(f"Внимание: найдено {len(unique_classes)} классов. Используем первые два: {unique_classes[:2]}")
        data = data[data[target_column].isin(unique_classes[:2])]
        unique_classes = unique_classes[:2]

    # Разделяем данные на признаки (X) и целевую переменную (y)
    X = data[numeric_columns].values
    y = data[target_column].values

    # Разделяем на тренировочную и тестовую выборки
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # Разделяем по классам
    class1, class2 = unique_classes
    X_1_train = X_train[y_train == class1]
    X_2_train = X_train[y_train == class2]
    X_1_test = X_test[y_test == class1]
    X_2_test = X_test[y_test == class2]

    return {
        'class1_name': str(class1),
        'class2_name': str(class2),
        'X_1_train': X_1_train.tolist(),
        'X_2_train': X_2_train.tolist(),
        'X_1_test': X_1_test.tolist(),
        'X_2_test': X_2_test.tolist(),
        'feature_names': numeric_columns,
        'target_column': target_column
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
    so_obrat = np.linalg.inv(so)
    a = so_obrat @ (X_11 - X_12)

    return a, X_11, X_12


def main():
    try:
        data_dict = load_credit_card_data('Credit_card.csv', 'Credit_card_label.csv')

        class1_name = data_dict['class1_name']
        class2_name = data_dict['class2_name']
        X_1_train = data_dict['X_1_train']
        X_2_train = data_dict['X_2_train']
        X_1_test = data_dict['X_1_test']
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
