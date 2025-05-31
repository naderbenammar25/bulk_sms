import pandas as pd
import psycopg2

# Charger le dataset
dataset_path = 'synthetic_dataset_with_locations.csv'  # Fichier CSV généré
data = pd.read_csv(dataset_path)

# Connexion à la base de données
conn = psycopg2.connect(
    dbname="new_mass_mailing_db",
    user="postgres",
    password="user01",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()


for index, row in data.iterrows():
    cursor.execute("""
        INSERT INTO campaigns_emailtracking2 (
            "EVENT_DATE", "EVENT_TYPE", "MessageHash", "ContactHash", "COMMUNICATION_NAME",
            "COMMUNICATION_SUBJECT", "CAMPAIGN_NAME", "EVENT_LOCATION"
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        row['EVENT_DATE'], row['EVENT_TYPE'], row['MessageHash'], row['ContactHash'],
        row['COMMUNICATION_NAME'], row['COMMUNICATION_SUBJECT'], row['CAMPAIGN_NAME'],
        row['EVENT_LOCATION']
    ))

# Valider la transaction
conn.commit()
cursor.close()
conn.close()

print("Dataset uploadé avec succès dans la base de données.")