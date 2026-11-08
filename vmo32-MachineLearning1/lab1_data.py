import pandas as pd

points2d = pd.read_csv("lab1_points2d_data.csv")
points3d = pd.read_csv('lab1_points3d_data.csv')
my_dataset = pd.read_csv('lab1_penguins.csv')
my_dataset.insert(0, 'object', my_dataset.index.tolist())
my_dataset['body_mass_g'] = my_dataset['body_mass_g']/1000
my_dataset['flipper_length_mm'] = my_dataset['flipper_length_mm']/100
my_dataset = my_dataset.dropna().drop('sex', axis=1).iloc[:40]#.drop('body_mass_g', axis=1)

if __name__ == "__main__":
        print(my_dataset)