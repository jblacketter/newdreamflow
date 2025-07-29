from django.urls import path
from . import views

app_name = 'patterns'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('network-data/', views.pattern_network, name='network_data'),
]