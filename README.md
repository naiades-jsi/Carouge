# Carouge - predictions for watering of flowerbeds

The component is communicating via Kafka topics.

Input topics (with feature vectors):

* `features_carouge_flowerbed8`
* `features_carouge_flowerbed6`
* `features_carouge_flowerbed1`
* `features_carouge_flowerbed7`
* `features_carouge_flowerbed4`
* `features_carouge_flowerbed2`
* `features_carouge_flowerbed3`

Output topics:

* `device_1f0d_pred_output` | FlowerBed1
* `device_1f08_pred_output` | FlowerBed2
* `device_1f10_pred_output` | FlowerBed3
* `device_1f06_pred_output` | FlowerBed4
* `device_1eff_pred_output` | FlowerBed6
* `device_1f02_pred_output` | FlowerBed7
* `device_1efe_pred_output` | FlowerBed8
* `device_1efd_pred_output` | ???
* `device_1f09_pred_output` | ???

# Running the component

The component is run with:

```python3 main.py -cc config_real_data.json -cs schedule_real_data.json```

The configuration files are being stored in `/configuration/main/` (for consumer config) and `/configuration/schedule/` (for schedule config).

Consumer config includes Kafka connection parameters as well as device configurations. The config looks like this:

```json
{
    "bootstrap_servers": ["localhost:9092"],
    "auto_offset_reset": "latest",
    "enable_auto_commit": "True",
    "group_id": "carouge-group",
    "value_deserializer": "lambda x: loads(x.decode('utf-8'))",
    "flowerbeds":["device_1efe", ...],
    "device_1efe": {
        "name" : "device_1efe",
        "topic": "features_carouge_flowerbed8",
        "initial_threshold": 24,
        "forecast_model": "DenseNN_RealData()",
        "forecast_model_conf": {
            "loss_coefs": [1, 1],
            "rise_time":2,
            "train_data": "flowerbed8_160h_new.npy"
        },
        "output": [],
        "output_conf": [{}]
    },
    ...
}
```

Scheduler config includes data on the hour when predictions are made, files, where predictions are stored and Kafka output topics.

```json
{
    "hour_of_time_predictions": "06:00",
    "predictions_files": [
        "device_1efd_prediction.json",
        ...
    ],
    "output_topics": [
        "device_1efd_pred_output",
        ...
    ],
    "bootstrap_server": ["localhost:9092"]
}
```

# Deploying and building

The component is deployed via Docker Hub at `e3ailab/carouge_ircai`.

The image is built with `docker build -t e3ailab/carouge_ircai`.

The component must be pushed to the Docker Hub via `docker push` command. Before deploying in the production the component needs to be pulled from repository with: `docker pull e3ailab/carouge_ircai`. Finally, the component is run with `docker run -d --network=host e3ailab/carouge_ircai`.

# Debugging

For debugging reasons several scripts are available in the repository. Kafka message receiver can be tested with `testkafka.py`. Note that the same Kafka group ID can interfere with messages being received at a particular component. Be careful that there is no other Kafka consumer with the same id running somewhere in your ecosystem.

For pushing current predictions, `upload_predictions.py` script can be used.


# Technical details

1. The Carouge component runs 2 simultaneous threads:
  - Predictions -> in this thread, the predictions are done as new feature vectors are uploaded to the input kafka topic. The predictions are stored in temporary files. (example configurations: configuration/main/)
  - Scheduling -> This thread runs a check once per day, to see if any of the predictions indicate that watering is needed within the next few days. If so, the watering reccomendation is sent forward to the fiware-uploader component.
(example configurations: configuration/schedule/)
2. Watering predictions are done based on past data from the `flowerbed1-8`, `device_*`, and weather entities.
The main prediction model is a densely connected NN, which takes feature vectors of length 8 as inputs, and produces soil moisture predictions for 80 horizons. From the predicted moisture profile, we check if the moisture will fall under the set threshold, within the time of the predictions and if so, we calculate in how many hours this will happen. The predicted profiles and reccomended times of watering are stored in `.json` files, for each flowerbed separately. Once per day at 6:00 (`scheduling.py`) these `.json` files are analysed. If any of the flowerbeds require watering, a message is sent to kafka, which is then handeled by the fiware-uploader component.

3. The main model's `x_train` and `y_train` data can be built using `data_prep.ipynb` and `data_prep2.ipynb`.
  - `x_train` vectors are read from .json files produced by data-fusion
  - `y_train` vectors are produced from the `device_...` entities' moisture values -> 80 "future" moisture values
