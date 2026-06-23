import pandas as pd
#transform phase of the ETL pipeline, where data is cleaned, transformed, and prepared for loading into the database. This module contains functions that perform various transformations on the extracted data, such as cleaning, filtering, and aggregating.

class DataTransformer:


    def __init__(self, csv_data, api_data):
        self.csv_data = csv_data
        self.api_data = api_data


    def normalize_column_names(self, df):
        df = df.copy()  # Create a copy of the DataFrame to avoid modifying the original data
        df.columns = df.columns.str.lower().str.strip()  # Normalize column names: lowercase and strip whitespace
        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')  # Convert 'date' column to datetime format, handling errors by coercing invalid values to NaT
        
        return df
        

    # csv transformation function that takes the extracted CSV data as input and performs various transformations on it, such as cleaning, filtering, and aggregating. The transformed data is returned as a dictionary of pandas DataFrames, where each key corresponds to a specific dataset (e.g., "results", "shootouts", "goalscorers").
    def transform_csv_data(self):

        return {key: self.normalize_column_names(df) for key, df in self.csv_data.items()}  # Apply normalization to each DataFrame in the CSV data dictionary

    # api transformation function that takes the extracted API data as input and performs similar transformations as the CSV transformation function. The transformed API data is returned as a dictionary of pandas DataFrames, where each key corresponds to a specific dataset (e.g., "results", "shootouts", "goalscorers").
    def transform_api_data(self):
        return {key: self.normalize_column_names(df) for key, df in self.api_data.items()}  # Apply normalization to each DataFrame in the API data dictionary
    
    def transform_results(self,df: pd.DataFrame):
        df = df.copy()  # Create a copy of the DataFrame to avoid modifying the
        if "home_score" in df.columns:
            df["home_score"] = pd.to_numeric(df["home_score"], errors='coerce').fillna(0).astype(int)  # Convert 'home_score' column to numeric, handling errors by coercing invalid values to NaN
        
        if "away_score" in df.columns:
            df["away_score"] = pd.to_numeric(df["away_score"], errors='coerce').fillna(0).astype(int)  # Convert 'away_score' column to numeric, handling errors by coercing invalid values to NaNdf
        if "neutral" in df.columns:
            df["neutral"] = df["neutral"].fillna(False).astype(bool)  # Convert 'neutral' column to boolean, defaulting to False if the value is missing or not provided

        return df

    def transform_goalscorers(self,df: pd.DataFrame):
        df = df.copy()  # Create a copy of the DataFrame to avoid modifying the original data
        if "minute" in df.columns:
            df["minute"] = pd.to_numeric(df["minute"], errors='coerce').fillna(0).astype(int)  # Convert 'minute' column to numeric, handling errors by coercing invalid values to NaN
       
        if "penalty" in df.columns: 
            df["penalty"] = df["penalty"].fillna(False).astype(bool)  # Convert 'penalty' column to boolean, defaulting to False if the value is missing or not provided
        
        if "scorer" in df.columns: 
            df = df.dropna(subset=["scorer"])

        return df
    
    def transform_shootouts(self,df: pd.DataFrame):
        df = df.copy()
        
        shootout_columns = {"winner", "first_shooter"}
        
        if shootout_columns.issubset(df.columns):
            df = df.dropna(subset=["winner", "first_shooter"])

        return df
    
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
        csv_data = self.apply_transformation(self.transform_csv_data())
        api_data = self.apply_transformation(self.transform_api_data())

        keys = set(csv_data.keys()).union(set(api_data.keys()))

        merged_dataset = {}

        for key in keys: 
            structure = [data[key] for data in [csv_data, api_data] if key in data]
            merged_dataset[key] = pd.concat(structure, ignore_index=True).drop_duplicates() if structure else pd.DataFrame()

        return merged_dataset