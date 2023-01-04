from django.contrib import admin
from django.urls import path, include
from hello import views
from django.conf.urls.static import static
from django.conf import settings
#from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('control/', include('control.urls')),
    path('hello/', include('hello.urls')),
    path('accounts/',include('accounts.urls')),
    path('', views.index, name='index'),
]
# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

#urlpatterns += static_urlpatterns()