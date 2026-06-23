from database import get_connection, init_db
import psycopg2
import pandas as pd


class DataLoader: 

    def __init__(self, transformed_data, db_configuration): 
        self.data = transformed_data
        self.connection = psycopg2.connect(
            host=db_configuration["host"], 
            database=db_configuration["database"], 
            user=db_configuration["user"], 
            password=db_configuration["password"], 
            port=db_configuration["port"]
        )
        self.cursor = self.connection.cursor()

        # Foreign Key Mapping after insertion 
        self.nation_map = {}
        self.tournament_map = {}
        self.player_map = {}
            


    # football.nation
    def load_nation(self, nation):
        query = """
            INSERT INTO football.nation (nation_name) 
            VALUES (%s)
            ON CONFLICT (nation_name)
            DO UPDATE SET nation_name = EXCLUDED.nation_name
            RETURNING nation_id
        """
        self.cursor.execute(query, (nation, ))
        nation_id = self.cursor.fetchone()[0]
    
        self.connection.commit()
        return nation_id

        

    # football.tournament
    def load_tournament(self, tournament_type): 
        query = """
            INSERT INTO football.tournament (tournament_name)
            VALUES (%s)
            ON CONFLICT (tournament_name)
            DO UPDATE SET tournament_name = EXCLUDED.tournament_name
            RETURNING tournament_id
        """ 
        self.cursor.execute(query,(tournament_type, ))
        tournament_id = self.cursor.fetchone()[0]

        self.connection.commit()
        return tournament_id


    # football.matches
    def load_matches(self, matches):
        query = """
            INSERT INTO football.matches (match_date, home_team_id, away_team_id, home_score, away_score, tournament_id, city, country, neutral)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING match_id 
        """ 
        self.cursor.execute(query, (
            matches["date"], 
            matches["home_team_id"], 
            matches["away_team_id"], 
            matches["home_score"], 
            matches["away_score"],
            matches["tournament_id"], 
            matches.get("city"), 
            matches.get("country"), 
            matches.get("neutral")
            ))
        match_id = self.cursor.fetchone()[0]

        self.connection.commit()
        return match_id


    def create_players(self, players): 
        query = """
        INSERT INTO football.players (player_name, nation_id)
        VALUES (%s, %s)
        RETURNING player_id 
        """
        self.cursor.execute (query, (
            players["player_name"], 
            players["nation_id"]
        ))
        player_id = self.cursor.fetchone()[0]

        self.connection.commit()
        return player_id 


    def create_goals(self, goals): 
        query = """
            INSERT INTO football.goals (match_id, player_id, minute_scored, is_penalty)
            VALUES (%s, %s, %s, %s)
            RETURNING goal_id
        """ 
        self.cursor.execute(query, (
            goals["match_id"],
            goals["player_id"],
            goals["minute_scored"],
            goals["is_penalty"]
        ))
        goal_id = self.cursor.fetchone()[0]
        self.connection.commit()
        return goal_id


    def create_shootout(self, shootout): 
        query = """
            INSERT INTO football.shootout (match_id, winner_team_id, first_shooting_team_id)
            VALUES (%s, %s, %s)
            RETURNING shootout_id
        """    
        self.cursor.execute(query, (
            shootout["match_id"], 
            shootout["winner_team_id"], 
            shootout["first_shooting_team_id"]
        ))
        shootout_id = self.cursor.fetchone()[0]
        self.connection.commit()
        return shootout_id