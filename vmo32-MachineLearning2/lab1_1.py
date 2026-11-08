import numpy as np
import pandas as pd
import math
from lab1_data import test_data, train_data

class Sigmoid:
    @classmethod
    def function(self, x: np.array):
        #return 1/(1+2.71828**(-x))
        return 1/(1+np.exp(-np.clip(x, -500, 500)))  # clip предотвращает переполнение

    @classmethod
    def function_diff(self, x: np.array):
        fx = self.function(x)
        return fx * (1 - fx)

class Neuron:
    def __init__(self, weights_count: int = 1):
        self.size = weights_count
        self.weights = np.array([np.random.randn() for _ in range(self.size)], dtype='float64').reshape(-1, 1)

    def set_size(self, weights_count: int):
        self.size = weights_count
        self.weights = np.array([np.random.randn() for _ in range(self.size)], dtype='float64').reshape(-1, 1)

    def compute(self, x: np.array, activation):
        y = (x @ self.weights).item() 
        return activation.function(y)

class Layer:
    def __init__(self, neurons_count: int = 1, index: str = "OUT" , previous_layer: object = None):
        self.size = neurons_count
        self.name = index
        self.neurons = [Neuron() for _ in range(self.size)]
        self.input, self.output = [], []

        if previous_layer:
            for i in range(self.size):
                self.neurons[i].set_size(previous_layer.size)

    def compute(self, x: np.array, activation):
        self.input = x.copy()
        self.output = np.array([N.compute(x, activation) for N in self.neurons])
        return self.output


class Network:
    def __init__(self, activation, hidden_layers_count: int = 0, input_size: int = 1, learning_rate: float = 0.01):
        self.size = hidden_layers_count
        self.input_size = input_size
        self.layers = [Layer() for _ in range(self.size)] + [Layer(1)]
        self.activation = activation
        self.learning_rate = learning_rate

        self.resize_neurons()

    def add_layer(self, index: int, size: int = 1):
        if index > self.size:
            index = self.size 
        self.layers.insert(index, Layer(neurons_count=size, index=index))
        self.resize_neurons()
        self.size += 1

    def resize_neurons(self):
        for N in self.layers[0].neurons:
            N.set_size(self.input_size)
        for l in range(1, len(self.layers)):
            for N in self.layers[l].neurons:
                N.set_size(self.layers[l-1].size)

    def show_network(self):
        print(f"Activation function: {self.activation}")

        counter = 0
        for L in self.layers:
            counter += 1
            print(f'Layer {L.name}: {L.size} × {L.neurons[0].weights.shape}')

    def compute(self, x: np.array):
        if not x.shape or x.shape[0] != self.input_size:
            print(f'Dimension error in {x}')
            return 0

        for L in self.layers:
            x = L.compute(x, self.activation)
        return x

    def back_propagation(self, x, y, d, error: float, grad):
        deltas = [None] * len(self.layers)
        out_layer = self.layers[-1]
        deltas[-1] = error * (out_layer.output * (1 - out_layer.output))

        for i in range(len(self.layers)-2, -1, -1):
            L = self.layers[i]
            Ln = self.layers[i+1]
            delta_n = deltas[i+1]
            weights_n = np.array([n.weights.flatten() for n in Ln.neurons])
            #if len(L.output) > 1: 
            #    raise Exception(f"Fuck, {L.output}")
            deltas[i] = (delta_n @ weights_n) * (L.output * (1 - L.output))
        
        for i in range(len(self.layers)):
            if i == 0:
                layer_input = x
            else:
                layer_input = self.layers[i-1].output

            for j, neuron in enumerate(self.layers[i].neurons):
                for k in range(len(neuron.weights)):
                    neuron.weights[k] -= self.learning_rate * deltas[i][j] * layer_input[k]

    def error_func(self, y: float, d: float):
        return y - d

    def test(self, test_set: np.array, test_labels: np.array, accept = 0.3):
        n, accuracy = len(test_set), 0
        for i in range(n):
            computed = self.compute(test_set[i]).item()
            if round(computed) == test_labels[i]:
                accuracy += 1
        return f'Test accuracy: ({accuracy/n:.2f}%)'
    
    def train(self, train_set: np.array, train_labels, accuracy: float = None, epoches: int = 50):
        for j in range(1, epoches+1):
            total_error = 0
            for i in range(len(train_set)):
                y = self.compute(train_set[i])
                error = self.error_func(y, train_labels[i])
                total_error += error
                grad = error * self.activation.function_diff(y)

                self.back_propagation(train_set[i], y, train_labels[i], error, grad)

            if j % 10 == 0:
                print(f"Итерация {j}, средняя ошибка: {total_error/len(train_set)}")


def test1():
    n = Network(Sigmoid, input_size=2)
    n.show_network()
    n.add_layer(10, 3)
    n.show_network()
    n.add_layer(4, 10)
    n.show_network()
    n.add_layer(2, 2)
    n.show_network()
    n.add_layer(10, 2)
    n.show_network()
    print(f'Y IS: {n.compute(np.array([3,5]))}')
    n.train(np.array([[3,5]]), np.array([100, 200]))
    n.show_network()
    print(f'Y IS: {n.compute(np.array([3,5]))}')

def wine():
    n = Network(Sigmoid, input_size=4, learning_rate=0.01)
    n.add_layer(0,8)
    n.add_layer(1, 4)
    n.show_network()
    Y = train_data['class'].values
    X = train_data.drop('class', axis=1).values
    Y_test = test_data['class'].values
    X_test = test_data.drop('class', axis=1).values
    n.train(X, Y,epoches = 50)
    print(n.test(X_test, Y_test))

if __name__ == "__main__":
    wine()
