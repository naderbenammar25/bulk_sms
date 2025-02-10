import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Contact, Group, Company
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group as AuthGroup

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




from django.contrib.auth.models import Group as AuthGroup

def register(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        logo = request.FILES.get('logo')
        colors = request.POST.getlist('colors')
        admin_username = request.POST.get('admin_username')
        admin_email = request.POST.get('admin_email')
        admin_password = request.POST.get('admin_password')

        # Vérifier que l'utilisateur a sélectionné au moins une couleur
        if not colors:
            return render(request, 'index.html', {'error': 'Vous devez sélectionner au moins une couleur.'})

        # Créer l'entreprise
        company = Company.objects.create(name=company_name, logo=logo, color=','.join(colors))

        # Créer l'administrateur
        admin_user = User.objects.create_user(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            role='admin',
            company=company
        )

        # Ajouter l'utilisateur au groupe des administrateurs
        admin_group, created = AuthGroup.objects.get_or_create(name='Administrateurs')
        admin_user.groups.add(admin_group)

        return redirect('login')
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
def admin_dashboard(request):
    user = request.user
    company = user.company
    colors = company.color.split(',')
    logo_url = company.logo.url
    return render(request, 'admin_dashboard.html', {'colors': colors, 'logo_url': logo_url})

@login_required
def marketing_dashboard(request):
    return render(request, 'marketing_dashboard.html')