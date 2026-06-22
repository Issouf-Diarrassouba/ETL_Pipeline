# allows for interaction directly with my os 
import os 
#importing passcode frmo secret file, hide sensitive information from the codebase and keep it secure
from project_secrets import postgres_password

#databse configuration class for PostgreSQL, encapsulating connection details and providing a method to generate a Data Source Name (DSN) string for connecting to the database.
class PostgreConfiguration: 

    def __init__(self): 
        # Setting the host to local host 
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.port = int(os.getenv("POSTGRES_PORT", 5433))
        self.dbname = os.getenv("POSTGRES_DB", "etl")
        self.user = os.getenv("POSTGRES_USER", "etl_user")
        self.password = os.getenv("POSTGRES_PASSWORD", postgres_password)
        self.sslmode = os.getenv("POSTGRES_SSLMODE", "prefer")

    # Data Source Name(DSN)
    # Centralized Hub for connection settings
    def dsn(self):
        #Added the tab space as, cofiguration details were getting concatenated with one another a meesing up the string input into the db 
        return ( 
            f"host={self.host}  "
            f"port={self.port}  "
            f"dbname={self.dbname}  "
            f"user={self.user}  "
            f"password={self.password}  "
            f"sslmode={self.sslmode}    "

        )