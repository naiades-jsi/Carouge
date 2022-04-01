# ML models to predict the time dependant dampness based on input data
# (watering ammount, current dampness, weather forecast)

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from typing import Any, Dict, List
from abc import abstractmethod, ABC   
import json  
from datetime import datetime

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
    def predict_time(self, input_values: list) -> None:
       pass 

    @abstractmethod
    def predict_WA(self, input_values: list) -> None:
        pass

class DenseNN(ForecastAbstract):
    def __init__(self, configuration_location: str = None) -> None:
        self.configuration_location = configuration_location
 
    def configure(self, con: Dict[Any, Any], configuration_location: str = None) -> None:
        
        self.loss_coefs = con["loss_coefs"]
        self.rise_time = con["rise_time"]
        print(self.rise_time)
        self.train()
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
        self.model.fit(x_train,y_train, epochs =20, batch_size = batch_size, validation_data = None, verbose = 0)
        pass

    def SimulateSteps(self, watering_ammount, current_val, T):
        top = current_val + watering_ammount
        s = top
        S = np.linspace(current_val, top, self.rise_time)
        for i in range(300):
            s -= 0.003*s + 0.03*s*(np.random.rand()-0.5)
            S = np.concatenate([S, [s]])
        
        return (S)  

    def predict_time(self, current_dampness: float, weather_data: list, estimated_th: float = 0) -> None:

        T = 1
        Ts = []
        
        #get the full curve which descends from 100% to 0%
        y_pred = 30*self.model.predict(np.atleast_2d([100, 0, T]))[0]

        #cut off the time of rising
        y_pred = y_pred[self.rise_time:]

        #observe the part of the curve which is lower than the current dampness
        y_pred = y_pred[y_pred < current_dampness]

        #finally get the time it takes to reach the threshold (in hours, the cap is 300 hours -- 12 days)
        t = len(y_pred[y_pred>=estimated_th])

        return(t)

    def predict_WA(self, current_dampness: float, weather_data: list, estimated_th: float = 0, hour_of_watering: int = 0):
        #Loss function to minimize
        Loss = lambda WA, time: self.loss_coefs[0]*WA - self.loss_coefs[1]*time

        WAs = np.linspace(0, 100, 100)
        Times = []
        Losses = []
        T = 1

        #Get the loss for all possible watering ammounts
        for i in WAs:
            y_pred = 30*self.model.predict(np.atleast_2d([i, current_dampness, T]))[0]
            t = len(y_pred[y_pred>=estimated_th])
            Times.append(t)
            Losses.append(Loss(i, t))

        #choose the minimal loss        
        idx = np.argmin(Losses)
        WA = WAs[idx]
        time = Times[idx]
        return(WA)


class DenseNN_RealData(ForecastAbstract):
    def __init__(self, configuration_location: str = None) -> None:
        self.configuration_location = configuration_location
 
    def configure(self, con: Dict[Any, Any], configuration_location: str = None) -> None:
        self.loss_coefs = con["loss_coefs"]
        self.train_data = "training_data/" + con["train_data"]
        #self.rise_time = con["rise_time"]
        #print(self.rise_time)
        self.train()
        pass

    def train(self) -> None:
        x_train, y_train = np.load(self.train_data, allow_pickle = True)

        horizon = 80

        self.model = tf.keras.Sequential()
        self.model.add(tf.keras.layers.Dense(len(x_train[0]),activation='relu'))
        self.model.add(tf.keras.layers.Dense(100))
        self.model.add(tf.keras.layers.Dropout(0.2))
        self.model.add(tf.keras.layers.Dense(200, activation='relu'))
        self.model.add(tf.keras.layers.Dropout(0.2))
        self.model.add(tf.keras.layers.Dense(horizon, activation='relu'))

        self.model.compile(optimizer =tf.keras.optimizers.Adam(lr = 0.001, beta_1 = 0.99), loss = 'mse')

        batch_size = 50
        self.model.fit(x_train,y_train, epochs =500, batch_size = batch_size, validation_data = None, verbose = 0)
        pass
  

    def predict_time(self, current_dampness, fv, estimated_th: float = 0):

        Ts = []

        y_pred = 30*self.model.predict(np.atleast_2d(np.array(fv)/30))[0]

        

        y_pred = np.add(y_pred, (current_dampness - y_pred[0]))

        expected_profile = [float(i) for i in y_pred]

        #get the time it takes to reach the threshold (in hours, the cap is 72 intervals -- 24h)
        t = len(y_pred[y_pred>=estimated_th])/1.5

        return(t, expected_profile)

    def predict_WA(self, current_dampness: float, fv, estimated_th: float = 0, hour_of_watering: int = 0):

        
        #Loss function to minimize
        Loss = lambda WA, time: self.loss_coefs[0]*WA - self.loss_coefs[1]*time

        WAs = np.linspace(0, 100, 100)
        Times = []
        Losses = []

        now = datetime.now()
        current_hour = now.hour
        

        #Get the loss for all possible starting moistures
        fv_copy = fv.copy()
        for i in WAs:
            fv_copy[0] = current_dampness + i
            fv_copy[1] = current_dampness + i
            y_pred = 30*self.model.predict(np.atleast_2d(np.array(fv_copy)/30))[0]
            t = len(y_pred[y_pred>=estimated_th])*2       #2-hour intervals
            Times.append(t)
            Losses.append(Loss(i, t))

        #choose the minimal loss        
        idx = np.argmin(Losses)
        WA = WAs[idx] - current_dampness
        if(WA < 0):
            WA = 0
        time = Times[idx]
        return(WA)

