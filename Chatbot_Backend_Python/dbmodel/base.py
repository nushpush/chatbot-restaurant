from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Define the base class
Base = declarative_base()

# Create an engine (replace the URL with your actual database URL)
engine = create_engine("postgresql://user:password@localhost/dbname")

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a session
session = Session()
