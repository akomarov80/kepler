from django.contrib import admin
from django.urls import path

from TimeTable_App.views import index, calc, tt_calc

urlpatterns = [
    path('', index),
    path('calc', calc, name='calculation'),
    path('tt_calc', tt_calc, name = 'test_view'),

]
