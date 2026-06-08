import unittest
from dbmodel.base import Base, engine
from sqlalchemy.orm import sessionmaker
from dbmodel.conversation import Conversation  # Import at least one model

# Create a session factory bound to the engine
Session = sessionmaker(bind=engine)

class TestBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up the database session for testing
        Base.metadata.create_all(engine)  # Create tables for testing
        cls.session = Session()

    @classmethod
    def tearDownClass(cls):
        cls.session.close()  # Close the session after test completion
        Base.metadata.drop_all(engine)  # Clean up: drop tables after testing

    def test_base_setup(self):
        # Check if the Base class is correctly initialized
        self.assertIsNotNone(Base.metadata, "Base metadata should not be None")

        # Ensure a valid session is created
        self.assertIsNotNone(self.session, "Session should be initialized")

        # Ensure tables can be created
        self.assertTrue(Base.metadata.tables, "Tables should be present in Base metadata")

if __name__ == "__main__":
    unittest.main()
