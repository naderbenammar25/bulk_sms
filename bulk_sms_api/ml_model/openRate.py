import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from regressor_sto_model import open_rate_message_time_slot, get_all_indexes_contact, load_data_from_db

def test_open_rate_message_time_slot():
    # Charger les données à partir de la base de données
    data = load_data_from_db()
    data['event_date'] = pd.to_datetime(data['event_date'], format='%Y-%m-%d %H:%M:%S')
    
    # Définir les paramètres de test
    contact_hash = "user_2080"
    
    # Appeler la fonction open_rate_message_time_slot
    open_rate = open_rate_message_time_slot(contact_hash, data)
    
    # Afficher les résultats pour vérification
    print(f"open_rate: {open_rate}")
    
    # Vérifier les résultats
    assert isinstance(open_rate, np.ndarray), f"Expected open_rate to be a numpy array but got {type(open_rate)}"
    assert open_rate.shape == (24,), f"Expected open_rate to have shape (24,) but got {open_rate.shape}"
    print("test_open_rate_message_time_slot passed.")
    
    # Visualiser les résultats
    plt.bar(range(24), open_rate)
    plt.xlabel('Hour of the day')
    plt.ylabel('Open rate')
    plt.title('Open rate per hour for contact')
    plt.show()

if __name__ == "__main__":
    test_open_rate_message_time_slot()