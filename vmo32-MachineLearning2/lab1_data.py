import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()

data_raw = pd.read_csv("wine.csv")
data = data_raw
data['class'] = np.where(data['quality'].isin([6,7,8]), 1, 0)
data = data.dropna().loc[:, ['pH', 'free sulfur dioxide', 'total sulfur dioxide', 'density', 'class']]#.drop('sex', axis=1).iloc[:40]
test_data = data.groupby('class').sample(n=50, random_state=42)
train_data = data.drop(test_data.index)

X_train = train_data.drop('class', axis=1)
y_train = train_data['class']
X_test = test_data.drop('class', axis=1)
y_test = test_data['class']
scaler = StandardScaler()
scaler.fit(X_train)
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)
X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns, index=X_train.index)
X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns, index=X_test.index)
train_data_scaled = X_train_scaled.copy()
train_data_scaled['class'] = y_train
test_data_scaled = X_test_scaled.copy()
test_data_scaled['class'] = y_test

if __name__ == "__main__":
    for i in train_data.columns.tolist():
        print(f'{i.upper()}: {train_data[i].mean():.4f} → {train_data_scaled[i].mean():.4f}')
