# routing.py

from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from webapp.consumer import YourConsumer
from django.urls import re_path

application = ProtocolTypeRouter({
    "websocket": URLRouter([
        path("ws/live_updates/", YourConsumer.as_asgi()),
    ]),
})

websocket_urlpatterns = [
    re_path(r"ws/live_updates/$", YourConsumer.as_asgi()),
]