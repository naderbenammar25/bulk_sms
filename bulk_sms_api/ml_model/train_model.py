import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
from .regressor_sto_model import load_data_from_db, create_dataset

def train_and_save_model(X, y, model_path='random_forest_model.pkl'):
    """
    Entraîne un modèle RandomForestRegressor et le sauvegarde dans un fichier.
    """
    print("Entraînement du modèle RandomForestRegressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    joblib.dump(model, model_path)
    print(f"Modèle entraîné et sauvegardé dans {model_path}.")

if __name__ == "__main__":

    print("Chargement des données...")
    data = load_data_from_db()
    data['EVENT_DATE'] = pd.to_datetime(data['EVENT_DATE'], format='%Y-%m-%d %H:%M:%S')  
    data['day_of_week'] = data['EVENT_DATE'].dt.day_name()  

    # Définir les noms de colonnes pour le dataset
    # Ces noms de colonnes doivent correspondre à ceux utilisés dans la fonction create_dataset
    column_names = ["COMMUNICATION_NAME", "ContactHash", "MessageHash", "OR 0-1", "OR 1-2", "OR 2-3", "OR 3-4", "OR 4-5", "OR 5-6", "OR 6-7", "OR 7-8", "OR 8-9", "OR 9-10", "OR 10-11", "OR 11-12",
    "OR 12-13", "OR 13-14", "OR 14-15", "OR 15-16", "OR 16-17", "OR 17-18", "OR 18-19", "OR 19-20", "OR 20-21", "OR 21-22", "OR 22-23", "OR 23-24",
    "CR 0-1", "CR 1-2", "CR 2-3", "CR 3-4", "CR 4-5", "CR 5-6", "CR 6-7", "CR 7-8", "CR 8-9", "CR 9-10", "CR 10-11", "CR 11-12",
    "CR 12-13", "CR 13-14", "CR 14-15", "CR 15-16", "CR 16-17", "CR 17-18", "CR 18-19", "CR 19-20", "CR 20-21", "CR 21-22", "CR 22-23", "CR 23-24",
    "OR-C 0-1", "OR-C 1-2", "OR-C 2-3", "OR-C 3-4", "OR-C 4-5", "OR-C 5-6", "OR-C 6-7", "OR-C 7-8", "OR-C 8-9", "OR-C 9-10", "OR-C 10-11", "OR-C 11-12", 
    "OR-C 12-13", "OR-C 13-14", "OR-C 14-15", "OR-C 15-16", "OR-C 16-17", "OR-C 17-18", "OR-C 18-19", "OR-C 19-20", "OR-C 20-21", "OR-C 21-22", "OR-C 22-23", "OR-C 23-24",
    "CR-C 0-1", "CR-C 1-2", "CR-C 2-3", "CR-C 3-4", "CR-C 4-5", "CR-C 5-6", "CR-C 6-7", "CR-C 7-8", "CR-C 8-9", "CR-C 9-10", "CR-C 10-11", "CR-C 11-12", 
    "CR-C 12-13", "CR-C 13-14", "CR-C 14-15", "CR-C 15-16", "CR-C 16-17", "CR-C 17-18", "CR-C 18-19", "CR-C 19-20", "CR-C 20-21", "CR-C 21-22", "CR-C 22-23", "CR-C 23-24",
    "fitSA", "fitAC", "Label"]

    sent_open_hour_range = 36  
    open_click_hour_range = 24  

    
    print("Création du dataset...")
    df, X, y = create_dataset(data, sent_open_hour_range, open_click_hour_range, column_names)
    print("Dataset créé avec succès.")

    # Entraîner et sauvegarder le modèle
    train_and_save_model(X, y, model_path='random_forest_model.pkl')