from django.contrib import admin
from django.urls import path

from TimeTable_App.views import index, calc

urlpatterns = [
    path('', index),
    path('calc', calc, name='calculation'),
]
