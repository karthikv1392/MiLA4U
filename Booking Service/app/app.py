import asyncio
import threading
import time
import tornado.ioloop
import tornado.web
from elasticsearch import Elasticsearch
from fpdf import FPDF
import tornado.httpserver
from datetime import datetime
import json
import requests
import traceback
import os
import random

port = int(os.environ['PORT_NUM'])
es_host1 =  str(os.environ['ES_HOST'])
es_host2 = es_host1


booking_counter = 0
available_counter = 0

class CustomPDF(FPDF):
    def header(self):
        # Set up a logo
        self.image("Icons/logo.png", 10, 8, 33)
        self.set_font('Arial', 'B', 15)

        # Add an address
        self.cell(100)
        self.cell(0, 5, 'XYZ Fair ', ln=1)
        self.cell(100)
        self.cell(0, 5, 'Sponsored By:', ln=1)
        self.cell(100)
        self.cell(0, 5, 'ABC university', ln=1)

        # Line break
        self.ln(20)

    def footer(self):
        self.set_y(-10)

        self.set_font('Arial', 'I', 8)

        # Add a page number
        page = 'Page ' + str(self.page_no()) + '/{nb}'
        self.cell(0, 10, page, 0, 0, 'C')


def create_booking(pdf_path, username, venueNumber):
    pdf = CustomPDF()
    # Create the special value {nb}
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Times', '', 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, txt="User: " + username, ln=1)
    pdf.cell(0, 10, txt="Venue: " + str(venueNumber), ln=2)
    pdf.set_text_color(255, 80, 80)
    pdf.cell(0, 10, txt="Date and Time: " + str(datetime.now()), ln=3)
    pdf.set_text_color(0, 155, 0)
    pdf.cell(0, 10, txt="Thank you very much for your participation and we hope you enjoy your time", ln=4)
    pdf.output(pdf_path)


class RequestBooking(tornado.web.RequestHandler):
    def post(self):
        start_time = datetime.now()
        global booking_counter
        try:

            booking_counter+=1
            json_request_string = self.request.body
            json_object = json.loads(json_request_string)
            username = json_object["username"]

            venueNumber = json_object["venue_number"]

            # Check if the venue has availability using rfid and venue count values
            sd_url_list = ['http://host.docker.internal:9006', 'http://host.docker.internal:9006']
            sd_instance_id = random.randint(0, 1)
            url_path_response_venue = requests.get(sd_url_list[sd_instance_id] + '/getServiceInstance?service_name=venue_service')
            # print (url_path_response.json())
            url_path_venue = url_path_response_venue.json()["url_path"]
            url_path_response_rfid = requests.get(sd_url_list[sd_instance_id] + '/getServiceInstance?service_name=rfid_service')
            url_path_rfid =  url_path_response_rfid.json()["url_path"]

            if venueNumber == 1:
                response1 = requests.get(
                'http://' + url_path_venue + '/CheckVenueArea1')
                response2 = requests.get(
                'http://' + url_path_rfid + '/CheckRFID1')

            elif venueNumber == 2:
                response1 = requests.get(
                    'http://' + url_path_venue + '/CheckVenueArea2')
                response2 = requests.get(
                    'http://' + url_path_rfid + '/CheckRFID2')

            if venueNumber == 3:
                response1 = requests.get(
                    'http://' + url_path_venue + '/CheckVenueArea3')
                response2 = requests.get(
                    'http://' + url_path_rfid + '/CheckRFID3')

            venue_count = response1.json()
            rfid_count  = response2.json()

            #print(username)
            doc = {
                'username': username,
                'venue': venueNumber,
                'date': datetime.now(),
                'timestamp': time.time(),
            }
            res = es.index(index="booking", body=doc)
            print(res['result'])
            print(res['_id'])

            # save the pdf with name .pdf
            #create_booking('bookings/' + res['_id'] + '.pdf', username, venueNumber)
            create_booking('bookings/' + "sample" + '.pdf', username, venueNumber)

            # define response header
            self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin', '*'))
            self.set_header('Access-Control-Allow-Methods', 'GET, POST')
            self.set_header('Content-Type', 'application/json')
            self.set_status(status_code=200, reason="Request successfully handled")
            end_time = datetime.now()
            json_data = {}

            json_data["service_name"] = "booking"
            json_data["instance"] = port
            json_data["handler"] = "requestBooking"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = booking_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 100000
            print(json_data)
            es.index(index="response_time", body=json_data)
            self.write("booking creation successful")
            #self.flush()
            #self.finish()

        except Exception as e:
            end_time = datetime.now()
            json_data = {}

            json_data["service_name"] = "booking"
            json_data["instance"] = port
            json_data["handler"] = "requestBooking"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = booking_counter
            json_data["latency"] = ((end_time - start_time).microseconds) / 100000
            print(json_data)
            es.index(index="response_time", body=json_data)
            self.write("error")

    get = post


class CheckAvailableBooking(tornado.web.RequestHandler):
    def post(self):
        start_time = datetime.now()
        global available_counter
        try:
            available_counter += 1
            while not es.ping:
                print("establishing connection ...")
                # DSL query
            search_param = {
                "query": {
                    "match_all": {
                    }
                }
            }
            res = es.search(index="booking", body=search_param, size=200)



            # define response header
            self.set_header('Access-Control-Allow-Origin', self.request.headers.get('Origin', '*'))
            self.set_header('Access-Control-Allow-Methods', 'GET, POST')
            self.set_header('Content-Type', 'application/json')
            self.set_status(status_code=200, reason="Request successfully handled")
            # create a dictionary for JSON response
            response = []
            counter = 0
            for hit in res['hits']['hits']:
                response.insert(counter, hit['_source'])
                counter += 1

            # check current status

            json_request_string = self.request.body
            json_object = json.loads(json_request_string)
            venueNumber = json_object["venue_number"]
            sd_url_list = ['http://host.docker.internal:9006', 'http://host.docker.internal:9006']
            sd_instance_id = random.randint(0, 1)
            # Check if the venue has availability using rfid and venue count values
            url_path_response_venue = requests.get( sd_url_list[sd_instance_id] +
                '/getServiceInstance?service_name=venue_service')
            # print (url_path_response.json())
            url_path_venue = url_path_response_venue.json()["url_path"]
            url_path_response_rfid = requests.get(
                sd_url_list[sd_instance_id] +'/getServiceInstance?service_name=rfid_service')
            url_path_rfid = url_path_response_rfid.json()["url_path"]

            url_path_response_camera = requests.get(
                sd_url_list[sd_instance_id] + '/getServiceInstance?service_name=camera_service')
            url_path_camera = url_path_response_rfid.json()["url_path"]


            if venueNumber == 1:
                response1 = requests.get(
                    'http://' + url_path_venue + '/CheckVenueArea1')
                response2 = requests.get(
                    'http://' + url_path_rfid + '/CheckRFID1')
                response3 = requests.get(
                    'http://' + url_path_camera + '/CheckCamera1')


            elif venueNumber == 2:
                response1 = requests.get(
                    'http://' + url_path_venue + '/CheckVenueArea2')
                response2 = requests.get(
                    'http://' + url_path_rfid + '/CheckRFID2')
                response3 = requests.get(
                    'http://' + url_path_camera + '/CheckCamera2')

            if venueNumber == 3:
                response1 = requests.get(
                    'http://' + url_path_venue + '/CheckVenueArea3')
                response2 = requests.get(
                    'http://' + url_path_rfid + '/CheckRFID3')
                response3 = requests.get(
                    'http://' + url_path_camera + '/CheckCamera3')

            venue_count = response1.json()
            rfid_count = response2.json()


            response_dictionary = {"bookings": response, "status": "success"}
            end_time = datetime.now()
            json_data = {}

            json_data["service_name"] = "booking"
            json_data["instance"] = port
            json_data["handler"] = "checkAvailablility"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = booking_counter
            json_data["latency"] = ((end_time - start_time).seconds)
            print(json_data)
            es.index(index="response_time", body=json_data)
            response_dictionary["status"] = 200
            self.write(response_dictionary)
            #self.flush()
            #self.finish()
        except Exception as e:
            response_dictionary = {}
            end_time = datetime.now()
            json_data = {}

            json_data["service_name"] = "booking"
            json_data["instance"] = port
            json_data["handler"] = "checkAvailablility"
            json_data["timestamp"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            json_data["requestId"] = booking_counter
            json_data["latency"] = ((end_time - start_time).seconds)
            print(json_data)
            es.index(index="response_time", body=json_data)
            response_dictionary["status"] = 500
            self.write(response_dictionary)
    get = post


''' 
tornado functions for starting an endpoint for each venue
each function will have a thread running so all of them are running at the same time
'''


def start_tornado_1():
    application = tornado.web.Application([(r"/checkAvailableBooking", CheckAvailableBooking),
                                           (r"/requestBooking", RequestBooking)])
    application.listen(port)

    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    try:
        es = Elasticsearch(es_host1)
        es2 = Elasticsearch(es_host2)
        print("Starting Tornado Web Server for Booking Service on " + str(port))
        #http_server = tornado.httpserver.HTTPServer(start_tornado_1())
        http_server = tornado.httpserver.HTTPServer(start_tornado_1())
        http_server.listen(port)
        tornado.ioloop.IOLoop.instance().start()
    except:
        # logger.exception( "Exception occurred when trying to start tornado on " + str(options.port))
        traceback.print_exc()

