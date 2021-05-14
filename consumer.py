from abc import ABC, abstractmethod
from typing import Any, Dict, List
from kafka import KafkaConsumer

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

    def __init__(self) -> None:
        pass

    def configure(self, con: Dict[Any, Any] = None) -> None:
        if(con is None):
            print("No configuration was given")
            return 

        self.topics = con['topics']
        
        self.consumer = KafkaConsumer(
                        bootstrap_servers=con['bootstrap_servers'],
                        auto_offset_reset=con['auto_offset_reset'],
                        enable_auto_commit=con['enable_auto_commit'],
                        group_id=con['group_id'],
                        value_deserializer=eval(con['value_deserializer']))
        self.consumer.subscribe(self.topics)

        #TODO
        #   where the data comes from
        #   create algo instance (probably per flowerbed?)
        #   configure each class

        self.flowerbed = []

        #TODO
        #   flowerbed_idx = 0
        #   for flowerbed in self.flowerbed_list:
        #       self.flowebed.append( ..flowerbed_instance(conf).. , flowerbed_idx = flowerbed_idx)
        #       flowerbed_idx +=1

        

    def read(self) -> None:
        for message in self.consumer:

            flowerbed_idx = self.topics.index(topic)

            # Get topic and insert into correct flowerbed instance and correct case (feedback or sensor data)
            topic = message.topic
            value = message.value
            
            if(topic in self.feedback_topics):
                self.flowerbed[flowerbed_idx].feedback_insert(value)
                pass
            elif(topic in self.flowerbed_data_topics):
                self.flowerbed[flowerbed_idx].data_insert(value)
                pass
                