import asyncio
import threading
import time
import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
from elasticsearch import Elasticsearch
from datetime import datetime
import traceback
import os

# for endless loops inside created threads


port = int(os.environ['PORT_NUM'])
es_host = str(os.environ['ES_HOST'])
rfid1_counter = 0
rfid2_counter = 0
rfid3_counter = 0

class CheckRFID1(tornado.web.RequestHandler):
    def post(self):
        # Check elasticsearch connection and loop till connected and query the database
        global rfid1_counter
        start_time = datetime.now()
        rfid1_counter+=1
        try:
            while not es1.ping:
                print("establishing connection ...")
            # DSL query
            search_param = {
                "query": {
                    "terms": {
                        "tag": ["1_leave ", "1_enter", "2_enter", "2_leave"]
                    }
                }
            }
            res = es1.search(index="rfid_data", body=search_param, size=200)

            # define response header
            self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin', '*'))
            self.set_header('Access-Control-Allow-Methods', 'GET, POST')
            self.set_header('Content-Type', 'application/json')

            # we calculate the average number of cars entering a parking
            average_number_of_people_entering_1 = 0
            average_number_of_people_leaving_1 = 0
            average_number_of_people_entering_2 = 0
            average_number_of_people_leaving_2 = 0

            # flag to check first result to calculate correctly average_number_of_people
            flag1 = False
            flag2 = False
            flag3 = False
            flag4 = False

            # create a dictionary for JSON response
            response_dictionary = {}

            for hit in res['hits']['hits']:
                if hit['_source']['tag'] == "1_enter":
                    if not flag1:
                        number_of_people_entering_1 = float(hit['_source']['text'])
                        flag1 = True
                    average_number_of_people_entering_1 = (number_of_people_entering_1 + float(
                        hit['_source']['text'])) / 2.0
                if hit['_source']['tag'] == "1_leave":
                    if not flag2:
                        number_of_people_leaving_1 = float(hit['_source']['text'])
                        flag2 = True
                    average_number_of_people_leaving_1 = (number_of_people_leaving_1 + float(hit['_source']['text'])) / 2.0
                if hit['_source']['tag'] == "2_enter":
                    if not flag3:
                        number_of_people_entering_2 = float(hit['_source']['text'])
                        flag3 = True
                    average_number_of_people_entering_2 = (number_of_people_entering_2 + float(
                        hit['_source']['text'])) / 2.0
                if hit['_source']['tag'] == "2_leave":
                    if not flag4:
                        number_of_people_leaving_2 = float(hit['_source']['text'])
                        flag4 = True
                    average_number_of_people_leaving_2 = (number_of_people_leaving_2 + float(hit['_source']['text'])) / 2.0

            # we calculate the average number of people inside
            # the new number of people entering = people entering - people leaving
            # ( if the value is - then the venue got less people inside )
            average_number_of_people_inside_venue_1 = average_number_of_people_entering_1 - average_number_of_people_leaving_1
            average_number_of_people_inside_venue_2 = average_number_of_people_entering_2 - average_number_of_people_leaving_2

            if average_number_of_people_inside_venue_1 < 0:
                response_dictionary["crowd_venue1"] = "decreased"
            if average_number_of_people_inside_venue_1 > 0:
                response_dictionary["crowd_venue1"] = "increased"
            if average_number_of_people_inside_venue_1 == 0:
                response_dictionary["crowd_venue1"] = "no_change"

            if average_number_of_people_inside_venue_2 < 0:
                response_dictionary["crowd_venue2"] = "decreased"
            if average_number_of_people_inside_venue_2 > 0:
                response_dictionary["crowd_venue2"] = "increased"
            if average_number_of_people_inside_venue_2 == 0:
                response_dictionary["crowd_venue2"] = "no_change"

            response_dictionary["number of people entering venue 1"] = average_number_of_people_inside_venue_1
            response_dictionary["number of people entering venue 2"] = average_number_of_people_inside_venue_2

            self.set_status(status_code=200, reason="Request successfully handled")
            end_time = datetime.now()

            json_data = {}

            json_data["service_name"] = "rfid"
            json_data["instance"] = port
            json_data["handler"] = "CheckRFID1"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = rfid1_counter
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
            json_data["service_name"] = "rfid"
            json_data["instance"] = port
            json_data["handler"] = "CheckRFID1"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = rfid1_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 1000000
            print(json_data)
            es1.index(index="response_time", body=json_data)
            response_dictionary["status"] = 500
            self.write(response_dictionary)

    get = post


class CheckRFID2(tornado.web.RequestHandler):
    def post(self):
        global rfid2_counter
        start_time = datetime.now()
        rfid2_counter+=1
        # Check elasticsearch connection and loop till connected and query the database
        try:
            while not es2.ping:
                print("establishing connection ...")
            # DSL query
            search_param = {
                "query": {
                    "terms": {
                        "tag": ["3_leave ", "3_enter", "4_enter", "4_leave"]
                    }
                }
            }
            res = es2.search(index="rfid_data", body=search_param, size=200)

            # define response header
            self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin', '*'))
            self.set_header('Access-Control-Allow-Methods', 'GET, POST')
            self.set_header('Content-Type', 'application/json')

            # we calculate the average number of cars entering a parking
            average_number_of_people_entering_3 = 0
            average_number_of_people_leaving_3 = 0
            average_number_of_people_entering_4 = 0
            average_number_of_people_leaving_4 = 0

            # flag to check first result to calculate correctly average_number_of_people
            flag1 = False
            flag2 = False
            flag3 = False
            flag4 = False

            # create a dictionary for JSON response
            response_dictionary = {}

            for hit in res['hits']['hits']:
                if hit['_source']['tag'] == "3_enter":
                    if not flag1:
                        number_of_people_entering_3 = float(hit['_source']['text'])
                        flag1 = True
                    average_number_of_people_entering_3 = (number_of_people_entering_3 + float(hit['_source']['text'])) / 2.0
                if hit['_source']['tag'] == "3_leave":
                    if not flag2:
                        number_of_people_leaving_3 = float(hit['_source']['text'])
                        flag2 = True
                    average_number_of_people_leaving_3 = (number_of_people_leaving_3 + float(hit['_source']['text'])) / 2.0
                if hit['_source']['tag'] == "4_enter":
                    if not flag3:
                        number_of_people_entering_4 = float(hit['_source']['text'])
                        flag3 = True
                    average_number_of_people_entering_4 = (number_of_people_entering_4 + float(hit['_source']['text'])) / 2.0
                if hit['_source']['tag'] == "2_leave":
                    if not flag4:
                        number_of_people_leaving_4 = float(hit['_source']['text'])
                        flag4 = True
                    average_number_of_people_leaving_4 = (number_of_people_leaving_4 + float(hit['_source']['text'])) / 2.0

            # we calculate the average number of people inside
            # the new number of people entering = people entering - people leaving
            # ( if the value is - then the venue got less people inside )
            average_number_of_people_inside_venue_3 = average_number_of_people_entering_3 - average_number_of_people_leaving_3
            average_number_of_people_inside_venue_4 = average_number_of_people_entering_4 - average_number_of_people_leaving_4

            if average_number_of_people_inside_venue_3 < 0:
                response_dictionary["crowd_venue3"] = "decreased"
            if average_number_of_people_inside_venue_3 > 0:
                response_dictionary["crowd_venue3"] = "increased"
            if average_number_of_people_inside_venue_3 == 0:
                response_dictionary["crowd_venue3"] = "no_change"

            if average_number_of_people_inside_venue_4 < 0:
                response_dictionary["crowd_venue4"] = "decreased"
            if average_number_of_people_inside_venue_4 > 0:
                response_dictionary["crowd_venue4"] = "increased"
            if average_number_of_people_inside_venue_4 == 0:
                response_dictionary["crowd_venue4"] = "no_change"

            response_dictionary["number of people entering venue 3"] = average_number_of_people_inside_venue_3
            response_dictionary["number of people entering venue 4"] = average_number_of_people_inside_venue_4

            self.set_status(status_code=200, reason="Request successfully handled")
            end_time = datetime.now()

            json_data = {}

            json_data["service_name"] = "rfid"
            json_data["instance"] = port
            json_data["handler"] = "CheckRFID2"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = rfid2_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 1000000
            print(json_data)
            es2.index(index="response_time", body=json_data)
            response_dictionary["status"] = 200
            self.write(response_dictionary)
            #self.flush()
            #self.finish()
        except Exception as e:
            end_time = datetime.now()
            response_dictionary = {}
            json_data = {}

            json_data["service_name"] = "rfid"
            json_data["instance"] = port
            json_data["handler"] = "CheckRFID2"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = rfid2_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 1000000
            print(json_data)
            es2.index(index="response_time", body=json_data)
            response_dictionary["status"] = 500
            self.write(response_dictionary)

    get = post


class CheckRFID3(tornado.web.RequestHandler):
    def post(self):
        global rfid3_counter
        start_time =datetime.now()

        rfid3_counter+=1
        # Check elasticsearch connection and loop till connected and query the database
        try:
            while not es3.ping:
                print("establishing connection ...")
            # DSL query
            search_param = {
                "query": {
                    "terms": {
                        "tag": ["5_leave ", "5_enter", "6_enter", "6_leave", "7_enter", "7_leave"]
                    }
                }
            }
            res = es3.search(index="rfid_data", body=search_param, size=200)

            # define response header
            self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin', '*'))
            self.set_header('Access-Control-Allow-Methods', 'GET, POST')
            self.set_header('Content-Type', 'application/json')

            # we calculate the average number of cars entering a parking
            average_number_of_people_entering_5 = 0
            average_number_of_people_leaving_5 = 0
            average_number_of_people_entering_6 = 0
            average_number_of_people_leaving_6 = 0
            average_number_of_people_entering_7 = 0
            average_number_of_people_leaving_7 = 0

            # flag to check first result to calculate correctly average_number_of_people
            flag1 = False
            flag2 = False
            flag3 = False
            flag4 = False
            flag5 = False
            flag6 = False

            # create a dictionary for JSON response
            response_dictionary = {}

            for hit in res['hits']['hits']:
                print(hit['_source']['tag'])
                if hit['_source']['tag'] == "5_enter":
                    if not flag1:
                        number_of_people_entering_5 = float(hit['_source']['text'])
                        flag1 = True
                    average_number_of_people_entering_5 = (number_of_people_entering_5 + float(
                        hit['_source']['text'])) / 2.0
                if hit['_source']['tag'] == "5_leave":
                    if not flag2:
                        number_of_people_leaving_5 = float(hit['_source']['text'])
                        flag2 = True
                    average_number_of_people_leaving_5 = (number_of_people_leaving_5 + float(hit['_source']['text'])) / 2.0
                if hit['_source']['tag'] == "6_enter":
                    if not flag3:
                        number_of_people_entering_6 = float(hit['_source']['text'])
                        flag3 = True
                    average_number_of_people_entering_6 = (number_of_people_entering_6 + float(
                        hit['_source']['text'])) / 2.0
                if hit['_source']['tag'] == "6_leave":
                    if not flag4:
                        number_of_people_leaving_6 = float(hit['_source']['text'])
                        flag4 = True
                    average_number_of_people_leaving_6 = (number_of_people_leaving_6 + float(hit['_source']['text'])) / 2.0
                if hit['_source']['tag'] == "7_enter":
                    if not flag5:
                        number_of_people_entering_7 = float(hit['_source']['text'])
                        flag3 = True
                    average_number_of_people_entering_7 = (number_of_people_entering_7 + float(
                        hit['_source']['text'])) / 2.0
                if hit['_source']['tag'] == "7_leave":
                    if not flag6:
                        number_of_people_leaving_7 = float(hit['_source']['text'])
                        flag4 = True
                    average_number_of_people_leaving_7 = (number_of_people_leaving_7 + float(hit['_source']['text'])) / 2.0

            # we calculate the average number of people inside
            # the new number of people entering = people entering - people leaving
            # ( if the value is - then the venue got less people inside )
            average_number_of_people_inside_venue_5 = average_number_of_people_entering_5 - average_number_of_people_leaving_5
            average_number_of_people_inside_venue_6 = average_number_of_people_entering_6 - average_number_of_people_leaving_6
            average_number_of_people_inside_venue_7 = average_number_of_people_entering_7 - average_number_of_people_leaving_7

            if average_number_of_people_inside_venue_5 < 0:
                response_dictionary["crowd_venue5"] = "decreased"
            if average_number_of_people_inside_venue_5 > 0:
                response_dictionary["crowd_venue5"] = "increased"
            if average_number_of_people_inside_venue_5 == 0:
                response_dictionary["crowd_venue5"] = "no_change"

            if average_number_of_people_inside_venue_6 < 0:
                response_dictionary["crowd_venue6"] = "decreased"
            if average_number_of_people_inside_venue_6 > 0:
                response_dictionary["crowd_venue6"] = "increased"
            if average_number_of_people_inside_venue_6 == 0:
                response_dictionary["crowd_venue6"] = "no_change"

            if average_number_of_people_inside_venue_7 < 0:
                response_dictionary["crowd_venue7"] = "decreased"
            if average_number_of_people_inside_venue_7 > 0:
                response_dictionary["crowd_venue7"] = "increased"
            if average_number_of_people_inside_venue_7 == 0:
                response_dictionary["crowd_venue7"] = "no_change"

            response_dictionary["number of people entering venue 5"] = average_number_of_people_inside_venue_5
            response_dictionary["number of people entering venue 6"] = average_number_of_people_inside_venue_6
            response_dictionary["number of people entering venue 7"] = average_number_of_people_inside_venue_7

            self.set_status(status_code=200, reason="Request successfully handled")
            end_time = datetime.now()

            json_data = {}

            json_data["service_name"] = "rfid"
            json_data["instance"] = port
            json_data["handler"] = "CheckRFID3"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = rfid3_counter
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

            json_data["service_name"] = "rfid"
            json_data["instance"] = port
            json_data["handler"] = "CheckRFID3"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = rfid3_counter
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


def start_tornado_1():
    application = tornado.web.Application(
        [(r"/CheckRFID1", CheckRFID1)
        ,(r"/CheckRFID2", CheckRFID2),
         (r"/CheckRFID3", CheckRFID3)])
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    try:
        es1 = Elasticsearch([es_host])
        es2 = Elasticsearch([es_host])
        es3 = Elasticsearch([es_host])
        print("Starting Tornado Web Server for RFID reading on " + str(port))
        # http_server = tornado.httpserver.HTTPServer(start_tornado_1())
        http_server = tornado.httpserver.HTTPServer(start_tornado_1())
        http_server.listen(port)
        tornado.ioloop.IOLoop.instance().start()
    except:
        # logger.exception( "Exception occurred when trying to start tornado on " + str(options.port))
        traceback.print_exc()
