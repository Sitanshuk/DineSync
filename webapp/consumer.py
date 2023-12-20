# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from ksql import KSQLAPI
from datetime import datetime
from decouple import config

config_overrides = {
    'auto.offset.reset': 'earliest',  # or 'latest' depending on your requirement
}
client = KSQLAPI(config('KSQL_URL'), api_key=config('KSQL_API_KEY'), secret=config('KSQL_API_SECRET'), config_overrides=config_overrides)

class YourConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.websocket_state = 'CONNECTED'

    async def disconnect(self, close_code):
        # Optionally, remove from group if used
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        restaurant_id = data['restaurant_id']
        print('RECEIVED',restaurant_id)

        # Fetch data and send it back to the client
        # while self.websocket_state == 'CONNECTED':
        try:
            current_datetime = datetime.now()
            query = client.query(f"SELECT * FROM AGG_CHECKINS WHERE RESTAURANT_ID = '{restaurant_id}'")
            json_sr = ''
            try:
                for check in query:
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
                await self.send(text_data=json.dumps({"availability" :  availability}))
        except Exception as e:
            print(e)

