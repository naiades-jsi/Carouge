import argparse
import sys
import schedule
import json
import time
from typing import Any, List
from kafka import KafkaProducer
from datetime import datetime

def run_time_predictions(scheduling):
    scheduling.time_predictions()

class Scheduling:
    hour_of_time_predictions: str
    predictions_files: List[str]
    output_topics: List[str]
    kafka_producer: Any

    def __init__(self, configuration_location: str) -> None:
        # Read config file
        with open("configuration/schedule/" + configuration_location) as data_file:
            conf = json.load(data_file)
        self.configure(configuration=conf)

    def configure(self, configuration: Any) -> None:
        self.hour_of_time_predictions = configuration["hour_of_time_predictions"]
        self.predictions_files = configuration["predictions_files"]
        self.output_topics = configuration["output_topics"]
        self.bootstrap_server = configuration["bootstrap_server"]

        # The lists must be of the same length
        assert len(self.predictions_files) == len(self.output_topics), "The number of prediction files and output topics must match."

        self.kafka_producer = KafkaProducer(bootstrap_servers= self.bootstrap_server,
                                      value_serializer=lambda x: json.dumps(x).encode('utf-8'))

        #Schedule daily time predictions
        schedule.every().day.at(self.hour_of_time_predictions).do(self.time_predictions)

        #Schedule prediction every minute (for testing)
        #schedule.every(1).minute.do(self.time_predictions)
        print('Sceduling config complete: ' + str(time.time()), flush=True)



    def time_predictions(self) -> None:

        print("Time predictions: " + str(time.time()), flush=True)
        # Reads predicted times and schedules prediction reads for water
        # amount and sends time predictions to kafka.

        # read all flower bed sensor files
        for prediction_file_indx in range(len(self.predictions_files)):
            prediction_files = self.predictions_files[prediction_file_indx]
            file_path = "./predictions/" + prediction_files
            with open(file_path) as predictions_json:
                last_prediction = json.load(predictions_json)
                # If the watering happens today
                hours_until_watering = last_prediction["T"]
                WA = last_prediction["WA"]
                if(hours_until_watering < 24):
                    sample_time = last_prediction["timestamp"]

                    # Sample time is in miliseconds (needs to be in seconds).
                    # To this time seconds untill watering are added.
                    time_of_watering = sample_time/1000 + hours_until_watering * 3600

                    # Send to kafka
                    kafka_topic = self.output_topics[prediction_file_indx]
                    output_dict = {"timestamp": time.time(),
                                    "T": datetime.fromtimestamp(time_of_watering).strftime("%Y-%m-%d %H:%M:%S"),
                                    "WA": WA}
                    self.kafka_producer.send(kafka_topic, value=output_dict)

                    #   Schedule water amount prediction (30 minutes before the actual watering)
                    #   schedule.every().day.at(datetime.fromtimestamp(time_of_watering-1800).strftime("%H:%M")).do(self.water_amount_predictions(prediction_file_indx))

    def water_amount_predictions(self, index: int) -> Any:
        print("Water amount predictions" + str(time.time()), flush=True)
        # Reads predicted water amount and sends it to kafka
        
        prediction_file = self.predictions_file[index]
        with open(prediction_file) as file:
            json_file = json.load(file)
            output_dict = {"W": json_file["W"]}
            self.kafka_producer.send(self.output_topics[index],
                                     value=output_dict)

        # So that the job only executes once
        return schedule.CancelJob

    def run(self) -> None:
        # Loop and run all jobs that need to be ran
        while True:
            # run_pending obtain calls
            schedule.run_pending()
            time.sleep(1)


    def printing(self):
        print('hello')