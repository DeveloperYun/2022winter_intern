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
    path('SingleAxisEStop/', views.SingleAxisEStop, name='SingleAxisEStop'),
    path('SingleAxisEStop1/', views.SingleAxisEStop1, name='SingleAxisEStop1'),
    path('SingleAxisEStop2/', views.SingleAxisEStop2, name='SingleAxisEStop2'),
    path('SingleAxisEStop3/', views.SingleAxisEStop3, name='SingleAxisEStop3'),
    path('SingleAxisSStop/', views.SingleAxisSStop, name='SingleAxisSStop'),
    path('SingleAxisSStop1/', views.SingleAxisSStop1, name='SingleAxisSStop1'),
    path('SingleAxisSStop2/', views.SingleAxisSStop2, name='SingleAxisSStop2'),
    path('SingleAxisSStop3/', views.SingleAxisSStop3, name='SingleAxisSStop3'),
    path('AxmMoveEStop/', views.AxmMoveEStop, name='AxmMoveEStop'),
    path('AxmMoveSStop/', views.AxmMoveSStop, name='AxmMoveSStop'),
    path('AxmMoveStartMultiPos/', views.AxmMoveStartMultiPos, name='AxmMoveStartMultiPos'),
    path('AxmMoveStartMultiPos2/', views.AxmMoveStartMultiPos2, name='AxmMoveStartMultiPos2'),
    path('signal_servo_on/', views.signal_servo_on, name='signal_servo_on'),
    path('signal_servo_off/', views.signal_servo_off, name='signal_servo_off'),
    path('SingleAxisStop/', views.SingleAxisStop, name='SingleAxisStop'),
]