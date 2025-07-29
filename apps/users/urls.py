from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('confirm-delete-account/', views.confirm_delete_account, name='confirm_delete_account'),
]