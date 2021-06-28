# simulation component

import time
import numpy as np
from kafka import KafkaConsumer, KafkaProducer
from json import dumps, loads
import matplotlib.pyplot as plt


#consumer
#producer
#configuration

configuration = {
    "name": "flowerbed1"
}

producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda x: dumps(x).encode('utf-8'))

consumer = KafkaConsumer(bootstrap_servers=["localhost:9092"],
                        auto_offset_reset="latest",
                        enable_auto_commit="True",
                        group_id="my-group",
                        value_deserializer=lambda x: loads(x.decode('utf-8')))

consumer.subscribe(["flowerbed1_WA"])

def simulate(WA, current, period):

    start = time.time()
    dampness = current

    top = dampness + WA
    s = top
    S = np.linspace(current, top, 10)
    for i in range(100):
        #condition = cond(i, T,  300)
        s -= 0.02*s + (np.random.rand()-0.5)*0.03
        S = np.concatenate([S, [s]])

    for i in range(len(S)):
        if((time.time() - start) < period):
            tosend = {
                "case": "dampness",
                "timestamp": time.time(),
                "value": S[i]
            }
            running_dampness.append(S[i])
            producer.send(kafka_topic, value=tosend)
            time.sleep(1)
            print("Step " + str(i) + " -- dampness = " +  str(S[i]))
    print('tle sm')
    return(running_dampness[-1])




running_dampness = []

current = 1.0
WA = 1
kafka_topic = "flowerbed1_data"
current = simulate(WA, current, 50)

for message in consumer:
    #once we get the WA:
    WA = message.value
    print("message: " + str(WA))
    current = simulate(WA["WA"], current, 50)

plt.plot(running_dampness)
plt.savefig('dampness.png')


