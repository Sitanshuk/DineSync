from django.shortcuts import render
import json
from pymongo import MongoClient
from datetime import datetime
from decouple import config

uri = config('MONGODB_URL_LOCAL')
client = MongoClient(uri)

db = client.get_database('Bigdata23')
restaurants = db.restaurant


from ksql import KSQLAPI
config_overrides = {
    'auto.offset.reset': 'earliest',  # or 'latest' depending on your requirement
}
client = KSQLAPI(config('KSQL_URL'), api_key=config('KSQL_API_KEY'), secret=config('KSQL_API_SECRET'), config_overrides=config_overrides)

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
        given_latitude = request.POST.get('latitude')
        given_longitude = request.POST.get('longitude')
        result = restaurants.aggregate([
            {
                "$geoNear": {
                    "near": {"type": "Point", "coordinates": [float(given_longitude), float(given_latitude)]},
                    "distanceField": "tempDistance",
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

            if (current_datetime - window_end).total_seconds() / 60 > 120:
                availability = 100
            else:
                availability = 100 - no_of_checkins
            nearest_restaurants[rest_id]['availability'] = availability

        coordinates = {
            "latitude" : given_latitude,
            "longitude" : given_longitude
        }
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

            if (current_datetime - window_end).total_seconds() / 60 > 120:
                availability = 100
            else:
                availability = 100 - no_of_checkins
            record['availability'] = availability
        return render(request, 'interested.html', {"selected_restaurant": record})
    pass

def new_recommendations(request):
    if request.method == 'POST':
        restaurant_id = request.POST.get('restaurant_id')
        print(restaurant_id)
        old_restaurant = restaurants.find({"Id" : restaurant_id})
        old_restaurant = [r for r in old_restaurant][0]
        cuisines = old_restaurant['Cuisine']
        location = old_restaurant['location']
        result = restaurants.aggregate([
            {
                "$geoNear": {
                    "near": location,
                    "distanceField": "tempDistance",
                    "spherical": True
                }
            },
            {
                "$match": {
                    "Cuisine": {"$in": cuisines}
                }
            },
            {
                "$limit": 30  # Limit the result to the top 10 records
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

        available_restaurants = list()
        for check in latest_checkins_json[1:]:

            rest_id = check['row']['columns'][0]
            window_start = datetime.utcfromtimestamp(check['row']['columns'][1] / 1000.0)
            window_end = datetime.utcfromtimestamp(check['row']['columns'][2] / 1000.0)
            no_of_checkins = check['row']['columns'][3]

            if (current_datetime - window_end).total_seconds() / 60 > 120:
                availability = 100
            else:
                availability = 100 - no_of_checkins
            nearest_restaurants[rest_id]['availability'] = availability
            if availability > 10: #Party size
                available_restaurants.append(nearest_restaurants[rest_id])
        if len(available_restaurants) > 10:
            available_restaurants = available_restaurants[:10]
        coordinates = {
            "latitude" : location['coordinates'][1],
            "longitude" : location['coordinates'][0]
        }
        if not available_restaurants:
            nearest_restaurants = sorted(nearest_restaurants.values(), key=lambda x: x['availability'], reverse=True)
            available_restaurants = nearest_restaurants[:10]
        cuisines = restaurants.distinct('Cuisine')
        return render(request, 'new_recommendations.html',
                  {"nearest_restaurants": available_restaurants, "coordinates": coordinates, "cuisines": cuisines})

