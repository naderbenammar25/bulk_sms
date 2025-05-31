import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.admin.views.decorators import staff_member_required
from .models import Company, CustomUser, Group, Contact
from django.urls import reverse
from .forms import UserEditForm, PasswordResetForm
from .models import CustomUser
from .serializers import CustomUserSerializer
from django.http import JsonResponse
from .forms import AddEmployeeForm
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth import views as auth_views
import pytz
from django.utils import timezone
from .models import CampaignAction
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .models import Contact, Group, Content, Campaign
import requests
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Campaign, Content, Group

from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Campaign, Content, Group
from django.contrib import messages

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Campaign, Content, Group
from django.contrib import messages

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Campaign, Content, Group
from django.contrib import messages

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Campaign, Content, Group
from django.contrib import messages

from django.urls import reverse

## importations pour les statistiques
from ml_model.regressor_sto_model import get_statistics
import pandas as pd
from ml_model.regressor_sto_model import load_data_from_db

User = get_user_model()

@api_view(['GET'])
def user_profile(request):
    user = request.user
    if user.is_authenticated:
        return Response({
            'username': user.username,
            'email': user.email,
            'role': user.role,
        })
    return Response(status=status.HTTP_401_UNAUTHORIZED)





def register(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        logo = request.FILES.get('logo')
        primary_color = request.POST.get('primary_color')
        secondary_color = request.POST.get('secondary_color', '#2A303D')  # Valeur par défaut
        tertiary_color = request.POST.get('tertiary_color', '#808080')  # Valeur par défaut
        admin_username = request.POST.get('admin_username')
        admin_email = request.POST.get('admin_email')
        admin_phone = request.POST.get('admin_phone')
        admin_password = request.POST.get('admin_password')
        confirm_password = request.POST.get('confirm_password')

        
        if admin_password != confirm_password:
            return render(request, 'index.html', {'error': 'Les mots de passe ne correspondent pas.'})

        
        if not primary_color:
            return render(request, 'index.html', {'error': 'Vous devez sélectionner la couleur principale.'})

        try:
            # Créer l'entreprise
            colors = ','.join([primary_color, secondary_color, tertiary_color])
            company = Company.objects.create(name=company_name, logo=logo, color=colors)

            # Créer l'administrateur sans l'activer
            admin_user = CustomUser.objects.create_user(
                username=admin_username,
                email=admin_email,
                phone=admin_phone,
                password=admin_password,
                role='admin',
                company=company,
                is_active=False  
            )

            #message de confirmation vers l'administrateur
            send_mail(
                'Inscription en cours de traitement',
                'Votre demande d\'inscription est en cours de traitement. Vous recevrez un email une fois votre compte approuvé.',
                'nader@metadia.net',
                [admin_email],
            )

            # notification vers le super administrateur
            super_admin_email = 'nader21benammar@gmail.com' 
            send_mail(
                'Nouvelle demande d\'inscription',
                f'Une nouvelle demande d\'inscription a été soumise par {admin_username}. Veuillez la traiter.',
                'nader@metadia.net',
                [super_admin_email],
            )

            return render(request, 'index.html', {'message': 'Votre demande d\'inscription est en cours de traitement.'})

        except IntegrityError:
            return render(request, 'index.html', {'error': 'Le nom d\'utilisateur est déjà pris. Veuillez en choisir un autre.'})

    return render(request, 'index.html')

def upload_csv(request):
    if request.method == "POST":
        group_name = request.POST.get("group")
        if not group_name:
            return HttpResponse("Group name is required.", status=400)
        
        group, _ = Group.objects.get_or_create(name=group_name)
        csv_file = request.FILES.get("file")
        if not csv_file:
            return HttpResponse("CSV file is required.", status=400)
        
        decoded_file = csv_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)

        for row in reader:
            Contact.objects.create(
                group=group,
                first_name=row["Prenom"],
                last_name=row["Nom"],
                phone=row["Tel"],
                email=row["Mail"],
            )
        return HttpResponse("Contacts uploaded successfully.")
    return render(request, "upload_csv.html")

def list_groups(request):
    groups = Group.objects.all()
    return render(request, "list_groups.html", {"groups": groups})

def send_emails(request):
    if request.method == "POST":
        group_ids = request.POST.getlist("groups")
        message = request.POST.get("message")
        
        for group_id in group_ids:
            group = get_object_or_404(Group, id=group_id)
            for contact in group.contacts.all():
                send_mail(
                    subject="Message SMS",
                    message=f"Bonjour {contact.first_name},\n\n{message}",
                    from_email="nader@metadia.net",
                    recipient_list=[contact.email],
                )
        return HttpResponse("Emails sent successfully.")
    
    groups = Group.objects.all()
    return render(request, "send_emails.html", {"groups": groups})

def index(request):
    return render(request, 'index.html')



from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.urls import reverse

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.urls import reverse

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirection en fonction du rôle de l'utilisateur
            if hasattr(user, 'role'):  
                if user.role == 'admin':
                    return redirect(f"{reverse('admin_dashboard')}?success=true&username={user.username}")
                elif user.role == 'marketing':
                    return redirect(f"{reverse('marketing_dashboard')}?success=true&username={user.username}")
                else:
                    return redirect(f"{reverse('default_dashboard')}?success=true&username={user.username}")
            else:
                return redirect(f"{reverse('default_dashboard')}?success=true&username={user.username}")
        else:
            
            return render(request, 'login.html', {'error': 'Nom d\'utilisateur ou mot de passe incorrect.'})
    return render(request, 'login.html')


def custom_logout(request):
    user = request.user
    if user.is_authenticated:
        user.is_logged_in = False
        user.save()
    auth_logout(request)
    return redirect('login')

@login_required
def marketing_dashboard(request):
    return render(request, 'marketing_dashboard.html')

@staff_member_required
def approve_registration(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = True
    user.save()

    password = request.POST.get('password')


    
    send_mail(
        'Compte approuvé',
        f'Bonjour {user.first_name},\n\n'
        'Votre compte a été approuvé. Vous pouvez maintenant vous connecter avec le lien suivant :\n\n'
        'Lien de connexion : http://127.0.0.1:8000/login/\n\n'
        'Cordialement,\n'
        'Projet PFE',
        'nader@metadia.net', 
        [user.email],
    )

    return redirect('/admin/')

@staff_member_required
def reject_registration(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        reason = request.POST.get('reason')
        # email de refus 
        send_mail(
            'Demande d\'inscription refusée',
            f'Votre demande d\'inscription a été refusée pour la raison suivante : {reason}',
            'nader@metadia.net',  
            [user.email],
        )
        
        if user.company:
            user.company.delete()
        
        user.delete()
        return redirect(reverse('admin:auth_user_changelist'))
    return render(request, 'reject_registration.html', {'user': user})

def gestion_employe(request):
    employees = CustomUser.objects.filter(role='marketing')
    return render(request, 'gestionEmploye.html', {'employees': employees})

@login_required
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = UserEditForm(instance=user)
    return render(request, 'edit_user.html', {'form': form})

@login_required
def reset_password(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('admin_dashboard')
    else:
        form = PasswordResetForm()
    return render(request, 'reset_password.html', {'form': form})

@login_required
def toggle_user_status(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('admin_dashboard')


@login_required
def toggle_contact_status(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    # gestion de statut des contacts
    if contact.status == 'Actif':
        contact.status = 'Inactif'
    else:
        contact.status = 'Actif'
    contact.save()
    return JsonResponse({'status': contact.status})


@api_view(['GET'])
def get_employees(request):
    employees = CustomUser.objects.filter(role='marketing')
    serializer = CustomUserSerializer(employees, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def toggle_employee_status(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = not user.is_active
    user.save()
    serializer = CustomUserSerializer(user)
    return Response(serializer.data)

from ml_model import dash_apps  # 

@login_required
def admin_dashboard(request):
  
    return render(request, 'admin_dashboard.html')

@login_required
def gestion_contacts(request):
    company = request.user.company
    colors = company.color.split(',')
    primary_color = colors[0]
    secondary_color = colors[1]
    tertiary_color = colors[2]
    group_id = request.GET.get('group_id')
    if group_id:
        contacts = Contact.objects.filter(group_id=group_id)
    else:
        contacts = Contact.objects.all()
    groupes = Group.objects.all()
    context = {
        'contacts': contacts,
        'groupes': groupes,
        'company': company,
        'primary_color': primary_color,
        'secondary_color': secondary_color,
        'tertiary_color': tertiary_color,
    }
    return render(request, 'gestion_contacts.html', context)

@login_required
def gestion_utilisateurs_marketing(request):
    company = request.user.company
    colors = company.color.split(',')
    primary_color = colors[0]
    secondary_color = colors[1]
    tertiary_color = colors[2]
    company_id = request.user.company_id  # Assurez-vous que l'utilisateur a un attribut company_id
    employees = CustomUser.objects.filter(role='marketing', company_id=company_id)
    active_employees = employees.filter(is_logged_in=True)
    context = {
        'employees': employees,
        'active_employees': active_employees,
        'company': company,
        'primary_color': primary_color,
        'secondary_color': secondary_color,
        'tertiary_color': tertiary_color,
    }
    return render(request, 'gestion_utilisateurs_marketing.html', context)

@login_required
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('gestion_utilisateurs_marketing')
    else:
        form = UserEditForm(instance=user)
    return render(request, 'edit_user.html', {'form': form})

@login_required
def reset_password(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('gestion_utilisateurs_marketing')
    else:
        form = PasswordResetForm()
    return render(request, 'reset_password.html', {'form': form})


@login_required
def add_employee(request):
    if request.method == 'POST':
        form = AddEmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.role = 'marketing'
            employee.is_active = True
            employee.company = request.user.company  
            employee.set_password(form.cleaned_data['password'])
            employee.save()

            
            send_mail(
                'Ouverture de votre compte',
                f'Bonjour {employee.first_name},\n\nVotre compte a été créé avec succès. Vous pouvez vous connecter avec les informations suivantes :\n\nNom d\'utilisateur : {employee.username}\nMot de passe : {form.cleaned_data["password"]}\n\nLien de connexion : http://127.0.0.1:8000/login/\n\nCordialement,\nL\'équipe',
                'nader@metadia.net',
                [employee.email],
            )

            
            return redirect(f"{reverse('gestion_utilisateurs_marketing')}?success=true")
    else:
        form = AddEmployeeForm()
    return render(request, 'add_employee.html', {'form': form})

@login_required
def accueil_MK_User(request):
    
    return render(request, 'accueil_MK_User.html')

@login_required
def employee_actions(request, employee_id):
    employee = get_object_or_404(CustomUser, id=employee_id)
    actions = {
        'last_campaign_created': '2025-02-10',
        'last_campaign_launched': '2025-02-12',
        'last_campaign_cancelled': '2025-02-11',
    }
    return JsonResponse(actions)


@login_required
def gestion_groupes(request):
    company = request.user.company
    colors = company.color.split(',')
    primary_color = colors[0]
    secondary_color = colors[1]
    tertiary_color = colors[2]
    groups = Group.objects.filter(company=request.user.company)
    context = {
        'company': company,
        'primary_color': primary_color,
        'secondary_color': secondary_color,
        'tertiary_color': tertiary_color,
        'groups': groups,
    }
    return render(request, 'gestion_groupes.html', context)





import psycopg2
import pandas as pd
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def load_data_from_db():
    conn = psycopg2.connect(
        dbname="new_mass_mailing_db",
        user="postgres",
        password="user01",
        host="localhost",
        port="5432"
    )
    query = "SELECT * FROM campaigns_campaign"
    data = pd.read_sql_query(query, conn)
    conn.close()
    return data

@login_required
def gestion_campagnes_mk(request):
    status_filter = request.GET.get('status')
    search_query = request.GET.get('search')

    campaigns = Campaign.objects.all()

    if status_filter:
        campaigns = campaigns.filter(status=status_filter)

    if search_query:
        campaigns = campaigns.filter(Q(name__icontains=search_query))

    contents = Content.objects.all()
    groups = Group.objects.all()
    total_campaigns = campaigns.count()
    ongoing_campaigns = campaigns.filter(status='en cours').count()
    scheduled_campaigns = campaigns.filter(status='planifiée').count()
    completed_campaigns = campaigns.filter(status='terminée').count()

    context = {
        'campaigns': campaigns, 
        'contents': contents,
        'groups': groups,
        'total_campaigns': total_campaigns if 'total_campaigns' in locals() else 0,
        'completed_campaigns': completed_campaigns if 'completed_campaigns' in locals() else 0,
        'ongoing_campaigns': ongoing_campaigns if 'ongoing_campaigns' in locals() else 0,
        'scheduled_campaigns': scheduled_campaigns if 'scheduled_campaigns' in locals() else 0,
    }
    return render(request, 'gestion_campagnes_MK.html', context)

@login_required
def gestion_campagnes_admin(request):
    status_filter = request.GET.get('status')
    search_query = request.GET.get('search')

    campaigns = Campaign.objects.all()

    if status_filter:
        campaigns = campaigns.filter(status=status_filter)

    if search_query:
        campaigns = campaigns.filter(Q(name__icontains=search_query))

    contents = Content.objects.all()
    groups = Group.objects.all()
    total_campaigns = campaigns.count()
    ongoing_campaigns = campaigns.filter(status='en cours').count()
    scheduled_campaigns = campaigns.filter(status='planifiée').count()
    completed_campaigns = campaigns.filter(status='terminée').count()

    context = {
        'campaigns': campaigns[:10],  
        'contents': contents,
        'groups': groups,
        'total_campaigns': total_campaigns,
        'ongoing_campaigns': ongoing_campaigns,
        'scheduled_campaigns': scheduled_campaigns,
        'completed_campaigns': completed_campaigns,
    }
    return render(request, 'gestion_campagnes_admin.html', context)





@login_required
def create_campaign(request):
    if request.method == 'POST':
        title = request.POST.get('campaign_title')
        campaign_type = request.POST.get('campaign_type')
        content_id = request.POST.get('campaign_content')
        message = request.POST.get('campaign_message')
        launch_date = request.POST.get('launch_date')
        target_group_id = request.POST.get('target_groups')
        duration = request.POST.get('duration')
        duration_unit = request.POST.get('duration_unit')
        messages_per_period = request.POST.get('messages_per_period')
        period_unit = request.POST.get('period_unit')

        content = Content.objects.get(id=content_id) if content_id else None
        target_group = Group.objects.get(id=target_group_id)

        if content:
            message = content.html_content  

        if campaign_type == 'lancement_rapide':
            launch_date = timezone.now()
            duration = 1 
            duration_unit = 'jours'  # durée par défaut 
            messages_per_period = 1 
            period_unit = 'semaine'  # periode par défaut

        campaign = Campaign.objects.create(
            name=title,
            campaign_type=campaign_type,
            content=content,
            message=message,
            launch_date=launch_date,
            group=target_group,
            duration=duration,
            duration_unit=duration_unit,
            messages_per_period=messages_per_period,
            period_unit=period_unit,
            status='terminée' if campaign_type == 'lancement_rapide' else 'brouillon'
        )

        if campaign_type == 'lancement_rapide':
            
            launch_fast_campaign(request, campaign.id)

        
        return redirect(f"{reverse('gestion_campagnes_mk')}?success=true")

    contents = Content.objects.all()
    groups = Group.objects.all()
    return render(request, 'creation_campagne.html', {'contents': contents, 'groups': groups})



def visualisation_performances(request):
    return render(request, 'visualisation_performances.html')

def gestion_feedback(request):
    return render(request, 'gestion_feedback.html')

def demander_intervention(request):
    return render(request, 'demander_intervention.html')
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import CustomUser

@login_required
def connect_as_employee(request, employee_id):
    employee = get_object_or_404(CustomUser, id=employee_id)
    if request.user.role == 'admin':
        
        request.session['admin_username'] = request.user.username
        request.session['employee_username'] = employee.username
        request.session.modified = True  
        login(request, employee)
        return redirect('marketing_dashboard')
    return redirect('gestion_utilisateurs_marketing')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
def update_profile_MK(request):
    if request.method == 'POST':
        user = request.user
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        user.language = request.POST.get('language', user.language)
        user.date_format = request.POST.get('date_format', user.date_format)
        user.timezone = 'Automatique' if request.POST.get('timezone_auto') else request.POST.get('timezone', user.timezone)
        
        if request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES['profile_picture']
        user.save()
        messages.success(request, 'Votre profil a été mis à jour avec succès.')
        return redirect('marketing_dashboard')
    # Si accès direct en GET, on redirige aussi vers le dashboard
    return redirect('marketing_dashboard')


@login_required
def gestion_profile_admin(request):
    user = request.user
    company = user.company  
    logo_url = company.logo.url if company.logo else None  
    timezones = pytz.all_timezones 
    detected_timezone = timezone.get_current_timezone_name()  # Detection du fuseau horaire actuel
    return render(request, 'gestion_profile_admin.html', {
        'full_name': f'{user.first_name} {user.last_name}',
        'email': user.email,
        'phone': user.phone,
        'language': user.language,
        'date_format': user.date_format,
        'timezone': user.timezone,
        'logo_url': logo_url,
        'company': company,
        'timezones': timezones,
        'detected_timezone': detected_timezone,  
    })

@login_required
def update_profile_MK(request):
    if request.method == 'POST':
        user = request.user
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        user.language = request.POST.get('language', user.language)
        user.date_format = request.POST.get('date_format', user.date_format)
        user.timezone = 'Automatique' if request.POST.get('timezone_auto') else request.POST.get('timezone', user.timezone)
        user.save()
        messages.success(request, 'Votre profil a été mis à jour avec succès.')
        return redirect('gestion_profile_MK')
    return render(request, 'gestion_profile_MK.html')

@login_required
def gestion_profile_MK(request):
    user = request.user
    company = user.company  
    logo_url = company.logo.url if company.logo else None  
    timezones = pytz.all_timezones  
    detected_timezone = timezone.get_current_timezone_name()  # detection du fuseau horaire actuel
    return render(request, 'gestion_profile_MK.html', {
        'full_name': f'{user.first_name} {user.last_name}',
        'email': user.email,
        'phone': user.phone,
        'language': user.language,
        'date_format': user.date_format,
        'timezone': user.timezone,
        'logo_url': logo_url,
        'company': company,
        'timezones': timezones,
        'detected_timezone': detected_timezone,  
    })

@login_required
def record_campaign_action(request, campaign_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        timestamp = timezone.now()  # affectation de l'heure actuelle
        CampaignAction.objects.create(
            user=request.user,
            campaign_id=campaign_id,
            action=action,
            timestamp=timestamp
        )
        messages.success(request, 'Action enregistrée avec succès.')
        return redirect('campaign_detail', campaign_id=campaign_id)
    return render(request, 'campaign_detail.html', {'campaign_id': campaign_id})


@login_required
def campaign_detail(request, campaign_id):
    campaign_actions = CampaignAction.objects.filter(campaign_id=campaign_id).order_by('-timestamp')
    for action in campaign_actions:
        action.timestamp = action.timestamp.astimezone(timezone.get_current_timezone())
    return render(request, 'campaign_detail.html', {'campaign_actions': campaign_actions})


@login_required
def marketing_dashboard(request):
    return render(request, 'marketing_dashboard.html')

@login_required
def securite(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # pour garder l'utilisateur connecté
            messages.success(request, 'Votre mot de passe a été mis à jour avec succès.')
            return redirect('securite')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'securite.html', {'form': form})

@login_required
def notifications(request):
    return render(request, 'notifications_MK.html')

@login_required
def gestion_campagnes(request):
    return render(request, 'gestion_campagnes.html')

from django.core.exceptions import ValidationError
from bs4 import BeautifulSoup

@login_required
def editeur_contenu(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        html_content = request.POST.get('html_content')

        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            if not soup.find():  
                raise ValidationError("Le contenu HTML est invalide.")
        except Exception as e:
            messages.error(request, f"Erreur dans le contenu HTML : {e}")
            return redirect('editeur_contenu')

        Content.objects.create(title=title, html_content=html_content)
        messages.success(request, 'Contenu créé avec succès.')
        return redirect('marketing_dashboard')

    user = request.user
    company = user.company
    logo_url = company.logo.url if company.logo else None
    company_name = company.name if company else "Nom de l'entreprise"

    return render(request, 'editeur_contenu.html', {
        'logo_url': logo_url,
        'company_name': company_name,
    })


@login_required
def suspend_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    if campaign.status == 'en cours':
        campaign.status = 'suspendue'
        messages.success(request, f"La campagne '{campaign.name}' a été suspendue.")
    elif campaign.status == 'suspendue':
        campaign.status = 'en cours'
        messages.success(request, f"La campagne '{campaign.name}' a été reprise.")
    else:
        messages.error(request, f"La campagne '{campaign.name}' ne peut pas être suspendue ou reprise.")

    campaign.save()
    return redirect('gestion_campagnes_mk')

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Campaign

@login_required
def delete_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    try:
        campaign.delete()
        messages.success(request, f"La campagne '{campaign.name}' a été supprimée avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression de la campagne : {e}")

    return redirect('gestion_campagnes_mk')


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Campaign

@login_required
def relancer_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    if campaign.status == 'terminée':
        campaign.status = 'en cours'
        campaign.launch_date = timezone.now()
        campaign.save()
        messages.success(request, f"La campagne '{campaign.name}' a été relancée avec succès.")
    else:
        messages.error(request, f"La campagne '{campaign.name}' ne peut pas être relancée car elle n'est pas terminée.")

    return redirect('gestion_campagnes_mk')

@login_required
def demande_assistance(request):
    return render(request, 'demande_assistance.html')

@login_required
def suivi_performances(request):
    return render(request, 'suivi_performances.html')   

@login_required
def gestion_profile_MK(request):
    return render(request, 'gestion_profile_MK.html')



@login_required
def update_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  
            messages.success(request, 'Votre mot de passe a été mis à jour avec succès.')
            return redirect('securite')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'update_password.html', {'form': form})

from django.views.decorators.csrf import csrf_protect
@csrf_protect
@login_required
def import_contacts(request):
    if request.method == 'POST':
        groupe_id = request.POST.get('groupe')
        groupe = get_object_or_404(Group, id=groupe_id)
        csv_file = request.FILES['csv_file']
        decoded_file = csv_file.read().decode('latin1').splitlines()
        reader = csv.reader(decoded_file, delimiter=';')  # séparateur ;
        next(reader)  
        for row in reader:
            if len(row) < 9:
                continue  # Ignorer les lignes qui ne contiennent pas au moins 9 colonnes
            nom, prenom, age, genre, adresse, ville, metier, email, telephone = row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]  # Adapter les indices selon les colonnes
            Contact.objects.create(
                group=groupe,
                company=request.user.company,
                first_name=prenom,
                last_name=nom,
                phone=telephone,
                email=email,
                age=int(age) if age.isdigit() else None,  
                status='Actif'
            )
        messages.success(request, 'Les contacts ont été importés avec succès.')
        return redirect('gestion_contacts')
    return redirect('gestion_contacts')



@login_required
def add_group(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        Group.objects.create(name=group_name, company=request.user.company)
        messages.success(request, 'Groupe ajouté avec succès.')
        return redirect('gestion_groupes')
    return redirect('gestion_groupes')

@login_required
def merge_groups(request):
    if request.method == 'POST':
        new_group_name = request.POST.get('new_group_name')
        groups_to_merge = request.POST.get('groups_to_merge').split(',')
        new_group = Group.objects.create(name=new_group_name, company=request.user.company)
        for group_id in groups_to_merge:
            group = get_object_or_404(Group, id=group_id)
            for contact in group.contacts.all():
                
                Contact.objects.create(
                    group=new_group,
                    company=contact.company,
                    first_name=contact.first_name,
                    last_name=contact.last_name,
                    phone=contact.phone,
                    email=contact.email,
                    status=contact.status
                )
        messages.success(request, 'Groupes fusionnés avec succès.')
        return redirect('gestion_groupes')
    return redirect('gestion_groupes')


import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

def validate_prompt(prompt):
    """Valide le prompt avant envoi à l'API"""
    if not prompt or not isinstance(prompt, str):
        return False
    if len(prompt) > 500: 
        return False
    return True

@csrf_exempt
def generate_content(request):
    if request.method != 'POST':
        logger.warning(f"Méthode non autorisée: {request.method}")
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

    try:
        # Décodage et validation des données
        try:
            data = json.loads(request.body)
            prompt = data.get('prompt', 'Tu es un assistant marketing expert en campagnes de mailing.').strip()
        except json.JSONDecodeError:
            logger.error("Erreur de décodage JSON")
            return JsonResponse({"error": "Format de données invalide"}, status=400)

        if not validate_prompt(prompt):
            logger.warning(f"Prompt invalide: {prompt}")
            return JsonResponse({"error": "Prompt vide ou trop long (max 500 caractères)"}, status=400)

        
        api_params = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Tu es un assistant marketing expert en campagnes de mailing. "
                        "Rédige des messages courts (<160 caractères), persuasifs "
                        "avec appel à l'action clair. Inclus l'offre et le CTA."
                    )
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 500,
            "frequency_penalty": 0.5  
        }

        
        try:
            response = requests.post(
                url="https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=api_params,
                timeout=10  
            )
            response.raise_for_status()  

        except requests.Timeout:
            logger.error("Timeout de l'API DeepSeek")
            return JsonResponse({"error": "Le service est temporairement indisponible"}, status=503)
        except requests.RequestException as e:
            logger.error(f"Erreur API: {str(e)}")
            return JsonResponse({"error": "Erreur de communication avec le service"}, status=502)

        
        result = response.json()
        generated_text = result['choices'][0]['message']['content']
        
        
        if not generated_text or len(generated_text) > 500:
            logger.warning("Contenu généré invalide")
            return JsonResponse({"error": "Erreur de génération de contenu"}, status=500)

        return JsonResponse({
            'generated_content': generated_text,
            'char_count': len(generated_text)
        })

    except Exception as e:
        logger.exception("Erreur serveur inattendue")
        return JsonResponse({
            'error': 'Une erreur technique est survenue'
        }, status=500)

from django.utils.crypto import get_random_string
from .models import EmailTracking 
import logging

logger = logging.getLogger(__name__)

@login_required
def launch_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    if campaign.status == 'brouillon':
        campaign.status = 'en cours'
        campaign.launch_date = timezone.now()
        campaign.save()

        
        company = request.user.company
        logo_url = request.build_absolute_uri(company.logo.url) if company.logo else ''
        company_name = company.name if company else 'Nom de l\'entreprise'

        
        contacts = campaign.group.contacts.filter(status='Actif')  
        for contact in contacts:
            subject = f"Campagne: {campaign.name}"
            message = campaign.message
            html_content = f"""
                <div class="header">
                    <img src="{logo_url}" alt="Logo de l'entreprise">
                    <h3>{company_name}</h3>
                </div>
                {message}
                <div class="footer">
                    <p>&copy; {company_name} - Tous droits réservés</p>
                </div>
            """

            try:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=message,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[contact.email],
                )
                email.attach_alternative(html_content, "text/html")
                email.send()
                logger.info(f"Email sent to {contact.email}")
            except Exception as e:
                logger.error(f"Failed to send email to {contact.email}: {e}")

    return redirect('gestion_campagnes_mk')

from .models import EmailTracking
import logging

logger = logging.getLogger(__name__)
from django.utils.timezone import now

def email_tracking_pixel(request, tracking_id):
    email_tracking = get_object_or_404(EmailTracking, tracking_id=tracking_id)
    if not email_tracking.opened_at:
        email_tracking.opened_at = now()
        email_tracking.save()
        logger.info(f"Email with tracking ID {tracking_id} opened at {email_tracking.opened_at}")

    # Retourner une image transparente de 1x1 pixel
    pixel = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b'
    return HttpResponse(pixel, content_type='image/gif')


import logging

logger = logging.getLogger(__name__)


logging.basicConfig(level=logging.DEBUG)


@login_required
def launch_fast_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    campaign.status = 'terminée'
    campaign.launch_date = timezone.now()
    campaign.save()

    company = request.user.company
    logo_url = request.build_absolute_uri(company.logo.url) if company.logo else ''
    company_name = company.name if company else 'Nom de l\'entreprise'

    
    contacts = campaign.group.contacts.filter(status='Actif')  # Exclure les contacts désactivés
    for contact in contacts:
        subject = f"Campagne: {campaign.name}"
        message = campaign.message
        html_content = f"""
            <div class="header">
                <img src="{logo_url}" alt="Logo de l'entreprise">
                <h3>{company_name}</h3>
            </div>
            {message}
            <div class="footer">
                <p>&copy; {company_name} - Tous droits réservés</p>
            </div>
        """

        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=settings.EMAIL_HOST_USER,
                to=[contact.email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            logger.info(f"Email sent to {contact.email}")
        except Exception as e:
            logger.error(f"Failed to send email to {contact.email}: {e}")

    return redirect('gestion_campagnes_mk')


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import Feedback, Campaign

@login_required
def gestion_feedback(request):
    

    feedbacks = Feedback.objects.all().order_by('-created_at')  

    if request.method == 'POST':
        feedback_id = request.POST.get('feedback_id')
        response_message = request.POST.get('response')
        feedback = get_object_or_404(Feedback, id=feedback_id)

        
        send_mail(
            subject=f"Réponse à votre feedback pour la campagne {feedback.campaign.name}",
            message=response_message,
            from_email="nader@metadia.net",
            recipient_list=[feedback.contact_email],
        )

        
        feedback.response = response_message
        feedback.responded_at = now()
        feedback.save()

        return redirect('gestion_feedback')

    return render(request, 'gestion_feedback.html', {'feedbacks': feedbacks})



from django.shortcuts import render
from ml_model.regressor_sto_model import load_data_from_db, prepare_prophet_data
from prophet import Prophet
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def prophet_plot_base64(prophet_data, forecast, contact_hash):
    model = Prophet()
    model.fit(prophet_data)
    fig = model.plot(forecast)
    plt.title(f"Prévision du taux d'ouverture pour {contact_hash}")
    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_base64

from .models import Group

from sklearn.metrics import mean_squared_error

def predictions_dashboard(request):
    data = load_data_from_db()
    data['EVENT_DATE'] = pd.to_datetime(data['EVENT_DATE'], format='%Y-%m-%d %H:%M:%S')
    predictions = []
    plot_base64 = None
    mse_value = None
    selected_contact = request.GET.get('contact')
    selected_group_name = request.GET.get('group')

    groupes = Group.objects.all()

    if selected_group_name:
        if 'GroupName' in data.columns:
            data = data[data['GroupName'] == selected_group_name]
        else:
            group_obj = Group.objects.filter(name=selected_group_name).first()
            if group_obj and 'Group_id' in data.columns:
                data = data[data['Group_id'] == group_obj.id]

    unique_contacts = list(data['ContactHash'].unique())[:100]

    for contact_hash in unique_contacts:
        prophet_data = prepare_prophet_data(data, contact_hash)
        if len(prophet_data) < 2:
            continue
        model = Prophet()
        model.fit(prophet_data)
        future = model.make_future_dataframe(periods=24, freq='H')
        forecast = model.predict(future)
        best_row = forecast.loc[forecast['yhat'].idxmax()]
        predictions.append({
            'contact': contact_hash,
            'best_time': best_row['ds'],
            'score': best_row['yhat'],
        })
        if selected_contact and str(contact_hash) == str(selected_contact):
            plot_base64 = prophet_plot_base64(prophet_data, forecast, contact_hash)
            # Calcul du (MSE) ==> la moyenne des différences au carré entre les valeurs cibles prédites
            y_true = prophet_data['y'].values
            y_pred = forecast.set_index('ds').loc[prophet_data['ds'], 'yhat'].values
            mse_value = mean_squared_error(y_true, y_pred)

    return render(request, 'predictions_dashboard.html', {
        'predictions': predictions,
        'selected_contact': selected_contact,
        'plot_base64': plot_base64,
        'mse_value': mse_value,
        'groupes': groupes,
        'selected_group_name': selected_group_name,
    })