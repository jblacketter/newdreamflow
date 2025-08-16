from django.urls import path
from . import views

app_name = 'things'

urlpatterns = [
    path('', views.thing_list, name='list'),
    path('community/', views.community_things, name='community'),
    path('create/', views.thing_create, name='create'),
    path('quick/', views.quick_capture, name='quick_capture'),
    path('quick/<uuid:pk>/', views.quick_capture, name='quick_capture_edit'),
    path('<uuid:pk>/', views.thing_detail, name='detail'),
    path('<uuid:pk>/edit/', views.quick_capture, name='edit'),
    path('<uuid:pk>/delete/', views.thing_delete, name='delete'),
    path('<uuid:pk>/toggle-privacy/', views.toggle_privacy, name='toggle_privacy'),
    path('record/', views.record_voice, name='record_voice'),
]