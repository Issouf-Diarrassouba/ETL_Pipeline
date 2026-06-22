#importing the cdb configuration 
from configuration import PostgreConfiguration # importing the configuration class from the configuration.py file to access the database connection details and methods for generating the Data Source Name (DSN) string.

import psycopg2

def get_connection(): 
    # Obtaining DB configuration
    config = PostgreConfiguration()
    print ("Obtained configuration: ", config)
    return psycopg2.connect(config.dsn())

# initializing database and creating the table structure 
def init_db(connection):
    with connection.cursor() as cursor:
        print ("Here in the databse")

        cursor.execute("""
                CREATE SCHEMA IF NOT EXISTS football;
                       """)
        print ("Created the Schema")

        #3NF : Nation
        cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS football.nation(
                        nation_id SERIAL PRIMARY KEY, 
                        nation_name VARCHAR(60) UNIQUE NOT NULL
                       )
                       """)
        # Tournament 
        cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS football.tournament( 
                        tournament_id SERIAL PRIMARY KEY, 
                        tournament_name VARCHAR(40)
                       )
                       """)
        
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS football.matches (
                match_id SERIAL PRIMARY KEY,
                match_date DATE,
                home_team_id INT NOT NULL,
                away_team_id INT NOT NULL,
                home_score INT NOT NULL, 
                away_score INT NOT NULL, 
                tournament_id INT NOT NULL, 
                city VARCHAR(45),
                country VARCHAR(45),
                neutral BOOLEAN, 
                FOREIGN KEY (home_team_id) REFERENCES football.nation(nation_id), 
                FOREIGN KEY (away_team_id) REFERENCES football.nation(nation_id), 
                FOREIGN KEY (tournament_id) REFERENCES football.tournament(tournament_id)
            )
            """
        )

        #was going to put unique constraint of pesonan name but that s a bad idea, could be ten johndoes from differenct nations
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS football.players(
                        player_id SERIAL PRIMARY KEY, 
                        player_name VARCHAR(50), 
                        nation_id INT, 
                        FOREIGN KEY (nation_id) REFERENCES football.nation(nation_id)
                       )
                       """)
    
        #player can score multiple goals 
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS football.goals ( 
                        goal_id SERIAL PRIMARY KEY, 
                        match_id INT NOT NULL, 
                        player_id INT NOT NULL, 
                        minute_scored INT NOT NULL, 
                        is_penalty BOOLEAN, 
                        FOREIGN KEY (match_id) REFERENCES football.matches(match_id),
                        FOREIGN KEY (player_id) REFERENCES football.players(player_id)
                       )
                       """)
        
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS football.shootout(
                        shootout_id SERIAL PRIMARY KEY, 
                        match_id INT UNIQUE NOT NULL, 
                        winner_team_id INT, 
                        first_shooting_team_id INT, 
                        FOREIGN KEY (match_id) REFERENCES football.matches(match_id), 
                        FOREIGN KEY (winner_team_id) REFERENCES football.nation(nation_id), 
                        FOREIGN KEY (first_shooting_team_id) REFERENCES football.nation(nation_id)
                       )
                       """)
        
    connection.commit()

# football.nation
def create_nation(connection, nation):
    query = """
        INSERT INTO football.nation (nation_name) 
        VALUES (%s)
        ON CONFLICT (nation_name)
        DO UPDATE SET nation_name = EXCLUDED.nation_name
        RETURNING nation_id
    """
    with connection.cursor() as cursor:
        cursor.execute(query, (nation, ))
        nation_id = cursor.fetchone()[0]
    
    connection.commit()
    return nation_id

        

# football.tournament
def create_tournament(connection, tournament_type): 
    query = """
        INSERT INTO football.tournament (tournament_name)
        VALUES (%s)
        ON CONFLICT (tournament_name)
        DO UPDATE SET tournament_name = EXCLUDED.tournament_name
        RETURNING tournament_id
    """
    with connection.cursor() as cursor: 
        cursor.execute(query,(tournament_type, ))
        tournament_id = cursor.fetchone()[0]
    connection.commit()
    return tournament_id

# football.matches
def create_matches(connection, matches):
    query = """
        INSERT INTO football.matches (match_date, home_team_id, away_team_id, home_score, away_score, tournament_id, city, country, neutral)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING match_id 
    """ 

    with connection.cursor() as cursor: 
        cursor.execute(query, (
            matches["match_date"], 
            matches["home_team_id"], 
            matches["away_team_id"], 
            matches["home_score"], 
            matches["away_score"],
            matches["tournament_id"], 
            matches.get("city"), 
            matches.get("country"), 
            matches.get("neutral")
            ))
        match_id = cursor.fetchone()[0]

    connection.commit()
    return match_id

def create_players(connection, players): 
    query = """
    INSERT INTO football.players (player_name, nation_id)
    VALUES (%s, %s)
    RETURNING player_id 
    """
    with connection.cursor() as cursor: 
        cursor.execute (query, (
            players["player_name"], 
            players["nation_id"]
        ))
        player_id = cursor.fetchone()[0]

    connection.commit()
    return player_id 

def create_goals(connection, goals): 
    query = """
        INSERT INTO football.goals (match_id, player_id, minute_scored, is_penalty)
        VALUES (%s, %s, %s, %s)
        RETURNING goal_id
    """ 
    with connection.cursor() as cursor: 
        cursor.execute(query, (
            goals["match_id"],
            goals["player_id"],
            goals["minute_scored"],
            goals["is_penalty"]
        ))
        goal_id = cursor.fetchone()[0]
    connection.commit()
    return goal_id

def create_shootout(connection, shootout): 
    query = """
        INSERT INTO football.shootout (match_id, winner_team_id, first_shooting_team_id)
        VALUES (%s, %s, %s)
        RETURNING shootout_id
    """    
    with connection.cursor() as cursor:
        cursor.execute(query, (
            shootout["match_id"], 
            shootout["winner_team_id"], 
            shootout["first_shooting_team_id"]
        ))
        shootout_id = cursor.fetchone()[0]
    connection.commit()
    return shootout_id