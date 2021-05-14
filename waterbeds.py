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
    def data_insert(value):
        #inserting measurements (weather, soil moisture ... single FV or separate?)
        pass
        
    @abstractmethod
    def configure(self) -> None:
        #configuring the flowerbed (might have different parameters based on location, flowerbed size, sun exposure,...)
        self.configuration_location = configuration_location
        pass




