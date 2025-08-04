from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('ttable/', include('TimeTable_App.urls'), name='ttable'),
    path('', include('TimeTable_App.urls'), name='root'),
]
