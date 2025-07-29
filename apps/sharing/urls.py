from django.urls import path
from . import views

app_name = 'sharing'

urlpatterns = [
    path('groups/', views.groups, name='groups'),
    path('groups/<int:pk>/dreams/', views.group_dreams, name='group_dreams'),
    path('groups/<int:pk>/invite/', views.invite_to_group, name='invite_to_group'),
    path('dream/<uuid:pk>/share/', views.share_dream, name='share_dream'),
]