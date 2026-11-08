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
from tensorflow.keras.regularizers import l2, l1

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

histories = []

def create_base_model():
    model = Sequential()
    model.add(Dense(128, activation='relu', input_dim=X_train.shape[1]))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(y.shape[1], activation='softmax'))

    model.compile(
        optimizer=Adam(0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    return model

model = create_base_model()

histories.append(('Base', model.fit(
    X_train, y_train,
    epochs=20,
    batch_size=32,
    validation_split=0.1
), model.evaluate(X_test, y_test)))

def create_l2_model(lmbd):
    model = Sequential()
    model.add(Dense(128, activation='relu',
                    kernel_regularizer=l2(lmbd),
                    input_dim=X_train.shape[1]))
    model.add(Dense(64, activation='relu',
                    kernel_regularizer=l2(lmbd)))
    model.add(Dense(y.shape[1], activation='softmax'))

    model.compile(optimizer=Adam(0.001),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    return model

model = create_l2_model(0.1)
histories.append(("L2", model.fit(X_train, y_train, epochs=20, validation_split=0.1), model.evaluate(X_test, y_test)))

def create_l1_model(lmbd):
    model = Sequential()
    model.add(Dense(128, activation='relu',
                    kernel_regularizer=l1(lmbd),
                    input_dim=X_train.shape[1]))
    model.add(Dense(64, activation='relu',
                    kernel_regularizer=l1(lmbd)))
    model.add(Dense(y.shape[1], activation='softmax'))

    model.compile(optimizer=Adam(0.001),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    return model

model = create_l1_model(1e-5)
histories.append(("L1", model.fit(X_train, y_train, epochs=20, validation_split=0.1), model.evaluate(X_test, y_test)))

def create_dropout_model(rate):
    model = Sequential()
    model.add(Dense(128, activation='relu', input_dim=X_train.shape[1]))
    model.add(Dropout(rate))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(rate))
    model.add(Dense(y.shape[1], activation='softmax'))

    model.compile(optimizer=Adam(0.001),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    return model

model = create_dropout_model(0.3)
histories.append(("Dropout", model.fit(X_train, y_train, epochs=20, validation_split=0.1), model.evaluate(X_test, y_test)))

def create_bn_model():
    model = Sequential()
    model.add(Dense(128, activation='relu', input_dim=X_train.shape[1]))
    model.add(BatchNormalization())
    model.add(Dense(64, activation='relu'))
    model.add(BatchNormalization())
    model.add(Dense(y.shape[1], activation='softmax'))

    model.compile(optimizer=Adam(0.001),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    return model

model = create_bn_model()
histories.append(("Batch Normalization", model.fit(X_train, y_train, epochs=20, validation_split=0.1), model.evaluate(X_test, y_test)))

early_stop = EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True
)

model = create_base_model()

histories.append(('Early stopping', model.fit(
    X_train, y_train,
    epochs=100,
    validation_split=0.1,
    callbacks=[early_stop]
), model.evaluate(X_test, y_test)))

import math

n = len(histories)

cols = 4
rows = math.ceil(n / cols)

fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
axes = axes.flatten()

for i, (name, history, ev) in enumerate(histories):
    loss, acc = ev
    hist = history.history
    ax = axes[i]
    
    ax.plot(hist['loss'], label=f'train loss, acc={acc:.2f}')
    
    if 'val_loss' in hist:
        ax.plot(hist['val_loss'], linestyle='--', label='val loss')
    
    ax.set_title(name)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Loss')
    ax.legend()
    ax.grid()

for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.show()
