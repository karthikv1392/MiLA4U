# Script to perform reactive adaptation based on the algorithm
import csv
import sys
import time
from kafka import KafkaConsumer, KafkaProducer
from Custom_Logger import logger
import numpy as np
from numpy import array
import pandas as pd
from datetime import datetime
from Adapter_IoT import Adaptation_Planner
import json


ada_obj = Adaptation_Planner()

 # Initialize the inital energy configuration

prev_vals = [19160.0, 19160.0, 19160.0, 19160.0, 19160.0, 19160.0, 19160.0, 19160.0, 19160.0, 19160.0, 19160.0,
             19160.0, 19160.0, 19160.0, 19160.0, 19160.0, 19160.0, 19160.0, 19160.0, 19160.0, 19160.0,
             19160.0]
main_energy_list = []
class Streaming_Consumer():
    # Class that will perform the prediction in near-real time
    def process_sensor_data(self):
        # This will process the data from the sensor and then perform the management of the data
        print ("processing")
    def gather_data(self,adaptation_type,horizon=10,lag=10,decision_period=10):
        global prev_vals
        global main_energy_forecast
        global main_traffic_forecast
        consumer = KafkaConsumer(auto_offset_reset='latest',
                                  bootstrap_servers=['localhost:9092'], api_version=(0, 10), consumer_timeout_ms=1000)

        consumer.subscribe(pattern='^sensor.*')    # Subscribe to a pattern
        main_energy_list = []
        while True:
            for message in consumer:
                if message.topic == "sensor":
                    # The QoS data comes here and the prediction needs to be done here
                    row = str(message.value).split(";")
                    if (len(row) > 3):
                        time_string = row[0]
                        second_level_data = []
                        row.pop()  # remove the unwanted last element
                        vals = [x1 - float(x2) for (x1, x2) in zip(prev_vals, row[1:])]
                        # print (len (vals))
                        if (len(vals) == 22):
                            # Check if we have 22 elements always
                            # spark_predictor.main_energy_list.append(vals)
                            main_energy_list.append(vals)
                            #final_energy_list = [x + y for x, y in zip(final_energy_list, vals)] ## Keep addding them
                            prev_vals = [float(i) for i in row[1:]]

                    if adaptation_type == "reactive":
                        if (len(main_energy_list) == 1):
                            #print (main_energy_list)
                            # Compute the energy consumed by each sensor
                            ada_obj.reactive(main_energy_list)
                            logger.info("adaptation count " + str(ada_obj.adapation_count) + " " + str(ada_obj.time_count))
                            main_energy_list = [] # This will mean only every 10 minutes an adaptation will be performed

if __name__ == '__main__':
    stream_consumer =  Streaming_Consumer()
    stream_consumer.gather_data(adaptation_type="reactive",horizon=1,lag=1,decision_period=1) # adaptation_type denotes the type of adaptation to be performed
