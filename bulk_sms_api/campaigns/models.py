from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class Content(models.Model):
    title = models.CharField(max_length=255)
    html_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='logos/')
    color = models.CharField(max_length=100)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    id = models.AutoField(primary_key=True)
    is_logged_in = models.BooleanField(default=False)
    ROLE_CHOICES = (
        ('superadmin', 'Super Administrateur'),
        ('admin', 'Administrateur'),
        ('marketing', 'Employé en Marketing'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='marketing')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=50, default='Français')
    date_format = models.CharField(max_length=20, default='JJ-MM-YYYY')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Group(models.Model):
    STATUS_CHOICES = (
        ('Actif', 'Actif'),
        ('Inactif', 'Inactif'),
    )
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="groups", default=1)  # Remplacez 1 par l'ID d'une entreprise existante
    creationDate = models.DateTimeField(auto_now_add=True)  # Date de création
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Actif')  # Statut du groupe

    def __str__(self):
        return self.name

class Contact(models.Model):
    STATUS_CHOICES = (
        ('Actif', 'Actif'),
        ('Inactif', 'Inactif'),
    )
    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="contacts")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="contacts", default=1)  # Remplacez 1 par l'ID d'une entreprise existante
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    age = models.IntegerField(null=True, blank=True)  # Nouvelle colonne pour l'âge
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Actif')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class Campaign(models.Model):
    STATUS_CHOICES = (
        ('brouillon', 'Brouillon'),
        ('planifiée', 'Planifiée'),
        ('en cours', 'En cours'),
        ('suspendue', 'Suspendue'),
        ('terminée', 'Terminée'),
        ('historisée', 'Historisée'),
    )

    TYPE_CHOICES = (
        ('brouillon', 'Brouillon'),
        ('planifié', 'Planifié'),
        ('lancement_rapide', 'Lancement Rapide'),
    )

    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="campaigns")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, default='No name provided.')
    launch_date = models.DateTimeField(null=True, blank=True)  # Date et heure de lancement
    end_date = models.DateTimeField(null=True, blank=True)  # Date de fin de la campagne
    duration = models.IntegerField(help_text="Durée de la campagne en jours")  # Durée de la campagne en jours
    messages_per_period = models.IntegerField(help_text="Nombre de messages par période")  # Nombre de messages par période
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='brouillon')  # Statut de la campagne
    campaign_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='brouillon')  # Type de la campagne
    content = models.ForeignKey(Content, on_delete=models.SET_NULL, null=True, blank=True)  # Contenu de la campagne
    duration_unit = models.CharField(max_length=20, default='jours')  # Unité de durée
    period_unit = models.CharField(max_length=20, default='semaine')  # Unité de période

    def __str__(self):
        return f"Campaign to {self.group.name} on {self.created_at}"

class CampaignAction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    campaign = models.ForeignKey('Campaign', on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField()

    def __str__(self):
        return f'{self.user.username} - {self.action} - {self.timestamp}'

class EmailTracking(models.Model):
    EVENT_DATE = models.DateTimeField(auto_now_add=True)
    EVENT_TYPE = models.CharField(max_length=50, default='Sent')
    MessageHash = models.CharField(max_length=255)
    ContactHash = models.ForeignKey('Contact', on_delete=models.CASCADE)  # Utiliser une clé étrangère pour ContactHash
    COMMUNICATION_NAME = models.CharField(max_length=255, default='Default Communication Name')
    COMMUNICATION_SUBJECT = models.CharField(max_length=255, default='Default Communication Subject')
    CAMPAIGN_NAME = models.CharField(max_length=255, default='Default Campaign Name')
    
    def __str__(self):
        return f"{self.COMMUNICATION_NAME} - {self.ContactHash} - {self.EVENT_DATE}"
    

from django.db import models
from django.utils.timezone import now

class Feedback(models.Model):
    contact_email = models.EmailField()  # Email du contact ayant répondu
    campaign = models.ForeignKey('Campaign', on_delete=models.CASCADE, related_name='feedbacks')  # Campagne associée
    message = models.TextField()  # Message reçu du contact
    response = models.TextField(blank=True, null=True)  # Réponse de l'administrateur
    created_at = models.DateTimeField(default=now)  # Date de réception du feedback
    responded_at = models.DateTimeField(blank=True, null=True)  # Date de réponse de l'administrateur

    def __str__(self):
        return f"Feedback de {self.contact_email} pour la campagne {self.campaign.name}"