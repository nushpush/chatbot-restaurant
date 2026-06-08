import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from agents.rag_agent import RagAgent

class TestRagAgent(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.rag_agent = RagAgent()
        self.user_prompt = "Test prompt"
        self.user_id = "12345"
    
    @patch('agents.rag_agent.request')
    @patch('agents.rag_agent.socketio')
    @patch('agents.rag_agent.call_llm')
    @patch('agents.rag_agent.get_auth_token')
    @patch('agents.rag_agent.getUrlReqbody')
    async def test_no_api_requests_llm_response(
        self, mock_get_url_req_body, mock_get_auth_token, mock_call_llm, mock_socketio, mock_request
    ):
        # Mocking the return values
        mock_get_url_req_body.return_value = None
        mock_get_auth_token.return_value = "fake_token"
        mock_call_llm.return_value = "Mock LLM response"
        mock_request.sid = "fake_sid"
        
        # Call the method
        response = await self.rag_agent.get_agent_help(self.user_prompt, self.user_id)
        
        # Check the expected response from LLM
        self.assertIn("Mock LLM response", response)
        self.assertIn("Response from OpenAI", response)
        
        # Check that socketio emits were called
        mock_socketio.emit.assert_any_call("show_loader", {"message": "Hideloader"}, room="fake_sid")
        mock_socketio.emit.assert_any_call(
            "response", {"message": "Mock LLM response<span style='color:black;font-weight: bold;font-family: sans-serif;'>Response from OpenAI</span>"}, room="fake_sid"
        )
    
    @patch('agents.rag_agent.request')
    @patch('agents.rag_agent.socketio')
    @patch('agents.rag_agent.call_ica_db')
    @patch('agents.rag_agent.get_auth_token')
    @patch('agents.rag_agent.getUrlReqbody')
    @patch('agents.rag_agent.generate_embeddings')
    @patch('agents.rag_agent.findresult.finalresult')
    async def test_api_requests_with_no_records_and_llm_fallback(
        self, mock_findresult, mock_generate_embeddings, mock_get_url_req_body, mock_get_auth_token, 
        mock_call_ica_db, mock_socketio, mock_request
    ):
        # Mocking the return values
        mock_get_url_req_body.return_value = [{"url": "http://fakeapi.com", "payload": {}}]
        mock_get_auth_token.return_value = "fake_token"
        mock_call_ica_db.return_value = {"success": True, "page": {"numberOfRecords": 0}}
        mock_findresult.return_value = "No records found"
        mock_request.sid = "fake_sid"
        
        # Call the method
        response = await self.rag_agent.get_agent_help(self.user_prompt, self.user_id)
        
        # Check if LLM response fallback is triggered
        self.assertIn("Response from OpenAI", response)
        
        # Check that socketio emits were called
        mock_socketio.emit.assert_any_call("show_loader", {"message": "Hideloader"}, room="fake_sid")
    
    @patch('agents.rag_agent.request')
    @patch('agents.rag_agent.socketio')
    @patch('agents.rag_agent.call_ica_db')
    @patch('agents.rag_agent.get_auth_token')
    @patch('agents.rag_agent.getUrlReqbody')
    @patch('agents.rag_agent.generate_embeddings')
    @patch('agents.rag_agent.findresult.finalresult')
    async def test_api_requests_with_records_and_embeddings(
        self, mock_findresult, mock_generate_embeddings, mock_get_url_req_body, mock_get_auth_token, 
        mock_call_ica_db, mock_socketio, mock_request
    ):
        # Mocking the return values
        mock_get_url_req_body.return_value = [{"url": "http://fakeapi.com", "payload": {}}]
        mock_get_auth_token.return_value = "fake_token"
        mock_call_ica_db.return_value = {
            "success": True, 
            "page": {"numberOfRecords": 1, "records": [{"id": "fake_entity_id"}]}
        }
        mock_findresult.return_value = "Found some records"
        mock_request.sid = "fake_sid"
        
        # Call the method
        response = await self.rag_agent.get_agent_help(self.user_prompt, self.user_id)
        
        # Check if embeddings and results were processed
        mock_generate_embeddings.main.assert_called_once()
        self.assertIn("Found some records", response)
        
        # Check that socketio emits were called
        mock_socketio.emit.assert_any_call("show_loader", {"message": "Hideloader"}, room="fake_sid")
        mock_socketio.emit.assert_any_call(
            "response", {"message": "Found some records<span style='color:black;font-weight: bold;font-family: sans-serif;'>Response from private</span>"}, room="fake_sid"
        )

if __name__ == '__main__':
    unittest.main()
