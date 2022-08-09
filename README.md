# Carouge
1. The Carouge component runs 2 simultaneous threads - 1) Predictions -> in this thread, the predictions are done as new feature vectors are uploaded to the input kafka topic. The predictions are stored in temporary files. 2) Scheduling -> This thread runs a check once per day, to see if any of the predictions indicate that watering is needed within the next few days. If so, the watering reccomendation is sent forward to the fiware-uploader component.

2. Watering predictions are done based on past data from the flowerbed1-8, device_, and weather entities. 
The main prediction model is a densely connected NN, which takes feature vectors of length 8 as inputs, and produces soil moisture predictions for 80 horizons. From the predicted moisture profile, we check if the moisture will fall under the set threshold, within the time of the predictions and if so, we calculate in how many hours this will happen. The predicted profiles and reccomended times of watering are stored in .json files, for each flowerbed separately. Once per day at 6:00 (scheduling.py) these .json files are analysed. If any of the flowerbeds require watering, a message is sent to kafka, which is then handeled by the fiware-uploader component.

3. The main model's x_train and y_train can be built using data_prep.ipynb and data_prep2.ipynb.
  - x_train vectors are read from .json files produced by data-fusion
  - y_train vectors are produced from the device_... entities' moisture values -> 80 "future" moisture values
