import argparse
import sys
import schedule
import json
import time
from typing import Any


def main():
    parser = argparse.ArgumentParser(description="consumer")

    parser.add_argument(
        "-c",
        "--config",
        dest="config",
        default="config1.json",
        help=u"Config file located in ./config/ directory."
    )

    # Display help if no arguments are defined
    if (len(sys.argv) == 1):
        parser.print_help()
        sys.exit(1)

    # Parse input arguments
    args = parser.parse_args()

    #this will be changed to a component which communicates with the API
    consumer = Scheduling(configuration_location=args.config)



if (__name__ == '__main__'):
    main()

class Scheduling:
    hour_of_time_predictions: str
    predictions_file: str

    def __init__(self, configuration_location: str) -> None:
        # Read config file
        with open("configuration/schedule" + configuration_location) as data_file:
            conf = json.load(data_file)
        self.configure(configuration=conf)

    def configure(self, configuration: Any) -> None:
        self.hour_of_time_predictions = configuration["hour_of_time_predictions"]
        self.predictions_file = configuration["predictions_file"]

        #Schedule daily time predictions

    def time_predictions(self) -> None:
        # Reads predicted times and schedules prediction reads for water
        # amount and sends time predictions to kafka.
        pass

    def water_amount_predictions(self) -> None:
        # Reads predicted water amount and sends it to kafka
        pass

    def run(self) -> None:
        # Loop and run all jobs that need to be ran
        while True:
            # run_pending obtain calls
            schedule.run_pending()
            time.sleep(1)
