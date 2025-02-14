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

from django.core.mail import send_mail
from django.shortcuts import render
from .models import Company, CustomUser

def register(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        logo = request.FILES.get('logo')
        primary_color = request.POST.get('primary_color')
        secondary_color = request.POST.get('secondary_color')
        tertiary_color = request.POST.get('tertiary_color')
        admin_username = request.POST.get('admin_username')
        admin_email = request.POST.get('admin_email')
        admin_password = request.POST.get('admin_password')

        # Vérifier que l'utilisateur a sélectionné les couleurs
        if not (primary_color and secondary_color and tertiary_color):
            return render(request, 'index.html', {'error': 'Vous devez sélectionner toutes les couleurs.'})

        # Créer l'entreprise
        colors = ','.join([primary_color, secondary_color, tertiary_color])
        company = Company.objects.create(name=company_name, logo=logo, color=colors)

        # Créer l'administrateur sans l'activer
        admin_user = CustomUser.objects.create_user(
            username=admin_username,
            email=admin_email,
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
        super_admin_email = 'superadmin@example.com'  # Remplacez par l'email du super administrateur
        send_mail(
            'Nouvelle demande d\'inscription',
            f'Une nouvelle demande d\'inscription a été soumise par {admin_username}. Veuillez la traiter.',
            'nader@metadia.net',
            [super_admin_email],
        )

        return render(request, 'index.html', {'message': 'Votre demande d\'inscription est en cours de traitement.'})

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

    # Envoyer un email de confirmation à l'utilisateur
    send_mail(
        'Compte approuvé',
        'Votre compte a été approuvé. Vous pouvez maintenant vous connecter.',
        'nader@metadia.net',  # Remplacez par votre adresse email
        [user.email],
    )

    return redirect(reverse('admin:auth_user_changelist'))

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

def gestion_contacts(request):
    return render(request, 'gestion_contacts.html')

@login_required
def gestion_utilisateurs_marketing(request):
    employees = CustomUser.objects.filter(role='marketing')
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
            employee.set_password(form.cleaned_data['password'])
            employee.save()

            # Envoyer un email à l'employé
            send_mail(
                'Ouverture de votre compte',
                f'Bonjour {employee.first_name},\n\nVotre compte a été créé avec succès. Vous pouvez vous connecter avec les informations suivantes :\n\nNom d\'utilisateur : {employee.username}\nMot de passe : {form.cleaned_data["password"]}\n\nLien de connexion : http://127.0.0.1:8000/login/\n\nCordialement,\nL\'équipe',
                'nader@metadia.netr',
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


def gestion_groupes(request):
    return render(request, 'gestion_groupes.html')

def gestion_campagnes(request):
    return render(request, 'gestion_campagnes.html')

def visualisation_performances(request):
    return render(request, 'visualisation_performances.html')

def gestion_feedback(request):
    return render(request, 'gestion_feedback.html')

def demander_intervention(request):
    return render(request, 'demander_intervention.html')