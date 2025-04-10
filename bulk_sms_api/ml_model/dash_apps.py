import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from ml_model.regressor_sto_model import load_data_from_db, get_statistics, create_dataset, get_sent_hour

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

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/open-rate':
        return deliverability_statistics_page(stats)
    elif pathname == '/click-rate':
        return click_rate_page(stats)
    elif pathname == '/hourly-distribution':
        return hourly_distribution_page(stats)
    elif pathname == '/mail-status':
        return mail_status_page(stats)
    elif pathname == '/bounce-rate':
        return bounce_rate_page(stats)
    elif pathname == '/temporal-distance':
        return temporal_distance_page(data)
    elif pathname == '/tunisia-map':
        return tunisia_map_page(data)
    elif pathname == '/predictions':
        return predictions_page(data)
    elif pathname == '/kpi-open-rate':
        return kpi_open_rate(stats)
    elif pathname == '/kpi-click-rate':
        return kpi_click_rate(stats)
    elif pathname == '/kpi-bounce-rate':
        return kpi_bounce_rate(stats)
    elif pathname == '/kpi-unsubscribe-rate':
        return kpi_unsubscribe_rate(stats)
    
def deliverability_statistics_page(stats):
    if stats['total_sent'] == 0:
        return html.Div("Aucune donnée disponible.", className="dashboard-container")
    
    # Calcul des données
    total_bounced = stats['total_bounced']
    total_sent = stats['total_sent']
    non_bounced = total_sent - total_bounced
    open_rate = stats['open_rate']
    click_rate = stats['click_rate']
    unsubscribe_rate = stats['unsubscribe_rate']

    event_counts = {
        'Sent': stats['total_sent'],
        'Open': stats['total_opened'],
        'Click': stats['total_clicked'],
        'Bounce': stats['total_bounced'],
        'Unsubscribed': stats['total_unsubscribed']
    }

    return html.Div([
        html.Div([
            html.H1(
                "Répartition des Événements", 
                style={'textAlign': 'center', 'marginBottom': '10px', 'color': '#2c3e50'}  # Réduction de la marge inférieure
            )
        ], className="dashboard-container"),
        
        
        
        # Première ligne de cartes
        html.Div([
            # Carte 1 - Diagramme en anneau
            html.Div([
                html.Div("Répartition des Événements", className="card-title"),
                dcc.Graph(
                    figure=px.pie(
                        names=list(event_counts.keys()),
                        values=list(event_counts.values()),
                        hole=0.5,
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    ).update_layout(
                        showlegend=True,
                        margin={"t": 0, "b": 0, "l": 0, "r": 0}
                    ),
                    config={'displayModeBar': False},
                    className="graph-container"
                )
            ], className="data-card"),
            
        ], className="card-row"),
        
        
    ], className="dashboard-container")
# Page Click Rate




def kpi_open_rate(stats):
    return html.Div([
        html.Div(
            "Total des messages ouverts", 
            className="kpi-label", 
            style={
                
                'fontSize': '1rem',  
                'textAlign': 'center',  
                'color': '#c60c30',  
                'marginBottom': '10px'  # Espacement sous le titre

                }
            ),
            html.Div(
                f"{stats['total_opened'] / 1000:.1f} K", 
                className="kpi-value", 
                style={
                    # Taille du texte en gros
                    'fontSize': '2.5rem',
                'fontFamily': 'Verdana, sans-serif',  # Police de caractères
                'textAlign': 'center',  # Centré
                'color': 'black',  # Couleur noire
                
            }
        )
    ], className="kpi-card-small", style={
        
        'display': 'flex',  # Affichage en flexbox
        'flexDirection': 'column',  # Orientation verticale
        'alignItems': 'center',  # Centrer les éléments horizontalement
        'justifyContent': 'center',
          # Hauteur de la carte
    })


def kpi_click_rate(stats):
    return html.Div([
        html.Div(
            "Total des clics", 
            className="kpi-label", 
            style={
                'fontSize': '1rem',  # Taille du texte en gros
                'textAlign': 'center',  # Centré
                'color': '#c60c30',  # Couleur rouge
                'marginBottom': '10px'  # Espacement sous le titre

            }
        ),
        html.Div(
            f"{stats['total_clicked'] / 1000:.1f} K", 
            className="kpi-value", 
            style={
                'fontSize': '2.5rem',
                'fontFamily': 'Verdana, sans-serif',  # Police de caractères # Taille du texte en gros
                'textAlign': 'center',  # Centré
                'color': 'black',  # Couleur noire
                
            }
        )
    ], className="kpi-card-small", style={
        
        'display': 'flex',  # Affichage en flexbox
        'flexDirection': 'column',  # Orientation verticale
        'alignItems': 'center',  # Centrer les éléments horizontalement
        'justifyContent': 'center'  # Centrer les éléments verticalement
    })


def kpi_bounce_rate(stats):
    return html.Div([
        html.Div(
            "Total des messages rebondis", 
            className="kpi-label", 
            style={
                'fontSize': '1rem',  # Taille du texte en gros
                'textAlign': 'center',  # Centré
                'color': '#c60c30',  # Couleur rouge
                'marginBottom': '10px'  # Espacement sous le titre
            }
        ),
        html.Div(
            f"{stats['total_bounced']/ 1000:.1f} K", 
            className="kpi-value", 
            style={
                
                'textAlign': 'center',  # Centré
                'color': 'black',  # Couleur noire
                'fontSize': '2.5rem',
                'fontFamily': 'Verdana, sans-serif',  # Police de caractères
            }
        )
    ], className="kpi-card-small", style={
        
        'display': 'flex',  # Affichage en flexbox
        'flexDirection': 'column',  # Orientation verticale
        'alignItems': 'center',  # Centrer les éléments horizontalement
        'justifyContent': 'center'  # Centrer les éléments verticalement
    })


def kpi_unsubscribe_rate(stats):
    return html.Div([
        html.Div(
            "total de désabonnements", 
            className="kpi-label", 
            style={
                'fontSize': '1rem',  # Taille du texte en gros
                'textAlign': 'center',  # Centré
                'color': '#c60c30',  # Couleur rouge
                'marginBottom': '10px'  # Espacement sous le titre
            }
        ),
        html.Div(
            f"{stats['total_unsubscribed']/ 1000:.1f} K", 
            className="kpi-value", 
            style={
                
                'textAlign': 'center',  # Centré
                'color': 'black',  # Couleur noire
                'fontSize': '2.5rem',
                'fontFamily': 'Verdana, sans-serif',  # Police de caractères
            }
        )
    ], className="kpi-card-small", style={
        
        'display': 'flex',  # Affichage en flexbox
        'flexDirection': 'column',  # Orientation verticale
        'alignItems': 'center',  # Centrer les éléments horizontalement
        'justifyContent': 'center'  # Centrer les éléments verticalement
    })



# Page Distance Temporelle
def temporal_distance_page(data):
    # Filtrer les événements 'sent' et 'open'
    sent_events = data[data['EVENT_TYPE'] == 'sent']
    open_events = data[data['EVENT_TYPE'] == 'open']
    
    # Fusionner pour calculer les différences de temps
    merged = pd.merge(
        sent_events, 
        open_events, 
        on=['ContactHash', 'COMMUNICATION_NAME'], 
        suffixes=('_sent', '_open')
    )
    
    if merged.empty:
        return html.Div("Aucune donnée disponible pour la distance temporelle.", style={'color': 'red'})
    
    merged['time_diff'] = (merged['EVENT_DATE_open'] - merged['EVENT_DATE_sent']).dt.total_seconds() / 3600
    time_diff_avg = merged.groupby(merged['EVENT_DATE_sent'].dt.hour)['time_diff'].mean()
    
    return html.Div([
        html.H2("Distance temporelle moyenne entre l'envoi et l'ouverture"),
        dcc.Graph(
            figure=px.line(
                x=time_diff_avg.index,
                y=time_diff_avg.values,
                labels={'x': 'Heure de la journée', 'y': 'Distance temporelle (heures)'}
            )
        )
    ])


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
        html.H3(f"Taux de clics : {stats['click_rate']:.2f}%"),
    ])

# Page Distribution par Heure
def hourly_distribution_page(stats):
    if stats['open_distribution'].empty or stats['unsubscribe_distribution'].empty:
        return html.Div("Aucune donnée disponible pour la distribution horaire.", style={'color': 'red'})

    return html.Div([
        html.H2("Distribution horaire des événements"),
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
            id='hourly-click-distribution-chart',
            figure=px.bar(
                x=stats['click_distribution'].index,
                y=stats['click_distribution'].values,
                title="Distribution des clics par heure",
                labels={'x': 'Heure', 'y': 'Nombre de clics'}
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


def bounce_rate_page(stats):
    total_bounced = stats['total_bounced']
    total_sent = stats['total_sent']
    non_bounced = total_sent - total_bounced

    return html.Div([
        html.Div("Emails Bounced", className="card-title"),
        dcc.Graph(
            figure=px.pie(
                names=['Bounced', 'Livrés'],
                values=[total_bounced, non_bounced],
                color_discrete_sequence=['#e74c3c', '#3498db']
            ).update_layout(
                showlegend=True,
                margin={"t": 0, "b": 0, "l": 0, "r": 0}
            ),
            config={'displayModeBar': False},
            className="graph-container"
        )
    ], className="data-card")



def mail_status_page(stats):
    
    return html.Div([
            # Carte 3 - Pie chart ouvertures
                html.Div([
                    html.Div("Statut des Emails", className="card-title"),
                    dcc.Graph(
                        figure=px.pie(
                            names=['Ouverts', 'Non ouverts'],
                            values=[stats['total_opened'], stats['total_sent'] - stats['total_opened']],
                            color_discrete_sequence=['#2ecc71', '#e74c3c']
                        ).update_layout(
                        showlegend=True,
                        margin={"t": 0, "b": 0, "l": 0, "r": 0}
                    ),
                    config={'displayModeBar': False},
                    className="graph-container"
                )
            ], className="data-card")
    ])



# Page Carte de la Tunisie
def tunisia_map_page(data):
    # Exemple de données pour la carte de la Tunisie
    tunisia_data = pd.DataFrame({
        'region': ['Tunis', 'Sfax', 'Sousse', 'Kairouan', 'Gabès'],
        'open_rate': [80, 70, 65, 60, 55]  # Exemple de taux d'ouverture par région
    })

    return html.Div([
        html.H2("Carte de la Tunisie - Taux d'ouverture par région"),
        dcc.Graph(
            id='tunisia-map-chart',
            figure=px.choropleth(
                tunisia_data,
                geojson="https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/tunisia.geojson",
                locations='region',
                color='open_rate',
                hover_name='region',
                title="Taux d'ouverture par région en Tunisie",
                labels={'open_rate': 'Taux d\'ouverture'}
            )
        ),
    ])

# Page Prédictions
def predictions_page(data):
    # Utiliser le modèle pour prédire l'heure optimale d'envoi
    column_names = ['ContactHash', 'COMMUNICATION_NAME', 'EVENT_DATE', 'EVENT_TYPE']
    df, X, y = create_dataset(data, sent_open_hour_range=36, open_click_hour_range=24, column_names=column_names)
    predicted_sent_hour = get_sent_hour(model=None, contact_hash=data['ContactHash'].iloc[0], comm=data['COMMUNICATION_NAME'].iloc[0], df=df, X=X)

    return html.Div([
        html.H2("Prédictions"),
        html.H3(f"Heure optimale d'envoi pour {data['ContactHash'].iloc[0]} et {data['COMMUNICATION_NAME'].iloc[0]} : {predicted_sent_hour}"),
    ])

# Lancer l'application Dash
if __name__ == '__main__':
    app.run_server(debug=False)  