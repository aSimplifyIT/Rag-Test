from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os


load_dotenv()


class DatabaseConnection:
    def engine_connection(self) -> Session:
        connection_str = (f"postgresql+psycopg2://{os.getenv('DB_USER')}:"
                          f"{quote_plus(os.getenv('DB_PASSWORD'))}@{os.getenv('DB_HOST')}:"
                          f"{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")
        engine = create_engine(connection_str)

        try:
            with engine.connect():
                print('Successfully connected to the PostgresSQL database')
        except Exception as ex:
            print(f'Sorry failed to connect: {ex}')
            return None

        session = sessionmaker(bind=engine)
        session = session()

        return session
