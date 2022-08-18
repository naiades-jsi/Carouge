"""A file to test Kafka connection!"""

from kafka import KafkaConsumer

import logging
from json import loads

LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", level=logging.INFO)

consumer = KafkaConsumer(
    bootstrap_servers=["localhost:9092"],
    auto_offset_reset="latest",
    enable_auto_commit="True",
    group_id='carouge-group',
    value_deserializer=eval( "lambda x: loads(x.decode('utf-8'))"),
    max_poll_records = 50,
    max_poll_interval_ms = 600000)

topics_data = [
    "features_carouge_flowerbed1",
    "features_carouge_flowerbed2",
    "features_carouge_flowerbed3",
    "features_carouge_flowerbed4",
    "features_carouge_flowerbed5",
    "features_carouge_flowerbed6",
    "features_carouge_flowerbed7",
    "features_carouge_flowerbed8"
]

consumer.subscribe(topics_data)

for message in consumer:
    topic = message.topic
    value = message.value
    LOGGER.info("%s, %s", topic, str(value))