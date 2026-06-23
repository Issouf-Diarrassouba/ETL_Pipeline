import pandas as pd
from etl_pipeline.project_logger import logger
class DataTransformer:

    def __init__(self, csv_data, api_data):
        self.csv_data = csv_data
        self.api_data = api_data

    # Cleaning Column names and Whitespace 
    def normalize_column_names(self, df):
        # If data getting passed in is not a datafarme wr dont process it and just return empty 
        if not hasattr(df, "columns"): 
            logger.warning("Invalid DataFrame Type: {type(df)}")
            return pd.DataFrame()
        
        df = df.copy() 
        df.columns = df.columns.str.lower().str.strip() 
        
        # Converting date' column to datetime format
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')  

        return df
        
    # Cleaning CSV Data 
    def transform_csv_data(self):

        return {key: self.normalize_column_names(df) for key, df in self.csv_data.items()} 
    
    # Cleaning Api Data 
    def transform_api_data(self):
        return {key: self.normalize_column_names(df) for key, df in self.api_data.items()}  
    
    def transform_results(self,df: pd.DataFrame):
        df = df.copy() 
        # Converting home score to an integer to match table constraint 
        if "home_score" in df.columns:
            df["home_score"] = pd.to_numeric(df["home_score"], errors='coerce').fillna(0).astype(int)  # Convert 'home_score' column to numeric, handling errors by coercing invalid values to NaN
        
        # Converting away score to an integer to match table constraint 
        if "away_score" in df.columns:
            df["away_score"] = pd.to_numeric(df["away_score"], errors='coerce').fillna(0).astype(int)  #
        
        # Converting Neutral to boolean and making sure missing values are defaulted to false 
        if "neutral" in df.columns:
            df["neutral"] = df["neutral"].fillna(False).astype(bool)  
            
        return df

    def transform_goalscorers(self,df: pd.DataFrame):
        df = df.copy()  

        #Converting minute to an integer to match table constraint 
        if "minute" in df.columns:
            df["minute"] = pd.to_numeric(df["minute"], errors='coerce').fillna(0).astype(int)  # Convert 'minute' column to numeric, handling errors by coercing invalid values to NaN
       
       # Convert penalty to boolena to match constraint and fill missing values as boolean 
        if "penalty" in df.columns: 
            df["penalty"] = df["penalty"].fillna(False).astype(bool)  
        
        # if scorer exists drop columns where values are null 
        if "scorer" in df.columns: 
            df = df.dropna(subset=["scorer"])

        return df
    
    def transform_shootouts(self,df: pd.DataFrame):
        df = df.copy()
        
        shootout_columns = {"winner", "first_shooter"}
        
        # Drop all null values only if  winner and first shooter exists in df 
        if shootout_columns.issubset(df.columns):
            df = df.dropna(subset=["winner", "first_shooter"])

        return df
    
    # Depending on the file inputted we are calling its respective transform function, to return the items in the df 
    def apply_transformation(self, data): 

        transform = { 
            "results": self.transform_results, 
            "goalscorers": self.transform_goalscorers, 
            "shootouts": self.transform_shootouts,
        }

        return { 
            key: transform[key](df) if key in transform else df.copy()
            for key, df in data.items()
        }
    
    def transform_all(self): 
        # Transforming api and csv sources independently 
        csv_data = self.apply_transformation(self.transform_csv_data())
        api_data = self.apply_transformation(self.transform_api_data())

        # Outer Joining both data sets together ,
        keys = set(csv_data.keys()).union(set(api_data.keys()))

        merged_dataset = {}
        #  Merging Corresponding tables and Removing duplicates from datasets , to prepare for loading 
        for key in keys: 
            structure = [data[key] for data in [csv_data, api_data] if key in data]
            merged_dataset[key] = pd.concat(structure, ignore_index=True).drop_duplicates() if structure else pd.DataFrame()

        return merged_dataset