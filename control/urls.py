from django.urls import path

from . import views

app_name = 'control'

urlpatterns = [
    path('control/', views.main, name='main'),
    path('ready/',views.control_initialization, name='control_initialization'),
    path('AxmMovePos/', views.AxmMovePos, name='AxmMovePos'),
    path('AxmMoveStartPos/', views.AxmMoveStartPos, name='AxmMoveStartPos'),
    path('AxmMoveVel/', views.AxmMoveVel, name='AxmMoveVel'),
    path('AxmMoveToAbsPos/', views.AxmMoveToAbsPos, name='AxmMoveToAbsPos'),
]