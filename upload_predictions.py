import numpy as np

import argparse
import json
import sys
import requests
import threading
import time
import logging

#from consumer import ConsumerKafka

from datetime import datetime
#from output import KafkaOutput
#from waterbeds import Flowerbed1
#from consumer import ConsumerKafka
#from forecasting import DenseNN
from scheduling import Scheduling
#from multiprocessing import Process

LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", level=logging.INFO)

def start_consumer(config):
    #this will be changed to a component which communicates with the API
    consumer = ConsumerKafka(configuration_location=config)
    consumer.read()

def start_scheduler(config):
    #this will be changed to a component which communicates with the API
    consumer = Scheduling(configuration_location=config)
    consumer.run()

def ping_watchdog(process_consumer, process_schedule):
    interval = 30 # ping interval in seconds
    url = "localhost"
    port = 5001
    path = "/pingCheckIn/Carouge plants watering"

    while(process_consumer.is_alive() and process_schedule.is_alive()):
        #print("{}: Pinging.".format(datetime.now()))
        try:
            r = requests.get("http://{}:{}{}".format(url, port, path))
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            logging.warning(e)
        else:
            logging.info('Successful ping at ' + time.ctime())
        time.sleep(interval)

    # Crash report
    if(not process_consumer.is_alive()):
        print("{}: Carouge consumer crashed.".format(datetime.now()))
    if(not process_schedule.is_alive()):
        print("{}: Carouge scheduler crashed.".format(datetime.now()))


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

    parser.add_argument(
        "-w",
        "--watchdog",
        dest="watchdog",
        action='store_true',
        help=u"Ping watchdog",
    )

    # Display help if no arguments are defined
    if (len(sys.argv) == 1 or len(sys.argv) == 2):
        parser.print_help()
        sys.exit(1)

    # Parse input arguments
    args = parser.parse_args()

    consumer = Scheduling(configuration_location=str(args.config_schedule))
    consumer.time_predictions()

if (__name__ == '__main__'):
    main()