from django.contrib import admin
from django.urls import path, include
from hello import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('control/', include('control.urls')),
    path('hello/', include('hello.urls')),
    path('accounts/',include('accounts.urls')),
    path('', views.index, name='index'),
]