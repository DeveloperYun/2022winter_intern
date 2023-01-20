from django.urls import path
from . import views
from .views import main

app_name = 'control'

# 127.0.0.1:8000/control/~~~
urlpatterns = [
    path('',main),
    path('ready/',views.control_initialization, name='control_initialization'),
    path('AxmMovePos/', views.AxmMovePos, name='AxmMovePos'),
    path('AxmMoveStartPos/', views.AxmMoveStartPos, name='AxmMoveStartPos'),
    path('AxmMoveVel/', views.AxmMoveVel, name='AxmMoveVel'),
    path('HomeSearchMove/', views.HomeSearchMove, name='HomeSearchMove'),
    path('AxmMoveSStop/', views.AxmMoveSStop, name='AxmMoveSStop'),
]