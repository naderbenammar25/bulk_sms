import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from ml_model.regressor_sto_model import load_data_from_db, get_statistics

# Charger les données depuis la base de données
data = load_data_from_db()
data['EVENT_DATE'] = pd.to_datetime(data['EVENT_DATE'], format='%Y-%m-%d %H:%M:%S')
stats = get_statistics(data)

# Créer une application Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Layout du dashboard
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Composant pour gérer l'URL

    # Contenu principal
    html.Div(id='page-content', style={'padding': '20px'}),
])

# Callback pour mettre à jour le contenu en fonction de l'URL
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/open-rate':
        return open_rate_page(stats)
    elif pathname == '/click-rate':
        return click_rate_page(stats)
    elif pathname == '/hourly-distribution':
        return hourly_distribution_page(stats)
    elif pathname == '/temporal-distance':
        return temporal_distance_page(data)
    else:
        return open_rate_page(stats)

# Page Open Rate
def open_rate_page(stats):
    if stats['total_sent'] == 0:  # Vérifier si les données sont valides
        return html.Div("Aucune donnée disponible pour le taux d'ouverture.", style={'color': 'red'})

    return html.Div([
        html.H2("Taux d'ouverture des emails"),
        dcc.Graph(
            id='open-rate-chart',
            figure=px.pie(
                names=['Ouverts', 'Non Ouverts'],
                values=[stats['total_opened'], stats['total_sent'] - stats['total_opened']],
                title="Répartition des emails ouverts"
            )
        ),
    ])

# Page Click Rate
def click_rate_page(stats):
    if stats['total_sent'] == 0:  # Vérifier si les données sont valides
        return html.Div("Aucune donnée disponible pour le taux de clics.", style={'color': 'red'})

    return html.Div([
        html.H2("Taux de clics des emails"),
        dcc.Graph(
            id='click-rate-chart',
            figure=px.pie(
                names=['Clics', 'Non Clics'],
                values=[stats['total_clicked'], stats['total_sent'] - stats['total_clicked']],
                title="Répartition des clics"
            )
        ),
    ])

# Page Distribution par Heure
def hourly_distribution_page(stats):
    if stats['open_distribution'].empty or stats['unsubscribe_distribution'].empty:
        return html.Div("Aucune donnée disponible pour la distribution horaire.", style={'color': 'red'})

    return html.Div([
        html.H2("Distribution horaire des ouvertures et désabonnements"),
        dcc.Graph(
            id='hourly-open-distribution-chart',
            figure=px.bar(
                x=stats['open_distribution'].index,
                y=stats['open_distribution'].values,
                title="Distribution des ouvertures par heure",
                labels={'x': 'Heure', 'y': 'Nombre d\'ouvertures'}
            )
        ),
        dcc.Graph(
            id='hourly-unsubscribe-distribution-chart',
            figure=px.bar(
                x=stats['unsubscribe_distribution'].index,
                y=stats['unsubscribe_distribution'].values,
                title="Distribution des désabonnements par heure",
                labels={'x': 'Heure', 'y': 'Nombre de désabonnements'}
            )
        ),
    ])

# Page Distance Temporelle
def temporal_distance_page(data):
    # Calculer la distance temporelle moyenne entre l'envoi et l'ouverture
    data['time_diff'] = (data[data['EVENT_TYPE'] == 'open']['EVENT_DATE'] - 
                         data[data['EVENT_TYPE'] == 'sent']['EVENT_DATE']).dt.total_seconds() / 3600  # En heures

    if data['time_diff'].empty:
        return html.Div("Aucune donnée disponible pour la distance temporelle.", style={'color': 'red'})

    time_diff_avg = data.groupby(data['EVENT_DATE'].dt.hour)['time_diff'].mean()

    return html.Div([
        html.H2("Distance temporelle moyenne entre l'envoi et l'ouverture"),
        dcc.Graph(
            id='temporal-distance-chart',
            figure=px.line(
                x=time_diff_avg.index,
                y=time_diff_avg.values,
                title="Distance temporelle moyenne (en heures)",
                labels={'x': 'Heure de la journée', 'y': 'Distance temporelle moyenne (heures)'}
            )
        ),
    ])

# Lancer l'application Dash
if __name__ == '__main__':
    app.run_server(debug=True)