import kagglehub
import os
import numpy as np
import matplotlib.pyplot as plt
import cv2
from PIL import Image
from tensorflow import keras
from tensorflow.keras.layers import *
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split

def get_data():
    # Download latest version
    #https://www.kaggle.com/datasets/karnikakapoor/digits
    path = kagglehub.dataset_download("karnikakapoor/digits")
    print("Path to dataset files:", path)
    path = f'{path}/digits updated/digits updated'

    folder = os.path.join(path, '1')
    img_path = os.path.join(folder, os.listdir(folder)[0])
    image = Image.open(img_path)
    width, height = image.size
    print(f"The image resolution is: {width}x{height}")

    X, y = load_data(path)

    print("Shape:", X.shape)
    print("Shape:", y.shape)

    X = X.reshape(-1, IMG_SIZE, IMG_SIZE, 1)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    y_train = to_categorical(y_train, NUM_CLASSES)
    y_test = to_categorical(y_test, NUM_CLASSES)

    X_cut = X_test[-10:]
    y_cut = y_test[-10:]

    return X_train, X_test, y_train, y_test, X_cut, y_cut

IMG_SIZE = 128
NUM_CLASSES = 10

def load_data(data_path):
    images = []
    labels = []

    for label in os.listdir(data_path):
        class_path = os.path.join(data_path, label)

        if os.path.isdir(class_path):
            for img_name in os.listdir(class_path):
                img_path = os.path.join(class_path, img_name)

                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
                img = img / 255.0

                images.append(img)
                labels.append(int(label))

    return np.array(images), np.array(labels)

MODEL1_PATH = 'C:/Users/simafrus/0-Space/01-Проекты/ВМО32/MachineLearning2/lab3_2.keras'
MODEL2_PATH = 'C:/Users/simafrus/0-Space/01-Проекты/ВМО32/MachineLearning2/lab3_3.keras'

if __name__ == '__main__':

    X_train, X_test, y_train, y_test, X_cut, y_cut = get_data()

    model1 = keras.Sequential([
        Input((IMG_SIZE,IMG_SIZE,1)),
        Conv2D(32, (3,3), padding='same', activation='relu'),
        BatchNormalization(),
        MaxPooling2D((3,3)),

        Conv2D(64, (3,3), padding='same', activation='relu'),
        BatchNormalization(),
        MaxPooling2D((3,3)),

        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.3),
        Dense(NUM_CLASSES, activation='softmax')
    ])

    model2 = keras.Sequential([
        Input((IMG_SIZE,IMG_SIZE,1)),
        Conv2D(32, (7,7), padding='same', activation='relu'),
        MaxPooling2D((3,3)),

        Conv2D(64, (7,7), padding='same', activation='relu'),
        MaxPooling2D((3,3)),

        Flatten(),
        Dense(128, activation='relu'),
        Dense(NUM_CLASSES, activation='softmax')
    ])

    model1.summary()
    model2.summary()

    SGDN = keras.optimizers.SGD(learning_rate=0.1, momentum=0.1, nesterov=1)

    early_stopping = keras.callbacks.EarlyStopping(
        monitor="val_loss",
        min_delta=0,
        patience=3,
        verbose=0,
        mode="auto",
        baseline=None,
        restore_best_weights=1,
        start_from_epoch=0,
    )


    model1.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    history1 = model1.fit(
        X_train, y_train,
        epochs=20,
        callbacks=[early_stopping],
        validation_split=0.1,
        batch_size=64
    )

    model2.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    history2 = model2.fit(
        X_train, y_train,
        epochs=20,
        callbacks=[early_stopping],
        validation_split=0.1,
        batch_size=64
    )

    model1.save(MODEL1_PATH)
    model2.save(MODEL2_PATH)

