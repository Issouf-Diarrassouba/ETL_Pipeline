import database
import pandas as pd
#loading phase: function to load data into the database, taking a database connection and a dictionary of pandas DataFrames as input. It iterates through the DataFrames and inserts the data into the corresponding tables in the PostgreSQL database using SQL INSERT statements.
def load_data(connection, dataframes):
    pass