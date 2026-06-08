
from sqlalchemy import text
import unittest
from dbmodel.db import engine, sync_database  # Import your actual engine and sync function
from sqlalchemy.exc import OperationalError

class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Ensure the schema exists and tables are created
        try:
            sync_database()
            cls.connection = engine.connect()
        except OperationalError as e:
            cls.fail(f"Could not connect to the database: {e}")

    @classmethod
    def tearDownClass(cls):
        # Close connection after all tests
        cls.connection.close()

    def test_schema_exists(self):
        # Test if schema creation worked
        result = self.connection.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'GenAIChatbot';"))
        schema = result.fetchone()
        self.assertIsNotNone(schema, "Schema 'GenAIChatbot' does not exist.")

if __name__ == '__main__':
    unittest.main()
