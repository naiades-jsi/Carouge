from abc import ABC, abstractmethod
from typing import Any, Dict, List
from datetime import datetime
from kafka import KafkaConsumer
from waterbeds import Flowerbed1
import json
from json import loads

class ConsumerAbstract(ABC):

    def __init__(self, configuration_location: str = None) -> None:
        self.configuration_location = configuration_location

    @abstractmethod
    def configure(self, con: Dict[Any, Any], configuration_location: str) -> None:
        self.configuration_location = configuration_location
        pass

    @abstractmethod
    def read(self) -> None:
        pass

class ConsumerKafka(ConsumerAbstract):

    def __init__(self, conf: Dict[Any, Any] = None,
                 configuration_location: str = None) -> None:
        super().__init__(configuration_location=configuration_location)
        if(conf is not None):
            self.configure(con=conf)
        elif(configuration_location is not None):
            # Read config file
            with open("configuration/main/" + configuration_location) as data_file:
                conf = json.load(data_file)
            self.configure(con=conf)
        else:
            print("No configuration was given")

    def configure(self, con: Dict[Any, Any] = None,  configuration_location: str = None) -> None:
        self.configuration_location = configuration_location
        if(con is None):
            print("No configuration was given")
            return 

        self.flowerbed_names = con["flowerbeds"]
        #array of flowerbed instances
        self.flowerbeds = []

        #kafka topics for incoming data and outgoing watering ammounts
        self.topics_data = []
        self.topics_WA = []

        for i in self.flowerbed_names:
            configuration = con[i]
            self.topics_data.append(configuration["topic"])
            self.topics_WA.append(configuration["topic"] + "_WA")
            new_instance = Flowerbed1()
            new_instance.configure(configuration)
            self.flowerbeds.append(new_instance)

        
        self.consumer = KafkaConsumer(
                        bootstrap_servers=con['bootstrap_servers'],
                        auto_offset_reset=con['auto_offset_reset'],
                        enable_auto_commit=con['enable_auto_commit'],
                        group_id=con['group_id'],
                        value_deserializer=eval(con['value_deserializer']))
        self.consumer.subscribe(self.topics_data)

        for topic in self.topics_data:
            print("Listening on: " + topic, flush=True)
        

    def read(self) -> None:
        for message in self.consumer:
            
            #incoming data is only from the "flowerbedx_data" topics -> including dampness and feedback loop information

            # Get topic and insert into correct flowerbed instance and correct case (feedback or sensor data)
            topic = message.topic
            value = message.value
            flowerbed_idx = self.topics_data.index(topic)
            
            # print("message: " + str(flowerbed_idx) + " at: {}".format(datetime.now()), flush=True)
            
            self.flowerbeds[flowerbed_idx].data_insert(value["ftr_vector"], value["timestamp"])


            #if(value["feedback"] == "Nan"):
            #    self.flowerbeds[flowerbed_idx].data_insert(value["value"], value["timestamp"])
            #else:
            #    self.flowerbeds[flowerbed_idx].feedback_insert(value["value"], value["timestamp"])
                