# replace localhost with the ip of the respective instances

import asyncio
import threading
import time

import tornado.ioloop
import tornado.web
from tornado.options import define, options
import tornado.httpserver
from elasticsearch import Elasticsearch
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
from random import randint
import traceback
import json
import requests
import math
from concurrent.futures import ThreadPoolExecutor

from Goal_Parser import Goal_Parser
import random

import nest_asyncio
nest_asyncio.apply()


goal_parse_obj = Goal_Parser()
es_host1 =  'localhost'


request_counter  = 0
port = 9100
from datetime import datetime
es_host =  'localhost'

json_data = {}


json_data["venue_number"] = 1
json_data["username"] = "username"

#json_data = json.dumps(json_data)
#print (json_data)

round_val = 0

composer_json = {"parking_reccommendation":
                     ["http://localhost:7772/recomendParking", ""
                                                                  "http://localhost:7782/recomendParking",
                      "http://localhost:8892/recomendParking"], "weather_service": ["http://localhost:7780/getWeather",
                                                                                        "http://localhost:7790/getWeather", "http://localhost:8890/getWeather"], "booking_service": ["http://localhost:7774/requestBooking", "http://localhost:8894/requestBooking", "http://localhost:7784/requestBooking"], "availability": ["http://localhost:7774/checkAvailableBooking", "http://localhost:8894/checkAvailableBooking", "http://localhost:7784/checkAvailableBooking"]}


class discovery_class():
    def __init__(self):
        # store the goal list
        self.goal_list = ["parking_reccommendation", "weather_service", "booking_service", "availability"]

        # Store the functionality and corresponding locations



discovery_obj = discovery_class()

def fetch(session, url):

    with session.post(url,json_data) as response:
        ##end_time =  datetime.now()
        #timediff = ((end_time - start_time).microseconds) / 1000000
        #time_completed_at = "{:5.2f}s".format(timediff)
        #query = "insert into user_goal(message, latency) values(" + "'" + str(goal) + "'," + str(timediff) + ");"
        # print (query)
        #sql_obj.insert(query)
        print (response)
        #print("completed time", time_completed_at)

        return "ok"


async def get_data_asynchronous(service_name):
    #print("{0:<30} {1:>20}".format("File", "Completed at"))
    with ThreadPoolExecutor(max_workers=len(service_name)) as executor:
        with requests.Session() as session:
            # Set any session parameters here before calling `fetch`
            loop = asyncio.get_event_loop()

            tasks = [
                loop.run_in_executor(
                    executor,
                    fetch,
                    *(session, url_generator(int(index))) # Allows us to pass in multiple arguments to `fetch`
                )
                for index in service_name
            ]
            for response in await asyncio.gather(*tasks):
                pass




def url_generator(index):
    # Get service request url
    round_val = randint(0,1)
    goal_key  = discovery_obj.goal_list[index]
    global composer_json
    # select among the top 2 ranked instances based on random selection to better manage the load
    if (len(composer_json[goal_key]) > 1):
        service_request_url = composer_json[goal_key][round_val]
    else:
        service_request_url = composer_json[goal_key][0]
    return service_request_url

def request_dispatcher(service_name,goal_type):
    # responsible for sending request to the service based on the url
    response_dict = {}
    if goal_type == "seq":
        for index in range(0, len(service_name)):
            goal_item = service_name[index]
            request_url = url_generator(int(goal_item))
            print (request_url)
            response = requests.post(request_url, json=json_data)
            print(response.text)
        response_dict["code"] = "success"
        return response_dict
    elif goal_type == "or" or goal_type == "oneof" :
        max_val = len(service_name) - 1
        random_selection = random.randint(0,max_val)
        goal_item = service_name[random_selection]
        request_url = url_generator(int(goal_item))
        response = requests.post(request_url, json=json_data)
        print (response.text)
        response_dict["code"] = "success"
        return response_dict

    elif goal_type == "and":
        # asynchronous requests
        thread_count = len(service_name)
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(get_data_asynchronous(service_name))
        # loop.run_until_complete(future)
        loop.run_until_complete(future)
        response_dict["code"] = "success"
        return response_dict

    elif goal_type == "single":
        for index in range(0, len(service_name)):
            goal_item = service_name[index]
            request_url = url_generator(int(goal_item))
            response = requests.post(request_url, json=json_data)
        response_dict["code"] = "success"
        return response_dict

    else:
        # If a new conidtion comes in
        response_dict["code"] = "error"
        return  response_dict



class FetchServiceInstance(tornado.web.RequestHandler):
    def post(self):
        # Check elasticsearch connection and loop till connected and query the database
        global request_counter
        request_counter+= 1
        print ("request counter", request_counter)
        try:
            start_time = datetime.now()
            json_request_string = self.request.body
            json_object = json.loads(json_request_string)
            user_goal = json_object["goal_string"]
            experiment = json_object["experiment"]

            #user_goal = self.get_argument('goal_string', None)

            #print (user_goal)
            goal_start_time = datetime.now()
            goal_parsed_json = goal_parse_obj.goal_string_generator(user_goal)
            goal_end_time = (datetime.now()- goal_start_time).microseconds
            print (" goal parsing time ", goal_end_time)
            print (goal_parsed_json)
            service_name = goal_parsed_json["goal_string"]
            goal_type = goal_parsed_json["goal_type"]
            self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin', '*'))
            self.set_header('Access-Control-Allow-Methods', 'GET, POST')
            self.set_header('Content-Type', 'application/json')
            response_dictionary = {}
            response_dictionary = request_dispatcher(service_name,goal_type)
            end_time = datetime.now()

            json_data = {}

            json_data["goal_type"] = goal_type
            json_data["goal"] = service_name
            json_data["experiment"] = experiment
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            json_data["latency"] = ((end_time - start_time).microseconds) / 1000000
            print(json_data)
            es.index(index="experiment_clock", body=json_data)

            response_dictionary["status"] = 200
            response_dictionary["goal_string"] = service_name
            response_dictionary["goal_type"]  = goal_type


            self.write(response_dictionary)
        except Exception as e:
            # handle error
            traceback.print_exc()
            response_dictionary = {}
            response_dictionary["status"] = 500
            self.write(response_dictionary)



class UpdateServiceInstance(tornado.web.RequestHandler):
    def post(self):
        # Check elasticsearch connection and loop till connected and query the database
        json_string = self.request.body
        global composer_json
        json_request_string = self.request.body
        json_object = json.loads(json_request_string)
        composer_json = json_object

        # define response header
        self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin', '*'))
        self.set_header('Access-Control-Allow-Methods', 'GET, POST')
        self.set_header('Content-Type', 'application/json')
        response_dictionary = {}
        #print ( res['hits']['hits'])
        response_dictionary["status"] = "success"
        self.write(response_dictionary)
        self.flush()
        self.finish()





'''
tornado functions for starting an endpoint for each venue
each function will have a thread running so all of them are running at the same time
'''


def server_start():
    application = tornado.web.Application(
        [(r"/accomplishGoal", FetchServiceInstance),
         (r"/updateServiceRanks", UpdateServiceInstance)
         ]
    )

    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    try:
        print("Starting Tornado Web Server for service discovery on " + str(port))
        es = Elasticsearch([es_host1])
        http_server = tornado.httpserver.HTTPServer(server_start())
        http_server.listen(port)
        tornado.ioloop.IOLoop.instance().start()
    except:
        # logger.exception( "Exception occurred when trying to start tornado on " + str(options.port))
        traceback.print_exc()
