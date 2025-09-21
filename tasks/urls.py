from django.urls import path
from .views import *

urlpatterns = [
    path('share/',share,name = "share"),
    path('yd/',yd,name = "yd"),
    path('',home,name = "home"),
]