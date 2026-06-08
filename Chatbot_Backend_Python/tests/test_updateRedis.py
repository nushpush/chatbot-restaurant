import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from agents.updateRedis import process_request


class TestProcessRequest(unittest.TestCase):
    @patch("agents.updateRedis.redis_client.exists")
    @patch("agents.updateRedis.findresult.finalresult")
    @patch("agents.updateRedis.RagAgent")
    @patch("agents.updateRedis.socketio")
    async def test_user_session_exists_with_info(
        self, mock_socketio, mock_rag_agent, mock_final_result, mock_redis_exists
    ):
        # Mock Redis client to return session exists
        mock_redis_exists.return_value = True
        mock_final_result.return_value = "INFORMATION:YES Valid Information"
        mock_socketio.emit = MagicMock()

        # Test process request
        result = await process_request("Hello", "user_123")

        # Assertions
        mock_socketio.emit.assert_called_with("response", {"message": "Valid Information<span style='color:black;font-weight: bold;font-family: sans-serif;'>Response from private</span>"})
        self.assertEqual(result, "Valid Information<span style='color:black;font-weight: bold;font-family: sans-serif;'>Response from private</span>")

    @patch("agents.updateRedis.redis_client.exists")
    @patch("agents.updateRedis.findresult.finalresult")
    @patch("agents.updateRedis.RagAgent")
    @patch("agents.updateRedis.socketio")
    async def test_user_session_exists_without_info(
        self, mock_socketio, mock_rag_agent, mock_final_result, mock_redis_exists
    ):
        # Mock Redis client to return session exists
        mock_redis_exists.return_value = True
        mock_final_result.return_value = "INFORMATION:NO No Information"
        mock_socketio.emit = MagicMock()

        mock_rag_agent_instance = AsyncMock()
        mock_rag_agent.return_value = mock_rag_agent_instance
        mock_rag_agent_instance.get_agent_help.return_value = "Agent help response"

        # Test process request
        result = await process_request("Hello", "user_123")

        # Assertions
        mock_rag_agent_instance.get_agent_help.assert_called_once_with("Hello", "user_123")
        self.assertEqual(result, "Agent help response")

    @patch("agents.updateRedis.redis_client.exists")
    @patch("agents.updateRedis.RagAgent")
    @patch("agents.updateRedis.socketio")
    async def test_user_session_does_not_exist(
        self, mock_socketio, mock_rag_agent, mock_redis_exists
    ):
        # Mock Redis client to return session does not exist
        mock_redis_exists.return_value = False
        mock_socketio.emit = MagicMock()

        mock_rag_agent_instance = AsyncMock()
        mock_rag_agent.return_value = mock_rag_agent_instance
        mock_rag_agent_instance.get_agent_help.return_value = "Agent help response"

        # Test process request
        result = await process_request("Hello", "user_123")

        # Assertions
        mock_rag_agent_instance.get_agent_help.assert_called_once_with("Hello", "user_123")
        self.assertEqual(result, "Agent help response")


if __name__ == "__main__":
    unittest.main()
