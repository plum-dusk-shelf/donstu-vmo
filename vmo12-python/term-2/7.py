import pandas as pd
from matplotlib import pyplot as plt

df = pd.read_csv('dataset_f1_cars\\teams.csv')
df.index = range(1, df.shape[0] + 1)  # замена столбца индексов

df2 = pd.read_csv('dataset_f1_cars\\drivers.csv')

print(df2.head())

# print(f'{df.loc[1]} {df.iloc[0]}')  # loc работает по столбцу индекса, iloc — по порядковому номеру

print(f'\n\nЗадание 1:\n'
      f'Было {sum(df.duplicated())} дубликатов, после замены стало'
      f'{sum(df.drop_duplicates(inplace=False).duplicated())}')

print(f'\n\nЗадание 2:\n'
      f'В столбце Positions {df["Pos"].nunique()} уникальных элементов, вот они: {", ".join(df["Pos"].unique())}')

print(f'\n\nЗадание 3: \n'
      f'{df.agg({"PTS": ["mean", "median", "min", "max"]})}')

grouped_by_nationality = df2.groupby('Nationality')
print(f'\n\nЗадание 4:\n'
      f'{grouped_by_nationality.agg({"PTS": "mean"}).sort_values("Nationality")}')
# grouped_by_nationality.agg({"PTS": "mean"}).plot(kind='bar')
# plt.show()

print(f'\n\nЗадание 5\n'
      f'{df2[df2["Car"]=="Alfa Romeo"].agg({"PTS": ["mean", "median", "min", "max"]})}')

grouped_by_car = df2.groupby('Car')
print(f'\n\nЗадание 6:\n'
      f'{grouped_by_car.agg({"PTS": "mean"})}')
grouped_by_car.agg({"PTS": "mean"}).plot(kind='bar')
# plt.show()

print(pd.crosstab(df2['Car'], df2['Nationality']))
pd.crosstab(df2['Car'], df2['Nationality'])


plt.show()
