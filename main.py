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
from scheduling import SimpleSchedule
from consumer import ConsumerKafka
from forecasting import DenseNN


def main():
    parser = argparse.ArgumentParser(description="consumer")

    parser.add_argument(
        "-c",
        "--config",
        dest="config",
        default="config1.json",
        help=u"Config file located in ./config/ directory."
    )

    parser.add_argument(
        "-fk",
        "--filekafka",
        dest="data_both",
        action="store_true",
        help=u"Read data from a specified file on specified location and then from kafka stream."
    )

    # Display help if no arguments are defined
    if (len(sys.argv) == 1):
        parser.print_help()
        sys.exit(1)

    # Parse input arguments
    args = parser.parse_args()

    #this will be changed to a component which communicates with the API
    consumer = ConsumerKafka(configuration_location=args.config)

    consumer.read()


if (__name__ == '__main__'):
    main()