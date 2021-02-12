
# Service discovery for east-west

# update the host in discovery_json to the respective ip address

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
import math

port = 9006
from datetime import datetime
es_host =  'localhost'

#asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())

discovery_json = {
"parking_count" : ["host.docker.internal:8891"],
"parking_reccommendation" : ["host.docker.internal:8892"],
"venue_service" : ["host.docker.internal:8889"],
"weather_service" : ["host.docker.internal:8890"],
"rfid_service" : ["host.docker.internal:8893"],
"booking_service" : ["host.docker.internal:8894"],
"camera_service" : ["host.docker.internal:8896"]
}


class FetchServiceInstance(tornado.web.RequestHandler):
    def get(self):
        # Check elasticsearch connection and loop till connected and query the database
        service_name =  self.get_argument('service_name', None)


        # define response header
        self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin', '*'))
        self.set_header('Access-Control-Allow-Methods', 'GET, POST')
        self.set_header('Content-Type', 'application/json')
        response_dictionary = {}
        #print ( res['hits']['hits'])

        response_dictionary["url_path"] = discovery_json[service_name][0]
        self.write(response_dictionary)
        self.flush()
        self.finish()


class UpdateServiceInstance(tornado.web.RequestHandler):
    def post(self):
        # Check elasticsearch connection and loop till connected and query the database
        json_string = self.request.body
        global discovery_json
        json_request_string = self.request.body
        json_object = json.loads(json_request_string)
        discovery_json = json_object
        print (discovery_json)
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
        [(r"/getServiceInstance", FetchServiceInstance),
         (r"/updateServiceInstance", UpdateServiceInstance)
         ]
    )

    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    #es1 = Elasticsearch(['localhost', '127.0.0.1', 'host.docker.internal'])
    #es2 = Elasticsearch(['localhost', '127.0.0.1', 'host.docker.internal'])
    #es3 = Elasticsearch(['localhost', '127.0.0.1', 'host.docker.internal'])
    #es = Elasticsearch([es_host], http_auth=('elastic', '#Sree@kichu143'),timeout=30, max_retries=10, retry_on_timeout=True)

    #print("Elasticsearch Started")

    try:
        print("Starting Tornado Web Server for service discovery on " + str(port))
        http_server = tornado.httpserver.HTTPServer(server_start())
        http_server.listen(port)
        tornado.ioloop.IOLoop.instance().start()
    except:
        # logger.exception( "Exception occurred when trying to start tornado on " + str(options.port))
        traceback.print_exc()
