from django.urls import path

from . import views

app_name = 'config_backup'

urlpatterns = [
    path('status', views.backup_status, name='backup_status')
]
