from abc import abstractmethod, ABC
from typing import Any, Dict
from kafka import KafkaProducer
import json
import csv
from json import dumps
import os
import logging

class OutputAbstract(ABC):

    def __init__(self) -> None:
        pass

    @abstractmethod
    def configure(self, conf: Dict[Any, Any]) -> None:
        pass

    @abstractmethod
    def send_out(self, value: Any) -> None:
        pass


class KafkaOutput(OutputAbstract):

    def __init__(self, conf: Dict[Any, Any] = None) -> None:
        super().__init__()
        if(conf is not None):
            self.configure(conf=conf)

    def configure(self, conf: Dict[Any, Any]) -> None:
        super().configure(conf=conf)
        self.producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'))

    def send_out(self, value: Any = None, name: Any = None, timestamp: Any = 0) -> None:
            kafka_topic = name
            self.producer.send(kafka_topic, value=value)

class TerminalOutput(OutputAbstract):

    def __init__(self, conf: Dict[Any, Any] = None) -> None:
        super().__init__()
        if(conf is not None):
            self.configure(conf=conf)

    def configure(self, conf: Dict[Any, Any] = None) -> None:
        super().configure(conf=conf)
        # Nothing to configure
        pass

    def send_out(self,  value: Any = None, name: Any = None, timestamp: Any = 0) -> None:
        # Send to kafka only if an anomaly is detected (or if it is specified
        # that ok values are to be sent)    
        o = str(timestamp) + ": (value: " + str(value) + ")"
        print(o)

class ToFile():
    #TODO