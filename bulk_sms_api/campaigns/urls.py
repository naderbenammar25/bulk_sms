from django.urls import path
from .views import index, admin_dashboard, marketing_dashboard, user_login, upload_csv, list_groups, send_emails, register

urlpatterns = [
    path('', index, name='index'),
    path('login/', user_login, name='login'),
    path('register/', register, name='register'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('marketing_dashboard/', marketing_dashboard, name='marketing_dashboard'),
    path('upload_csv/', upload_csv, name='upload_csv'),
    path('list_groups/', list_groups, name='list_groups'),
    path('send_emails/', send_emails, name='send_emails'),
]