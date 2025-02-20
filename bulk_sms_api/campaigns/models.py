from django.db import models
from django.contrib.auth.models import AbstractUser

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
    ROLE_CHOICES = (
        ('superadmin', 'Super Administrateur'),
        ('admin', 'Administrateur'),
        ('marketing', 'Employé en Marketing'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='marketing')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Group(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Contact(models.Model):
    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="contacts")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class Campaign(models.Model):
    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="campaigns")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Campaign to {self.group.name} on {self.created_at}"