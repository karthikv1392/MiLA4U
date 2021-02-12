import asyncio
import threading
import time
import tornado.ioloop
import tornado.web
import requests
import tornado.httpserver
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
from elasticsearch import Elasticsearch
from datetime import datetime
import traceback
import os
import random
# for endless loops inside created threads


service_composer = 9006
port = int(os.environ['PORT_NUM'])
es_host =  str(os.environ['ES_HOST'])
reccommend_counter = 0

class RecomendParking(tornado.web.RequestHandler):
    def post(self):
        start_time = datetime.now()
        global reccommend_counter
        reccommend_counter+=1
        try:
            sd_url_list = ['http://host.docker.internal:9006','http://host.docker.internal:9006']
            sd_instance_id = random.randint(0,1)
            url_path_response = requests.get(sd_url_list[sd_instance_id]+ '/getServiceInstance?service_name=parking_count')
            #print (url_path_response.json())
            url_path = url_path_response.json()["url_path"]

            response = requests.get(
                'http://' + url_path + '/CheckCarMats1')
            response2 = requests.get(
                'http://' + url_path + '/CheckCarMats2')
            response3 = requests.get(
                'http://' + url_path + '/CheckCarMats3')
            parking_mat_1 = response.json()
            parking_mat_2 = response2.json()
            parking_mat_3 = response3.json()

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

            if parking_mat_1['value'] < parking_mat_2['value'] and parking_mat_1['value'] < parking_mat_3['value']:
                print(parking_mat_1['value'])
            elif parking_mat_2['value'] > parking_mat_1['value'] and parking_mat_2['value'] > parking_mat_3['value']:
                print(parking_mat_2['value'])
            else:
                print(parking_mat_3['value'])
            self.set_status(status_code=200, reason="Request successfully handled")
            end_time = datetime.now()
            json_data = {}

            json_data["service_name"] = "parking_reccommendation"
            json_data["instance"] = port
            json_data["handler"] = "recommendParking"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = reccommend_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 1000000
            print (json_data)
            es1.index(index="response_time", body=json_data)
            self.write(parking_mat_1)
            self.write(parking_mat_2)
            self.write(parking_mat_3)
            #self.flush()
            #self.finish()
        except Exception as e:
            end_time = datetime.now()
            json_data = {}
            response_dictionary = {}

            json_data["service_name"] = "parking_reccommendation"
            json_data["instance"] = port
            json_data["handler"] = "recommendParking"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = reccommend_counter
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


def start_tornado():
    application = tornado.web.Application(
        [(r"/recomendParking", RecomendParking)])
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    try:
        es1 = Elasticsearch([es_host])

        print("Starting Tornado Web Server for parking recommendation on " + str(port))
        # http_server = tornado.httpserver.HTTPServer(start_tornado_1())
        http_server = tornado.httpserver.HTTPServer(start_tornado())
        http_server.listen(port)
        tornado.ioloop.IOLoop.instance().start()
    except:
        # logger.exception( "Exception occurred when trying to start tornado on " + str(options.port))
        traceback.print_exc()
