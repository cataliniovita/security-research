from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('set-host', views.set_host, name='set_host'),
    path('reflect', views.reflect, name='reflect'),
]


