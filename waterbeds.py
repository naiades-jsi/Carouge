from abc import abstractmethod, ABC
from typing import Any, Dict, List
import datetime
from datetime import datetime
import time
from forecasting import DenseNN, DenseNN_RealData
from output import KafkaOutput
import numpy as np
import pandas as pd
import json
import os

class FlowerBedAbstract(ABC):

    def __init__(self) -> None: 
        pass

    @abstractmethod
    def feedback_insert(value):
        # inserting data which comes from the feedback topic (soil too dry, too wet)
        # to continuously fix the estimated threshold
        pass

    @abstractmethod
    def data_insert(self, value):
        #inserting measurements (weather, soil moisture ... single FV or separate?)
        pass
        
    @abstractmethod
    def configure(self, conf) -> None:
        #configuring the flowerbed (might have different parameters based on location, flowerbed size, sun exposure,...)
        self.outputs = [eval(o) for o in conf["output"]]
        output_configurations = conf["output_conf"]
        for o in range(len(self.outputs)):
            self.outputs[o].configure(output_configurations[o])
        pass

class Flowerbed1(FlowerBedAbstract):
    def __init__(self) -> None: 
        pass

    def configure(self, conf: dict):
        super().configure(conf)
        self.name = conf["name"]
        self.threshold = conf["initial_threshold"]

        #how early before the scheduled watering time the W.A. is calculated (seconds)
        #self.watering_info = conf["watering_info"]

        #self.drying_model = eval(conf["drying_model"])
        #self.drying_model.configure(con = conf["drying_model_conf"])

        self.forecast_model = eval(conf["forecast_model"])
        #print('FORECAST MODEL: ' + str(conf["forecast_model"]), flush = True)
        self.forecast_model.configure(con = conf["forecast_model_conf"])

        #self.watering_interval = conf["watering_interval"][0]*24*3600 + conf["watering_interval"][1]*3600 + conf["watering_interval"][2]

        #self.loss_coefs = conf["loss_coefs"]

        self.current_dampness = 0.0
        #self.next_watering = time.time() + self.watering_interval


        #TODO: fix this!!
        self.topic_data = conf["name"] + "_data"
        self.topic_WA = conf["name"] + "_WA"
        pass

    def data_insert(self, value: float, timestamp):
        # the value here is the dampness from the sensor
        # once per day at 6AM
        # the output is time and ammount of watering


        #self.time = time.time()
        print('Message inserted: ' + str(value), flush = True)
        print('Timestamp: ' + str(timestamp), flush = True)

        self.current_dampness = value[0]

        #print("Data inserted: " + str(value))

        #1. step - how long untill the current dampness falls under the threshold
        timetowatering = self.forecast_model.predict_time(current_dampness = self.current_dampness, weather_data = None, estimated_th = self.threshold)

        print('timetowatering: ' + str(timetowatering), flush = True)

        now = datetime.now()
        hour_of_watering = (now.hour + timetowatering)%24

        #2. step - when we do water the plants: how much water to use
        WA = self.forecast_model.predict_WA(current_dampness = self.threshold, 
                                        weather_data = None,
                                        estimated_th = self.threshold, 
                                        hour_of_watering = hour_of_watering)

        print('WA: ' + str(WA), flush = True)

        # T-time to next watering
        # WA - watering ammount
        tosend = {
            "timestamp": timestamp*1000,  #UNIX, ms
            "T": timetowatering,
            "WA": WA
        }

        self.save_prediction(tosend)
        
        for output in self.outputs:
            output.send_out(value=tosend,
                            name = self.topic_WA)
        
        

    def feedback_insert(self, value: float, timestamp):
        #correcting the internal threshold once we get the feedback (too wet, too dry)
        self.threshold = threshold_correction(self.threshold, value)

    def save_prediction(self, tosave):
        # Make predictions file is it does not exists
        dir = "./predictions"
        if not os.path.isdir(dir):
            os.makedirs(dir)


        filename = dir + "/" + self.name + "_prediction.json"
        file = open(filename, "w")
        json.dump(tosave, file)
        file.close()

def threshold_correction(current_threshold, feedback):
    #if feedback = 1 -> threshold too high
    #if feedback = -1 -> threshold too low
    #other correction functions can be added
    
    if(feedback == 1):
        new_threshold = current_threshold*1.1
    elif(feedback == -1):
        new_threshold = current_threshold*0.9
    else:
        new_threshold = current_threshold

    return(new_threshold)



class FlowerbedAlternative(FlowerBedAbstract):
    #Alternative method of forecasting

    def __init__(self) -> None: 
        pass

    def configure(self, conf: dict):
        super().configure(conf)
        self.name = conf["name"]
        self.threshold = conf["initial_threshold"]

        self.upper_bound_estimation = eval(conf["upper_bound_estimation"])
        self.upper_bound_estimation.configure(con = conf["UBE_conf"])


        self.current_dampness = 0.0

        #self.topic_data = conf["name"] + "_data"
        pass

    def data_insert(self, value: float, timestamp):
        # the value here is the dampness from the sensor
        # the output is time and ammount of watering

        self.current_dampness = value[0]


        #print("Data inserted: " + str(value))

        #1. step - how long untill the current dampness falls under the threshold
        timetowatering = self.forecast_model.predict_time(current_dampness = self.current_dampness, weather_data = None, estimated_th = self.threshold)

        now = datetime.now()
        hour_of_watering = (now.hour + timetowatering)%24

        #2. step - when we do water the plants: how much water to use
        WA = self.forecast_model.predict_WA(current_dampness = self.threshold, 
                                        weather_data = None,
                                        estimated_th = self.threshold, 
                                        hour_of_watering = hour_of_watering)

        # T-time to next watering
        # WA - watering ammount
        tosend = {
            "timestamp": timestamp*1000,  #UNIX, ms
            "T": timetowatering,
            "WA": WA
        }

        self.save_prediction(tosend)
        
        for output in self.outputs:
            output.send_out(value=tosend,
                            name = self.topic_WA)
        
        

    def feedback_insert(self, value: float, timestamp):
        #correcting the internal threshold once we get the feedback (too wet, too dry)
        self.threshold = threshold_correction(self.threshold, value)

    def save_prediction(self, tosave):
        # Make predictions file is it does not exists
        dir = "./predictions"
        if not os.path.isdir(dir):
            os.makedirs(dir)


        filename = dir + "/" + self.name + "_prediction.json"
        file = open(filename, "w")
        json.dump(tosave, file)
        file.close()

def threshold_correction(current_threshold, feedback):
    #if feedback = 1 -> threshold too high
    #if feedback = -1 -> threshold too low
    #other correction functions can be added
    
    if(feedback == 1):
        new_threshold = current_threshold*1.1
    elif(feedback == -1):
        new_threshold = current_threshold*0.9
    else:
        new_threshold = current_threshold

    return(new_threshold)