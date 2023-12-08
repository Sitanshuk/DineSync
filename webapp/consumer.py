# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from ksql import KSQLAPI
import asyncio
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

config_overrides = {
    'auto.offset.reset': 'earliest',  # or 'latest' depending on your requirement
}
client = KSQLAPI('https://pksqlc-x1m9q.us-east-1.aws.confluent.cloud:443', api_key="IV3K2EGMX5VYDGOK", secret="QAfCvTvGR7DbsxAyc2hSUWS5Z7dhIjueSnT6lIaBEcMlJsfHrlIRo6zZzIZ38yz+", config_overrides=config_overrides)

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

        # You can add this connection to a group based on restaurant_id if needed
        # await self.channel_layer.group_add(restaurant_id, self.channel_name)

        # Fetch data and send it back to the client
        # while self.websocket_state == 'CONNECTED':
        try:
            query = client.query(f"SELECT * FROM AGG_CHECKINS WHERE RESTAURANT_ID = '{restaurant_id}'")
            json_sr = ''
            try:
                for check in query:
                    json_sr += check
            except Exception as e:
                print(e)
            latest_checkins_json = json.loads(json_sr)
            time.sleep(10)
            for item in query:
                await self.send(text_data=json.dumps(item))
        except Exception as e:
            pass
                # print(f"Error: {e}")  # Log the error for debugging
