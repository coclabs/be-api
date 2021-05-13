from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import sessionmaker
import cx_Oracle

# oracle_connection_string = 'oracle+cx_oracle://{username}:{password}@'+ cx_Oracle.makedsn('{hostname}', '{port}', service_name='{service_name}')

# engine = create_engine(
#     oracle_connection_string.format(
#         username='system',
#         password='Dealrockkung123.',
#         hostname='localhost',
#         port='1521',
#         service_name='orcl',
#     )
# )
connection_url = 'postgresql+psycopg2://postgres:1234@localhost:5432/postgres'
engine = create_engine(connection_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()