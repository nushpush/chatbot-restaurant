import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from agents.agent import GreetingAgent, IngredientAgent


class TestAgents(unittest.TestCase):
    
    def setUp(self):
        self.greeting_agent = GreetingAgent()
        self.ingredient_agent = IngredientAgent()

    def test_greeting_agent(self):
        response = self.greeting_agent.greet()
        self.assertEqual(response, "How can I assist you?")
    
    @patch('agents.agent.get_auth_token')
    @patch('agents.agent.call_llm')
    @patch('agents.agent.call_ica_db', new_callable=AsyncMock)
    @patch('agents.agent.socketio.emit')
    async def test_ingredient_agent_with_records(self, mock_emit, mock_call_ica_db, mock_call_llm, mock_get_auth_token):
        # Mock the return values for the external services
        mock_get_auth_token.return_value = "mock_token"
        mock_call_ica_db.return_value = {
            'page': {
                'records': [{'name': 'Ingredient 1'}, {'name': 'Ingredient 2'}]
            }
        }
        mock_call_llm.return_value = "Mock LLM response"
        
        user_prompt = "get ingredient details"
        allhistory = "some conversation history"
        
        # Call the method
        response = await self.ingredient_agent.get_ingredient_help(user_prompt, allhistory)
        
        # Assert that the correct response is returned
        self.assertIn("Mock LLM response", response)
        self.assertIn("Response from private", response)
        
        # Check if socketio.emit was called to show and hide the loader
        mock_emit.assert_any_call('show_loader', {'message': 'Loading...'})
        mock_emit.assert_any_call('show_loader', {'message': 'Hideloader'})
        mock_emit.assert_any_call('response', {'message': response})

    @patch('agents.agent.get_auth_token')
    @patch('agents.agent.call_llm')
    @patch('agents.agent.call_ica_db', new_callable=AsyncMock)
    @patch('agents.agent.socketio.emit')
    async def test_ingredient_agent_without_records(self, mock_emit, mock_call_ica_db, mock_call_llm, mock_get_auth_token):
        # Mock the return values for the external services
        mock_get_auth_token.return_value = "mock_token"
        mock_call_ica_db.return_value = {'page': {'records': []}}
        mock_call_llm.return_value = "Mock LLM response"
        
        user_prompt = "get ingredient details"
        allhistory = "some conversation history"
        
        # Call the method
        response = await self.ingredient_agent.get_ingredient_help(user_prompt, allhistory)
        
        # Assert that the correct response is returned
        self.assertIn("Mock LLM response", response)
        self.assertIn("Response from OpenAI", response)
        
        # Check if socketio.emit was called to show and hide the loader
        mock_emit.assert_any_call('show_loader', {'message': 'Loading...'})
        mock_emit.assert_any_call('show_loader', {'message': 'Hideloader'})
        mock_emit.assert_any_call('response', {'message': response})

    @patch('agents.agent.get_auth_token')
    @patch('agents.agent.call_ica_db', new_callable=AsyncMock)
    @patch('agents.agent.socketio.emit')
    async def test_ingredient_agent_exception(self, mock_emit, mock_call_ica_db, mock_get_auth_token):
        # Simulate an exception in fetching data from ICA DB
        mock_call_ica_db.side_effect = Exception("DB Error")
        mock_get_auth_token.return_value = "mock_token"
        
        user_prompt = "get ingredient details"
        allhistory = "some conversation history"
        
        # Call the method and expect an error response
        response = await self.ingredient_agent.get_ingredient_help(user_prompt, allhistory)
        
        self.assertEqual(response, 'Error: Could not process your request. Please try again.')
        
        # Check if socketio.emit was called to handle the error
        mock_emit.assert_any_call('show_loader', {'message': 'Hideloader'})

if __name__ == '__main__':
    unittest.main()
