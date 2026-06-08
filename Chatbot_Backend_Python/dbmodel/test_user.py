import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
from message import Message
from user import User
from base import Base

# Setup your database URL here
DATABASE_URL = 'postgresql://user:password@localhost/dbname'

class TestUserModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(cls.engine)

    def setUp(self):
        self.session= self.Session()

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    def test_user_creation(self):
        user = User(
            username="testuser",
            password="password123",
            email="test@example.com",
            role="user",
            mobile="1234567890",
            organisation_id=1  # Ensure there's an Organisation with ID 1 for this to pass
        )
        self.session.add(user)
        self.session.commit()

        self.assertIsNotNone(user.user_id)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")

    def test_user_relationship_with_messages(self):
        user = User(
            username="testuser2",
            password="password123",
            email="test2@example.com",
            role="user",
            mobile="0987654321",
            organisation_id=1
        )
        self.session.add(user)
        self.session.commit()

        self.assertIsNotNone(user.user_id)

        message1 = Message(
            content="Message from user 2",
            sender_id=user.user_id,
            conversation_id=uuid.uuid4()  # Replace with a valid UUID if needed
        )
        message2 = Message(
            content="Another message from user 2",
            sender_id=user.user_id,
            conversation_id=uuid.uuid4()  # Replace with a valid UUID if needed
        )
        self.session.add(message1)
        self.session.add(message2)
        self.session.commit()

        messages = self.session.query(Message).filter_by(sender_id=user.user_id).all()
        self.assertEqual(len(messages), 2)

if __name__ == '__main__':
    unittest.main()
