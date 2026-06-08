import unittest
from unittest.mock import patch, MagicMock
from app import app, dbsession, redis_client, user_sid_mapping, connected_clients, socketio
from flask_socketio import SocketIOTestClient
from dbmodel.message import Message
from dbmodel.response import Response
from dbmodel.conversation import Conversation
from flask import jsonify
import json

class TestApp(unittest.TestCase):

    def setUp(self):
        # Setup test client
        self.app = app.test_client()
        self.app.testing = True
        self.socketio_test_client = socketio.test_client(app)

    def tearDown(self):
        # Cleanup
        dbsession.remove()

    @patch('dbmodel.user.User')
    def test_validate_user_success(self, mock_user):
        # Mocking a successful login
        mock_user = mock_user.return_value
        mock_user.email = "test@example.com"
        mock_user.password = "password123"

        data = {
            "email": "test@example.com",
            "password": "password123"
        }
        response = self.app.post('/login', json=data)
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['message'], "Login successful")
    
    @patch('dbmodel.user.User')
    def test_validate_user_invalid_credentials(self, mock_user):
        # Mocking invalid credentials
        mock_user = mock_user.return_value
        mock_user.email = "test@example.com"
        mock_user.password = "wrongpassword"

        data = {
            "email": "test@example.com",
            "password": "password123"
        }
        response = self.app.post('/login', json=data)
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response_data['message'], "Invalid credentials")

    def test_validate_user_missing_data(self):
        # Missing email or password
        data = {
            "email": "",
            "password": ""
        }
        response = self.app.post('/login', json=data)
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['message'], "Email and password are required")

    @patch('redis.StrictRedis.exists')
    @patch('redis.StrictRedis.delete')
    def test_logout_success(self, mock_redis_exists, mock_redis_delete):
        # Mock Redis behavior
        mock_redis_exists.return_value = True

        data = {"user_id": "123"}
        response = self.app.post('/logout', json=data)
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['message'], "Logout successful")

    @patch('redis.StrictRedis.exists')
    def test_logout_user_not_found(self, mock_redis_exists):
        mock_redis_exists.return_value = False

        data = {"user_id": "123"}
        response = self.app.post('/logout', json=data)
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['message'], "Logout")

    def test_create_conversation_missing_data(self):
        # Emit event with missing data
        data = {
            "user_id": "",
            "workspace_id": ""
        }
        self.socketio_test_client.emit('create_conversation', data)
        received = self.socketio_test_client.get_received()
        self.assertEqual(received[0]['name'], 'conversation_creation_error')
        self.assertEqual(received[0]['args'][0]['error'], 'user_id and workspace_id are required')

    @patch('dbmodel.conversation.Conversation')
    def test_create_conversation_success(self, mock_conversation):
        # Mock the creation of a new conversation
        mock_conversation = mock_conversation.return_value
        mock_conversation.conversation_id = '12345'

        data = {
            "user_id": "1",
            "workspace_id": "2"
        }
        self.socketio_test_client.emit('create_conversation', data)
        received = self.socketio_test_client.get_received()

        self.assertEqual(received[0]['name'], 'conversation_created')
        self.assertEqual(received[0]['args'][0]['conversationId'], '12345')

    @patch('dbmodel.message.Message')
    def test_create_message_success(self, mock_message):
        # Mock the creation of a new message
        mock_message = mock_message.return_value
        mock_message.message_id = 1
        mock_message.content = "Test message"

        data = {
            "conversationId": "12345",
            "message": "Test message",
            "user_id": "1"
        }
        self.socketio_test_client.emit('create_message', data)
        received = self.socketio_test_client.get_received()

        self.assertEqual(received[0]['name'], 'message_created')
        self.assertEqual(received[0]['args'][0]['content'], 'Test message')

    def test_handle_connect_with_user_id(self):
        # Test connect with user_id in query
        self.socketio_test_client.emit('connect', {'user_id': '1'})
        self.assertIn('1', user_sid_mapping)
    
    def test_handle_disconnect(self):
        # Simulate a user connecting and then disconnecting
        self.socketio_test_client.emit('connect', {'user_id': '1'})
        self.socketio_test_client.emit('disconnect')

        self.assertNotIn('1', user_sid_mapping)
        self.assertNotIn(self.socketio_test_client.sid, connected_clients)
    
    def setUp(self):
        # Set up the test client
        self.app = app.test_client()
        self.socketio_test_client = socketio.test_client(app, flask_test_client=self.app)
        
    def tearDown(self):
        self.socketio_test_client.disconnect()

    @patch("app.Session")
    def test_create_response_success(self, mock_session):
        # Mocking session and message
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        mock_message = MagicMock()
        mock_message.message_id = 1
        mock_session_instance.query().filter_by().first.return_value = mock_message
        
        # Simulating the client sending a create_response event
        data = {
            "messageId": 1,
            "response": "Test response",
            "conversationId": 1,
            "flesch_kincaid_grade_level": 5.6,
            "ari_grade_level": 4.8,
            "answer_similarity": 0.9,
            "answer_correctness": True,
            "answer_relevance": 0.85
        }
        self.socketio_test_client.emit("create_response", data)
        
        # Verify that the response has been created and event emitted
        emitted_event = self.socketio_test_client.get_received()
        self.assertEqual(emitted_event[0]['name'], 'response_created')
        self.assertTrue(emitted_event[0]['args'][0]['success'])

    @patch("app.Session")
    def test_create_response_error_message_not_found(self, mock_session):
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        mock_session_instance.query().filter_by().first.return_value = None
        
        data = {
            "messageId": 1,
            "response": "Test response",
            "conversationId": 1
        }
        self.socketio_test_client.emit("create_response", data)
        
        emitted_event = self.socketio_test_client.get_received()
        self.assertEqual(emitted_event[0]['name'], 'response_creation_error')
        self.assertIn("error", emitted_event[0]['args'][0])

    @patch("app.dbsession")
    def test_get_all_chats_success(self, mock_dbsession):
        # Mock conversation query result
        mock_dbsession.query().filter().with_entities().order_by().all.return_value = [
            MagicMock(conversation_name="Chat1", conversation_id=1, updated_at="2024-10-22T12:34:56")
        ]
        
        data = {"userId": 1}
        self.socketio_test_client.emit("get_all_chats", data)
        
        emitted_event = self.socketio_test_client.get_received()
        self.assertEqual(emitted_event[0]['name'], 'get_all_chats_response')
        self.assertTrue(emitted_event[0]['args'][0]['success'])

    @patch("app.dbsession")
    def test_get_chat_history_success(self, mock_dbsession):
        mock_conversation = MagicMock(conversation_id=1, conversation_name="Chat1", soft_delete=False, created_at="2024-10-21T12:34:56", updated_at="2024-10-22T12:34:56", messages=[])
        mock_dbsession.query().filter_by().first.return_value = mock_conversation
        
        data = {"conversationId": 1}
        self.socketio_test_client.emit("get_chat_history", data)
        
        emitted_event = self.socketio_test_client.get_received()
        self.assertEqual(emitted_event[0]['name'], 'chat_history_response')
        self.assertTrue(emitted_event[0]['args'][0]['success'])

    @patch("app.Session")
    def test_vote_response_success(self, mock_session):
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        mock_response = MagicMock()
        mock_response.response_id = 1
        mock_session_instance.query().filter_by().first.return_value = mock_response

        data = {"responseId": 1, "vote": True}
        self.socketio_test_client.emit("vote_response", data)

        emitted_event = self.socketio_test_client.get_received()
        self.assertEqual(emitted_event[0]['name'], 'vote_response_success')
        self.assertTrue(emitted_event[0]['args'][0]['success'])

if __name__ == '__main__':
    unittest.main()
