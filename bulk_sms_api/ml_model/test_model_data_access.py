import pandas as pd
from regressor_sto_model import load_data_from_db

def test_data_access():
    
    data = load_data_from_db()
    
    
    data['EVENT_DATE'] = pd.to_datetime(data['EVENT_DATE'], format='%Y-%m-%d %H:%M:%S')
    
    
    data['day_of_week'] = data['EVENT_DATE'].dt.day_name()
    
    
    print("Les 10 premières lignes du dataset :")
    print(data.head(10))

if __name__ == "__main__":
    test_data_access()