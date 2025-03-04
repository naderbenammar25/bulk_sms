from django.urls import path
from .views import index, admin_dashboard, marketing_dashboard, user_login, upload_csv, list_groups, send_emails, register, approve_registration, reject_registration
from .views import gestion_employe, toggle_employee_status, get_employees, gestion_contacts, gestion_utilisateurs_marketing, gestion_groupes, gestion_campagnes, visualisation_performances, gestion_feedback, demander_intervention
from .views import edit_user, reset_password, toggle_user_status, add_employee, accueil_MK_User, employee_actions, connect_as_employee, gestion_profile_admin, update_profile , create_campaign
from .views import securite, notifications, editeur_contenu, demande_assistance, gestion_profile_MK, update_profile_MK, update_password , import_contacts, add_group, merge_groups,gestion_campagnes_mk, generate_content, suivi_performances, launch_campaign
from django.contrib.auth import views as auth_views
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('gestion_employe/', gestion_employe, name='gestion_employe'),
    path('api/employees/', get_employees, name='get_employees'),
    path('api/employees/<int:user_id>/toggle_status/', toggle_employee_status, name='toggle_employee_status'),
    path('login/', user_login, name='login'),
    path('register/', register, name='register'),
    path('approve-registration/<int:user_id>/', approve_registration, name='approve_registration'),
    path('reject-registration/<int:user_id>/', reject_registration, name='reject_registration'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('marketing_dashboard/', marketing_dashboard, name='marketing_dashboard'),
    path('upload_csv/', upload_csv, name='upload_csv'),
    path('list_groups/', list_groups, name='list_groups'),
    path('send_emails/', send_emails, name='send_emails'),
    path('gestion_contacts/', gestion_contacts, name='gestion_contacts'),
    path('gestion_utilisateurs_marketing/', gestion_utilisateurs_marketing, name='gestion_utilisateurs_marketing'),
    path('gestion_groupes/', gestion_groupes, name='gestion_groupes'),
    path('gestion_campagnes/', gestion_campagnes, name='gestion_campagnes'),
    path('visualisation_performances/', visualisation_performances, name='visualisation_performances'),
    path('gestion_feedback/', gestion_feedback, name='gestion_feedback'),
    path('demander_intervention/', demander_intervention, name='demander_intervention'),
    path('edit_user/<int:user_id>/', edit_user, name='edit_user'),
    path('reset_password/<int:user_id>/', reset_password, name='reset_password'),
    path('toggle_user_status/<int:user_id>/', toggle_user_status, name='toggle_user_status'),
    path('add_employee/', add_employee, name='add_employee'),
    path('accueil_MK_User/', accueil_MK_User, name='accueil_MK_User'),
    path('employee_actions/<int:employee_id>/', employee_actions, name='employee_actions'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('connect_as_employee/<int:employee_id>/', connect_as_employee, name='connect_as_employee'),
    path('gestion_profile_admin/', gestion_profile_admin, name='gestion_profile_admin'), 
    path('update_profile/', update_profile, name='update_profile'),
    path('marketing_dashboard/', marketing_dashboard, name='marketing_dashboard'),
    path('securite/', securite, name='securite'),
    path('notifications/', notifications, name='notifications'),
    path('gestion_campagnes/', gestion_campagnes, name='gestion_campagnes'),
    path('editeur_contenu/', editeur_contenu, name='editeur_contenu'),
    path('generate_content/', generate_content, name='generate_content'),
    path('demande_assistance/', demande_assistance, name='demande_assistance'),
    path('gestion_profile_MK/', gestion_profile_MK, name='gestion_profile_MK'),
    path('update_profile_MK/', update_profile_MK, name='update_profile_MK'),
    path('import_contacts/', import_contacts, name='import_contacts'),
    path('add_group/', add_group, name='add_group'),
    path('merge_groups/', merge_groups, name='merge_groups'),
    path('gestion_campagnes_mk/', gestion_campagnes_mk, name='gestion_campagnes_mk'),
    path('suivi_performances/', suivi_performances, name='suivi_performances'),
    path('launch_campaign/<int:campaign_id>/', launch_campaign, name='launch_campaign'),
    path('create_campaign/', create_campaign, name='create_campaign'),

    # URL pour la réinitialisation du mot de passe
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
]