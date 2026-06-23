import pandas as pd  
import requests  

# extract_csv() : function to extract data from CSV files, returning a dictionary of pandas DataFrames for results, shootouts, and goalscorers.
def extract_csv(): 

    results = pd.read_csv("international_football_data/results.csv")
    shootouts = pd.read_csv("international_football_data/shootouts.csv")
    goalscorers = pd.read_csv("international_football_data/goalscorers.csv")
    
    # Returning the df as a dictionary
    return { 
        "results": results, 
        "shootouts": shootouts, 
        "goalscorers": goalscorers
    }

def extract_api(url:str): 

    response = requests.get(url)
    response.raise_for_status()  # Check for HTTP errors
    return pd.DataFrame(response.json())  # JSON Response converted to df 
   