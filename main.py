import numpy as np

import argparse
import json
import sys
import requests
import threading
import time
import logging

from consumer import ConsumerKafka

from output import KafkaOutput
from waterbeds import Flowerbed1
from consumer import ConsumerKafka
from forecasting import DenseNN
from scheduling import Scheduling
from multiprocessing import Process

def start_consumer(config):
    #this will be changed to a component which communicates with the API
    consumer = ConsumerKafka(configuration_location=config)
    consumer.read()

def start_scheduler(config):
    #this will be changed to a component which communicates with the API
    consumer = Scheduling(configuration_location=config)
    consumer.run()


def main():
    parser = argparse.ArgumentParser(description="consumer")

    parser.add_argument(
        "-cc",
        "--configconsumer",
        dest="config_consumer",
        default="consumer/config1.json",
        help=u"Config file for consumer located in ./config/ directory."
    )

    parser.add_argument(
        "-cs",
        "--configschedule",
        dest="config_schedule",
        default="schedule/config1.json",
        help=u"Config file for scheduler located in ./config/ directory."
    )

    # Display help if no arguments are defined
    if (len(sys.argv) == 1 or len(sys.argv) == 2):
        parser.print_help()
        sys.exit(1)

    # Parse input arguments
    args = parser.parse_args()

    # Define paralell proceses
    consumer_process = Process(target=start_consumer,
                               args=(str(args.config_consumer),))
    schedule_process = Process(target=start_scheduler,
                               args=(str(args.config_schedule),))
    
    # Start paralell processes
    consumer_process.start()
    schedule_process.start()
    


if (__name__ == '__main__'):
    main()