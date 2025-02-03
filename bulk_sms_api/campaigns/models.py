from django.db import models

class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Contact(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="contacts")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class Campaign(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="campaigns")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Campaign to {self.group.name} on {self.created_at}"
