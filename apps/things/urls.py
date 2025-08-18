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
    path('<uuid:pk>/convert-to-story/', views.convert_thing_to_story, name='convert_to_story'),
    path('record/', views.record_voice, name='record_voice'),
    
    # Story URLs
    path('stories/', views.story_list, name='story_list'),
    path('stories/create/', views.story_create, name='story_create'),
    path('stories/<uuid:pk>/', views.story_detail, name='story_detail'),
    path('stories/<uuid:pk>/edit/', views.story_edit, name='story_edit'),
    path('stories/<uuid:pk>/play/', views.story_play, name='story_play'),
    path('stories/<uuid:pk>/delete/', views.story_delete, name='story_delete'),
]