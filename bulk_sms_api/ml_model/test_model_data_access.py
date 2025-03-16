import pandas as pd
from regressor_sto_model import load_data_from_db, create_dataset

def test_data_access():
    # Charger les données à partir de la base de données
    
    
    data = load_data_from_db()
    
    if  load_data_from_db():
        print("Les données n'ont pas été chargées correctement.")
        return
    