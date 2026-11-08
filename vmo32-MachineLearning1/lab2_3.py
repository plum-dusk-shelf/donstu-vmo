import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from Discriminate_Analize_3 import X_2_t

problem = 3 # int(input('Введите номер задачи: '))

match problem:
    case 1:
        data_0 = pd.read_csv('Discriminate_Analize_DataSet_1.csv')
        X_1_t = data_0[data_0['object'] == 'X_1'].drop(columns=['object']).values.tolist()
        X_2_t = data_0[data_0['object'] == 'X_2'].drop(columns=['object']).values.tolist()
        X_0 = data_0[data_0['object'] == 'X_0'].drop(columns=['object']).values.tolist()

    case 2:
        # Загрузка данных из csv файла
        data = pd.read_csv('Discriminate_Analize_DataSet_4.csv')
        data_2 = pd.read_csv('Discriminate_Analize_DataSet_3.csv')

        # Разделение данных по группам
        # X_1 = data[data['object'] == 'Adelie'].drop(columns=['object']).values.tolist()
        # X_2 = data[data['object'] == 'Gentoo'].drop(columns=['object']).values.tolist()

        X_1_t = data_2[data_2['object'] == 'Adelie'].drop(columns=['object']).values.tolist()
        X_2_t = data_2[data_2['object'] == 'Gentoo'].drop(columns=['object']).values.tolist()
        X_1, X_2 = (X_1_t, X_2_t)
        X_0 = data_2[data_2['object'] == 'object_researh'].drop(columns=['object']).values.tolist()

    case 3:
        data = pd.read_csv('Credit_card_label.csv')
        data_2 = pd.read_csv('Credit_card.csv')
        data_merged = pd.merge(data, data_2, on='Ind_ID')

        X_1 = data_merged[data_merged['object'] == 0].drop(columns=['object']).values.tolist()[:1400]
        X_2 = data_merged[data_merged['object'] == 1].drop(columns=['object']).values.tolist()[:1400]

        X_1_t = data_merged[data_merged['object'] == 0].drop(columns=['object']).values.tolist()[:1400]
        X_2_t = data_merged[data_merged['object'] == 1].drop(columns=['object']).values.tolist()[:1400]
        X_0 = data_merged[data_merged['object'] == 'object_researh'].drop(columns=['object']).values.tolist()[1400:]


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

SO = (1 / (n1 + n2 - 2)) * (n1 * s1 + n2 * s2)
SO_obrat = np.linalg.inv(SO)
A = SO_obrat @ (X_11 - X_12)

F_1 = np.sum(A * X_1_ar, axis=1)
F_2 = np.sum(A * X_2_ar, axis=1)

F_1_mean = F_1.mean()
F_2_mean = F_2.mean()
F_all = (F_1_mean + F_2_mean) / 2

F_1_centered = F_1 - F_all
F_2_centered = F_2 - F_all

# n1_t = len(X_1_t)
# n2_t = len(X_2_t)
# X_1_ar_t = np.array(X_1_t)
# X_2_ar_t = np.array(X_2_t)
#
# X_11_t = np.mean(X_1_ar_t, axis=0)
# X_12_t = np.mean(X_2_ar_t, axis=0)
#
# s1_t = np.zeros((X_1_ar_t.shape[1], X_1_ar_t.shape[1]))
# s2_t = np.zeros((X_2_ar_t.shape[1], X_2_ar_t.shape[1]))
#
# for j in range(X_1_ar_t.shape[1]):
#     for l in range(X_1_ar_t.shape[1]):
#         sum_cov_1_t = sum((X_1_ar_t[i][j] - X_11_t[j]) * (X_1_ar_t[i][l] - X_11_t[l]) for i in range(n1_t))
#         s1_t[j][l] = sum_cov_1_t / n1_t
#
# for j in range(X_2_ar_t.shape[1]):
#     for l in range(X_2_ar_t.shape[1]):
#         sum_cov_2_t = sum((X_2_ar_t[i][j] - X_12_t[j]) * (X_2_ar_t[i][l] - X_12_t[l]) for i in range(n2_t))
#         s2_t[j][l] = sum_cov_2_t / n2_t
#
# SO_t = (1 / (n1_t + n2_t - 2)) * (n1_t * s1_t + n2_t * s2_t)
# SO_obrat_t = np.linalg.inv(SO_t)
# A_t = SO_obrat_t @ (X_11_t - X_12_t)
#
# F_1_t = np.sum(A_t * X_1_ar_t, axis=1)
# F_2_t = np.sum(A_t * X_2_ar_t, axis=1)
#
# F_1_t_mean = F_1_t.mean()
# F_2_t_mean = F_2_t.mean()
# F_all_t = (F_1_t_mean + F_2_t_mean) / 2
#
# F_1_t_centered = F_1_t - F_all_t
# F_2_t_centered = F_2_t - F_all_t

F_0 = np.sum(A * np.array(X_0), axis=1) - F_all

plt.figure(figsize=(15, 6))

plt.subplot(1, 2, 1)
plt.plot(range(1, len(F_1_centered) + 1), F_1_centered, 'bo', label='class1', markersize=8)
plt.plot(range(len(F_1_centered) + 1, len(F_1_centered) + len(F_2_centered) + 1),
         F_2_centered, 'ro', label='class2', markersize=8)

plt.axhline(y=0, color='black', linestyle='--', linewidth=2,
            label='Граница классификации (FFf = 0)')

plt.xlabel('Номер объекта', fontsize=12)
plt.ylabel('FFf', fontsize=12)
plt.title('Значения FFf для class1 и class2 (тестовые данные)', fontsize=14)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
plt.plot(range(1, len(F_1_centered) + 1), F_1_centered, 'bo', label='class1 (обучение)', markersize=8)
plt.plot(range(len(F_1_centered) + 1, len(F_1_centered) + len(F_2_centered) + 1),
         F_2_centered, 'ro', label='class2 (обучение)', markersize=8)
plt.plot(range(len(F_1_centered) + len(F_2_centered) + 1,
               len(F_1_centered) + len(F_2_centered) + len(F_0) + 1),
         F_0, 'go', label='object_researh', markersize=8)

plt.axhline(y=0, color='black', linestyle='--', linewidth=2,
            label='Граница классификации (Ff = 0)')

plt.xlabel('Номер объекта', fontsize=12)
plt.ylabel('Ff', fontsize=12)
plt.title('Значения Ff для всех объектов', fontsize=14)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print(f"\nСТАТИСТИКА ДАННЫХ:")
print(f"ОБУЧАЮЩИЕ ДАННЫХ:")
print(f"  class1: {len(F_1_centered)} объектов, среднее F: {F_1_centered.mean():.4f}")
print(f"  class2: {len(F_2_centered)} объектов, среднее F: {F_2_centered.mean():.4f}")
print(f"  Исходная граница классификации: {F_all:.4f}")

print(f"\nТЕСТОВЫЕ ДАННЫЕ:")
print(f"  class1: {len(F_1_t_centered)} объектов, среднее F: {F_1_t_centered.mean():.4f}")
print(f"  class2: {len(F_2_t_centered)} объектов, среднее F: {F_2_t_centered.mean():.4f}")
print(f"  Исходная граница классификации: {F_all_t:.4f}")

print(f"\nОБЪЕКТЫ ДЛЯ ИССЛЕДОВАНИЯ:")
print(f"  object_researh: {len(F_0)} объектов")

print(f"\nВСЕГО ОБЪЕКТОВ: {len(F_1_centered) + len(F_2_centered) + len(F_0)}")

print(f"\nКЛАССИФИКАЦИЯ ОБЪЕКТОВ ИССЛЕДОВАНИЯ:")
for i, f_value in enumerate(F_0):
    if f_value > 0:
        classification = "class1"
    else:
        classification = "class2"
    print(f"  Объект {i+1}: F = {f_value:.4f} -> {classification}")

print(f"\nСРАВНЕНИЕ ИСХОДНЫХ ГРАНИЦ КЛАССИФИКАЦИИ:")
print(f"  Обучающие данные: {F_all:.4f}")
print(f"  Тестовые данные: {F_all_t:.4f}")
print(f"  Разница: {abs(F_all - F_all_t):.4f}")

print(f"\nРАСПРЕДЕЛЕНИЕ ЗНАЧЕНИЙ ОТНОСИТЕЛЬНО ГРАНИЦЫ 0:")
print(f"  class1 (обучение): {np.sum(F_1_centered > 0)}/{len(F_1_centered)} объектов выше границы")
print(f"  class2 (обучение): {np.sum(F_2_centered < 0)}/{len(F_2_centered)} объектов ниже границы")
print(f"  class1 (тест): {np.sum(F_1_t_centered > 0)}/{len(F_1_t_centered)} объектов выше границы")
print(f"  class2 (тест): {np.sum(F_2_t_centered < 0)}/{len(F_2_t_centered)} объектов ниже границы")
