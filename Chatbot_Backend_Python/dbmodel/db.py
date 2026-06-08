# import os
# import uuid
# from sqlalchemy import Column, String, Text, Integer, ForeignKey, create_engine, text, Boolean, DECIMAL
# from sqlalchemy.dialects.postgresql import UUID as PG_UUID
# from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session
# from sqlalchemy.exc import OperationalError
# import subprocess

# # Define the declarative base for models
# Base = declarative_base()

# # Import models to ensure they are registered with Base
# from dbmodel.conversation import Conversation
# from dbmodel.message import Message
# from dbmodel.response import Response
# from dbmodel.organisation import Organisation
# from dbmodel.user import User
# from dbmodel.workspace import Workspace
# from dbmodel.workspace_member import WorkspaceMember

# # Configuration for Database Connection
# class Config:
#     DB_HOST = os.environ.get('DB_HOST', 'localhost')
#     DB_PORT = os.environ.get('DB_PORT', '5432')
#     DB_DATABASE = os.environ.get('DB_DATABASE', 'GenAI')
#     DB_USER = os.environ.get('DB_USER', 'postgres')
#     DB_PASSWORD = os.environ.get('DB_PASSWORD', 'qwerty')
#     # DB_SSL_MODE ='require'

#     # DB_HOST = os.environ.get('DB_HOST', 'localhost')
#     # DB_PORT = os.environ.get('DB_PORT', '5432')
#     # DB_DATABASE = os.environ.get('DB_DATABASE', 'new_postgres')
#     # DB_USER = os.environ.get('DB_USER', 'postgres')
#     # DB_PASSWORD = os.environ.get('DB_PASSWORD', '2712')


#     @staticmethod
#     def get_database_uri():
#         return f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_DATABASE}"

#     SQLALCHEMY_TRACK_MODIFICATIONS = False

# # Create the database engine
# engine = create_engine(Config.get_database_uri())

# # Create a session factory bound to the engine
# Session = sessionmaker(bind=engine)

# # Scoped session to ensure thread safety
# db_session = scoped_session(Session)

# # Function to ensure the schema exists
# def ensure_schema_exists(engine, schema_name):
#     with engine.connect() as connection:
#         connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS \"{schema_name}\";"))
#         print(f"Schema '{schema_name}' ensured to exist.")

# # Function to synchronize the database schema
# def sync_database():
#     try:
#         # Attempt to connect to the database
#         with engine.connect() as connection:
#             print("Pg Connection has been established successfully")

#             # Ensure the schema exists before creating tables
#             ensure_schema_exists(engine, "GenAIChatbot")

#             # Bind the engine to the Base class and create tables if necessary
#             Base.metadata.create_all(engine)
#             print("Tables created successfully.")
#     except OperationalError as e:
#         print(f"OperationalError: {e}")

# # Create tables and synchronize the database schema
# sync_database()

# # Create tables and synchronize the database schema
# sync_database()


# import os
# import json
# import uuid
# import urllib.parse
# from sqlalchemy import (
#     Column,
#     String,
#     Text,
#     Integer,
#     ForeignKey,
#     create_engine,
#     text,
#     Boolean,
#     DECIMAL,
# )
# from sqlalchemy.dialects.postgresql import UUID as PG_UUID
# from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session
# from sqlalchemy.exc import OperationalError

# # Define the declarative base for models
# Base = declarative_base()
# print("Base----------", Base.metadata.tables)


# # Import models to ensure they are registered with Base
# from dbmodel.conversation import Conversation
# from dbmodel.message import Message
# from dbmodel.response import Response
# from dbmodel.organisation import Organisation
# from dbmodel.user import User
# from dbmodel.workspace import Workspace
# from dbmodel.workspace_member import WorkspaceMember


# # Load the JSON configuration file
# def load_config(env):
#     with open("dbmodel/config.json") as config_file:
#         config_data = json.load(config_file)
#         return config_data[env]


# # Detect the current environment (default to 'development')
# current_env = os.getenv("FLASK_ENV", "development")

# # Load the config based on the current environment
# config = load_config(current_env)


# # Configuration for Database Connection
# class Config:
#     DB_HOST = config.get("DB_HOST")
#     DB_PORT = config.get("DB_PORT")
#     DB_DATABASE = config.get("DB_DATABASE")
#     DB_USER = config.get("DB_USER")
#     DB_PASSWORD = urllib.parse.quote_plus(config.get("DB_PASSWORD"))
#     print("Host", DB_HOST)

#     @staticmethod
#     def get_database_uri():

#         return f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_DATABASE}"

#     SQLALCHEMY_TRACK_MODIFICATIONS = False


# # Create the database engine
# engine = create_engine(Config.get_database_uri())

# # Create a session factory bound to the engine
# Session = sessionmaker(bind=engine)

# # Scoped session to ensure thread safety
# db_session = scoped_session(Session)


# # Function to ensure the schema exists
# def ensure_schema_exists(engine, schema_name):
#     with engine.connect() as connection:
#         connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}";'))
#         print(f"Schema '{schema_name}' ensured to exist.")


# # Function to synchronize the database schema
# def sync_database():
#     try:
#         # Attempt to connect to the database
#         with engine.connect() as connection:
#             print(
#                 f"Pg Connection to {Config.DB_DATABASE} has been established successfully"
#             )

#             # Ensure the schema exists before creating tables
#             ensure_schema_exists(engine, "GenAIChatbot")
#             print("engine---------", engine)

#             # Bind the engine to the Base class and create tables if necessary
#             Base.metadata.create_all(engine)
#             print("Tables created successfully.")
#             print(f"Connecting to database: {Config.get_database_uri()}")

#     except OperationalError as e:
#         print(f"OperationalError: {e}")


# # Create tables and synchronize the database schema
# sync_database()


# ---------------------------------------------------------------------------------------------
import os
import json
import uuid
import urllib.parse
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    ForeignKey,
    create_engine,
    text,
    Boolean,
    DECIMAL,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session
from sqlalchemy.exc import OperationalError
from dbmodel.base import Base


# Define the declarative base for models
# Base = declarative_base()

# Import models to ensure they are registered with Base
from dbmodel.conversation import Conversation
from dbmodel.message import Message
from dbmodel.response import Response
from dbmodel.organisation import Organisation
from dbmodel.user import User
from dbmodel.workspace import Workspace
from dbmodel.workspace_member import WorkspaceMember
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, SQLAlchemyError

# Load the JSON configuration file
def load_config(env):
    with open("dbmodel/config.json") as config_file:
        config_data = json.load(config_file)
        return config_data[env]

# Detect the current environment (default to 'development')
current_env = os.getenv("FLASK_ENV", "development")

# Load the config based on the current environment
config = load_config(current_env)

# Configuration for Database Connection
class Config:

    DB_HOST = config.get("DB_HOST")
    DB_PORT = config.get("DB_PORT")
    DB_DATABASE = config.get("DB_DATABASE")
    DB_USER = config.get("DB_USER")
    DB_PASSWORD = urllib.parse.quote_plus(config.get("DB_PASSWORD"))

    @staticmethod
    def get_database_uri():
        return f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_DATABASE}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False


# Create the database engine
engine = create_engine(Config.get_database_uri())

# Create a session factory bound to the engine
Session = scoped_session(sessionmaker(bind=engine))

# Scoped session to ensure thread safety
db_session = scoped_session(Session)


# Function to ensure the schema exists
def ensure_schema_exists(engine, schema_name):
    try:
        # Using begin() ensures the transaction is committed
        with engine.begin() as connection:
            connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}";'))
            print(f"Schema '{schema_name}' ensured to exist.")
    except SQLAlchemyError as e:
        print(f"An error occurred while ensuring schema exists: {e}")



# Function to synchronize the database schema
def sync_database():
    try:
        # Attempt to connect to the database
        print("engine : ", engine)
        with engine.connect():
            print(f"Pg Connection to {Config.DB_DATABASE} has been established successfully.")

            # Ensure the schema exists before creating tables
            ensure_schema_exists(engine, "GenAIChatbot")
            Base.metadata.bind = engine
            print("Synchronizing database schema...")
            # Bind the engine to the Base class and create tables if necessary
            Base.metadata.create_all(engine)
            print("Tables created successfully.")
    except OperationalError as e:
        print(f"OperationalError: {e}")
    except SQLAlchemyError as e:
        print(f"An unexpected error occurred: {e}")


# Create tables and synchronize the database schema
sync_database()
