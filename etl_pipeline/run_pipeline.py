from extract import extract_data   # if you have it
from transform import DataTransformer
from load import DataLoader
from database import get_connection, init_db


# -------------------------
# 1. CONNECT DB + INIT
# -------------------------
conn = get_connection()
init_db(conn)


# -------------------------
# 2. EXTRACT
# -------------------------
csv_data, api_data = extract_data()


# -------------------------
# 3. TRANSFORM
# -------------------------
transformer = DataTransformer(csv_data, api_data)
transformed_data = transformer.transform_all()


# -------------------------
# 4. LOAD
# -------------------------
db_config = {
    "host": "localhost",
    "database": "your_db",
    "user": "postgres",
    "password": "your_password",
    "port": 5432
}

loader = DataLoader(transformed_data, db_config)


# -------------------------
# 5. INSERT FLOW (ORDER MATTERS)
# -------------------------

# 1. Nations
nation_ids = {}
for df in transformed_data["nation"].itertuples():
    nation_ids[df.nation_name] = loader.load_nation(df.nation_name)

# 2. Tournaments
tournament_ids = {}
for df in transformed_data["tournament"].itertuples():
    tournament_ids[df.tournament_name] = loader.load_tournament(df.tournament_name)

# 3. Matches
match_ids = []
for _, row in transformed_data["match"].iterrows():
    row["home_team_id"] = nation_ids.get(row["home_team"])
    row["away_team_id"] = nation_ids.get(row["away_team"])
    row["tournament_id"] = tournament_ids.get(row["tournament"])

    match_ids.append(loader.load_matches(row))


# -------------------------
# 6. VALIDATION
# -------------------------
print("Inserted nations:", len(nation_ids))
print("Inserted tournaments:", len(tournament_ids))
print("Inserted matches:", len(match_ids))

print("\nPIPELINE COMPLETE ✔")