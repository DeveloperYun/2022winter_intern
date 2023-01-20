from django.urls import path
from .views import GraphConsumer

ws_urlpatterns = [
    path('ws/control/', GraphConsumer.as_asgi()),
]