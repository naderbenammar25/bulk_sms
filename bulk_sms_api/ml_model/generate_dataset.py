import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Configuration
num_events = 120000
num_users = 2942
event_types = ['Sent', 'Open', 'Click', 'Unsubscribed', 'Complaint', 'Bounced']
campaign_names = ['Campaign1', 'Campaign2', 'Campaign3']
communication_names = ['Comm1', 'Comm2', 'Comm3']
subjects = ['Subject1', 'Subject2', 'Subject3']
locations = [
    'Ariana', 'Tunis', 'Beja', 'Ben Arous', 'Bizerte', 'Gabes', 'Gafsa', 'Jendouba', 'Kairouan', 'Kasserine',
    'Kebili', 'Kef', 'Mahdia', 'Manouba', 'Medenine', 'Monastir', 'Nabeul', 'Sfax', 'Sidi Bouzid', 'Siliana',
    'Sousse', 'Tataouine', 'Tozeur', 'Zaghouan'
]

# Probabilités ajustées 
event_probabilities = {
    'Click': 0.35,         # 35% des événements
    'Open': 0.30,          # 30% des événements
    'Unsubscribed': 0.20,  # 20% des événements
    'Bounced': 0.10,       # 10% des événements
    'Sent': 0.03,          # 3% des événements
    'Complaint': 0.02      # 2% des événements
}

# Générer des données aléatoires
data = {
    'EVENT_DATE': [],
    'EVENT_TYPE': [],
    'MessageHash': [],
    'ContactHash': [],
    'COMMUNICATION_NAME': [],
    'COMMUNICATION_SUBJECT': [],
    'CAMPAIGN_NAME': [],
    'EVENT_LOCATION': []  
}

start_date = datetime(2021, 1, 1)
for _ in range(num_events):
    event_date = start_date + timedelta(minutes=random.randint(0, 525600))  
    event_type = random.choices(list(event_probabilities.keys()), weights=event_probabilities.values(), k=1)[0]
    message_hash = f"msg_{random.randint(1, num_events)}"
    contact_hash = f"user_{random.randint(1, num_users)}"
    communication_name = random.choice(communication_names)
    subject = random.choice(subjects)
    campaign_name = random.choice(campaign_names)
    event_location = random.choice(locations)  
    
    data['EVENT_DATE'].append(event_date)
    data['EVENT_TYPE'].append(event_type)
    data['MessageHash'].append(message_hash)
    data['ContactHash'].append(contact_hash)
    data['COMMUNICATION_NAME'].append(communication_name)
    data['COMMUNICATION_SUBJECT'].append(subject)
    data['CAMPAIGN_NAME'].append(campaign_name)
    data['EVENT_LOCATION'].append(event_location)

# création du DataFrame
df = pd.DataFrame(data)

# Sauvegarder dans un fichier CSV
df.to_csv('synthetic_dataset_with_locations.csv', index=False)
print("Dataset généré avec succès dans 'synthetic_dataset_with_locations.csv'.")