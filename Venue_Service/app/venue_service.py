import asyncio
import threading
import time

import tornado.ioloop
import tornado.web
import tornado.httpserver
import traceback
from elasticsearch import Elasticsearch
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
from random import randint
import math
import os

port = int(os.environ['PORT_NUM'])
from datetime import datetime
es_host = str(os.environ['ES_HOST'])
# for endless loops inside created threads
venue1_counter = 0
venue2_counter = 0
venue3_counter  = 0



class CheckVenueArea1(tornado.web.RequestHandler):
    def post(self):
        # Check elasticsearch connection and loop till connected and query the database
        global venue1_counter
        venue1_counter+=1
        start_time = datetime.now()
        try:
            while not es1.ping:
                print("Establishing connection ...")
            search_param = {
                "query": {
                    "range": {
                        "tag": {
                            "lte": 2,
                            "gte": 1,
                        }
                    }
                }
            }
            res = es1.search(index="people_count", body=search_param, size=10)

            # define response header
            self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin', '*'))
            self.set_header('Access-Control-Allow-Methods', 'GET, POST')
            self.set_header('Content-Type', 'application/json')

            # we calculate the average number of people from the selected venues and return
            average_number_of_people = 0

            # flag to check first result to calculate correctly average_number_of_people
            flag = False

            # create a dictionary for JSON response
            response_dictionary = {}

            for hit in res['hits']['hits']:
                if hit['_source']['tag'] == "1" or hit['_source']['tag'] == "2":
                    if not flag:
                        average_number_of_people = float(hit['_source']['text'])
                        flag = True
                    average_number_of_people = (average_number_of_people + float(hit['_source']['text'])) / 2.0
            if average_number_of_people <= 20:
                response_dictionary["value"] = "Low"
            if 20 < average_number_of_people < 30:
                response_dictionary["value"] = "Medium"
            if average_number_of_people >= 30:
                response_dictionary["value"] = "High"
            # print("Average number of people in venues 1 and 2 is : " + average_number_of_people)
            response_dictionary["average_number_of_people"] = average_number_of_people

            # Simulate cpu load


            self.set_status(status_code=200, reason="Request successfully handled")
            end_time = datetime.now()
            json_data = {}
            response_dictionary = {}
            json_data["service_name"] = "venue"
            json_data["instance"] = port
            json_data["handler"] = "CheckVenueArea1"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = venue1_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 1000000
            print (json_data)
            es1.index(index="response_time",body=json_data)
            response_dictionary["status"] = 200
            self.write(response_dictionary)
            #self.flush()
            #self.finish()
        except Exception as e:
            end_time = datetime.now()
            json_data = {}
            response_dictionary = {}
            json_data["service_name"] = "venue"
            json_data["instance"] = port
            json_data["handler"] = "CheckVenueArea1"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = venue1_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 1000000
            print(json_data)
            es1.index(index="response_time", body=json_data)
            response_dictionary["status"] = 500
            self.write(response_dictionary)

    get = post


class CheckVenueArea2(tornado.web.RequestHandler):
    def post(self):
        # Check elasticsearch connection and loop till connected and query the database
        start_time = datetime.now()
        global venue2_counter
        venue2_counter +=1
        try:
            while not es2.ping:
                print("establishing connection ...")
            search_param = {
                "query": {
                    "range": {
                        "tag": {
                            "lte": 4,
                            "gte": 3,
                        }
                    }
                }
            }
            res = es2.search(index="people_count", body=search_param, size=10)

            # define response header
            self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin', '*'))
            self.set_header('Access-Control-Allow-Methods', 'GET, POST')
            self.set_header('Content-Type', 'application/json')

            # we calculate the average number of people from the selected venues and return  the crowdiness
            average_number_of_people = 0

            # flag to check first result to calculate correctly average_number_of_people
            flag = False

            # create a dictionary for JSON response
            response_dictionary = {}

            for hit in res['hits']['hits']:
                if hit['_source']['tag'] == "3" or hit['_source']['tag'] == "4":
                    if not flag:
                        average_number_of_people = float(hit['_source']['text'])
                        flag = True
                    average_number_of_people = (average_number_of_people + float(hit['_source']['text'])) / 2.0
            if average_number_of_people <= 20:
                response_dictionary["value"] = "Low"
            if 20 < average_number_of_people < 30:
                response_dictionary["value"] = "Medium"
            if average_number_of_people >= 30:
                response_dictionary["value"] = "High"
            # print("Average number of people in venues 3 and 4 is : " + average_number_of_people)
            response_dictionary["average_number_of_people"] = average_number_of_people
            self.set_status(status_code=200, reason="Request successfully handled")
            end_time = datetime.now()
            json_data = {}

            json_data["service_name"] = "venue"
            json_data["instance"] = port
            json_data["handler"] = "CheckVenueArea2"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = venue2_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 1000000
            print(json_data)
            es1.index(index="response_time", body=json_data)
            response_dictionary["status"] = 200
            self.write(response_dictionary)
            #self.flush()
            #self.finish()
        except Exception as e:
            end_time = datetime.now()
            json_data = {}
            response_dictionary = {}
            json_data["service_name"] = "venue"
            json_data["instance"] = port
            json_data["handler"] = "CheckVenueArea2"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = venue2_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 1000000
            print(json_data)
            es1.index(index="response_time", body=json_data)
            response_dictionary["status"] = 500
            self.write(response_dictionary)

    get = post


class CheckVenueArea3(tornado.web.RequestHandler):
    def post(self):
        # Check elasticsearch connection and loop till connected and query the database
        start_time = datetime.now()
        global venue3_counter
        venue3_counter += 1
        try:
            while not es3.ping:
                print("establishing connection ...")
            search_param = {
                "query": {
                    "range": {
                        "tag": {
                            "lte": 7,
                            "gte": 5,
                        }
                    }
                }
            }
            res = es3.search(index="people_count", body=search_param, size=20)

            # define response header
            self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin', '*'))
            self.set_header('Access-Control-Allow-Methods', 'GET, POST')
            self.set_header('Content-Type', 'application/json')

            # we calculate the average number of people from the selected venues and return  the crowdiness
            average_number_of_people = 0

            # flag to check first result to calculate correctly average_number_of_people
            flag = False

            # create a dictionary for JSON response
            response_dictionary = {}

            for hit in res['hits']['hits']:
                if hit['_source']['tag'] == "5" or hit['_source']['tag'] == "6" or hit['_source']['tag'] == "7":
                    if not flag:
                        average_number_of_people = float(hit['_source']['text'])
                        flag = True
                    average_number_of_people = (average_number_of_people + float(hit['_source']['text'])) / 2.0
            if average_number_of_people <= 20:
                response_dictionary["value"] = "Low"
            if 20 < average_number_of_people < 30:
                response_dictionary["value"] = "Medium"
            if average_number_of_people >= 30:
                response_dictionary["value"] = "High"
            # print("Average number of people in venues 5, 6 and 7 is : " + average_number_of_people)
            response_dictionary["average_number_of_people"] = average_number_of_people
            self.set_status(status_code=200, reason="Request successfully handled")
            end_time = datetime.now()
            json_data = {}

            json_data["service_name"] = "venue"
            json_data["instance"] = port
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            json_data["handler"] = "CheckVenueArea3"
            json_data["requestId"] = venue3_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 1000000
            print(json_data)
            es1.index(index="response_time", body=json_data)
            response_dictionary["status"] = 200
            self.write(response_dictionary)
            #self.flush()
            #self.finish()
        except Exception as e:
            response_dictionary  = {}
            end_time = datetime.now()
            json_data = {}

            json_data["service_name"] = "venue"
            json_data["instance"] = port
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            json_data["handler"] = "CheckVenueArea3"
            json_data["requestId"] = venue3_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 1000000
            print(json_data)
            es1.index(index="response_time", body=json_data)
            response_dictionary["status"] = 500
            self.write(response_dictionary)

    get = post


''' 
tornado functions for starting an endpoint for each venue
each function will have a thread running so all of them are running at the same time
'''


def server_start():
    application = tornado.web.Application(
        [(r"/CheckVenueArea3", CheckVenueArea3),
         (r"/CheckVenueArea2", CheckVenueArea2),
         (r"/CheckVenueArea1", CheckVenueArea1)])
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()



if __name__ == "__main__":
    try:
        es1 = Elasticsearch([es_host])
        es2 = Elasticsearch([es_host])
        es3 = Elasticsearch([es_host])
        print("Starting Tornado Web Server for Booking Service on " + str(port))
        # http_server = tornado.httpserver.HTTPServer(start_tornado_1())
        http_server = tornado.httpserver.HTTPServer(server_start())
        http_server.listen(port)
        tornado.ioloop.IOLoop.instance().start()
    except:
        # logger.exception( "Exception occurred when trying to start tornado on " + str(options.port))
        traceback.print_exc()
