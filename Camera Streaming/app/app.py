import asyncio
import threading
import time
import tornado.ioloop
import tornado.web
import tornado.httpserver
import traceback
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
from elasticsearch import Elasticsearch
import os
# for endless loops inside created threads
asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
port = int(os.environ['PORT_NUM'])

from datetime import datetime
es_host =  str(os.environ['ES_HOST'])

venue1_cam_counter = 0
venue2_cam_counter = 0
venue3_cam_counter  = 0


class Camera1(tornado.web.RequestHandler):
    def post(self):
        # Check elasticsearch connection and loop till connected and query the database
        global venue1_cam_counter
        venue1_cam_counter += 1
        start_time = datetime.now()
        try:
            while not es1.ping:
                print("establishing connection ...")
            # DSL query
            search_param = {
                "query": {
                    "terms": {
                        "tag": ["1", "2"]
                    }
                }
            }
            res = es1.search(index="camera_frames", body=search_param, size=200)

            # define response header
            self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin', '*'))
            self.set_header('Access-Control-Allow-Methods', 'GET, POST')
            self.set_header('Content-Type', 'application/json')

            # we calculate the average number of people in a venue
            average_number_of_people = 0
            average_number_of_people_venue2 = 0
            # flag to check first result to calculate correctly average_number_of_people
            flag1 = False
            flag2 = False

            # create a dictionary for JSON response
            response_dictionary = {}

            for hit in res['hits']['hits']:
                if hit['_source']['tag'] == "1":
                    if not flag1:
                        average_number_of_people = float(hit['_source']['text'])
                        flag1 = True
                    average_number_of_people = (average_number_of_people + float(
                        hit['_source']['text'])) / 2.0
                if hit['_source']['tag'] == "2":
                    if not flag2:
                        average_number_of_people_venue2 = float(hit['_source']['text'])
                        flag2 = True
                    average_number_of_people_venue2 = (average_number_of_people_venue2 + float(
                        hit['_source']['text'])) / 2.0

            # we calculate the average number of people inside
            # the new number of people entering = people entering - people leaving
            # ( if the value is - then the venue got less people inside )
            response_dictionary["Venue 1 Percentage"] = average_number_of_people

            if average_number_of_people < 30:
                response_dictionary["Crowd Venue 1"] = "Low"
            if 30 <= average_number_of_people <= 60:
                response_dictionary["Crowd Venue 1"] = "Medium"
            if average_number_of_people > 60:
                response_dictionary["Crowd Venue 1"] = "High"

            response_dictionary["Venue 2 Percentage"] = average_number_of_people_venue2

            if average_number_of_people_venue2 < 30:
                response_dictionary["Crowd Venue 2"] = "Low"
            if 30 <= average_number_of_people_venue2 <= 60:
                response_dictionary["Crowd Venue 2"] = "Medium"
            if average_number_of_people_venue2 > 60:
                response_dictionary["Crowd Venue 2"] = "High"

            self.set_status(status_code=200, reason="Request successfully handled")

            end_time = datetime.now()
            json_data = {}

            json_data["service_name"] = "camera"
            json_data["instance"] = port
            json_data["handler"] = "checkCamera1"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = venue1_cam_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 100000
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
            response_dictionary["status"] = 500
            json_data["service_name"] = "camera"
            json_data["instance"] = port
            json_data["handler"] = "checkCamera1"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = venue1_cam_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 100000
            print(json_data)
            es1.index(index="response_time", body=json_data)
            self.write(response_dictionary)


    get = post


class Camera2(tornado.web.RequestHandler):
    def post(self):
        # Check elasticsearch connection and loop till connected and query the database
        start_time = datetime.now()
        global venue2_cam_counter
        venue2_cam_counter += 1
        try:

            while not es3.ping:
                print("establishing connection ...")
            # DSL query
            search_param = {
                "query": {
                    "terms": {
                        "tag": ["3", "4"]
                    }
                }
            }
            res = es2.search(index="camera_frames", body=search_param, size=200)

            # define response header
            self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin', '*'))
            self.set_header('Access-Control-Allow-Methods', 'GET, POST')
            self.set_header('Content-Type', 'application/json')

            # we calculate the average number of people in a venue
            average_number_of_people = 0
            average_number_of_people_venue2 = 0
            # flag to check first result to calculate correctly average_number_of_people
            flag1 = False
            flag2 = False

            # create a dictionary for JSON response
            response_dictionary = {}

            for hit in res['hits']['hits']:
                if hit['_source']['tag'] == "3":
                    if not flag1:
                        average_number_of_people = float(hit['_source']['text'])
                        flag1 = True
                    average_number_of_people = (average_number_of_people + float(hit['_source']['text'])) / 2.0
                if hit['_source']['tag'] == "4":
                    if not flag2:
                        average_number_of_people_venue2 = float(hit['_source']['text'])
                        flag2 = True
                    average_number_of_people_venue2 = (average_number_of_people_venue2 + float(
                        hit['_source']['text'])) / 2.0

            # we calculate the average number of people inside
            # the new number of people entering = people entering - people leaving
            # ( if the value is - then the venue got less people inside )
            response_dictionary["Venue 3 Percentage"] = average_number_of_people

            if average_number_of_people < 30:
                response_dictionary["Crowd Venue 3"] = "Low"
            if 30 <= average_number_of_people <= 60:
                response_dictionary["Crowd Venue 3"] = "Medium"
            if average_number_of_people > 60:
                response_dictionary["Crowd Venue 3"] = "High"

            response_dictionary["Venue 4 Percentage"] = average_number_of_people_venue2

            if average_number_of_people_venue2 < 30:
                response_dictionary["Crowd Venue 4"] = "Low"
            if 30 <= average_number_of_people_venue2 <= 60:
                response_dictionary["Crowd Venue 4"] = "Medium"
            if average_number_of_people_venue2 > 60:
                response_dictionary["Crowd Venue 4"] = "High"

            self.set_status(status_code=200, reason="Request successfully handled")

            end_time = datetime.now()
            json_data = {}

            json_data["service_name"] = "camera"
            json_data["instance"] = port
            json_data["handler"] = "checkCamera2"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = venue2_cam_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 100000
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
            json_data["service_name"] = "camera"
            json_data["instance"] = port
            json_data["handler"] = "checkCamera2"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = venue2_cam_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 100000
            print(json_data)
            es1.index(index="response_time", body=json_data)
            response_dictionary["status"] = 500
            self.write(response_dictionary)

    get = post


class Camera3(tornado.web.RequestHandler):
    def post(self):
        # Check elasticsearch connection and loop till connected and query the database
        start_time = datetime.now()
        global venue3_cam_counter
        venue3_cam_counter += 1

        try:
            while not es3.ping:
                print("establishing connection ...")
            # DSL query
            search_param = {
                "query": {
                    "terms": {
                        "tag": ["5", "6"]
                    }
                }
            }
            res = es2.search(index="camera_frames", body=search_param, size=200)

            # define response header
            self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin', '*'))
            self.set_header('Access-Control-Allow-Methods', 'GET, POST')
            self.set_header('Content-Type', 'application/json')

            # we calculate the average number of people in a venue
            average_number_of_people = 0
            average_number_of_people_venue2 = 0
            # flag to check first result to calculate correctly average_number_of_people
            flag1 = False
            flag2 = False

            # create a dictionary for JSON response
            response_dictionary = {}

            for hit in res['hits']['hits']:
                if hit['_source']['tag'] == "5":
                    if not flag1:
                        average_number_of_people = float(hit['_source']['text'])
                        flag1 = True
                    average_number_of_people = (average_number_of_people + float(hit['_source']['text'])) / 2.0
                if hit['_source']['tag'] == "6":
                    if not flag2:
                        average_number_of_people_venue2 = float(hit['_source']['text'])
                        flag2 = True
                    average_number_of_people_venue2 = (average_number_of_people_venue2 + float(hit['_source']['text'])) / 2.0

            # we calculate the average number of people inside
            # the new number of people entering = people entering - people leaving
            # ( if the value is - then the venue got less people inside )
            response_dictionary["Venue 5 Percentage"] = average_number_of_people

            if average_number_of_people < 30:
                response_dictionary["Crowd Venue 5"] = "Low"
            if 30 <= average_number_of_people <= 60:
                response_dictionary["Crowd Venue 5"] = "Medium"
            if average_number_of_people > 60:
                response_dictionary["Crowd Venue 5"] = "High"

            response_dictionary["Venue 6 Percentage"] = average_number_of_people_venue2

            if average_number_of_people_venue2 < 30:
                response_dictionary["Crowd Venue 6"] = "Low"
            if 30 <= average_number_of_people_venue2 <= 60:
                response_dictionary["Crowd Venue 6"] = "Medium"
            if average_number_of_people_venue2 > 60:
                response_dictionary["Crowd Venue 6"] = "High"

            self.set_status(status_code=200, reason="Request successfully handled")

            end_time = datetime.now()
            json_data = {}

            json_data["service_name"] = "camera"
            json_data["instance"] = port
            json_data["handler"] = "checkCamera3"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = venue3_cam_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 100000
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
            json_data["service_name"] = "camera"
            json_data["instance"] = port
            json_data["handler"] = "checkCamera3"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = venue3_cam_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 100000
            print(json_data)
            es1.index(index="response_time", body=json_data)
            response_dictionary["status"] = 500
            self.write(response_dictionary)

    get = post


''' 
tornado functions for starting an endpoint for each venue
each function will have a thread running so all of them are running at the same time
'''


def start_tornado_1():
    application = tornado.web.Application(
        [(r"/CheckCamera1", Camera1)
        ,(r"/CheckCamera2", Camera2),
         (r"/CheckCamera3", Camera3)])
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    try:
        es1 = Elasticsearch([es_host])
        es2 = Elasticsearch([es_host])
        es3 = Elasticsearch([es_host])
        print("Starting Tornado Web Server for Booking Service on " + str(port))
        #http_server = tornado.httpserver.HTTPServer(start_tornado_1())
        http_server = tornado.httpserver.HTTPServer(start_tornado_1())
        http_server.listen(port)
        tornado.ioloop.IOLoop.instance().start()
    except:
        # logger.exception( "Exception occurred when trying to start tornado on " + str(options.port))
        traceback.print_exc()

