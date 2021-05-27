from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('djoser/', include('djoser.urls')),
    path('djoser/', include('djoser.urls.authtoken')),
]