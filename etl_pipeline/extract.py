import pandas as pd  # type: ignore
import requests  # type: ignore
# for paper writing this file was having difficult import pnadas, i had to clear cahche but also found out that the naming or secrets.py was causing a conflict with pythons built-in secrets.y

# Extract = bring raw data in, regardless of format (CSV, JSON, API, DB).
# multi-source extraction
# extract_csv() : function to extract data from CSV files, returning a dictionary of pandas DataFrames for results, shootouts, and goalscorers.
def extract_csv(): 
    print("In here")
    results = pd.read_csv("international_football_data/results.csv")
    shootouts = pd.read_csv("international_football_data/shootouts.csv")
    goalscorers = pd.read_csv("international_football_data/goalscorers.csv")
    
    #returning the dataframes as a dictionary for easier access in the next steps of the pipeline
    return { 
        "results": results, 
        "shootouts": shootouts, 
        "goalscorers": goalscorers
    }

#passing in a patameter for the url to make it more flexible and reusable, we can call this function with different urls to extract data from various sources
def extract_api(url:str): 

    response = requests.get(url)
    response.raise_for_status()  # Check for HTTP errors
    return pd.DataFrame(response.json())  # Assuming the API returns JSON data that can be directly converted to a DataFrame
    # Placeholder for API extraction logic
    # pass