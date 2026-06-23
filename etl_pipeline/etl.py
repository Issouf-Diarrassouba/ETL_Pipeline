#importing the cdb configuration 
from database import get_connection , init_db #importing the database connection and initialization functions from the database.py file to establish a connection to the PostgreSQL database and create the necessary schema and tables for the ETL pipeline.
from extract import extract_csv, extract_api
from transform import DataTransformer
from load import DataLoader
from project_secrets import postgres_password


import psycopg2

def db_connection():

    connection = get_connection()
    print("Succeccessful connection to Database}")

    #calling the schema function
    #passingt eh database connection as a parameter 
    init_db(connection)
    
    #connection.close()
    return connection #allowing us to use the connection in other parts of the pipeline, such as loading data into the database or performing transformations that require database access

def main(): 
    print("Starting ETL pipeline...")
    connection = db_connection() # setting up the database connection and initializing the database schema
    # Extraction phase: calling the extract functions to retrieve data from CSV files and an API endpoint
    print("Extracting data from CSV files and API...")
    print("ETL setup complete (DB ready)")
    csv_data = extract_csv()
    # Extracting data from the API endpoint, assuming the Flask app is running locally on port 5000 and has an endpoint for results. It is important to ensure that the Flask app is running before executing this ETL pipeline, otherwise the API extraction will fail.
    # It can also change to any other endpoint that is available in the Flask app, such as /api/shootouts or /api/goalscorers, depending on the data needed for the ETL process. The extracted data from the API will be in JSON format and converted to a pandas DataFrame for further processing in the ETL pipeline.
    api_data = {
        "results": extract_api("http://127.0.0.1:5000/api/results"),
        "shootouts": extract_api("http://127.0.0.1:5000/api/shootouts"),
        "goalscorers": extract_api("http://127.0.0.1:5000/api/goalscorers")
    }
    # Note : CSV and Json contains the same data but not the same order-structure, but we are extracting from both sources to demonstrate the multi-source extraction capability of the ETL pipeline. This allows us to compare the data from both sources and ensure that our extraction logic is working correctly for different formats and structures of data. It also provides flexibility in case one source becomes unavailable or if we want to switch to a different source in the future without having to change the entire ETL pipeline.
    # Test print statements to verify that the data has been extracted correctly from both sources and to check the structure of the extracted data. This can help identify any issues with the extraction logic or with the data itself before proceeding to the transformation and loading phases of the ETL pipeline.
    print("CSV Shootouts")
    print(csv_data["shootouts"].head())

    print("CSV Goalscorers")
    print(csv_data["goalscorers"].head())

    print("Data extraction complete", csv_data.keys())

    print("API Data extraction results complete", api_data["results"].head())
    print("API Data extraction shootouts complete", api_data["shootouts"].head())
    print("API Data extraction goalscorers complete", api_data["goalscorers"].head())
    #transformation phase: placeholder for any data transformation logic that might be needed before loading the data into the database
    transformer = DataTransformer(csv_data,api_data)
    transformed_data = transformer.transform_all()

    print("Data Transformation Completed ")

    # Loading phase: placeholder for loading the extracted (and potentially transformed) data into the database
    load_data = DataLoader(transformed_data,db_configuration={
            "host": "localhost",
            "database": "etl",
            "user": "etl_user",
            "password": postgres_password,
            "port": 5433
    })   

    nation_map = {}
    tournament_map = {}
    player_map = {}

    all_nations = set(transformed_data["results"]["home_team"].unique()).union(transformed_data["results"]["away_team"].unique())

    for nation in all_nations:
        nation_map[nation] = load_data.load_nation(nation)
    
    for tournament in transformed_data["results"]["tournament"].unique():
        tournament_map[tournament] = load_data.load_tournament(tournament)
    
    for i, row in transformed_data["results"].iterrows():
        match = row.to_dict()

        match["home_team_id"] = nation_map[match["home_team"]]
        match["away_team_id"] = nation_map[match["away_team"]]
        match["tournament_id"] = tournament_map[match["tournament"]]

        load_data.load_matches(match)
    print("Nations in dataset:", transformed_data["results"]["home_team"].unique())
    print("Sample row:", transformed_data["results"].iloc[0])
    print("COmpleted Loading")

    connection.close() # closing the database connection after the ETL process is complete  
    print("ETL pipeline completed successfully. Database connection closed.")


if __name__ == "__main__": 
    print("in here")
    main()
    print("Left the DB")
