from abc import abstractmethod, ABC

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
    def configure(self) -> None:
        #configuring the flowerbed (might have different parameters based on location, flowerbed size, sun exposure,...)
        self.configuration_location = configuration_location
        pass

class Flowerbed1(FlowerBedAbstract):
    def __init__(self) -> None: 
        pass

    def configure(self, conf: dict):
        self.threshold = conf["starting_threshold"]
        self.current_dampness = 0.0
        pass

    def data_insert(self, value: float):
        # the value here is the dampness from the sensor
        self.current_dampness = value

        # TODO
        # timing is important. We need to figure out when to make the predictions, 
        # probably at a set time before the watering is scheduled

