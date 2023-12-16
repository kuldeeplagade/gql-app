from sqlalchemy import URL
url = URL.create(
    drivername="postgresql",  # driver name = postgresql + the library we are using (psycopg2)
    username='postgres',
    password='kuldeep',
    host='localhost',
    database='jobboard',
    port=5432
)

SECRET_KEY="job_board_app_secret!"
ALGORITHM="HS256"
TOKEN_EXPIRATION_TIME_MINITES =15