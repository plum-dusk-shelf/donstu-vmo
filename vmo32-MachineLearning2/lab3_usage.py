from lab3_train import *

import os
import numpy as np
import matplotlib.pyplot as plt
import cv2
from PIL import Image

from tensorflow import keras

X_train, X_test, y_train, y_test, X_cut, y_cut = get_data()

model1 = keras.models.load_model(MODEL1_PATH)
model2 = keras.models.load_model(MODEL2_PATH)

def predict_image(img, verbose_):
    img = img/ 255.0
    img = np.reshape(img, (1,IMG_SIZE,IMG_SIZE,1))
    pred1 = model1.predict(img, verbose=verbose_)
    pred2 = model2.predict(img, verbose=verbose_)
    return int(np.argmax(pred1)), int(np.argmax(pred2))

for i in range(len(X_cut)):
    preds = predict_image(X_cut[i], verbose_=0)
    print(f'Model 1 saw {preds[0]} in {np.argmax(y_cut[i])}')
    print(f'Model 2 saw {preds[1]} in {np.argmax(y_cut[i])}')

exit()
test_loss, test_acc = model1.evaluate(X_test, y_test)
print("Test accuracy 1:", test_acc)
test_loss, test_acc = model2.evaluate(X_test, y_test)
print("Test accuracy 2:", test_acc)
img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
img = cv2.resize(img, (IMG_SIZE,IMG_SIZE))
img = img / 255.0
img = img.reshape(1,IMG_SIZE,IMG_SIZE,1)
pred = predict_image(f'{path}/1/img002-00113.png')
print("Prediction 1:", pred[0])
print("Prediction 2:", pred[1])
