import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Normalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical


data = pd.read_csv("wine.csv")

data = data.drop(columns=["Id"])

data.info()
print(data["quality"].value_counts(normalize=True))

X = data.drop(columns=["quality"])
y = data["quality"]

y = y - y.min()

y = to_categorical(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

model = Sequential()

model.add(Dense(64,
                input_dim=X_train.shape[1],
                activation='sigmoid'))

model.add(Dense(32, activation='sigmoid'))

model.add(Dropout(0.3))

model.add(Dense(16, activation='sigmoid'))

model.add(Dropout(0.3))

model.add(Dense(y.shape[1], activation='softmax'))

model.compile(
    optimizer=Adam(learning_rate=0.01),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

history = model.fit(
    X_train,
    y_train,
    epochs=50,
    batch_size=8,
    validation_split=0.1
)

loss, accuracy = model.evaluate(X_test, y_test)

print("Точность на тестовой выборке:", accuracy)

plt.figure(figsize=(12,4))

plt.subplot(1,2,1)
plt.plot(history.history['loss'], label='Loss обучение')
plt.plot(history.history['val_loss'], label='Loss валидация')
plt.title('Функция потерь')
plt.xlabel('Эпохи')
plt.ylabel('Loss')
plt.legend()

plt.subplot(1,2,2)
plt.plot(history.history['accuracy'], label='Accuracy обучение')
plt.plot(history.history['val_accuracy'], label='Accuracy валидация')
plt.title('Точность')
plt.xlabel('Эпохи')
plt.ylabel('Accuracy')
plt.legend()

plt.show()

predictions = model.predict(X_test)

print("Пример предсказаний:")
print(y_test[:10])
print(np.argmax(predictions[:10], axis=1))


y_pred = np.argmax(predictions, axis=1)
y_true = np.argmax(y_test, axis=1)

cm = confusion_matrix(y_true, y_pred)

print("Матрица ошибок:")
print(cm)
