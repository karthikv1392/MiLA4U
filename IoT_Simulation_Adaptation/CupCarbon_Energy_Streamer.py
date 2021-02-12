_Author_ = "***********"

import subprocess

import csv
import sys
import time
from kafka import KafkaConsumer, KafkaProducer

ENERGY_PATH = "XYZ_Case/results/"

ENERGY_FILE = "wisen_simulation.csv"

class kafka_producer():
    def publish_message(self,producer_instance, topic_name, key, value):
        try:
            key_bytes = bytearray(key,'utf8')
            value_bytes = bytearray(value,'utf8')
            producer_instance.send(topic_name, key=key_bytes, value=value_bytes)
            producer_instance.flush()
            print('Message published successfully.')
        except Exception as ex:
            print('Exception in publishing message')
            print(str(ex))

    def connect_kafka_producer(self):
        _producer = None
        try:
            _producer = KafkaProducer(bootstrap_servers=['localhost:9092'], api_version=(0, 10))
        except Exception as ex:
            print('Exception while connecting Kafka')
            print(str(ex))
        finally:
            return _producer

producer_object = kafka_producer()




def stream_csv_file():
    # read and stream csv files
    producer_instance = producer_object.connect_kafka_producer()
    row_list = ""
    count = 0

    with open(ENERGY_PATH + ENERGY_FILE) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        while (True):
            #for row in csv.reader(iter(csv_file.readline,'')):
            for row in csv.reader(iter(csv_file.readline,'')):
                #print (row)
                if count > 1:
                    if len(row)>0:
                        text = row[0].strip("\n") # Get the first tex# t
                        if not "Time" in text:
                            row_list = row_list + text
                            line_data = row_list
                        #line_data = row[0].strip("\n")
                        #print (line_data.split(";"))
                            if(len(line_data.split(";"))>23):
                                #print(line_data)
                                # Sent the QoS data obtained from CupCarbon
                                #print (row[0])
                                if not "Time" in line_data:
                                    print (line_data)
                                    print (len(line_data.split(";")))
                                    #time.sleep(1)
                                    producer_object.publish_message(producer_instance,"sensor","data",line_data)
                                    row_list=""

                count +=1
                #time.sleep(2)
if __name__ == '__main__':
    stream_csv_file()
