import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statistics
import math
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import warnings
import time
import random
import psycopg2
import datetime
import numpy as np
from prophet import Prophet

warnings.filterwarnings('ignore')

def load_data_from_db():
    conn = psycopg2.connect(
        dbname="new_mass_mailing_db",
        user="postgres",
        password="user01",
        host="localhost",
        port="5432"
    )
    query = "SELECT * FROM campaigns_emailtracking2"
    data = pd.read_sql_query(query, conn)
    conn.close()
    
    # Afficher les colonnes et les 10 premières lignes du dataset
    print("Colonnes du DataFrame chargé :", data.columns)
    print("Premières lignes du dataset chargé :")
    print(data.head(10))
    
    return data

data = load_data_from_db()

# Convertir le format datetime
data['EVENT_DATE'] = pd.to_datetime(data['EVENT_DATE'], format='%Y-%m-%d %H:%M:%S')

# Ajouter la colonne du jour de la semaine
data['day_of_week'] = data['EVENT_DATE'].dt.day_name()
def sent_date_to_min(sents):
    ''' Given the sent date, return the overall minutes.'''
    return sents.hour * 60 + sents.minute

def from_min_to_hour_and_min(mins):
    '''Given the minutes, return a string that represents the hour and minutes.'''
    hours = int(round(mins)) // 60
    minutes = int(round(mins)) % 60
    return "{}:{}".format(hours, minutes)

def exp_decay_fit(x, sent_open_hour_range):
    '''Return a value from 0 to 1 following an exponential decreasing function.'''
    if x > sent_open_hour_range * 60:
        return .0
    if x < 0:
        return 1
    return math.exp(15 * ((-math.log(2) / (sent_open_hour_range * 60)) * x) + math.log(2)) / 2

import logging

logging.basicConfig(filename='missing_sent_events.log', level=logging.WARNING)

def compute_fitSA(message_hash, contact_hash, sent_open_hour_range, data):
    '''Given the message hash, the contact hash and the data (raw data), return the fitSA 
    for that message hash and contact hash.'''
    sents, opens, clicks = [], [], []
    list_index = get_all_indexes(message_hash, contact_hash, data)
    for i in list_index:
        if data['EVENT_TYPE'][i] == 'Sent':
            sents.append(data["EVENT_DATE"][i])
        elif data['EVENT_TYPE'][i] == 'Open':
            opens.append(data["EVENT_DATE"][i])
        elif data['EVENT_TYPE'][i] == 'Click':
            clicks.append(data["EVENT_DATE"][i])
    
    if not sents:
        # Aucun événement 'Sent' trouvé, ignorer cette combinaison
        print(f"No 'Sent' events found for message_hash={message_hash} and contact_hash={contact_hash}")
        return None, None  # Retourner None pour indiquer que cette combinaison doit être ignorée
    
    y = sent_date_to_min(sents[0])  # Heure d'envoi en minutes
    oldest = None
    if opens != []:
        for i in opens:
            if oldest is None:
                oldest = i
            elif i < oldest:
                oldest = i
    elif clicks != []:
        for i in clicks:
            if oldest is None:
                oldest = i
            elif i < oldest:
                oldest = i
    else:
        # Aucun événement 'Open' ou 'Click' trouvé
        return 0.0, y
    
    # Calculer la différence de temps en minutes
    mins = ((oldest - sents[0]).days * 24 * 60) + ((oldest - sents[0]).seconds // 3600) * 60 + ((oldest - sents[0]).seconds // 60) % 60
    return exp_decay_fit(mins, sent_open_hour_range), y

def compute_fitAC(message_hash, contact_hash, open_click_hour_range, data):
    '''Given the message, the contact hash and the data (raw data), return the fitAC
    for that message hash and contact hash.'''
    opens, clicks = [], []

    list_index = get_all_indexes(message_hash, contact_hash, data)
    for i in list_index:
        if data['EVENT_TYPE'][i] == 'Open':
            opens.append(data["EVENT_DATE"][i])
        elif data['EVENT_TYPE'][i] == 'Click':
            clicks.append(data["EVENT_DATE"][i])
    
    oldest_open = None
    oldest_click = None

    if opens == [] and clicks != []: # message clicked but open is not detected: I assign -1 and then a function
        return -1                    # computes the avg
    
    if clicks == []: # covers cases when a message is sent and is never open and never clicked
        return .0
    elif opens != [] and clicks != []:
        for i in opens: # get oldest open
            if oldest_open is None:
                oldest_open = i
            elif i < oldest_open:
                oldest_open = i
        for i in clicks: # get oldest click
            if oldest_click is None:
                oldest_click = i
            elif i < oldest_click:
                oldest_click = i
    # compute minutes of the distance between open-click
    mins = ((oldest_click - oldest_open).days * 24 * 60) + ((oldest_click - oldest_open).seconds // 3600) * 60 + ((oldest_click - oldest_open).seconds // 60) % 60
    return exp_decay_fit(mins, open_click_hour_range)

def avg_fitAC(df):
    '''If a contact has the Click event registered but the Open event is not registered, 
    the avg of the average of fitAC column has to be assigned to that contact.'''
    fitAC_column = df['fitAC'].dropna().tolist()  # Supprimer les valeurs NaN avant de convertir en liste
    l = []
    for i in fitAC_column:
        if i != -1:
            l.append(i)
    if len(l) == 0:  # Vérifier si la liste est vide
        return 0  # Retourner une valeur par défaut (par exemple, 0)
    return statistics.mean(l)

def open_rate_message_time_slot(contact_hash, data):
    '''Given a contact hash and the raw data, return the open rate for that contact in for each
    hour (from 0 to 24).'''
    message_plus_contact_distinct = []
    dates = []
    list_index = get_all_indexes_contact(contact_hash, data)
    for i in list_index:
        if "nan" not in str(data["EVENT_DATE"][i]) and str(data["EVENT_TYPE"][i]) == 'Open' and (data["MessageHash"][i] + data['ContactHash'][i]) not in message_plus_contact_distinct:
            message_plus_contact_distinct.append(data["MessageHash"][i] + data['ContactHash'][i])
            dates.append(data["EVENT_DATE"][i])
    # add messages clicked but not opened
    for i in list_index:
        if "nan" not in str(data["EVENT_DATE"][i]) and str(data["EVENT_TYPE"][i]) == 'Click' and (data["MessageHash"][i] + data['ContactHash'][i]) not in message_plus_contact_distinct:
            message_plus_contact_distinct.append(data["MessageHash"][i] + data['ContactHash'][i])
            dates.append(data["EVENT_DATE"][i])

    total_messages_opened = len(message_plus_contact_distinct)
    if len(dates) == 0: # it means that the user has never opened messages
        return np.zeros((24,))
    df = pd.DataFrame(dates, columns =['dates'])

    df = df.assign(session=pd.cut(df["dates"].dt.hour,
                                [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],
                                labels=['0-1','1-2','2-3','3-4','4-5','5-6','6-7', '7-8', '8-9', '9-10', '10-11', '11-12', '12-13', '13-14', '14-15', '15-16', '16-17', '17-18', '18-19', '19-20', '20-21', '21-22', '22-23', '23-24'],
                                include_lowest=True))
    numpy_output = df['session'].value_counts().sort_index().to_numpy() / total_messages_opened

    return numpy_output
def dp_open_rate_message_time_slot(data):
    '''Given the raw data, return a dictionary that represents for each contact
    its open rate.'''
    d = {}
    for i in data["ContactHash"].unique():
        if i not in d:
            d[i] = None
    for key in d:
        d[key] = open_rate_message_time_slot(key, data)

    return d

def click_rate_message_time_slot(contact_hash, data):
    '''Given a contact hash and the raw data, return the click rate for that contact in for each
    hour (from 0 to 24).'''
    message_plus_contact_distinct = set()  # Utiliser un ensemble pour éviter les doublons
    dates = []
    list_index = get_all_indexes_contact(contact_hash, data)
    
    for i in list_index:
        if (
            pd.notna(data["EVENT_DATE"][i]) and  # Vérifier si EVENT_DATE n'est pas NaN
            str(data["EVENT_TYPE"][i]) == 'Click' and
            (data["MessageHash"][i], data['ContactHash'][i]) not in message_plus_contact_distinct
        ):
            message_plus_contact_distinct.add((data["MessageHash"][i], data['ContactHash'][i]))
            dates.append(data["EVENT_DATE"][i])

    total_messages_clicked = len(message_plus_contact_distinct)
    if len(dates) == 0:  # Aucun clic trouvé
        return np.zeros((24,))
    
    df = pd.DataFrame(dates, columns=['dates'])
    df = df.assign(session=pd.cut(
        df["dates"].dt.hour,
        bins=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
        labels=['0-1', '1-2', '2-3', '3-4', '4-5', '5-6', '6-7', '7-8', '8-9', '9-10', '10-11', '11-12',
                '12-13', '13-14', '14-15', '15-16', '16-17', '17-18', '18-19', '19-20', '20-21', '21-22', '22-23', '23-24'],
        include_lowest=True
    ))
    
    numpy_output = df['session'].value_counts().sort_index().to_numpy() / total_messages_clicked
    return numpy_output

def dp_click_rate_message_time_slot(data):
    '''Given the raw data, return a dictionary that represents for each contact
    its click rate.'''
    d = {}
    unique_contacts = data["ContactHash"].unique()
    
    for contact_hash in unique_contacts:
        d[contact_hash] = click_rate_message_time_slot(contact_hash, data)
    
    return d

def rate_comm_time_slot(data, open_or_click):
    '''"open_or_click" can assume only the values "Open" or "Click".
    If "open_or_click" is "Open" and given the raw data, return the rate of opened messages 
    for each communication for each hour (from 0 to 24).
    If "open_or_click" is "Click" and given the raw data, return the rate of clicked messages 
    for each communication for each hour (from 0 to 24).
    '''
    
    if open_or_click != 'Open' and open_or_click != 'Click':
        raise Exception('open_or_click value must be either \'Open\' or \'Click\'') 
    d = {}
    for i in data["COMMUNICATION_NAME"].unique():
        if i not in d:
            d[i] = {'total_open': 0, 'dates': [], 'time_slot_distribution': None}

    for comm in data['COMMUNICATION_NAME'].unique():
        message_plus_contact_distinct = []
        
        
        list_index = get_indexes_of_comm(comm, data)
        for i in list_index:
            if str(data["EVENT_TYPE"][i]) == open_or_click and (data["MessageHash"][i] + data['ContactHash'][i]) not in message_plus_contact_distinct:
                message_plus_contact_distinct.append(data["MessageHash"][i] + data['ContactHash'][i])
                d[data['COMMUNICATION_NAME'][i]]['total_open'] += 1
                d[data['COMMUNICATION_NAME'][i]]['dates'].append(data["EVENT_DATE"][i])
        # add messages clicked but not opened
        if open_or_click == 'Open':
            for i in list_index:
                if str(data["EVENT_TYPE"][i]) == 'Click' and (data["MessageHash"][i] + data['ContactHash'][i]) not in message_plus_contact_distinct:
                    message_plus_contact_distinct.append(data["MessageHash"][i] + data['ContactHash'][i])
                    d[data['COMMUNICATION_NAME'][i]]['total_open'] += 1
                    d[data['COMMUNICATION_NAME'][i]]['dates'].append(data["EVENT_DATE"][i])

    
    
    for key, value in d.items():
        if len(d[key]['dates']) == 0: # it means that the communication has never been opened
            return np.zeros((24,))
        df = pd.DataFrame(d[key]['dates'], columns =['dates'])

        df = df.assign(session=pd.cut(df["dates"].dt.hour,
                                    [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],
                                    labels=['0-1','1-2','2-3','3-4','4-5','5-6','6-7', '7-8', '8-9', '9-10', '10-11', '11-12', '12-13', '13-14', '14-15', '15-16', '16-17', '17-18', '18-19', '19-20', '20-21', '21-22', '22-23', '23-24'],
                                    include_lowest=True))

        d[key]['time_slot_distribution'] = df['session'].value_counts().sort_index().to_numpy() / d[key]['total_open']

    return d

def compute_fitSA_evaluation(message_hash, contact_hash, sent_open_hour_range, data, sent_pred):
    '''Given the message hash, contact hash, raw data and the predicted sent hour,
    return the fitSA for that contact and message.'''
    sent_pred = from_min_to_hour_and_min(sent_pred)
    df2 = data[(data['MessageHash'] == message_hash)]
    df3 = df2[(df2['ContactHash'] == contact_hash)]
    df4 = df3[(df3['EVENT_TYPE'] == 'Open')]
    opens = list(df4['EVENT_DATE'])
    df5 = df3[(df3['EVENT_TYPE'] == 'Click')]
    clicks = list(df5['EVENT_DATE'])
    
    oldest = None
    if opens != []:
        for i in opens:
            if oldest is None:
                oldest = i
            elif i < oldest:
                oldest = i
    elif clicks != []:
        for i in clicks:
            if oldest is None:
                oldest = i
            elif i < oldest:
                oldest = i
    else: # this means that the mail has never been opened/clicked
        return .0
    oldest = str(oldest.hour) +":"+ str(oldest.minute)
    oldest = pd.to_datetime(oldest, format='%H:%M')
    sent_pred = pd.to_datetime(sent_pred, format='%H:%M')
    # compute minutes of the distance between sent-open/sent-click
    mins = ((oldest - sent_pred).days*24*60) + ((oldest - sent_pred).seconds//3600)*60 + ((oldest - sent_pred).seconds//60)%60
    return exp_decay_fit(mins, sent_open_hour_range)

def compute_fitSC_evaluation(message_hash, contact_hash, open_click_hour_range, data, sent_pred):
    '''Given the message, the contact hash and the data (raw data), return the fitAC
    for that message hash and contact hash.'''
    sent_pred = from_min_to_hour_and_min(sent_pred)
    df2 = data[(data['MessageHash'] == message_hash)]
    df3 = df2[(df2['ContactHash'] == contact_hash)]
    df4 = df3[(df3['EVENT_TYPE'] == 'Click')]
    clicks = list(df4['EVENT_DATE'])
    
    oldest_click = None

    if clicks == []: # covers cases when a message is sent and is never open and never clicked
        return .0
    else:
        for i in clicks: # get oldest click
            if oldest_click is None:
                oldest_click = i
            elif i < oldest_click:
                oldest_click = i
    # compute minutes of the distance between sent pred-click
    oldest_click = str(oldest_click.hour) +":"+ str(oldest_click.minute)
    oldest_click = pd.to_datetime(oldest_click, format='%H:%M')
    sent_pred = pd.to_datetime(sent_pred, format='%H:%M')
    # compute minutes of the distance between sent-open/sent-click
    mins = ((oldest_click - sent_pred).days*24*60) + ((oldest_click - sent_pred).seconds//3600)*60 + ((oldest_click - sent_pred).seconds//60)%60
    return exp_decay_fit(mins, sent_open_hour_range)

def evaluate(df, X, data, sent_open_hour_range, preds):
    '''Given the prediction of the model "preds" returns:
    - how many fitSA are better than the ground truth fitSA
    - how many fitSA are equal than the ground truth fitSA
    - how many fitSA are worse than the ground truth fitSA.
    '''
    # from [0, 1] to mins
    for i in range(len(preds)):
        preds[i] *= 24*60 # this 24*60 is required to convert mins from [0, 1] into real mins
    # get fitSA using the predicted sent
    fitSA_preds = []
    fitSC_preds = []
    for i in range(len(df)):
        fitSA_preds.append(compute_fitSA_evaluation(df['MessageHash'][i], df['ContactHash'][i], sent_open_hour_range, data, preds[i]))
        fitSC_preds.append(compute_fitSC_evaluation(df['MessageHash'][i], df['ContactHash'][i], sent_open_hour_range, data, preds[i]))
    
    total_messages = len(fitSA_preds)
    predicted_sent_better_usual_sent = 0
    predicted_sent_equal_usual_sent = 0
    predicted_sent_worst_usual_sent = 0
    for i in range(total_messages):
        if fitSA_preds[i] > X.loc[i, 'fitSA']: # new position of fitSA
            predicted_sent_better_usual_sent += 1
        elif fitSA_preds[i] == X.loc[i, 'fitSA']:
            predicted_sent_equal_usual_sent += 1
        elif fitSC_preds[i] > X.loc[i, 'fitAC']: # new position of fitAC
            predicted_sent_better_usual_sent += 1
        elif fitSC_preds[i] == X.loc[i, 'fitAC']:
            predicted_sent_equal_usual_sent += 1
        else:
            predicted_sent_worst_usual_sent += 1 # case fitSC predicted < fitAC real
    return predicted_sent_better_usual_sent/total_messages, predicted_sent_equal_usual_sent/total_messages, predicted_sent_worst_usual_sent/total_messages

def avg_for_new_contact(X):
    '''For a new contact, the average of the open rate, click rate, open rate for communication
    , click rate for communication need to be assigned to it. Given all the processed dataset X,
    return these averages.'''
    open_rate_avg = X[["OR 0-1", "OR 1-2", "OR 2-3", "OR 3-4", "OR 4-5", "OR 5-6", "OR 6-7", "OR 7-8", "OR 8-9", "OR 9-10", "OR 10-11", "OR 11-12",
    "OR 12-13", "OR 13-14", "OR 14-15", "OR 15-16", "OR 16-17", "OR 17-18", "OR 18-19", "OR 19-20", "OR 20-21", "OR 21-22", "OR 22-23", "OR 23-24"]].mean()

    click_rate_avg = X[["CR 0-1", "CR 1-2", "CR 2-3", "CR 3-4", "CR 4-5", "CR 5-6", "CR 6-7", "CR 7-8", "CR 8-9", "CR 9-10", "CR 10-11", "CR 11-12",
    "CR 12-13", "CR 13-14", "CR 14-15", "CR 15-16", "CR 16-17", "CR 17-18", "CR 18-19", "CR 19-20", "CR 20-21", "CR 21-22", "CR 22-23", "CR 23-24"]].mean()

    open_rate_comm = X[["OR-C 0-1", "OR-C 1-2", "OR-C 2-3", "OR-C 3-4", "OR-C 4-5", "OR-C 5-6", "OR-C 6-7", "OR-C 7-8", "OR-C 8-9", "OR-C 9-10", "OR-C 10-11", "OR-C 11-12", 
    "OR-C 12-13", "OR-C 13-14", "OR-C 14-15", "OR-C 15-16", "OR-C 16-17", "OR-C 17-18", "OR-C 18-19", "OR-C 19-20", "OR-C 20-21", "OR-C 21-22", "OR-C 22-23", "OR-C 23-24"]].mean()

    click_rate_comm = X[["CR-C 0-1", "CR-C 1-2", "CR-C 2-3", "CR-C 3-4", "CR-C 4-5", "CR-C 5-6", "CR-C 6-7", "CR-C 7-8", "CR-C 8-9", "CR-C 9-10", "CR-C 10-11", "CR-C 11-12", 
    "CR-C 12-13", "CR-C 13-14", "CR-C 14-15", "CR-C 15-16", "CR-C 16-17", "CR-C 17-18", "CR-C 18-19", "CR-C 19-20", "CR-C 20-21", "CR-C 21-22", "CR-C 22-23", "CR-C 23-24"]].mean()
    return open_rate_avg, click_rate_avg, open_rate_comm, click_rate_comm
def get_sent_hour(model, contact_hash, comm, df, X):
    """
    Utilise le modèle pour prédire l'heure d'envoi pour un contact et une communication donnés.
    """
    features_contact = X.iloc[df.index[(df['ContactHash'] == contact_hash) & (df['COMMUNICATION_NAME'] == comm)], :]
    if features_contact.size != 0:
        features_contact.loc[0, 'fitSA'] = 1  # fitSA
        features_contact.loc[0, 'fitAC'] = 1  # fitAC
        features_contact = features_contact.iloc[0, :].to_numpy()  # Prendre la première ligne
        features_contact = features_contact.reshape(-1, 1).T
        preds = model.predict(features_contact)
        # Convertir la prédiction en minutes
        mins = preds[0] * 24 * 60  # Convertir de [0, 1] en minutes réelles
        return from_min_to_hour_and_min(mins)
    else:
        print("Aucune donnée disponible pour ce contact ou cette communication.")
        return None

def split_train_test_by_lifetime(X, df, data, test_size, random_seed):
    d7 = {}
    for i in data["ContactHash"].unique():
        if i not in d7:
            d7[i] = []
    for i in range(len(data)):
        if "nan" not in str(data["EVENT_DATE"][i]) and (str(data["EVENT_TYPE"][i]) == 'Open' or str(data["EVENT_TYPE"][i]) == 'Click'):
            d7[data["ContactHash"][i]].append(data["EVENT_DATE"][i])
    # Here I merge in the same category (assign 0 days) who never opened with the users that opened just once
    for i in data["ContactHash"].unique():
        if len(d7[i]) == 0 or len(d7[i]) == 1:
            d7[i] = 0 # 0 days as lifetime
        else:
        # retain newest and oldest date
            newest_date = d7[i][0] # get the first date
            oldest_date = d7[i][0] # get the first date
            for j in d7[i]:
                if j > newest_date:
                    newest_date = j
                if j < oldest_date:
                    oldest_date = j
            # assign the lifetime for the contact i
            d7[i] = (newest_date - oldest_date).days
    df['Lifetime'] = 0
    for i in range(len(df)):
        df.loc[i, 'Lifetime'] = d7[df['ContactHash'][i]]
    lt = df['Lifetime'].to_numpy()
    zero = []
    today = []
    between = []
    for i in range(len(lt)):
        if lt[i] == 0:
            zero.append(i)
        elif lt[i] >= 320: # TODO: here I assume that a user still open today whether his lifetime is greater than or equal than 320 (it means that the last time he opened is 1 month ago)
            today.append(i)
        else:
            between.append(i)
            
    random.Random(random_seed).shuffle(zero) # 39%
    random.Random(random_seed).shuffle(today) # 17%
    random.Random(random_seed).shuffle(between) # 43%
    
    percentage_zero_train = round(len(zero) - (test_size * len(zero)))
    percentage_today_train = round(len(today) - (test_size * len(today)))
    percentage_between_train = round(len(between) - (test_size * len(between)))
    
    train_indexes_zero = zero[:percentage_zero_train]
    test_indexes_zero = zero[percentage_zero_train:]

    train_indexes_today = today[:percentage_today_train]
    test_indexes_today = today[percentage_today_train:]

    train_indexes_between = between[:percentage_between_train]
    test_indexes_between = between[percentage_between_train:]
    
    X_train = X.iloc[train_indexes_zero + train_indexes_today + train_indexes_between, :]
    y_train = df.iloc[train_indexes_zero + train_indexes_today + train_indexes_between, :]['Label']
    X_test = X.iloc[test_indexes_zero + test_indexes_today + test_indexes_between, :]
    y_test = df.iloc[test_indexes_zero + test_indexes_today + test_indexes_between, :]['Label']
    
    df_train = df.iloc[train_indexes_zero + train_indexes_today + train_indexes_between, :]
    df_test = df.iloc[test_indexes_zero + test_indexes_today + test_indexes_between, :]
    return X_train, X_test, y_train, y_test, df_train, df_test

def get_all_indexes(message_hash, contact_hash, data):
    '''Given the message hash, contact hash and raw data, return the indexes
    for the message hash and contact hash in the raw data.'''
    return data.index[(data['MessageHash'] == message_hash) & (data['ContactHash'] == contact_hash)].tolist()

def get_all_indexes_contact(contact_hash, data):
    '''Given the contact hash and raw data, return the indexes
    for contact hash in the raw data.'''
    return data.index[(data['ContactHash'] == contact_hash)]

def get_indexes_of_comm(comm, data):
    '''Given the communication and raw data, return the indexes
    for communication in the raw data.'''
    return data.index[(data['COMMUNICATION_NAME'] == comm)]

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


def create_dataset(data, sent_open_hour_range, open_click_hour_range, column_names):
    print("Début de la création du dataset...")
    rows = []

    # Étape 1 : Calculer les taux d'ouverture et de clic par communication
    print("Calcul des taux d'ouverture et de clic par communication...")
    open_rate_comm_dict = rate_comm_time_slot(data, 'Open')
    click_rate_comm_dict = rate_comm_time_slot(data, 'Click')
    print("Taux d'ouverture et de clic calculés.")

    # Étape 2 : Filtrer les combinaisons valides avec des événements 'Sent'
    print("Filtrage des combinaisons avec des événements 'Sent'...")
    sent_data = data[data['EVENT_TYPE'] == 'Sent']
    valid_combinations = set(zip(sent_data['MessageHash'], sent_data['ContactHash']))
    print(f"Nombre de combinaisons valides trouvées : {len(valid_combinations)}")

    # Étape 3 : Construire le dictionnaire des contacts et des messages
    print("Construction du dictionnaire des contacts et des messages...")
    dk = {}
    for cont in data['ContactHash'].unique():
        if cont not in dk:
            dk[cont] = {'MessageHash': []}

    for i in range(len(data)):
        dk[data['ContactHash'][i]]['MessageHash'].append(data['MessageHash'][i])

    for key in dk:
        vals = list(set(dk[key]['MessageHash']))
        dk[key]['MessageHash'] = vals
    print("Dictionnaire des contacts et des messages construit.")

    # Étape 4 : Parcourir les combinaisons et créer les lignes du dataset
    print("Création des lignes du dataset...")
    total_combinations = sum(len(dk[cont]['MessageHash']) for cont in dk)
    processed_combinations = 0

    for cont in dk:
        for mex in dk[cont]['MessageHash']:
            processed_combinations += 1
            if processed_combinations % 100 == 0:
                print(f"Progression : {processed_combinations}/{total_combinations} combinaisons traitées...")

            # Vérifier si la combinaison est valide
            if (mex, cont) not in valid_combinations:
                continue

            idx = get_all_indexes(mex, cont, data)
            if len(idx) == 0:
                continue

            row = {}
            row['COMMUNICATION_NAME'] = data['COMMUNICATION_NAME'][idx[0]]
            row['ContactHash'] = cont
            row['MessageHash'] = mex
            fitSA, y = compute_fitSA(mex, cont, sent_open_hour_range, data)
            if fitSA is None:  # Ignorer les combinaisons sans événement 'Sent'
                continue
            row['Label'] = y
            row['fitSA'] = fitSA
            fitAC = compute_fitAC(mex, cont, open_click_hour_range, data)
            row['fitAC'] = fitAC
            if row['COMMUNICATION_NAME'] in open_rate_comm_dict:
                row.update({f'OR-C {i}': val for i, val in enumerate(open_rate_comm_dict[row['COMMUNICATION_NAME']]['time_slot_distribution'])})
            if row['COMMUNICATION_NAME'] in click_rate_comm_dict:
                row.update({f'CR-C {i}': val for i, val in enumerate(click_rate_comm_dict[row['COMMUNICATION_NAME']]['time_slot_distribution'])})
            rows.append(row)
    print("Lignes du dataset créées.")

    # Étape 5 : Créer le DataFrame
    print("Création du DataFrame...")
    df = pd.DataFrame(rows, columns=column_names)
    if 'Label' not in df.columns:
        raise KeyError("La colonne 'Label' est manquante dans le DataFrame.")
    max_y = 24 * 60
    df['Label'] = df['Label'] / max_y

    # Étape 6 : Ajouter les taux d'ouverture et de clic par contact
    print("Ajout des taux d'ouverture par contact...")
    d = dp_open_rate_message_time_slot(data)
    for i in range(len(df)):
        df.loc[i, 'OR 0-1':'OR 23-24'] = d[df.loc[i, 'ContactHash']]

    print("Ajout des taux de clic par contact...")
    d2 = dp_click_rate_message_time_slot(data)
    for i in range(len(df)):
        df.loc[i, 'CR 0-1':'CR 23-24'] = d2[df.loc[i, 'ContactHash']]

    # Étape 7 : Remplacer les valeurs manquantes dans 'fitAC'
    print("Remplacement des valeurs manquantes dans 'fitAC'...")
    avgAC = avg_fitAC(df)
    for i in range(len(df)):
        if df['fitAC'][i] == -1:
            df['fitAC'][i] = avgAC

    # Étape 8 : Séparer les features (X) et les labels (y)
    print("Séparation des features (X) et des labels (y)...")
    y = df['Label']
    X = df.drop(['MessageHash', 'ContactHash', 'Label', 'COMMUNICATION_NAME'], axis=1)

    print("Création du dataset terminée.")
    return df, X, y






from sklearn.ensemble import RandomForestRegressor
import joblib

# Charger le modèle une seule fois au démarrage
MODEL = None

def load_model_once(model_path='random_forest_model.pkl'):
    """
    Charge le modèle RandomForestRegressor une seule fois.
    """
    global MODEL
    if MODEL is None:
        try:
            MODEL = joblib.load(model_path)
            print("Modèle chargé avec succès.")
        except FileNotFoundError:
            print(f"Erreur : Le fichier {model_path} n'a pas été trouvé.")
            MODEL = None
    return MODEL


    ##############Prophet model pour la prédiction STO ####################

def prepare_prophet_data(data, contact_hash):
    # Filtrer les événements 'Open' pour ce contact
    df = data[(data['ContactHash'] == contact_hash) & (data['EVENT_TYPE'].str.lower() == 'open')]
    # Grouper par date (par exemple, par heure ou jour)
    df_grouped = df.groupby(df['EVENT_DATE'].dt.floor('H')).size().reset_index(name='y')
    df_grouped.rename(columns={'EVENT_DATE': 'ds'}, inplace=True)
    return df_grouped







    ##############statsmodels####################
def get_statistics(data):
    # Utiliser le modèle global
    model = load_model_once(model_path='random_forest_model.pkl')
    if model is None:
        raise ValueError("Le modèle n'a pas été chargé. Assurez-vous que le fichier du modèle existe.")

    # Normaliser les valeurs dans EVENT_TYPE (tout en minuscules et sans espaces)
    data['EVENT_TYPE'] = data['EVENT_TYPE'].str.lower().str.strip()

    # Calculer les totaux
    total_sent = len(data[data['EVENT_TYPE'] == 'sent'])
    total_opened = len(data[data['EVENT_TYPE'] == 'open'])
    total_clicked = len(data[data['EVENT_TYPE'] == 'click'])
    total_unsubscribed = len(data[data['EVENT_TYPE'] == 'unsubscribed'])
    total_bounced = len(data[data['EVENT_TYPE'] == 'bounced'])
    total_complaints = len(data[data['EVENT_TYPE'] == 'complaint'])

    # Calculer les taux
    open_rate = (total_opened / total_sent) * 100 if total_sent > 0 else 0
    click_rate = (total_clicked / total_sent) * 100 if total_sent > 0 else 0
    unsubscribe_rate = (total_unsubscribed / total_sent) * 100 if total_sent > 0 else 0

    # Calculer les distributions horaires
    open_distribution = data[data['EVENT_TYPE'] == 'open']['EVENT_DATE'].dt.hour.value_counts().sort_index()
    click_distribution = data[data['EVENT_TYPE'] == 'click']['EVENT_DATE'].dt.hour.value_counts().sort_index()
    unsubscribe_distribution = data[data['EVENT_TYPE'] == 'unsubscribed']['EVENT_DATE'].dt.hour.value_counts().sort_index()

    # Calculer la distribution par jour de la semaine
    day_of_week_distribution = data['EVENT_DATE'].dt.day_name().value_counts()

    # Calculer la distribution par campagne
    campaign_distribution = data['CAMPAIGN_NAME'].value_counts()

    # Calculer les prédictions
    df, X, y = create_dataset(data, sent_open_hour_range=36, open_click_hour_range=24, column_names=column_names)
    predicted_sent_hour = get_sent_hour(model=model, contact_hash=data['ContactHash'].iloc[0], comm=data['COMMUNICATION_NAME'].iloc[0], df=df, X=X)

    return {
        'total_sent': total_sent,
        'total_opened': total_opened,
        'total_clicked': total_clicked,
        'total_unsubscribed': total_unsubscribed,
        'total_bounced': total_bounced,
        'total_complaints': total_complaints,
        'open_rate': open_rate,
        'click_rate': click_rate,
        'unsubscribe_rate': unsubscribe_rate,
        'open_distribution': open_distribution,
        'click_distribution': click_distribution,
        'unsubscribe_distribution': unsubscribe_distribution,
        'day_of_week_distribution': day_of_week_distribution,
        'campaign_distribution': campaign_distribution,
        'predicted_sent_hour': predicted_sent_hour,
    }

import os
import pickle

def create_or_load_dataset(data=None, sent_open_hour_range=36, open_click_hour_range=24, column_names=None, dataset_path='dataset.pkl'):
    """
    Crée le dataset ou le charge depuis un fichier si déjà existant.
    """
    if os.path.exists(dataset_path):
        print(f"Chargement du dataset depuis {dataset_path}...")
        with open(dataset_path, 'rb') as f:
            df, X, y = pickle.load(f)
        print("Dataset chargé avec succès.")
    else:
        if data is None or column_names is None:
            raise ValueError("Les données et les colonnes doivent être fournies pour créer le dataset.")
        print("Création du dataset...")
        df, X, y = create_dataset(data, sent_open_hour_range, open_click_hour_range, column_names)
        print(f"Sauvegarde du dataset dans {dataset_path}...")
        with open(dataset_path, 'wb') as f:
            pickle.dump((df, X, y), f)
        print("Dataset sauvegardé avec succès.")
    return df, X, y


if __name__ == "__main__":
    # Charger les données depuis la base de données
    data = load_data_from_db()
    data['EVENT_DATE'] = pd.to_datetime(data['EVENT_DATE'], format='%Y-%m-%d %H:%M:%S')  # Convertir les dates
    data['day_of_week'] = data['EVENT_DATE'].dt.day_name()  # Ajouter la colonne du jour de la semaine

    # Charger ou créer le dataset
    df, X, y = create_or_load_dataset(data, sent_open_hour_range=36, open_click_hour_range=24, column_names=column_names)

    