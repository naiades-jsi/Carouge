from abc import abstractmethod, ABC
from typing import Any, Dict
from kafka import KafkaProducer

class OutputAbstract(ABC):

    def __init__(self) -> None:
        pass

    @abstractmethod
    def configure(self) -> None:
        pass

    @abstractmethod
    def send_out(self, value: Any) -> None:
        pass


class KafkaOutput(OutputAbstract):

    def __init__(self, conf: Dict[Any, Any] = None) -> None:
        super().__init__()
        if(conf is not None):
            self.configure(conf=conf)

    def configure(self) -> None:
        self.producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'))

    def send_out(self, value: Any = None, topic_name: Any = None) -> None:
            kafka_topic = topic_name
            self.producer.send(kafka_topic, value=value)