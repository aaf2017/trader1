
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('', include('myapp.urls')), #localhost:8000/
    path('admin/', admin.site.urls), #localhost:8000/admin
]

#urlpatterns +=staticfiles_urlpatterns()
