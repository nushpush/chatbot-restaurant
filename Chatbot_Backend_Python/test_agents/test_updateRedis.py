import unittest
from unittest.mock import patch, MagicMock
from agents.updateRedis import process_request
import redis


class TestProcessRequest(unittest.TestCase):
    def setUp(self):
        # Setup any initial values if needed
        self.user_prompt = "What is the weather today?"
        self.user_id = "test_user_123"

    @patch("agents.updateRedis.redis_client")
    @patch("agents.updateRedis.findresult.finalresult")
    @patch("agents.updateRedis.RagAgent")
    @patch("agents.updateRedis.socketio.emit")
    def test_process_request_user_session_exists(self, mock_emit, mock_rag_agent, mock_finalresult, mock_redis_client):
        """
        Test the scenario when a user session exists in Redis.
        """

        # Setup mock behavior
        mock_redis_client.exists.return_value = True
        mock_finalresult.return_value = "INFORMATION:YES\nSome response from Redis"
        mock_rag_agent_instance = MagicMock()
        mock_rag_agent.return_value = mock_rag_agent_instance

        # Call the function under test
        result = process_request(self.user_prompt, self.user_id)

        # Assertions
        self.assertEqual(result, "Some response from Redis")
        mock_emit.assert_called_with("show_loader", {"message": "Hideloader"})
        mock_emit.assert_called_with("response", {"message": "Some response from Redis<span style='color:black;font-weight: bold;font-family: sans-serif;'>Response from private</span>"})

        # Ensure the RAG agent was not called
        mock_rag_agent.assert_not_called()

    @patch("agents.updateRedis.redis_client")
    @patch("agents.updateRedis.findresult.finalresult")
    @patch("agents.updateRedis.RagAgent")
    @patch("agents.updateRedis.socketio.emit")
    def test_process_request_user_session_does_not_exist(self, mock_emit, mock_rag_agent, mock_finalresult, mock_redis_client):
        """
        Test the scenario when a user session does not exist in Redis.
        """

        # Setup mock behavior
        mock_redis_client.exists.return_value = False
        mock_rag_agent_instance = MagicMock()
        mock_rag_agent.return_value = mock_rag_agent_instance
        mock_rag_agent_instance.get_agent_help.return_value = "RAG agent help response"

        # Call the function under test
        result = process_request(self.user_prompt, self.user_id)

        # Assertions
        self.assertEqual(result, "RAG agent help response")
        mock_emit.assert_called_with("show_loader", {"message": "Hideloader"})
        mock_emit.assert_called_with("response", {"message": "RAG agent help response"})

        # Ensure the RAG agent was called
        mock_rag_agent.assert_called_once_with()
        mock_rag_agent_instance.get_agent_help.assert_called_once_with(self.user_prompt, self.user_id)

    @patch("agents.updateRedis.redis_client")
    @patch("agents.updateRedis.findresult.finalresult")
    @patch("agents.updateRedis.RagAgent")
    @patch("agents.updateRedis.socketio.emit")
    def test_process_request_no_information(self, mock_emit, mock_rag_agent, mock_finalresult, mock_redis_client):
        """
        Test the scenario where the response from Redis contains 'INFORMATION:NO' and the RAG agent is called.
        """

        # Setup mock behavior
        mock_redis_client.exists.return_value = True
        mock_finalresult.return_value = "INFORMATION:NO\nNo relevant information available"
        mock_rag_agent_instance = MagicMock()
        mock_rag_agent.return_value = mock_rag_agent_instance
        mock_rag_agent_instance.get_agent_help.return_value = "RAG agent help response"

        # Call the function under test
        result = process_request(self.user_prompt, self.user_id)

        # Assertions
        self.assertEqual(result, "RAG agent help response")
        mock_emit.assert_called_with("show_loader", {"message": "Hideloader"})
        mock_emit.assert_called_with("response", {"message": "RAG agent help response"})

        # Ensure the RAG agent was called since information from Redis was not available
        mock_rag_agent.assert_called_once_with()
        mock_rag_agent_instance.get_agent_help.assert_called_once_with(self.user_prompt, self.user_id)

    @patch("agents.updateRedis.redis_client")
    @patch("agents.updateRedis.findresult.finalresult")
    @patch("agents.updateRedis.RagAgent")
    @patch("agents.updateRedis.socketio.emit")
    def test_process_request_cleaned_response(self, mock_emit, mock_rag_agent, mock_finalresult, mock_redis_client):
        """
        Test the scenario when the response from Redis has "INFORMATION:YES" and the response is cleaned.
        """

        # Setup mock behavior
        mock_redis_client.exists.return_value = True
        mock_finalresult.return_value = "INFORMATION:YES\nSome response from Redis"
        mock_rag_agent_instance = MagicMock()
        mock_rag_agent.return_value = mock_rag_agent_instance

        # Call the function under test
        result = process_request(self.user_prompt, self.user_id)

        # Assertions
        self.assertEqual(result, "Some response from Redis")
        mock_emit.assert_called_with("show_loader", {"message": "Hideloader"})
        mock_emit.assert_called_with("response", {"message": "Some response from Redis<span style='color:black;font-weight: bold;font-family: sans-serif;'>Response from private</span>"})

        # Ensure that the regular expression cleaned the response
        self.assertNotIn("INFORMATION:YES", result)

if __name__ == "__main__":
    unittest.main()
