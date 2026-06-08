import unittest
from unittest.mock import patch, AsyncMock
from agents.rag_agent import RagAgent

class TestRagAgent(unittest.TestCase):
    def setUp(self):
        self.agent = RagAgent()

    @patch('services.get_auth_token', return_value='fake_token')
    @patch('services.call_ica_db', new_callable=AsyncMock)
    @patch('services.call_llm', return_value='LLM response')
    @patch('utils.getUrlReqbody', return_value=[{'url': 'http://fake.url', 'payload': {}}])
    async def test_get_agent_help_success(self, mock_get_url_req_body, mock_call_llm, mock_call_ica_db, mock_get_auth_token):
        # Mock the API response
        mock_call_ica_db.return_value = {'success': True, 'page': {'numberOfRecords': 1, 'records': [{'id': 'entity_id'}]}}

        # Call the async method
        result = await self.agent.get_agent_help('user prompt', 'user_id')
        
        # Assertions
        self.assertIn('Response from private', result)

    @patch('services.get_auth_token', return_value='fake_token')
    @patch('services.call_ica_db', new_callable=AsyncMock)
    @patch('services.call_llm', return_value='LLM response')
    @patch('utils.getUrlReqbody', return_value=[{'url': 'http://fake.url', 'payload': {}}])
    async def test_get_agent_help_no_records(self, mock_get_url_req_body, mock_call_llm, mock_call_ica_db, mock_get_auth_token):
        # Mock the API response with no records
        mock_call_ica_db.return_value = {'success': True, 'page': {'numberOfRecords': 0}}

        # Call the async method
        result = await self.agent.get_agent_help('user prompt', 'user_id')

        # Assertions
        self.assertIn('Response from OpenAI', result)

    @patch('services.get_auth_token', return_value='fake_token')
    @patch('services.call_ica_db', new_callable=AsyncMock)
    @patch('services.call_llm', return_value='LLM response')
    @patch('utils.getUrlReqbody', return_value=[])
    async def test_get_agent_help_empty_urlreq(self, mock_get_url_req_body, mock_call_llm, mock_call_ica_db, mock_get_auth_token):
        # Call the async method
        result = await self.agent.get_agent_help('user prompt', 'user_id')

        # Assertions
        self.assertIn('Response from OpenAI', result)

if __name__ == '__main__':
    unittest.main()
