import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


problem = 4 #  int(input('Введите номер задачи: '))

match problem:
    case 1:
        data = pd.read_csv('Discriminate_Analize_DataSet_1.csv')
        X_1 = data[data['object'] == 'X_1'].drop(columns=['object']).values.tolist()
        X_2 = data[data['object'] == 'X_2'].drop(columns=['object']).values.tolist()
        X_0 = data[data['object'] == 'X_0'].drop(columns=['object']).values.tolist()

    case 2:
        data = pd.read_csv('Discriminate_Analize_DataSet_4.csv')
        data_2 = pd.read_csv('Discriminate_Analize_DataSet_3.csv')

        X_1 = data_2[data_2['object'] == 'Adelie'].drop(columns=['object']).values.tolist()
        X_2 = data_2[data_2['object'] == 'Gentoo'].drop(columns=['object']).values.tolist()
        X_0 = data_2[data_2['object'] == 'object_researh'].drop(columns=['object']).values.tolist()

    case 3:
        data = pd.read_csv('Credit_card_label.csv')
        data_2 = pd.read_csv('Credit_card.csv')
        data_merged = pd.merge(data, data_2, on='Ind_ID').copy()
        border = 1000

        # data_merged.drop(columns=['Birthday_count', 'Phone', 'EMAIL_ID', 'Mobile_phone', 'Work_Phone'], inplace=True)
       #  data_processed = data_merged[['Ind_ID', 'object', 'GENDER', 'Car_Owner', 'Propert_Owner', 'CHILDREN',
       # 'Annual_income', 'Type_Income', 'EDUCATION', 'Marital_status',
       # 'Housing_type', 'Employed_days', 'Type_Occupation', 'Family_Members']].copy()
        data_processed = data_merged[['object', 'Car_Owner', 'Propert_Owner',
                                      'Annual_income']].copy()
        data_processed['Annual_income'] = data_processed['Annual_income']/10**4
        data_processed.dropna(inplace=True)

        # data_merged = pd.Categorical(data_merged.drop(columns=['object']))
        for col in data_processed.columns:
            if data_processed[col].dtype == 'object':
                data_processed.loc[:, col] = pd.Categorical(data_processed[col]).codes

        mask_0 = data_processed['object'] == 0
        mask_1 = data_processed['object'] == 1

        X_1 = data_processed.loc[mask_0].drop(columns=['object']).iloc[:150].values.tolist()
        X_2 = data_processed.loc[mask_1].drop(columns=['object']).iloc[:150].values.tolist()
        # X_0 = (data_processed.loc[mask_0].drop(columns=['object']).iloc[1340:].values.tolist() +
        #        data_processed.loc[mask_1].drop(columns=['object']).iloc[150:].values.tolist())
        X_01 = data_processed.loc[mask_0].drop(columns=['object']).iloc[1340:].values.tolist()
        X_02 = data_processed.loc[mask_1].drop(columns=['object']).iloc[150:].values.tolist()
        # X_0 = data_processed[border:].drop(columns=['object']).values.tolist()

    case 4:
        data = pd.read_csv('Raisin_Dataset.csv')
        data = data.rename(columns={'Class': 'object'})
        mask_0 = data['object'] == 'Kecimen'
        mask_1 = data['object'] == 'Besni'

        length = len(data[data['object'] == "Kecimen"])
        c = 0.8
        border = round(length*c)

        X_1 = data.loc[mask_0].drop(columns=['object']).iloc[:border].values.tolist()
        X_2 = data.loc[mask_1].drop(columns=['object']).iloc[:border].values.tolist()
        X_01 = data.loc[mask_0].drop(columns=['object']).iloc[border:].values.tolist()
        X_02 = data.loc[mask_1].drop(columns=['object']).iloc[border:].values.tolist()

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


from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_all = data.drop(columns=['object']).values
X_all_scaled = scaler.fit_transform(X_all)

data_scaled = pd.DataFrame(X_all_scaled, columns=data.drop(columns=['object']).columns)
data_scaled['object'] = data['object'].values


s1 = np.cov(X_1_ar, rowvar=False, ddof=1)
s2 = np.cov(X_2_ar, rowvar=False, ddof=1)
SO = ((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2)
SO_obrat = np.linalg.inv(SO)


print("X_11 (mean class1):", X_11)
print("X_12 (mean class2):", X_12)
diff = X_11 - X_12
print("mean difference (X_11 - X_12):", diff, "norm:", np.linalg.norm(diff))

print("SO shape:", SO.shape)
print("det(SO):", np.linalg.det(SO))
print("rank(SO):", np.linalg.matrix_rank(SO))

eigvals = np.linalg.eigvals(SO)
print("eigvals(SO):", eigvals)

A = None
try:
    SO_obrat = np.linalg.inv(SO)
    A = SO_obrat @ diff
    print("A:", A, "norm(A):", np.linalg.norm(A))
except Exception as e:
    print("Ошибка при обращении SO:", e)

A = SO_obrat @ (X_11 - X_12)

F_1 = np.sum(A * X_1_ar, axis=1)
F_2 = np.sum(A * X_2_ar, axis=1)


sep = (F_1.mean() - F_2.mean())**2 / (F_1.var() + F_2.var())
print("Fisher separation (bigger is better):", sep)


F_1_mean = F_1.mean()
F_2_mean = F_2.mean()
F_all = (F_1_mean + F_2_mean) / 2

F_1_centered = F_1 - F_all
F_2_centered = F_2 - F_all

F_01 = np.sum(A * np.array(X_01), axis=1) - F_all
F_02 = np.sum(A * np.array(X_02), axis=1) - F_all

def visualization():
    plt.figure(figsize=(19, 9))

    # plt.subplot(1, 2, 1)
    # plt.plot(range(1, len(F_1_centered) + 1), F_1_centered, 'bo', label='class1', markersize=8)
    # plt.plot(range(len(F_1_centered) + 1, len(F_1_centered) + len(F_2_centered) + 1),
    #          F_2_centered, 'ro', label='class2', markersize=8)
    #
    # plt.axhline(y=0, color='black', linestyle='--', linewidth=2,
    #             label='Граница классификации (FFf = 0)')
    #
    # plt.xlabel('Номер объекта', fontsize=12)
    # plt.ylabel('FFf', fontsize=12)
    # plt.title('Значения FFf для class1 и class2 (тестовые данные)', fontsize=14)
    # plt.legend(fontsize=10)
    # plt.grid(True, alpha=0.3)

    # plt.subplot(1, 2, 2)
    plt.plot(range(1, len(F_1_centered) + 1), F_1_centered, 'bo', label='class1 (обучение)', markersize=8)
    plt.plot(range(len(F_1_centered) + 1, len(F_1_centered) + len(F_2_centered) + 1),
             F_2_centered, 'ro', label='class2 (обучение)', markersize=8)
    plt.plot(range(len(F_1_centered) + len(F_2_centered) + 1,
                   len(F_1_centered) + len(F_2_centered) + len(F_01) + 1),
             F_01, 'bs', label='class2 (тест)', markersize=8)

    plt.plot(range(len(F_1_centered) + len(F_2_centered) + 1,
                   len(F_1_centered) + len(F_2_centered) + len(F_02) + 1),
             F_02, 'rs', label='class2 (тест)', markersize=8)

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
print(f"  class1: {len(F_1_centered)} объектов, среднее F: {F_1_centered.mean():.4f}")
print(f"  class2: {len(F_2_centered)} объектов, среднее F: {F_2_centered.mean():.4f}")
print(f"  Исходная граница классификации: {F_all:.4f}")

print(f"\nОБЪЕКТЫ ДЛЯ ИССЛЕДОВАНИЯ:")
print(f"  object_researh: {len(F_01)+len(F_02)} объектов")

print(f"\nВСЕГО ОБЪЕКТОВ: {len(F_1_centered) + len(F_2_centered) + len(F_01)+len(F_02)}")

print(f"\nКЛАССИФИКАЦИЯ ОБЪЕКТОВ ИССЛЕДОВАНИЯ:")
for i, f_value in enumerate(F_01):
    if f_value > 0:
        classification = "class1"
    else:
        classification = "class2"
    print(f"  Объект {i+1}: F = {f_value:.4f} -> {classification}")

print(f"\nСРАВНЕНИЕ ИСХОДНЫХ ГРАНИЦ КЛАССИФИКАЦИИ:")
print(f"  Обучающие данные: {F_all:.4f}")
print(f"  Тестовые данные: {F_all:.4f}")
print(f"  Разница: {abs(F_all - F_all):.4f}")

print(f"\nРАСПРЕДЕЛЕНИЕ ЗНАЧЕНИЙ ОТНОСИТЕЛЬНО ГРАНИЦЫ 0:")
print(f"  class1 (обучение): {np.sum(F_1_centered > 0)}/{len(F_1_centered)} объектов выше границы")
print(f"  class2 (обучение): {np.sum(F_2_centered < 0)}/{len(F_2_centered)} объектов ниже границы")
print(f"  class1 (тест): {np.sum(F_01 > 0)}/{len(F_01)} объектов выше границы")
print(f"  class2 (тест): {np.sum(F_02 < 0)}/{len(F_02)} объектов ниже границы")
print(f"  Итого точность: {(np.sum(F_01 > 0)+np.sum(F_02 < 0))/(len(F_01)*2)*100}%")

# visualization()
