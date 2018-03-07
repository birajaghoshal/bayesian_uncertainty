from sklearn.base import BaseEstimator, RegressorMixin
import numpy as np
import scipy.stats

from keras.layers.core import Lambda
from keras import backend as K
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import Adam

BATCH_SIZE = 100
N_EPOCHS = 50
BD_SAMPLES = 50


class MLPBayesianDropout(BaseEstimator, RegressorMixin):  
    def __init__(self):
        pass
    
    def fit(self, X, y):
        self.model = Sequential()
        self.model.add(Dense(512, activation='relu', input_shape=(X.shape[-1],)))
        self.model.add(Lambda(lambda x: K.dropout(x, level=0.5)))
        self.model.add(Dense(512, activation='relu'))
        self.model.add(Lambda(lambda x: K.dropout(x, level=0.5)))
        self.model.add(Dense(1, activation='linear'))

        self.model.compile(loss='mean_squared_error',
              optimizer=Adam(),
              metrics=['mse'])

        self.model.fit(X, y,
                    batch_size=BATCH_SIZE,
                    epochs=N_EPOCHS,
                    verbose=0)
        
        return self

    def predict(self, X, y=None):
        pred = [self.model.predict(X).reshape(-1) for _ in range(BD_SAMPLES)]
        pred_mean = np.mean(pred, axis=0)
        pred_std = np.std(pred, axis=0)
        return pred_mean, pred_std
    
    
class MLPBaseline(BaseEstimator, RegressorMixin):  
    def __init__(self):
        pass
    
    def fit(self, X, y):
        self.model = Sequential()
        self.model.add(Dense(512, activation='relu', input_shape=(X.shape[-1],)))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(512, activation='relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(1, activation='linear'))

        self.model.compile(loss='mean_squared_error',
              optimizer=Adam(),
              metrics=['mse'])

        self.model.fit(X, y,
                    batch_size=BATCH_SIZE,
                    epochs=N_EPOCHS,
                    verbose=0)
        
        errors = y - self.model.predict(X).reshape(-1)
        self.std = np.std(errors)
        
        return self

    def predict(self, X, y=None):
        pred_mean = self.model.predict(X).reshape(-1) 
        pred_std = self.std * np.ones(len(pred_mean))
        return pred_mean, pred_std
    