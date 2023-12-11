from typing import Union

from _decimal import Decimal

import certifi
from django.shortcuts import render
from django.http import JsonResponse
import json
from pymongo import MongoClient
from datetime import datetime
import time
from pymongo.server_api import ServerApi

# uri = 'mongodb+srv://sitwinbd23:OdStltpcigGglByz@bigdata-23.nafbdt6.mongodb.net/?retryWrites=true&w=majority'
uri = 'mongodb://localhost:27017/'
client = MongoClient(uri)

db = client.get_database('Bigdata23')
restaurants = db.restaurant
# Create your views here.
# def home(request):
#     return render(request, 'home.html')

from ksql import KSQLAPI
config_overrides = {
    'auto.offset.reset': 'earliest',  # or 'latest' depending on your requirement
}
client = KSQLAPI('https://pksqlc-x1m9q.us-east-1.aws.confluent.cloud:443', api_key="IV3K2EGMX5VYDGOK", secret="QAfCvTvGR7DbsxAyc2hSUWS5Z7dhIjueSnT6lIaBEcMlJsfHrlIRo6zZzIZ38yz+", config_overrides=config_overrides)

# query = client.query(f'SELECT * FROM AGG_CHECKINS_EARLIEST EMIT CHANGES')
# for item in query:
#     print(item)
from confluent_kafka import Consumer

# consumer_config = {
#     'bootstrap.servers': 'pkc-p11xm.us-east-1.aws.confluent.cloud:9092',  # Replace with your broker address
#     'group.id': 'python-consumer',
#     'auto.offset.reset': 'earliest',  # Set to 'latest' if you want to consume only new messages
#     'security.protocol': 'SASL_SSL',
#     'sasl.mechanisms': 'PLAIN',
#     'sasl.username': 'AYJRH5K3FC3NT2RK',  # Replace with your Confluent Cloud API key
#     'sasl.password': 'rUVldxt++itwJuyf8UeNmsM3i/wu+wRljks3WaKEPX5RXN9PsymPrCdaD7pA8Uct'  # Replace with your Confluent Cloud API secret
# }

# consumer = Consumer(consumer_config)
# consumer.subscribe(["pksqlc-x1m9qAGG_PART_SIZE"])
#
# avro_schema = {
#     "type": "record",
#     "name": "KsqlDataSourceSchema",
#     "namespace": "io.confluent.ksql.avro_schemas",
#     "fields": {"name": "TOTAL_PARTY_SIZE", "type": ["null", "int"]}
# }

from fastavro import schemaless_reader
from fastavro.schema import load_schema
# import fastavro
# from io import BytesIO
# # parsed_schema = load_schema(avro_schema)
# try:
#     while True:
#         msg = consumer.poll(1.0)
#         if msg is not None:
#             avro_file = BytesIO(msg.value())
#             avro_reader = fastavro.reader(avro_file)
#             for record in avro_reader:
#                 print(record)
#             # print(msg.topic(), msg.value().decode('utf-8'),msg.timestamp().decode('utf-8'))
#             # print("value = {value:12}".format(value=msg.value().decode('utf-16', 'ignore')))
#         # if msg is not None:
#         #     print("key = {key:12} value = {value:12}".format(key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))
# except KeyboardInterrupt:
#     pass
# finally:
#     consumer.close()

def home(request):

    return render(request, 'home.html')
def your_location_view(request):
    if request.method == 'POST':
        given_latitude = request.POST.get('latitude')
        given_longitude = request.POST.get('longitude')
        cuisines = restaurants.distinct('Cuisine')
        coordinates = {
            "latitude": given_latitude,
            "longitude": given_longitude
        }
        return render(request, 'home.html',
                      {"cuisines": cuisines, "coordinates": coordinates})

    pass

def location_plus_cuisine(request):
    if request.method == 'POST':
        selected_cuisines = request.POST.getlist('cuisines')
        print(selected_cuisines)
        given_latitude = request.POST.get('latitude')
        given_longitude = request.POST.get('longitude')
        print(given_latitude, given_longitude)
        # Do something with the latitude and longitude, e.g., save to the database
        result = restaurants.aggregate([
            {
                "$geoNear": {
                    "near": {"type": "Point", "coordinates": [float(given_longitude), float(given_latitude)]},
                    "distanceField": "tempDistance",
                    # "maxDistance": max_distance_meters,
                    "spherical": True
                }
            },
            {
                "$match": {
                    "Cuisine": {"$in": selected_cuisines}
                }
            },
            {
                "$limit": 10  # Limit the result to the top 10 records
            }
        ])
        nearest_restaurants = dict()
        current_datetime = datetime.now()
        for document in result:
            del document['_id']
            Id = document['Id']
            document['availability'] = 100
            nearest_restaurants[Id] = document

        restaurant_ids = [doc['Id'] for doc in nearest_restaurants.values()]
        latest_checkins = client.query(f"SELECT * FROM AGG_CHECKINS WHERE RESTAURANT_ID in {tuple(restaurant_ids)}")
        json_sr = ''
        try:
            for check in latest_checkins:
                json_sr += check
        except Exception as e:
            print(e)
        latest_checkins_json = json.loads(json_sr)
        for check in latest_checkins_json[1:]:

            rest_id = check['row']['columns'][0]
            window_start = datetime.utcfromtimestamp(check['row']['columns'][1]/1000.0)
            window_end = datetime.utcfromtimestamp(check['row']['columns'][2]/1000.0)
            no_of_checkins = check['row']['columns'][3]

            # print(rest_id, window_start, window_end, no_of_checkins)
            if (current_datetime - window_end).total_seconds() / 60 > 120:
                availability = 100
            else:
                availability = 100 - no_of_checkins
            nearest_restaurants[rest_id]['availability'] = availability

        coordinates = {
            "latitude" : given_latitude,
            "longitude" : given_longitude
        }
        # return HttpResponse(f"Received location: Latitude {latitude}, Longitude {longitude}")
    return render(request, 'home.html', {"nearest_restaurants" : nearest_restaurants.values(), "coordinates" : coordinates})

def process_selected_restaurant(request):
    if request.method == 'POST':
        restaurant_id = request.POST.get('restaurant_id')
        record = restaurants.find({"Id" : restaurant_id})
        record = [r for r in record][0]
        current_datetime = datetime.now()
        latest_checkins = client.query(f"SELECT * FROM AGG_CHECKINS WHERE RESTAURANT_ID = '{restaurant_id}'")
        json_sr = ''
        try:
            for check in latest_checkins:
                json_sr += check
        except Exception as e:
            print(e)
        latest_checkins_json = json.loads(json_sr)
        for check in latest_checkins_json[1:]:

            rest_id = check['row']['columns'][0]
            window_start = datetime.utcfromtimestamp(check['row']['columns'][1] / 1000.0)
            window_end = datetime.utcfromtimestamp(check['row']['columns'][2] / 1000.0)
            no_of_checkins = check['row']['columns'][3]

            # print(rest_id, window_start, window_end, no_of_checkins)
            if (current_datetime - window_end).total_seconds() / 60 > 120:
                availability = 100
            else:
                availability = 100 - no_of_checkins
            record['availability'] = availability
        return render(request, 'interested.html', {"selected_restaurant": record})
    pass