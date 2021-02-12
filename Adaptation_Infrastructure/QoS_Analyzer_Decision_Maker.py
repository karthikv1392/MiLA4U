# Implements the QoS Analyzer and Decision Maker algorithm

# replace localhost1 with the ip address of first instance

# replace localhost2 with ip address of second instance

from elasticsearch import Elasticsearch
from ES_Manager import ES_Manager
from datetime import datetime
from datetime import timedelta
import requests
import time
import json
import math

# types of adaptation naive, reactive and static
# naive is for dyanmic approach with no adaptation or usage of ranking algorithm
adaptation_type = "reactive"
#adaptation_type = "naive"

round_val = 0
es_obj = ES_Manager()

vm_instance_ip_2 = "localhost1"
vm_instance_ip_1 = "localhost2"
#vm_instance_ip_1 = "127.0.0.1"



service_composer_2_url = "http://localhost1:9100/updateServiceRanks"
service_composer_1_url = "http://localhost2:8100/updateServiceRanks"


service_discovery_instance1_url_1 = "http://localhost2:8006/updateServiceInstance"
service_discovery_instance1_url_2 = "http://localhost2:8007/updateServiceInstance"

service_discovery_instance2_url_1 = "http://localhost1:9006/updateServiceInstance"
service_discovery_instance2_url_2 = "http://localhost1:9007/updateServiceInstance"

naive_instance2_sd_json = {"parking_count": ["localhost1:8891"], "venue_service": ["localhost1:8889"], "rfid_service": ["localhost1:8893"], "camera_service": ["localhost1:8896"]}
naive_instance1_sd_json =  {"parking_count": ["localhost2:7771", "localhost2:7781"], "venue_service": ["localhost2:7769", "localhost2:7779"], "rfid_service": ["localhost2:7783", "localhost2:7793"], "camera_service": ["localhost2:7786", "localhost2:7796"]}

naive_composer_json1 = {"parking_reccommendation": ["http://localhost2:7772/recomendParking", "http://localhost2:7782/recomendParking", "http://localhost1:8892/recomendParking"], "weather_service": ["http://localhost2:7780/getWeather", "http://localhost2:7790/getWeather", "http://localhost1:8890/getWeather"], "booking_service": ["http://localhost2:7774/requestBooking", "http://localhost1:8894/requestBooking", "http://localhost2:7784/requestBooking"], "availability": ["http://localhost2:7774/checkAvailableBooking", "http://localhost1:8894/checkAvailableBooking", "http://localhost2:7784/checkAvailableBooking"]}
naive_composer_json2 = {"parking_reccommendation": ["http://localhost1:8892/recomendParking", "http://localhost2:7782/recomendParking", "http://localhost1:8892/recomendParking"], "weather_service": ["http://localhost1:8890/getWeather", "http://localhost2:7790/getWeather", "http://localhost1:8890/getWeather"], "booking_service": ["http://localhost1:8894/requestBooking", "http://localhost1:8894/requestBooking", "http://localhost2:7784/requestBooking"], "availability": ["http://localhost1:8894/checkAvailableBooking", "http://localhost1:8894/checkAvailableBooking", "http://localhost2:7784/checkAvailableBooking"]}


class QoS_Analyzer():

    def __init__(self):
        self.service_names = ["parking","booking","weather"]

        self.msa_qos_threshold = 0.5

        self.instance_map_list = {
            "parking" : ["8892","8882","7782","7772"],
            "booking" : ["8894","8884","7784","7774"],
            "weather" : ["8890","8880","7790","7780"]
        }

        self.instance_status_map = {
            "8892" : "active",
            "8894" : "active",
            "8890" : "active",
            "8882" : "inactive",
            "8884" : "inactive",
            "8880" : "inactive",
            "7782" : "active",
            "7784" : "active",
            "7774" : "active",
            "7790" : "active",
            "7772" : "active",
            "7780" : "active",
            "8891" : "active",
            "8881" : "inactive",
            "8896" : "active",
            "8886" : "inactive",
            "8889" : "active",
            "8879" : "inactive",
            "8893" : "active",
            "8883" : "inactive",
            "7793" : "active",
            "7783" : "active",
            "7779" : "active",
            "7769" : "active",
            "7786" : "active",
            "7796" : "active",
            "7771" : "active",
            "7781" : "active"
        }

        self.composer_json = {
            "parking_reccommendation": [],
            "weather_service": [],
            "booking_service": [],
            "availability": []
        }

        self.composer_json_2 = {
            "parking_reccommendation": [],
            "weather_service": [],
            "booking_service": [],
            "availability": []
        }

        # discovery for each running instance
        self.discovery_json_instance = {

            "instance1": {
            "parking_count": [],
            "venue_service": [],
            "rfid_service": [],
            "camera_service": []
            },
            "instance2" : {
                "parking_count": [],
                "venue_service": [],
                "rfid_service": [],
                "camera_service": []
            }
        }



        # spot instances are the one that can be added or removed for adaptation at service level
        self.spot_instance_map = {
            "parking_reccommendation" : ["8882"],
            "booking" : ["8884"],
            "weather" : ["8880"],
            "parking_count" : ["8881"],
            "venue" : ["8879"],
            "rfid" : ["8883"],
            "camera" : ["8886"]
        }

        self.discovery_url_string_template = "$IP:$PORT"

        self.mapping_json = {
            "parking_reccommendation": "http://$IP:$PORT/recomendParking",
            "weather_service": "http://$IP:$PORT/getWeather",
            "booking_service": "http://$IP:$PORT/requestBooking",
            "availability": "http://$IP:$PORT/checkAvailableBooking"
        }

        self.instance_avg_qos = {
            "parking_reccommendation" : {
                "8892" : 0.0,
                "8882" : 0.0,
                "7782" : 0.0,
                "7772" : 0.0
            },
            "booking": {
                    "8894" : 0.0,
                    "8884" : 0.0,
                    "7784" : 0.0,
                    "7774" : 0.0
            },
            "weather" :
                {
                    "8890" : 0.0,
                    "8880" : 0.0,
                    "7790" : 0.0,
                    "7780" : 0.0
                },
            "parking_count":
                {
                    "8881" : 0.0,
                    "8891" : 0.0,
                    "7781" : 0.0,
                    "7771" : 0.0
                },
            "camera" :
                {
                    "7786" : 0.0,
                    "7796" : 0.0,
                    "8886" : 0.0,
                    "8896" : 0.0
                },
            "venue" :
                {
                    "8879" : 0.0,
                    "8889" : 0.0,
                    "7769" : 0.0,
                    "7779" : 0.0
                },
            "rfid" :
                {
                    "7793" : 0.0,
                    "7783" : 0.0,
                    "8883" : 0.0,
                    "8893" : 0.0
                }
        }

        self.instance_avg_calculator = {
            "parking_reccommendation": {
                "8892": [0.0],
                "8882": [0.0],
                "7782": [0.0],
                "7772": [0.0]
            },
            "booking": {
                "8894": [0.0],
                "8884": [0.0],
                "7784": [0.0],
                "7774": [0.0]
            },
            "weather":
                {
                    "8890": [0.0],
                    "8880": [0.0],
                    "7790": [0.0],
                    "7780": [0.0]
                },
            "parking_count":
                {
                    "8881": [0.0],
                    "8891": [0.0],
                    "7781": [0.0],
                    "7771": [0.0]
                },
            "camera":
                {
                    "7786": [0.0],
                    "7796":[0.0],
                    "8886": [0.0],
                    "8896": [0.0]
                },
            "venue":
                {
                    "8879": [0.0],
                    "8889": [0.0],
                    "7769": [0.0],
                    "7779": [0.0]
                },
            "rfid":
                {
                    "7793": [0.0],
                    "7783": [0.0],
                    "8883":[0.0],
                    "8893": [0.0]
                }
        }

        self.microservice_arrival = {
            "parking_count" : 0.0,
            "venue" : 0.0,
            "camera" : 0.0,
            "rfid" : 0.0,
        }

        #self.instance_qos_dict = self.instance_avg_qos
    def query_es(self):

        query = {
            "query": {
                "range": {
                    "timestamp": {
                        # Change this to 1 hour back if running from local as server time is in GMT
                        "gte": (datetime.now() - timedelta (seconds=8)).strftime("%Y/%m/%d %H:%M:%S"),
                        "lte": datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                        #"lte": (datetime.now() - timedelta (seconds=3600)).strftime("%Y/%m/%d %H:%M:%S")
                    }
                }
            }
        }




        '''
        query = {
            "query": {
                "match_all": {}
            },
            "size": 25,
            "sort": [
                {
                    "timestamp": {
                    "order": "desc"
                    }
                }
            ]
        }
            '''
        es_manager_results = es_obj.search_es(index="response_time", query=query)

        for hit in es_manager_results['hits']['hits']:
            yield  hit["_source"]


    def rank_generator(self):
        # first query es to get all the values
        data_obj = self.query_es()


        for data in data_obj:
            instance = data["instance"]
            latency = data["latency"]
            service_name = data["service_name"]
            #print (instance, latency)
            #print (data["handler"], data["instance"])
            #print (service_name)
            #print (instance)
            #print (data["timestamp"])
            #print (service_name)
            #print (data["timestamp"])
            if service_name in self.instance_avg_qos.keys():
                self.instance_avg_calculator[service_name][str(instance)].append(latency)

            #self.instance_avg_qos[service_name][str(instance)] = latency

            if service_name in self.microservice_arrival.keys():
                self.microservice_arrival[service_name] = self.microservice_arrival[service_name] + 1

        #print (self.instance_avg_calculator)
        for key in self.instance_avg_calculator:
            for item in self.instance_avg_calculator[key]:
                if (len(self.instance_avg_calculator[key][item]) > 1):
                    self.instance_avg_qos[key][item] = sum(self.instance_avg_calculator[key][item])/(len(self.instance_avg_calculator[key][item])-1)
                else:
                    self.instance_avg_qos[key][item] = self.instance_avg_calculator[key][item][0]

                #self.instance_avg_calculator[key][item] = [0.0]
        #print(self.instance_avg_calculator)
        #print (self.instance_avg_qos)
        #print (self.instance_avg_qos)
        goal_start_time = datetime.now()
        for key in self.instance_avg_qos:
            sorted_dict = sorted(self.instance_avg_qos[key].items(), key=lambda x: x[1], reverse=False)
            #print (sorted_dict)
            if "parking_reccommendation" in key:
                self.composer_json["parking_reccommendation"] = []
                self.composer_json_2["parking_reccommendation"] = []
                for val in sorted_dict:
                    #print (val)
                    if self.instance_status_map[str(val[0])] == "active":
                        existing_handle = self.mapping_json["parking_reccommendation"]
                        existing_handle = existing_handle.replace("$PORT",str(val[0]))
                        port = str(val[0])
                        if "7" in port:
                            existing_handle = existing_handle.replace("$IP","127.0.0.1")
                            self.composer_json_2["parking_reccommendation"].append(existing_handle)
                        else:
                            existing_handle = existing_handle.replace("$IP", "127.0.0.1")
                            self.composer_json["parking_reccommendation"].append(existing_handle)
            elif "booking" in key:
                self.composer_json["availability"] = []
                self.composer_json["booking_service"] = []
                self.composer_json_2["availability"] = []
                self.composer_json_2["booking_service"] = []
                for val in sorted_dict:
                    if (str(val[0])) not in self.instance_status_map.keys():
                        continue
                    if self.instance_status_map[str(val[0])] == "active":
                        existing_handle1 = self.mapping_json["booking_service"]
                        existing_handle2 = self.mapping_json["availability"]
                        existing_handle1 = existing_handle1.replace("$PORT", str(val[0]))
                        existing_handle2 = existing_handle2.replace("$PORT", str(val[0]))
                        port = str(val[0])
                        if "7" in port:
                            existing_handle1 = existing_handle1.replace("$IP","127.0.0.1")
                            existing_handle2 = existing_handle2.replace("$IP","127.0.0.1")

                            self.composer_json_2["booking_service"].append(existing_handle1)
                            self.composer_json_2["availability"].append(existing_handle2)
                        else:
                            existing_handle1 = existing_handle1.replace("$IP", "127.0.0.1")
                            existing_handle2 = existing_handle2.replace("$IP", "127.0.0.1")

                            self.composer_json["booking_service"].append(existing_handle1)
                            self.composer_json["availability"].append(existing_handle2)
                        #break

            elif "weather" in key:
                self.composer_json["weather_service"] = []
                self.composer_json_2["weather_service"] = []
                for val in sorted_dict:
                    if self.instance_status_map[str(val[0])] == "active":
                        existing_handle = self.mapping_json["weather_service"]
                        existing_handle = existing_handle.replace("$PORT", str(val[0]))
                        port = str(val[0])
                        if "7" in port:
                            existing_handle = existing_handle.replace("$IP", "127.0.0.1")
                            self.composer_json_2["weather_service"].append(existing_handle)
                        else:
                            existing_handle = existing_handle.replace("$IP", "127.0.0.1")
                            self.composer_json["weather_service"].append(existing_handle)
                        #break

        goal_end_time = (datetime.now() - goal_start_time).microseconds
        print(" goal time ranking", goal_end_time)
        # find the instance with minimum QoS check if it is active and if yes update the service composer
        return self.composer_json,self.composer_json_2



    def update_service_composer(self,type):
        if type == "reactive":
            composer_json1,composer_json2 = self.rank_generator()
            print (composer_json1)
            print (composer_json2)

            requests.post(service_composer_1_url,json=composer_json2)
            requests.post(service_composer_2_url, json=composer_json1)

        elif type == "naive":

            #request_json = json.dumps(naive_composer_json)
            #print(naive_composer_json2)
            response = requests.post(service_composer_1_url, json=naive_composer_json1)
            #print(response.text)
            response = requests.post(service_composer_2_url, json=naive_composer_json2)
            #print(response.text)
            #print (response.text)
        elif type == "static":
            # just run the ranker which can be used for discovery
            composer_json1,composer_json2 = self.rank_generator()

    def service_discovery_rank_generator(self):
        # update the service discovery urls in the instances
        for key in self.instance_avg_qos:
            if key in ["parking_count","venue","rfid","camera"]:
                sorted_dict = sorted(self.instance_avg_qos[key].items(), key=lambda x: x[1], reverse=False)
                #print(sorted_dict)
                if "parking_count" in key:
                    # first empty the discovery options
                    self.discovery_json_instance["instance1"]["parking_count"] = []
                    self.discovery_json_instance["instance2"]["parking_count"] = []
                    for val in sorted_dict:
                        if self.instance_status_map[str(val[0])] == "active":
                            existing_handle = self.discovery_url_string_template
                            existing_handle = existing_handle.replace("$PORT", str(val[0]))
                            if "77" in str(val[0]):
                                existing_handle = existing_handle.replace("$IP", vm_instance_ip_1)
                                self.discovery_json_instance["instance1"]["parking_count"].append(existing_handle)
                            else:
                                existing_handle = existing_handle.replace("$IP", vm_instance_ip_2)
                                self.discovery_json_instance["instance2"]["parking_count"].append(existing_handle)

                elif "venue" in key:
                    # first empty the discovery options
                    self.discovery_json_instance["instance1"]["venue_service"] = []
                    self.discovery_json_instance["instance2"]["venue_service"] = []
                    for val in sorted_dict:
                        if self.instance_status_map[str(val[0])] == "active":
                            existing_handle = self.discovery_url_string_template
                            existing_handle = existing_handle.replace("$PORT", str(val[0]))
                            if "77" in str(val[0]):
                                existing_handle = existing_handle.replace("$IP", vm_instance_ip_1)
                                self.discovery_json_instance["instance1"]["venue_service"].append(existing_handle)
                            else:
                                existing_handle = existing_handle.replace("$IP", vm_instance_ip_2)
                                self.discovery_json_instance["instance2"]["venue_service"].append(existing_handle)

                elif "camera" in key:
                    # first empty the discovery options
                    self.discovery_json_instance["instance1"]["camera_service"] = []
                    self.discovery_json_instance["instance2"]["camera_service"] = []
                    for val in sorted_dict:
                        if self.instance_status_map[str(val[0])] == "active":
                            existing_handle = self.discovery_url_string_template
                            existing_handle = existing_handle.replace("$PORT", str(val[0]))
                            if "77" in str(val[0]):
                                existing_handle = existing_handle.replace("$IP", vm_instance_ip_1)
                                self.discovery_json_instance["instance1"]["camera_service"].append(existing_handle)
                            else:
                                existing_handle = existing_handle.replace("$IP", vm_instance_ip_2)
                                self.discovery_json_instance["instance2"]["camera_service"].append(existing_handle)

                elif "rfid" in key:
                    # first empty the discovery options
                    self.discovery_json_instance["instance1"]["rfid_service"] = []
                    self.discovery_json_instance["instance2"]["rfid_service"] = []
                    for val in sorted_dict:
                        if self.instance_status_map[str(val[0])] == "active":
                            existing_handle = self.discovery_url_string_template
                            existing_handle = existing_handle.replace("$PORT", str(val[0]))
                            if "77" in str(val[0]):
                                existing_handle = existing_handle.replace("$IP", vm_instance_ip_1)
                                self.discovery_json_instance["instance1"]["rfid_service"].append(existing_handle)
                            else:
                                existing_handle = existing_handle.replace("$IP", vm_instance_ip_2)
                                self.discovery_json_instance["instance2"]["rfid_service"].append(existing_handle)

        return self.discovery_json_instance

    def update_service_discovery(self,type):
        if type == "reactive" or type == "static" :
            discovery_json = self.service_discovery_rank_generator()

            request_json1 = json.dumps(discovery_json["instance1"])
            request_json2 = json.dumps(discovery_json["instance2"])

            print (request_json1)
            print (request_json2)

            requests.post(service_discovery_instance1_url_1,request_json2)
            requests.post(service_discovery_instance1_url_2,request_json2)

            requests.post(service_discovery_instance2_url_1, request_json1)
            requests.post(service_discovery_instance2_url_2, request_json1)
        elif type == "naive":
            request_json1 = json.dumps(naive_instance1_sd_json)
            request_json2 = json.dumps(naive_instance2_sd_json)
            response = requests.post(service_discovery_instance1_url_1, request_json2)
            print(response.text)
            response = requests.post(service_discovery_instance1_url_2, request_json2)
            print(response.text)
            response = requests.post(service_discovery_instance2_url_1, request_json2)
            print(response.text)
            response = requests.post(service_discovery_instance2_url_2, request_json2)
            print (response.text)


    def check_microservice_adaptation_need(self):
        # find average QoS for each service check if it is above a threshold
        for key in self.instance_avg_qos:
            avg = 0
            sum = 0
            count = 0
            for instance in self.instance_avg_qos[key]:
                if self.instance_avg_qos[key][instance] > 0.0:
                    count+=1
                    sum = sum + self.instance_avg_qos[key][instance]
            if (count!=0):
                avg = sum / count
                #print ("average " + str(key) + " " + str(avg))
            if avg > self.msa_qos_threshold:
                self.instance_status_map[self.spot_instance_map[key][0]] = "active"
            else:
                self.instance_status_map[self.spot_instance_map[key][0]] = "inactive"

        print (self.instance_avg_qos)
        #self.instance_avg_qos = self.instance_qos_dict




    def update_service_arriva_iot_adaptations(self):
        # send the arrival rate information to IoT
        print (qos_analyze_comp_obj.microservice_arrival)
        es_obj.insert_into_es_id(qos_analyze_comp_obj.microservice_arrival,"arrival_rate","iot1")
        for keys in qos_analyze_comp_obj.microservice_arrival.keys():
            qos_analyze_comp_obj.microservice_arrival[keys] = 0






if __name__ == '__main__':
    qos_analyze_comp_obj = QoS_Analyzer()
    # continously perform the update
    if adaptation_type == "reactive":
        start_time = datetime.now()
        while(True):
            goal_start_time = time.time()
            try:
                qos_analyze_comp_obj.update_service_composer(adaptation_type)
                qos_analyze_comp_obj.update_service_discovery(adaptation_type)
                qos_analyze_comp_obj.check_microservice_adaptation_need()
                goal_end_time = time.time() - goal_start_time
                #print(" goal time", goal_end_time)
                current_time = datetime.now()
                print (qos_analyze_comp_obj.microservice_arrival)
                if (current_time-start_time).seconds >= 60:
                    # refresh the calculations
                    # update es  index on arrival rate
                    #print ("here ")
                    qos_analyze_comp_obj.update_service_arriva_iot_adaptations()
                    start_time = current_time
                time.sleep(5)
            except Exception as e:
                # keep conituing the program
                pass
            #break
    elif adaptation_type == "naive":
        while(True):
            qos_analyze_comp_obj.update_service_composer(adaptation_type)
            qos_analyze_comp_obj.update_service_discovery(adaptation_type)
            time.sleep(2)

    elif adaptation_type == "static":
        start_time = datetime.now()
        while (True):
            current_time = datetime.now()
            qos_analyze_comp_obj.update_service_composer(adaptation_type)
            qos_analyze_comp_obj.update_service_discovery(adaptation_type)
            qos_analyze_comp_obj.check_microservice_adaptation_need()
            if (current_time - start_time).seconds >= 60:
                # refresh the calculations
                # update es  index on arrival rate
                qos_analyze_comp_obj.update_service_arriva_iot_adaptations()
                start_time = current_time

            time.sleep(20)
