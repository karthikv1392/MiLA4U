import asyncio
import threading
import time
import requests
import tornado.ioloop
import tornado.web
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
from datetime import datetime
from elasticsearch import Elasticsearch
import time
import os

port = int(os.environ['PORT_NUM'])
request_counter = 0
# for endless loops inside created threads
asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
es_host = str(os.environ['ES_HOST'])

es = Elasticsearch([es_host])


class CheckWeatherStatus(tornado.web.RequestHandler):
    def post(self):
        global request_counter
        start_time = datetime.now()
        request_counter +=1
        try:
            response = requests.get(
                'http://api.openweathermap.org/data/2.5/forecast/?id=6541999&units=metric&APPID=2dae9207bdd3b385febd446f264d555b')
            weather_now = response.json()
            # define response header
            self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin', '*'))
            self.set_header('Access-Control-Allow-Methods', 'GET, POST')
            self.set_header('Content-Type', 'application/json')
            self.set_status(status_code=200, reason="Request successfully handled")
            #for weather_hour in weather_now['list']:
            #    print(weather_hour['weather'][0]['main'] + "  " + weather_hour['dt_txt'])
            end_time = datetime.now()
            json_data = {}

            json_data["service_name"] = "weather"
            json_data["instance"] = port
            json_data["handler"] = "getWeather"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = request_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 1000000
            print(json_data)
            es.index(index="response_time", body=json_data)
            weather_now["status"] = 200
            self.write(weather_now)
            #self.flush()
            #self.finish()
            #for weather_hour in weather_now['list']:
            #    print(weather_hour['weather'][0]['main'] + "  " + weather_hour['dt_txt'])
        except Exception as e:
            end_time = datetime.now()
            json_data = {}
            weather_now = {}
            json_data["service_name"] = "weather"
            json_data["instance"] = port
            json_data["handler"] = "getWeather"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = request_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 1000000
            #print(json_data)
            es.index(index="response_time", body=json_data)
            #time.sleep(0.2)
            weather_now["status"] = 500
            self.write(weather_now)


    get = post


''' 
tornado functions for starting an endpoint for each venue
each function will have a thread running so all of them are running at the same time
'''


def start_tornado_1():
    application = tornado.web.Application([(r"/getWeather", CheckWeatherStatus)])
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    try:
        print("Starting Tornado Web Server for weather service on " + str(port))
        # http_server = tornado.httpserver.HTTPServer(start_tornado_1())
        http_server = tornado.httpserver.HTTPServer(start_tornado_1())
        http_server.listen(port)
        tornado.ioloop.IOLoop.instance().start()
    except:
        # logger.exception( "Exception occurred when trying to start tornado on " + str(options.port))
        traceback.print_exc()
