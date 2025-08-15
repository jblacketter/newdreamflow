from django.urls import path
from . import views

app_name = 'dreams'

urlpatterns = [
    path('', views.dream_list, name='list'),
    path('community/', views.community_dreams, name='community'),
    path('create/', views.dream_create, name='create'),
    path('quick/', views.quick_capture, name='quick_capture'),
    path('<uuid:pk>/', views.dream_detail, name='detail'),
    path('<uuid:pk>/edit/', views.dream_edit, name='edit'),
    path('<uuid:pk>/delete/', views.dream_delete, name='delete'),
    path('<uuid:pk>/toggle-privacy/', views.toggle_privacy, name='toggle_privacy'),
    path('record/', views.record_voice, name='record_voice'),
]