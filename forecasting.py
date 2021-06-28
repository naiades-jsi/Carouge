# ML models to predict the time dependant dampness based on input data
# (watering ammount, current dampness, weather forecast)

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from typing import Any, Dict, List
from abc import abstractmethod, ABC

class ForecastAbstract(ABC):

    def __init__(self, configuration_location: str = None) -> None:
        self.configuration_location = configuration_location

    @abstractmethod
    def configure(self, con: Dict[Any, Any], configuration_location: str = None) -> None:
        self.configuration_location = configuration_location
        pass

    @abstractmethod
    def train(self) -> None:
        pass

    @abstractmethod
    def predict(self, input_values: list) -> None:
       pass 

class DenseNN(ForecastAbstract):
    def __init__(self, configuration_location: str = None) -> None:
        self.configuration_location = configuration_location
 
    def configure(self, con: Dict[Any, Any], configuration_location: str = None) -> None:
        self.train()
        pass

    def train(self) -> None:
        x_train = []
        y_train = []

        for i in range(8000):
            WA = 2*np.random.rand()+0.3
            current = 2*np.random.rand() + 0.1
            T = 1
            x_train.append([WA, current, T])
            y_train.append(self.SimulateSteps(WA, current, T))
            
        x_train = np.array(x_train)
        y_train = np.array(y_train)

        self.model = tf.keras.Sequential()
        self.model.add(tf.keras.layers.Dense(3,activation='relu'))
        self.model.add(tf.keras.layers.Dense(8))
        self.model.add(tf.keras.layers.Dense(20, activation='relu'))
        self.model.add(tf.keras.layers.Dense(100, activation='relu'))
        self.model.add(tf.keras.layers.Dropout(0.2))
        self.model.add(tf.keras.layers.Dense(320, activation='relu'))

        self.model.compile(optimizer =tf.keras.optimizers.Adam(lr = 0.001, beta_1 = 0.95), loss = 'mse')

        batch_size = 10
        self.model.fit(x_train,y_train, epochs =20, batch_size = batch_size, validation_data = None, verbose = 1)
        pass

    def SimulateSteps(self, watering_ammount, current_val, T):
        top = current_val + watering_ammount
        s = top
        S = np.linspace(current_val, top, 20)
        for i in range(300):
            #condition = cond(i, T,  300)
            s -= 0.01*s + (np.random.rand()-0.5)*0.03
            S = np.concatenate([S, [s]])
        
        return (S)  

    def predict(self, current_dampness: float, weather_data: list, estimated_th: float = 0, 
        Period: int = 0) -> None:
        T = 1
        Ts = []
        for j in np.linspace(0.3, 2.5, 20):
            #forecasts for different WA
            y_pred = self.model.predict(np.atleast_2d([j, current_dampness, T]))[0]
            t = len(y_pred[y_pred>=estimated_th])
            Ts.append(t)
     
        #Choose the WA, which reaches the threshold closest to the target time
        WA = np.linspace(0.3, 2.5, 20)[np.argmin(np.abs(np.array(Ts) - Period))]
        return(WA)