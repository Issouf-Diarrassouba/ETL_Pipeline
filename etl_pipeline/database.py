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

        cursor.execute ( """ DROP SCHEMA football CASCADE;
CREATE SCHEMA football;""")

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
                        tournament_name VARCHAR(100) UNIQUE
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
