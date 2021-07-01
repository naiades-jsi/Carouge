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
        self.loss_coefs = con["loss_coefs"]
        self.rise_time = con["rise_time"]
        pass

    def train(self) -> None:
        x_train = []
        y_train = []

        #TODO: include training from real data and weather info (T)

        for i in range(8000):
            WA = 100*np.random.rand()
            current = 100*np.random.rand()
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
        self.model.add(tf.keras.layers.Dense(300 + self.rise_time, activation='relu'))

        self.model.compile(optimizer =tf.keras.optimizers.Adam(lr = 0.001, beta_1 = 0.95), loss = 'mse')

        batch_size = 10
        self.model.fit(x_train,y_train, epochs =20, batch_size = batch_size, validation_data = None, verbose = 1)
        pass

    def SimulateSteps(self, watering_ammount, current_val, T):
        top = current_val + watering_ammount
        s = top
        S = np.linspace(current_val, top, self.rise_time)
        for i in range(300):
            s -= 0.02*s + (np.random.rand()-0.5)
            S = np.concatenate([S, [s]])
        
        return (S)  

    def predict_time(self, current_dampness: float, weather_data: list, estimated_th: float = 0) -> None:

        #TODO: include weather data
        T = 1
        Ts = []
        
        #get the full curve which descends from 100% to 0%
        y_pred = self.model.predict(np.atleast_2d([100, 0, T]))[0]

        #cut off the time of rising
        y_pred = y_pred[self.rise_time:]

        #observe the part of the curve which is lower than the current dampness
        y_pred = y_pred[y_pred < current_dampness]

        #finally get the time it takes to reach the threshold (in hours, the cap is 300 hours -- 12 days)
        t = len(y_pred[y_pred>=estimated_th])

        return(t)

    def predict_WA(self, current_dampness: float, weather_data: list, estimated_th: float = 0):

        #TODO: include weather data

        #Loss function to minimize
        Loss = lambda WA, time: self.loss_coefs[0]*WA - self.loss_coefs[1]*time

        WAs = np.linspace(0, 100, 100)
        Times = []
        Losses = []
        T = 1

        #Get the loss for all possible watering ammounts
        for i in WAs:
            y_pred = self.model.predict(np.atleast_2d([i, current_dampness, T]))[0]
            t = len(y_pred[y_pred>=estimated_th])
            Times.append(t)
            Losses.append(Loss(i, t))

        #choose the minimal loss        
        idx = np.argmin(Losses)
        WA = WAs[idx]
        time = Times[idx]
        return(WA)
