import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
from dbmodel.message import Message
from dbmodel.user import User
from dbmodel.base import Base

# Setup your database URL here
DATABASE_URL = 'postgresql://user:password@localhost/dbname'

class TestMessageModel(unittest.TestCase):

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

    def test_message_creation(self):
        user = User(
            username="testuser3",
            password="password123",
            email="test3@example.com",
            role="user",
            mobile="1234567890",
            organisation_id=1
        )
        self.session.add(user)
        self.session.commit()

        message = Message(
            content="Hello, this is a test message.",
            sender_id=user.user_id,
            conversation_id=uuid.uuid4()
        )
        self.session.add(message)
        self.session.commit()

        self.assertIsNotNone(message.message_id)
        self.assertEqual(message.content, "Hello, this is a test message.")

    def test_message_relationship_with_responses(self):
        user = User(
            username="testuser4",
            password="password123",
            email="test4@example.com",
            role="user",
            mobile="0987654321",
            organisation_id=1
        )
        self.session.add(user)
        self.session.commit()

        message = Message(
            content="Test message for response.",
            sender_id=user.user_id,
            conversation_id=uuid.uuid4()
        )
        self.session.add(message)
        self.session.commit()

        response = Response(
            response="This is a test response.",
            message_id=message.message_id,
            conversation_id=message.conversation_id
        )
        self.session.add(response)
        self.session.commit()

        responses = self.session.query(Response).filter_by(message_id=message.message_id).all()
        self.assertEqual(len(responses), 1)

if __name__ == '__main__':
    unittest.main()
