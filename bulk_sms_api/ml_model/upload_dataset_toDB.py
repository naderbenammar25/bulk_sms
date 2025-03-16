import pandas as pd
import psycopg2
from psycopg2 import sql

# Charger les données du fichier CSV
csv_file_path = "synthetic_dataset_remake.csv"
data = pd.read_csv(csv_file_path)

# Connexion à la base de données PostgreSQL
conn = psycopg2.connect(
    dbname="new_mass_mailing_db",
    user="postgres",
    password="user01",
    host="localhost",
    port="5432"
)
cur = conn.cursor()


# Insérer les données dans la table campaigns_emailtracking2
insert_query = """
INSERT INTO campaigns_emailtracking2 (EVENT_DATE, EVENT_TYPE, MessageHash, ContactHash, COMMUNICATION_NAME, COMMUNICATION_SUBJECT, CAMPAIGN_NAME)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

for index, row in data.iterrows():
    cur.execute(insert_query, (
        row['EVENT_DATE'],
        row['EVENT_TYPE'],
        row['MessageHash'],
        row['ContactHash'],
        row['COMMUNICATION_NAME'],
        row['COMMUNICATION_SUBJECT'],
        row['CAMPAIGN_NAME']
    ))

# Valider les transactions et fermer la connexion
conn.commit()
cur.close()
conn.close()

print("Les données ont été importées avec succès dans la table campaigns_emailtracking2.")