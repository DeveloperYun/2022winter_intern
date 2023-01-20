from django.contrib import admin
from django.urls import path, include
from hello import views

# 127.0.0.1:8000/control/
urlpatterns = [
    path('admin/', admin.site.urls),
    path('control/', include('control.urls')), #path('', include('graph.urls')),
    path('hello/', include('hello.urls')),
    path('accounts/',include('accounts.urls')),
    path('', views.index, name='index'),
]