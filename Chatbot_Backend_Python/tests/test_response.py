import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
from dbmodel.response import Response
from dbmodel.message import Message
from dbmodel.user import User
from dbmodel.base import Base

# Setup your database URL here
DATABASE_URL = 'postgresql://user:password@localhost/dbname'

class TestResponseModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(cls.engine)

    def setUp(self):
        self.session = self.Session()

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    def test_response_creation(self):
        user = User(
            username="testuser5",
            password="password123",
            email="test5@example.com",
            role="user",
            mobile="2233445566",
            organisation_id=1
        )
        self.session.add(user)
        self.session.commit()

        message = Message(
            content="Response test message.",
            sender_id=user.user_id,
            conversation_id=uuid.uuid4()
        )
        self.session.add(message)
        self.session.commit()

        response = Response(
            response="This is a test response for the message.",
            message_id=message.message_id,
            conversation_id=message.conversation_id
        )
        self.session.add(response)
        self.session.commit()

        self.assertIsNotNone(response.response_id)
        self.assertEqual(response.response, "This is a test response for the message.")

if __name__ == '__main__':
    unittest.main()
