import django
import pytz
from django.utils import timezone
from campaigns.models import Campaign, CampaignAction, CustomUser
import uuid

django.setup()

# Créez un utilisateur de test avec un nom d'utilisateur unique
username = f'testuser_{uuid.uuid4()}'
user = CustomUser.objects.create_user(username=username, password='password', timezone='Europe/Paris')

# Créez une campagne de test
campaign = Campaign.objects.create(name='Test Campaign', description='This is a test campaign.')

# Ajoutez des actions de campagne
CampaignAction.objects.create(user=user, campaign=campaign, action='Action 1', timestamp=timezone.now())
CampaignAction.objects.create(user=user, campaign=campaign, action='Action 2', timestamp=timezone.now())

print('Actions de campagne ajoutées avec succès.')