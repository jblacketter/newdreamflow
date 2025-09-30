from django.urls import path
from django.conf import settings
from . import views

app_name = 'sharing'

urlpatterns = [
    path('thing/<uuid:pk>/share/', views.share_thing, name='share_thing'),
]

# Only expose group routes when groups feature is enabled
if getattr(settings, 'FEATURE_GROUPS', False):
    urlpatterns += [
        path('groups/', views.groups, name='groups'),
        path('groups/<int:pk>/things/', views.group_things, name='group_things'),
        path('groups/<int:pk>/invite/', views.invite_to_group, name='invite_to_group'),
    ]
