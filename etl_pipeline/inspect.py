from etl_pipeline.database import get_connection

def show_tables():
    conn = get_connection()
    cur = conn.cursor()

    tables = ["football.players", "football.nation", "football.tournament"]

    for table in tables:
        print(f"\n===== {table} =====")
        cur.execute(f"SELECT * FROM {table} LIMIT 5;")
        rows = cur.fetchall()

        for row in rows:
            print(row)

if __name__ == "__main__":
    show_tables()