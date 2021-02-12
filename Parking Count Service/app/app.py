import asyncio
import threading
import time
import tornado.ioloop
import tornado.web
import tornado.httpserver
from elasticsearch import Elasticsearch
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
import traceback
import os
# for endless loops inside created threads


port = int(os.environ['PORT_NUM'])
from datetime import datetime
es_host = str(os.environ['ES_HOST'])
# for endless loops inside created threads
park1_counter = 0
park2_counter = 0
park3_counter  = 0

class CheckCarMats1(tornado.web.RequestHandler):
    def post(self):
        # Check elasticsearch connection and loop till connected and query the database

        start_time = datetime.now()
        global park1_counter
        park1_counter += 1
        try:
            while not es1.ping:
                print("establishing connection ...")
            # DSL query
            search_param = {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"tag": "1"}}
                        ]
                    }
                }
            }
            res = es1.search(index="park_mats", body=search_param, size=50)

            # define response header
            self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin', '*'))
            self.set_header('Access-Control-Allow-Methods', 'GET, POST')
            self.set_header('Content-Type', 'application/json')

            # we calculate the average number of cars entering a parking
            average_number_of_cars = 0

            # flag to check first result to calculate correctly average_number_of_people
            flag = False

            # create a dictionary for JSON response
            response_dictionary = {}

            for hit in res['hits']['hits']:
                if hit['_source']['tag'] == "1":
                    if not flag:
                        average_number_of_cars = float(hit['_source']['text'])
                        flag = True
                    average_number_of_cars = (average_number_of_cars + float(hit['_source']['text'])) / 2.0
            if average_number_of_cars <= 20:
                response_dictionary["value"] = "Low"
            if 20 < average_number_of_cars < 30:
                response_dictionary["value"] = "Medium"
            if average_number_of_cars >= 30:
                response_dictionary["value"] = "High"
            response_dictionary["average_number_of_cars"] = average_number_of_cars
            self.set_status(status_code=200, reason="Request successfully handled")
            end_time = datetime.now()
            json_data = {}

            json_data["service_name"] = "parking_count"
            json_data["instance"] = port
            json_data["handler"] = "CheckCarMats1"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = park1_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 1000000
            print(json_data)
            es1.index(index="response_time", body=json_data)
            response_dictionary["status"] = 200
            self.write(response_dictionary)
            #self.flush()
            #self.finish()

        except Exception as e:
            end_time = datetime.now()
            response_dictionary = {}
            json_data = {}

            json_data["service_name"] = "parking_count"
            json_data["instance"] = port
            json_data["handler"] = "CheckCarMats1"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = park1_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 1000000
            print(json_data)
            es1.index(index="response_time", body=json_data)
            response_dictionary["status"] = 500
            self.write(response_dictionary)
    get = post


class CheckCarMats2(tornado.web.RequestHandler):
    def post(self):
        # Check elasticsearch connection and loop till connected and query the database
        start_time = datetime.now()
        global park2_counter
        park2_counter += 1
        try:
            while not es2.ping:
                print("establishing connection ...")
            # DSL query
            search_param = {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"tag": "2"}}
                        ]
                    }
                }
            }
            res = es2.search(index="park_mats", body=search_param, size=20)

            # define response header
            self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin', '*'))
            self.set_header('Access-Control-Allow-Methods', 'GET, POST')
            self.set_header('Content-Type', 'application/json')

            # we calculate the average number of cars entering a parking
            average_number_of_cars = 0

            # flag to check first result to calculate correctly average_number_of_people
            flag = False

            # create a dictionary for JSON response
            response_dictionary = {}

            for hit in res['hits']['hits']:
                if hit['_source']['tag'] == "2":
                    if not flag:
                        average_number_of_cars = float(hit['_source']['text'])
                        flag = True
                    average_number_of_cars = (average_number_of_cars + float(hit['_source']['text'])) / 2.0
            if average_number_of_cars <= 20:
                response_dictionary["value"] = "Low"
            if 20 < average_number_of_cars < 30:
                response_dictionary["value"] = "Medium"
            if average_number_of_cars >= 30:
                response_dictionary["value"] = "High"
            response_dictionary["average_number_of_cars"] = average_number_of_cars
            self.set_status(status_code=200, reason="Request successfully handled")
            end_time = datetime.now()
            json_data = {}

            json_data["service_name"] = "parking_count"
            json_data["instance"] = port
            json_data["handler"] = "CheckCarMats2"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = park2_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 1000000
            print(json_data)
            es2.index(index="response_time", body=json_data)
            response_dictionary["status"] = 200
            self.write(response_dictionary)
            #self.flush()
            #self.finish()
        except Exception as e:
            end_time = datetime.now()
            json_data = {}
            response_dictionary = {}
            json_data["service_name"] = "parking_count"
            json_data["instance"] = port
            json_data["handler"] = "CheckCarMats2"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = park2_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 1000000
            print(json_data)
            es2.index(index="response_time", body=json_data)
            response_dictionary["status"] = 500
            self.write(response_dictionary)

    get = post


class CheckCarMats3(tornado.web.RequestHandler):
    def post(self):
        # Check elasticsearch connection and loop till connected and query the database
        start_time = datetime.now()
        global park3_counter
        park3_counter += 1
        try:
            while not es3.ping:
                print("establishing connection ...")
            # DSL query
            search_param = {
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"tag": "3"}}
                        ]
                    }
                }
            }
            while True:
                try:
                    res = es3.search(index="park_mats", body=search_param, size=20)
                    break
                except ValueError:
                    print("establishing connection ...")

            # define response header
            self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin', '*'))
            self.set_header('Access-Control-Allow-Methods', 'GET, POST')
            self.set_header('Content-Type', 'application/json')

            # we calculate the average number of cars entering a parking
            average_number_of_cars = 0

            # flag to check first result to calculate correctly average_number_of_people
            flag = False

            # create a dictionary for JSON response
            response_dictionary = {}

            for hit in res['hits']['hits']:
                if hit['_source']['tag'] == "3":
                    if not flag:
                        average_number_of_cars = float(hit['_source']['text'])
                        flag = True
                    average_number_of_cars = (average_number_of_cars + float(hit['_source']['text'])) / 2.0
            if average_number_of_cars <= 20:
                response_dictionary["value"] = "Low"
            if 20 < average_number_of_cars < 30:
                response_dictionary["value"] = "Medium"
            if average_number_of_cars >= 30:
                response_dictionary["value"] = "High"
            response_dictionary["average_number_of_cars"] = average_number_of_cars
            self.set_status(status_code=200, reason="Request successfully handled")
            end_time = datetime.now()
            json_data = {}

            json_data["service_name"] = "parking_count"
            json_data["instance"] = port
            json_data["handler"] = "CheckCarMats3"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = park3_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 1000000
            print(json_data)
            es3.index(index="response_time", body=json_data)
            response_dictionary["status"] = 200
            self.write(response_dictionary)
            #self.flush()
            #self.finish()

        except Exception as e:
            end_time = datetime.now()
            json_data = {}
            response_dictionary = {}
            json_data["service_name"] = "parking_count"
            json_data["instance"] = port
            json_data["handler"] = "CheckCarMats3"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = park3_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 1000000
            print(json_data)
            es3.index(index="response_time", body=json_data)
            response_dictionary["status"] = 500
            self.write(response_dictionary)

    get = post


''' 
tornado functions for starting an endpoint for each venue
each function will have a thread running so all of them are running at the same time
'''


def start_tornado():
    application = tornado.web.Application(
            [(r"/CheckCarMats1", CheckCarMats1)
            , (r"/CheckCarMats2", CheckCarMats2),
             (r"/CheckCarMats3", CheckCarMats3)])
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    try:
        es1 = Elasticsearch([es_host])
        es2 = Elasticsearch([es_host])
        es3 = Elasticsearch([es_host])
        print("Starting Tornado Web Server for Booking Service on " + str(port))
        # http_server = tornado.httpserver.HTTPServer(start_tornado_1())
        http_server = tornado.httpserver.HTTPServer(start_tornado())
        http_server.listen(port)
        tornado.ioloop.IOLoop.instance().start()
    except:
        # logger.exception( "Exception occurred when trying to start tornado on " + str(options.port))
        traceback.print_exc()
