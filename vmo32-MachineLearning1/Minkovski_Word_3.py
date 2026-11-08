import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
import lab1_data

# Ввод числа p для расстояния Минковского
p = int(input("Введите число p для расстояния Минковского: "))
st = str(input("Введите название файла: "))
# Чтение данных из CSV с определенными условиями Minkovski_Ward_DataSet_1.csv pinguine_type_MW.csv pinguine_type.csv
df = lab1_data.my_dataset
print("Исходные данные:")
print(df)
print()

# Определяем признаки и объекты
objects = df['object'].values
features = df.iloc[:, 1:].values

# Шаг 1: Каждый объект представляется как отдельный кластер
clusters = {i: np.array([features[i]]) for i in range(len(df))}
cluster_names = {i: [objects[i]] for i in range(len(df))}
cluster_indices = list(range(len(df)))

print("Начальные кластеры:")
for i in cluster_indices:
    print(f"C{i + 1} {cluster_names[i]}: {clusters[i]}")
print()

# Функция для вычисления расстояния Минковского
def minkowski_distance(point1, point2, p=2):
    return np.sum(np.abs(point1 - point2) ** p) ** (1 / p)

# Шаг 2: Создаем начальную матрицу расстояний (расстояние Минковского)
def create_initial_distance_matrix(clusters, indices):
    n = len(indices)
    distance_matrix = np.zeros((n, n))

    for idx_i, i in enumerate(indices):
        for idx_j, j in enumerate(indices):
            if idx_i < idx_j:
                # Расстояние Минковского между точками
                dist = minkowski_distance(clusters[i][0], clusters[j][0], p)
                distance_matrix[idx_i, idx_j] = dist
                distance_matrix[idx_j, idx_i] = dist

    return distance_matrix

# Функция для обновления матрицы расстояний по методу Ворда
def update_distance_matrix_ward(old_matrix, min_i_idx, min_j_idx, cluster_sizes, indices):
    n = len(old_matrix)
    new_matrix = np.zeros((n - 1, n - 1))
    new_indices = indices.copy()
    i_val = indices[min_i_idx]
    j_val = indices[min_j_idx]

    new_indices.remove(i_val)
    new_indices.remove(j_val)
    new_indices.append(i_val)  # Используем i_val как индекс нового кластера

    idx_map = {}
    for new_idx, old_val in enumerate(new_indices):
        idx_map[old_val] = new_idx

    for a_idx, a_val in enumerate(indices):
        if a_val == i_val or a_val == j_val:
            continue
        for b_idx, b_val in enumerate(indices):
            if b_val == i_val or b_val == j_val or b_idx <= a_idx:
                continue
            if a_val in idx_map and b_val in idx_map:
                new_a = idx_map[a_val]
                new_b = idx_map[b_val]
                new_matrix[new_a, new_b] = old_matrix[a_idx, b_idx]
                new_matrix[new_b, new_a] = old_matrix[a_idx, b_idx]

    new_cluster_idx = idx_map[i_val]
    for k_idx, k_val in enumerate(indices):
        if k_val == i_val or k_val == j_val:
            continue
        new_k = idx_map[k_val]

        k_u = cluster_sizes[i_val]
        k_v = cluster_sizes[j_val]
        k_s = cluster_sizes[k_val]
        k_w = k_u + k_v

        p_us = old_matrix[min_i_idx, k_idx]
        p_vs = old_matrix[min_j_idx, k_idx]
        p_uv = old_matrix[min_i_idx, min_j_idx]

        # Формула метода Ворда
        p_ws = np.sqrt(((k_u + k_s) / (k_w + k_s)) * p_us ** 2 + ((k_v + k_s) / (k_w + k_s)) * p_vs ** 2 - (k_s / (k_w + k_s)) * p_uv ** 2)


        new_matrix[new_k, new_cluster_idx] = p_ws
        new_matrix[new_cluster_idx, new_k] = p_ws

    return new_matrix, new_indices, idx_map

# Инициализация
t = 0
n_clusters = len(clusters)
cluster_sizes = {i: 1 for i in range(len(df))}
current_indices = list(range(len(df)))

distance_matrix = create_initial_distance_matrix(clusters, current_indices)

# Для построения дендрограммы
linkage_data = []

print("ШАГ 1: Начальная матрица расстояний (Минковский):")
print("Матрица расстояний:")
print(np.round(distance_matrix, 2))
print()

# Процесс кластеризации
while n_clusters > 1:
    t += 1
    print(f"ШАГ {t}:")

    # Шаг 3: Находим минимальное расстояние в матрице
    min_distance = np.inf
    min_i_idx, min_j_idx = -1, -1

    for i in range(len(distance_matrix)):
        for j in range(i + 1, len(distance_matrix)):
            if distance_matrix[i, j] < min_distance:
                min_distance = distance_matrix[i, j]
                min_i_idx, min_j_idx = i, j

    # Получаем реальные индексы кластеров
    i_val = current_indices[min_i_idx]
    j_val = current_indices[min_j_idx]

    print(f"Минимальное расстояние: {min_distance:.4f} между кластерами {i_val + 1} и {j_val + 1}")
    print(f"Объединяем кластеры {i_val + 1} {cluster_names[i_val]} и {j_val + 1} {cluster_names[j_val]}")

    # Шаг 4: Объединяем кластеры
    new_cluster_points = np.vstack([clusters[i_val], clusters[j_val]])
    clusters[i_val] = new_cluster_points
    cluster_names[i_val] = cluster_names[i_val] + cluster_names[j_val]

    # Обновляем размеры кластеров
    cluster_sizes[i_val] = cluster_sizes[i_val] + cluster_sizes[j_val]

    # Сохраняем данные для дендрограммы
    linkage_data.append([i_val, j_val, min_distance, cluster_sizes[i_val]])

    # Шаг 5: Обновляем матрицу расстояний
    if n_clusters > 2:
        distance_matrix, current_indices, idx_map = update_distance_matrix_ward(
            distance_matrix, min_i_idx, min_j_idx, cluster_sizes, current_indices
        )

        print("Обновленная матрица расстояний:")
        print(np.round(distance_matrix, 2))
    else:
        print("Все кластеры объединены!")

    n_clusters -= 1
    print()

# Построение дендрограммы
print("ФИНАЛЬНЫЙ РЕЗУЛЬТАТ:")
final_cluster_idx = current_indices[0] if current_indices else 0
print(f"Все кластеры объединены в один: {cluster_names[final_cluster_idx]}")
print()

# Вывод подробной информации о кластеризации
print("ДЕТАЛИ КЛАСТЕРИЗАЦИИ:")
for i, step in enumerate(linkage_data):
    cluster1, cluster2, distance, size = step
    print(f"Шаг {i + 1}: Объединены кластеры {cluster1 + 1} и {cluster2 + 1}, "
          f"расстояние = {distance:.4f}, размер нового кластера = {size}")

# Подготовка данных для дендрограммы
X = df.iloc[:, 1:].values
areas = df['object'].values

# Использование встроенной функции linkage из scipy
Z = linkage(X, method='ward', metric='euclidean')

# Построение дендрограммы
plt.figure(figsize=(12, 8))
dendrogram(Z, labels=areas, orientation='top', leaf_rotation=90)
plt.title('Дендрограмма иерархической кластеризации (метод Ворда)')
plt.xlabel('Области')
plt.ylabel('Расстояние')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()


if features.shape[1] == 2:  # Если два признака
    plt.figure(figsize=(10, 6))
    plt.scatter(features[:, 0], features[:, 1], c='blue', marker='o')
    for i, txt in enumerate(objects):
        plt.annotate(txt, (features[i, 0], features[i, 1]), fontsize=9)
    plt.title('2D график признаков')
    plt.xlabel('p1')
    plt.ylabel('p2')
    plt.grid(True)
    plt.show()
elif features.shape[1] == 3:  # Если три признака
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(features[:, 0], features[:, 1], features[:, 2], c='blue', marker='o')
    for i, txt in enumerate(objects):
        ax.text(features[i, 0], features[i, 1], features[i, 2], txt, fontsize=9)

    ax.set_title('3D график признаков')
    ax.set_xlabel('p1')
    ax.set_ylabel('p2')
    ax.set_zlabel('p3')
    plt.show()
else:
    print("Количество признаков должно быть 2 или 3 для построения графика.")

