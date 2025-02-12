from django.urls import path
from .views import index, admin_dashboard, marketing_dashboard, user_login, upload_csv, list_groups, send_emails, register,approve_registration,reject_registration 
from .views import gestion_employe,toggle_employee_status, get_employees
urlpatterns = [
    path('', index, name='index'),
    path('gestion_employe/', gestion_employe, name='gestion_employe'),
    path('api/employees/', get_employees, name='get_employees'),
    path('api/employees/<int:user_id>/toggle_status/',toggle_employee_status, name='toggle_employee_status'),
    path('login/', user_login, name='login'),
    path('register/', register, name='register'),
    path('approve-registration/<int:user_id>/', approve_registration, name='approve_registration'),
    path('reject-registration/<int:user_id>/', reject_registration, name='reject_registration'),

    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('marketing_dashboard/', marketing_dashboard, name='marketing_dashboard'),
    path('upload_csv/', upload_csv, name='upload_csv'),
    path('list_groups/', list_groups, name='list_groups'),
    path('send_emails/', send_emails, name='send_emails'),
]