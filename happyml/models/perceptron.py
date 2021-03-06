

import numpy as np

from model import Model


class Perceptron(Model):

    plot_type = "binary_ones"


    def __init__(self, w=None, b=None, d=2):
        self.w = np.asarray(w) if w is not None \
                               else np.zeros(d)
        self.b = b if b is not None else 0


    def h(self, x):
        # FIXME: np.sign output is in {-1, 0, +1}
        return np.sign(np.dot(self.w.T, x) + self.b)

    def predict(self, X):
        # FIXME: np.sign output is in {-1, 0, +1}
        return np.sign(np.dot(X, self.w) + self.b)

    def plot_predict(self, X):
        return np.dot(X, self.w) + self.b

    def pla(self, X, y, iterations=10):
        """Perceptron Learning Algorithm."""
        y = y.flatten()
        idx = np.arange(X.shape[0])
        for i in range(iterations):
            np.random.shuffle(idx)
            error = False
            for j in idx:
                x = X[j, :].T
                if self.h(x) != y[j]:
                    error = True
                    self.w += y[j] * x
                    self.b += y[j]
                    break
            if not error: return i
        return iterations

    def pocket(self, X, y, iterations=10):
        max_accuracy = 0.0
        y = y.flatten()
        pocket_w = np.array(self.w)
        pocket_b = self.b
        idx = np.arange(X.shape[0])
        for iteration in range(iterations):
            np.random.shuffle(idx)
            for i in idx:
                x = X[i, :].T
                if self.h(x) != y[i]:
                    self.w += y[i] * x
                    self.b += y[i]
                    accuracy = self.accuracy(X, y)
                    if accuracy > max_accuracy:
                        max_accuracy = accuracy
                        pocket_w = np.array(self.w)
                        pocket_b = self.b
                    break
        self.w = pocket_w
        self.b = pocket_b

