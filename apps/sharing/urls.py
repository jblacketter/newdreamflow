from django.urls import path
from . import views

app_name = 'sharing'

urlpatterns = [
    path('groups/', views.groups, name='groups'),
    path('groups/<int:pk>/things/', views.group_things, name='group_things'),
    path('groups/<int:pk>/invite/', views.invite_to_group, name='invite_to_group'),
    path('thing/<uuid:pk>/share/', views.share_thing, name='share_thing'),
]