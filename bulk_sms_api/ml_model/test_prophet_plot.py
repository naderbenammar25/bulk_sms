import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt

# Chargez vos données ici (exemple)
from regressor_sto_model import load_data_from_db, prepare_prophet_data

data = load_data_from_db()
data['EVENT_DATE'] = pd.to_datetime(data['EVENT_DATE'], format='%Y-%m-%d %H:%M:%S')

for contact_hash in data['ContactHash'].unique():
    prophet_data = prepare_prophet_data(data, contact_hash)
    if len(prophet_data) < 2:
        print(f"Contact {contact_hash} : pas assez de données pour la prédiction.")
        continue

    model = Prophet()
    model.fit(prophet_data)
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    best_row = forecast.loc[forecast['yhat'].idxmax()]
    print(f"Contact {contact_hash} : meilleur créneau = {best_row['ds']}, score prédit = {best_row['yhat']}")

    fig = model.plot(forecast)
    plt.title(f"Prévision du taux d'ouverture pour {contact_hash}")
    plt.show()