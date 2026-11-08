import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.regularizers import l2

# загрузка
data = pd.read_csv("wine.csv")
data = data.drop(columns=["Id"])

X = data.drop(columns=["quality"])
y = data["quality"]

y = y - y.min()
y = to_categorical(y)

# split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# нормализация
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

def build_model(lr=0.001, dropout=0.3):
    model = Sequential()
    model.add(Dense(128, activation='relu', input_dim=X_train.shape[1]))
    model.add(Dropout(dropout))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(y.shape[1], activation='softmax'))

    model.compile(optimizer=Adam(lr),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    return model


best_acc = 0
histories = []
for i in range(20):
    lr = np.random.uniform(0.0001, 0.01)
    dr = np.random.choice([0.2, 0.3, 0.5])

    model = build_model(lr, dr)
    history = model.fit(X_train, y_train, epochs=10, verbose=0)
    histories.append(((lr, dr), history))

    loss, acc = model.evaluate(X_test, y_test, verbose=0)

    if acc > best_acc:
        best_acc = acc
        best_params = (lr, dr)

print("Лучшие параметры:", best_params)

for i, (params, history) in enumerate(histories):
    lr, dr = params

    plt.figure(figsize=(20,4))

    # Loss
    plt.subplot(i,2,1)
    plt.plot(history.history['loss'], label='train')
    plt.plot(history.history['val_loss'], label='val')
    plt.title(f"Loss | lr={lr:.4f}, dr={dr}")
    plt.legend()

    # Accuracy
    plt.subplot(i,2,2)
    plt.plot(history.history['accuracy'], label='train')
    plt.plot(history.history['val_accuracy'], label='val')
    plt.title(f"Accuracy | lr={lr:.4f}, dr={dr}")
    plt.legend()

plt.show()


