import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, Dropout, BatchNormalization

# Отключаем все предупреждения
tf.get_logger().setLevel('ERROR')
tf.autograph.set_verbosity(0)
tf.keras.utils.disable_interactive_logging()

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, Input
from tensorflow.keras.optimizers import Adam
from scikeras.wrappers import KerasClassifier
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import uniform
from sklearn.model_selection import GridSearchCV
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split, KFold
from sklearn.preprocessing import StandardScaler

data = pd.read_csv("wine.csv")
data = data.drop(columns=["Id"])

X = data.drop(columns=["quality"])
y = data["quality"]

y = y - y.min()
y = to_categorical(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

def build_model(learning_rate=0.01, dropout_rate=0.3, neurons=8):
    model = Sequential([
        Input(shape=(X_train.shape[1],)),
        Dense(neurons, activation='relu'),
        BatchNormalization(),
        Dropout(dropout_rate),

        Dense(y_train.shape[1], activation='softmax')
    ])

    optimizer = Adam(learning_rate=learning_rate)

    model.compile(
        optimizer=optimizer,
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    return model

model_wrapper = KerasClassifier(
    model=build_model,
    dropout_rate=0.3,
    neurons=64,
    learning_rate=0.01,
    epochs=10,
    batch_size=32,
    verbose=0
)


param_dist = {
    'learning_rate': uniform(0.0001, 0.01),
    'dropout_rate': [0.2, 0.3, 0.5],
    'neurons': [4, 8, 16],
    'batch_size': [4, 8],
    'epochs': [10, 20]
}

random_search = RandomizedSearchCV(
    estimator=model_wrapper,
    param_distributions=param_dist,
    n_iter=10,              # ОБЯЗАТЕЛЬНО по методичке
    cv=3,
    scoring='accuracy',
    verbose=1,
    n_jobs=-1
)

history_random = random_search.fit(X_train, y_train)

param_grid = {
    'learning_rate': [0.001, 0.01],
    'dropout_rate': [0.2, 0.4],
    'neurons': [4, 8],
    'batch_size': [4, 8],
    'epochs': [10]
}

grid_search = GridSearchCV(
    estimator=model_wrapper,
    param_grid=param_grid,
    cv=3,
    scoring='accuracy',
    verbose=1,
    n_jobs=-1
)

history_grid = grid_search.fit(X_train, y_train)

print('RANDOM SEARCH')
print("Лучшие параметры:", random_search.best_params_)
print("Лучшая точность:", random_search.best_score_)
print("Точность на тестовой выборке", random_search.best_estimator_.score(X_test, y_test))
print("Прочие параметры:")
for key, value in random_search.cv_results_.items():
    print(f'\t{key}: {value}')
df = pd.DataFrame(random_search.cv_results_)

print("\n\n")
print('GRID SEARCH')
print("Лучшие параметры:", grid_search.best_params_)
print("Лучшая точность:", grid_search.best_score_)
print("Точность на тестовой выборке:", grid_search.best_estimator_.score(X_test, y_test))
print("Прочие параметры:")
for key, value in grid_search.cv_results_.items():
    print(f'\t{key}: {value}')
df = pd.DataFrame(grid_search.cv_results_)

best_params = grid_search.best_params_

model = build_model(
    learning_rate=best_params['learning_rate'],
    dropout_rate=best_params['dropout_rate'],
    neurons=best_params['neurons']
)

history = model.fit(
    X_train,
    y_train,
    epochs=best_params['epochs'],
    batch_size=best_params['batch_size'],
    validation_split=0.2
)

plt.title(f'Best model, acc={history.history["accuracy"][-1]:.3f}')
plt.plot(history.history['loss'], label=f'Train loss')
plt.plot(history.history['val_loss'], label=f'Validation loss', linestyle='--')
plt.legend()
plt.show()

