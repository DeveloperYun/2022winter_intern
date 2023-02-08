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
    path('AxmMoveStartPos2/', views.AxmMoveStartPos2, name='AxmMoveStartPos2'),
    path('AxmMoveVel/', views.AxmMoveVel, name='AxmMoveVel'),
    path('AxmMoveVel2/', views.AxmMoveVel2, name='AxmMoveVel2'),
    path('HomeSearchMove/', views.HomeSearchMove, name='HomeSearchMove'),
    path('AxmMoveEStop/', views.AxmMoveEStop, name='AxmMoveEStop'),
    path('AxmMoveSStop/', views.AxmMoveSStop, name='AxmMoveSStop'),
    path('AxmMoveStartMultiPos/', views.AxmMoveStartMultiPos, name='AxmMoveStartMultiPos'),
    path('AxmMoveStartMultiPos2/', views.AxmMoveStartMultiPos2, name='AxmMoveStartMultiPos2'),
    path('signal_servo_on/', views.signal_servo_on, name='signal_servo_on'),
    path('signal_servo_off/', views.signal_servo_off, name='signal_servo_off'),
    path('SingleAxisStop/', views.SingleAxisStop, name='SingleAxisStop'),
    path('SingleAxisEStop/', views.SingleAxisEStop, name='SingleAxisEStop'),
    path('SingleAxisSStop/', views.SingleAxisSStop, name='SingleAxisSStop'),
]