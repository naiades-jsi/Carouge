# ML models to predict the time dependant dampness based on input data
# (watering ammount, current dampness, weather forecast)


class ForecastAbstract(ABC):

    def __init__(self, configuration_location: str = None) -> None:
        self.configuration_location = configuration_location

    @abstractmethod
    def configure(self, con: Dict[Any, Any], configuration_location: str) -> None:
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
    
    @abstractmethod
    def configure(self, con: Dict[Any, Any], configuration_location: str) -> None:
        self.configuration_location = configuration_location
        pass

    @abstractmethod
    def train(self) -> None:
        pass

    @abstractmethod
    def predict(self, input_values: list) -> None:
       pass 