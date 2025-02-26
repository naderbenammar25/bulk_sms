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

        # Vérifier que les mots de passe correspondent
        if admin_password != confirm_password:
            return render(request, 'index.html', {'error': 'Les mots de passe ne correspondent pas.'})

        # Vérifier que l'utilisateur a sélectionné la couleur principale
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
                is_active=False  # Désactiver le compte jusqu'à approbation
            )

            # Envoyer un message de confirmation à l'administrateur
            send_mail(
                'Inscription en cours de traitement',
                'Votre demande d\'inscription est en cours de traitement. Vous recevrez un email une fois votre compte approuvé.',
                'nader@metadia.net',
                [admin_email],
            )

            # Envoyer une notification au super administrateur
            super_admin_email = 'nader21benammar@gmail.com'  # Remplacez par l'email du super administrateur
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



def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'marketing':
                return redirect('marketing_dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')



@login_required
def marketing_dashboard(request):
    return render(request, 'marketing_dashboard.html')

@staff_member_required
def approve_registration(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = True
    user.save()

    password = request.POST.get('password')


    # Mail de confirmation à l'utilisateur
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
        # Envoyer un email de refus à l'utilisateur
        send_mail(
            'Demande d\'inscription refusée',
            f'Votre demande d\'inscription a été refusée pour la raison suivante : {reason}',
            'nader@metadia.net',  # Remplacez par votre adresse email
            [user.email],
        )
        # Supprimer l'entreprise associée
        if user.company:
            user.company.delete()
        # Supprimer l'utilisateur
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


@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@login_required
def gestion_contacts(request):
    contacts = Contact.objects.filter(company=request.user.company)
    groupes = Group.objects.filter(company=request.user.company)
    return render(request, 'gestion_contacts.html', {'contacts': contacts, 'groupes': groupes})

@login_required
def gestion_utilisateurs_marketing(request):
    employees = CustomUser.objects.filter(company=request.user.company, role='marketing')
    return render(request, 'gestion_utilisateurs_marketing.html', {'employees': employees})

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
            employee.company = request.user.company  # Définir le company_id de l'employé
            employee.set_password(form.cleaned_data['password'])
            employee.save()

            # Envoyer un email à l'employé
            send_mail(
                'Ouverture de votre compte',
                f'Bonjour {employee.first_name},\n\nVotre compte a été créé avec succès. Vous pouvez vous connecter avec les informations suivantes :\n\nNom d\'utilisateur : {employee.username}\nMot de passe : {form.cleaned_data["password"]}\n\nLien de connexion : http://127.0.0.1:8000/login/\n\nCordialement,\nL\'équipe',
                'nader@metadia.net',
                [employee.email],
            )

            return redirect('gestion_utilisateurs_marketing')
    else:
        form = AddEmployeeForm()
    return render(request, 'add_employee.html', {'form': form})

@login_required
def accueil_MK_User(request):
    # Logic to handle the marketing user dashboard
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
    groups = Group.objects.filter(company=request.user.company)
    return render(request, 'gestion_groupes.html', {'groups': groups})

def gestion_campagnes(request):
    return render(request, 'gestion_campagnes_admin.html')

@login_required
def gestion_campagnes_mk(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        group_id = request.POST.get('group')
        content_id = request.POST.get('content')
        group = get_object_or_404(Group, id=group_id)
        content = get_object_or_404(Content, id=content_id)
        Campaign.objects.create(
            name=name,
            description=description,
            group=group,
            message=content.html_content
        )
        messages.success(request, 'Campagne créée avec succès.')
        return redirect('gestion_campagnes')
    groups = Group.objects.filter(company=request.user.company)
    contents = Content.objects.all()
    return render(request, 'gestion_campagnes_MK.html', {'groups': groups, 'contents': contents})

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
        # Stocker les informations de connexion dans la session
        request.session['admin_username'] = request.user.username
        request.session['employee_username'] = employee.username
        request.session.modified = True  # Assurez-vous que la session est marquée comme modifiée
        login(request, employee)
        return redirect('marketing_dashboard')
    return redirect('gestion_utilisateurs_marketing')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
def update_profile(request):
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
        return redirect('gestion_profile_admin')
    return render(request, 'gestion_profile_admin.html')


@login_required
def gestion_profile_admin(request):
    user = request.user
    company = user.company  # Assurez-vous que l'utilisateur a une relation avec l'entreprise
    logo_url = company.logo.url if company.logo else None  # Assurez-vous que l'entreprise a un logo
    timezones = pytz.all_timezones  # Get the list of all timezones
    detected_timezone = timezone.get_current_timezone_name()  # Detect the current timezone
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
        'detected_timezone': detected_timezone,  # Pass the detected timezone to the template
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
    company = user.company  # Assurez-vous que l'utilisateur a une relation avec l'entreprise
    logo_url = company.logo.url if company.logo else None  # Assurez-vous que l'entreprise a un logo
    timezones = pytz.all_timezones  # Get the list of all timezones
    detected_timezone = timezone.get_current_timezone_name()  # Detect the current timezone
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
        'detected_timezone': detected_timezone,  # Pass the detected timezone to the template
    })

@login_required
def record_campaign_action(request, campaign_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        timestamp = timezone.now()  # Utilise le fuseau horaire de l'utilisateur
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
            update_session_auth_hash(request, user)  # Important, to keep the user logged in
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

@login_required
def editeur_contenu(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        html_content = request.POST.get('html_content')
        Content.objects.create(title=title, html_content=html_content)
        messages.success(request, 'Contenu créé avec succès.')
        return redirect('marketing_dashboard')
    
    user = request.user
    company = user.company  # Assurez-vous que l'utilisateur a une relation avec l'entreprise
    logo_url = company.logo.url if company.logo else None  # Assurez-vous que l'entreprise a un logo
    company_name = company.name if company else "Nom de l'entreprise"
    
    return render(request, 'editeur_contenu.html', {
        'logo_url': logo_url,
        'company_name': company_name,
    })

@login_required
def demande_assistance(request):
    return render(request, 'demande_assistance.html')

@login_required
def gestion_profile_MK(request):
    return render(request, 'gestion_profile_MK.html')



@login_required
def update_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important, to keep the user logged in
            messages.success(request, 'Votre mot de passe a été mis à jour avec succès.')
            return redirect('securite')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'update_password.html', {'form': form})


@login_required
def import_contacts(request):
    if request.method == 'POST':
        groupe_id = request.POST.get('groupe')
        groupe = get_object_or_404(Group, id=groupe_id)
        csv_file = request.FILES['csv_file']
        decoded_file = csv_file.read().decode('latin1').splitlines()
        reader = csv.reader(decoded_file, delimiter=';')  # Utilisation du délimiteur ;
        next(reader)  # Ignorer la première ligne (les en-têtes)
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
                age=int(age) if age.isdigit() else None,  # Convertir l'âge en entier
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
                # Créer une copie du contact dans le nouveau groupe
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

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from google.cloud import aiplatform

# Initialisation de Vertex AI avec le bon projet
aiplatform.init(project="django mass mailing web app")  # Remplace par ton vrai ID Google Cloud

@csrf_exempt
def generate_content(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prompt = data.get('prompt', '')

            # Utilisez l'API Gemini pour générer du contenu
            api_url = "https://api.gemini.com/generate"  # Remplacez par l'URL réelle de l'API
            api_key = settings.GEMINI_API_KEY

            response = requests.post(api_url, json={
                "prompt": prompt,
                "max_tokens": 500
            }, headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            })

            print("Réponse de l'API Gemini:", response.json())  # Affichez la réponse brute dans la console

            if response.status_code == 200:
                generated_content = response.json().get('generated_text', '')
                return JsonResponse({'generated_content': generated_content})
            else:
                return JsonResponse({'error': 'Failed to generate content'}, status=500)
        except Exception as e:
            print("Erreur:", e)  # Affichez l'erreur dans la console
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)

