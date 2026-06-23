#importing the cdb configuration 
from database import get_connection , init_db #importing the database connection and initialization functions from the database.py file to establish a connection to the PostgreSQL database and create the necessary schema and tables for the ETL pipeline.
from extract import extract_csv, extract_api
from transform import DataTransformer
from load import DataLoader
from project_secrets import postgres_password
from project_logger import logger
import psycopg2

def db_connection():
    connection = get_connection()
    logger.info(f"Successful db connection {connection}")

    # Calling database.py to create schmeas and initialize tables 
    init_db(connection)
    
    # allowing us to use the connection in other parts of the pipeline, such as loading data into the database or performing transformations that require database access
    return connection 

def main(): 
    print("--------------Starting ETL pipeline--------------")
    # Set up db connection
    connection = db_connection() 
    # Extraction phase: 

    # Extracting CSV Data 
    try: 
        csv_data = extract_csv()
        logger.info(f"Extracting CSV data. Total Rows: {list(csv_data.keys())}")
    except Exception as exception: 
        logger.critical(f"CSV Data Failed To Extract: {exception}")

    # Extracting API Data 
    try: 
        api_data = {
            "results": extract_api("http://127.0.0.1:5000/api/results"),
            "shootouts": extract_api("http://127.0.0.1:5000/api/shootouts"),
            "goalscorers": extract_api("http://127.0.0.1:5000/api/goalscorers")
        }

        logger.info(f"Extracting API Results Rows: {len(api_data['results'])}")
        logger.info(f"Extracting API Shootouts Rows: {len(api_data['shootouts'])}")
        logger.info(f"Extracting API GoalScorers Rows: {len(api_data['goalscorers'])}")

    except Exception as exception: 
        logger.critical(f"Failure Extracting API Data : {exception}") 
    
    # Transformation Phase 
    try: 
        transformer = DataTransformer(csv_data,api_data)
        transformed_data = transformer.transform_all()
        logger.info("Extracted Data Transforamtion Completed")
    
    except Exception as exception: 
        logger.critical(f"Failed to Transform Extracted Data: {exception}")

    # Loading Phase

    # Creating data Loader Instance to Load data 
    load_data = DataLoader(transformed_data,db_configuration={
            "host": "localhost",
            "database": "etl",
            "user": "etl_user",
            "password": postgres_password,
            "port": 5433
    })   

    # Table Mapping 
    nation_map = {}
    tournament_map = {}
    player_map = {}
    match_map = {}

    # Nation Loading Phase  
    
    # Obtaining all nations that was found in the dataset 
    all_nations = set(transformed_data["results"]["home_team"].unique()).union(transformed_data["results"]["away_team"].unique())

    for nation in all_nations:
        # Loading Nation Names (UNIQUE CONSTRAINT)
        try: 
            logger.info(f"Attempting to Load Nations {nation}")
            nation_map[nation] = load_data.load_nation(nation)
            logger.info(f"Successfully Loaded Nations {nation}")
        except Exception as exception: 
            load_data.load_stg_rejects(nation, {exception}, "nations")
            logger.error(f"Failed Nation Load: {nation} | {exception}")

    
    # Tournament Loading Phase  
    for tournament in transformed_data["results"]["tournament"].unique():
        # Loading Tournament names (UNIQUE CONSTRAINT)
        try: 
            logger.info(f"Attempting to Load Tournaments {tournament}")
            tournament_map[tournament] = load_data.load_tournament(tournament)
            logger.info(f"Successfully Inserted Tournaments {tournament}")
        except Exception as exception: 
            load_data.load_stg_rejects(tournament, str(exception), "tournament")
            logger.error(f"Failed Tournament Load: {tournament} | {exception}")
    
    # Matches Loading Phase 
    # Mapping Columns from transformed data 
    for i, col in transformed_data["results"].iterrows():
        # Converting row to dictionary as its easier to access fields and map ids cleaner 
        match = col.to_dict()

        match["home_team_id"] = nation_map[match["home_team"]]
        match["away_team_id"] = nation_map[match["away_team"]]
        match["tournament_id"] = tournament_map[match["tournament"]]
        try: 
            match_id = load_data.load_matches(match)
            logger.info("Loading Match Data")
        except Exception as exception: 
            load_data.load_stg_rejects(col, str(exception), "matches")
       
        key = (match["home_team"], match["away_team"], match["date"])
        match_map[key] = match_id

    # Players Loading Phase 
    # The Only players in the DB would be indiivudauls that have scored wh appreared in the db not every single player in the world 
    for i , col in transformed_data["goalscorers"].iterrows():
        player_name = col["scorer"]
        player_nation = col["team"]
        try:
            if player_name not in player_map: 
                player_map[player_name] = load_data.load_players({
                    "player_name": player_name , 
                    "nation_id"  : nation_map[player_nation]
                })
            logger.info("Loading Player Data")
        except Exception as exception: 
            load_data.load_stg_rejects(col, str(exception), "players")
            logger.info(f"Failed to Load Player Data: {player_name} : exception : {exception}")

    # Goals Loading Phase 
    for i , col in transformed_data["goalscorers"].iterrows(): 
        player_name = col["scorer"]
        player_nation = col["team"]

        # Obtainting Player ID
        player_id = player_map[player_name]

        if player_id is None: 
            logger.info(f"No player_id found for {player_name} from {player_nation}")
        

        key = (col["home_team"], col["away_team"], col["date"])
        match_id = match_map.get(key)

        if match_id is None: 
            logger.info(f"No match_id found for key={key} ")
            continue


        load_data.load_goals({
            "match_id"  : match_id, 
            "player_id" : player_id,
            "minute_scored" : col["minute"],
            "is_penalty" :col["penalty"]
        })

        logger.info(f"Inserted goal: {player_name} : Minute Scored : {col['minute']} , Match ID : {match_id} ")


    # Shootout Loading Phase  
    for i , col in transformed_data["shootouts"].iterrows(): 
        first_shooting_team = col["first_shooter"]
        match_winner = col["winner"]

        key = (col["home_team"], col["away_team"], col["date"])
        match_id = match_map.get(key)
    
        if match_id is None: 
            logger.info(f"No match_id found for key={key} ")
            continue


        load_data.load_shootout({
            "match_id"  : match_id, 
            "winner_team_id" : nation_map[match_winner],
            "first_shooting_team_id" : nation_map[first_shooting_team]
        })

        logger.info(f"Penalty shootout: {col['home_team']} vs {col['away_team']}, \n First shooter : {first_shooting_team} \n Winner: {match_winner}")
    

    connection.close() # closing the database connection after the ETL process is complete  
    print("------------Successfully Ending ETL Pipeline------------")


if __name__ == "__main__": 
    main()
