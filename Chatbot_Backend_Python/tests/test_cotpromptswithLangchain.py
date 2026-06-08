import unittest
from unittest.mock import patch, MagicMock
from retriever.cotpromptswithLangchain import (
    get_client,
    get_chat_response,
    initate_cot,
    invoke_recipe_module,
    check_if_multiple_product_requested,
    split_prompt_process,
    check_sub_type,
    handle_product_confirmation,
    get_ingredients,
    get_recipe,
)

class TestCotPromptsWithLangChain(unittest.TestCase):
    
    @patch('retriever.cotpromptswithLangchain.AzureOpenAI')
    def test_get_client_with_deployment(self, mock_azure_openai):
        mock_azure_openai.return_value = MagicMock()
        client = get_client('genailllmpocmodel')
        self.assertIsNotNone(client)
        self.assertTrue(mock_azure_openai.called)

    @patch('retriever.cotpromptswithLangchain.AzureOpenAI')
    def test_get_chat_response_success(self, mock_azure_openai):
        mock_client = MagicMock()
        mock_azure_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content='Test response'))])
        
        response = get_chat_response(mock_client, 'genailllmpocmodel', [{'role': 'user', 'content': 'Hello'}])
        self.assertEqual(response, 'Test response')
        self.assertTrue(mock_client.chat.completions.create.called)

    @patch('retriever.cotpromptswithLangchain.socketio')
    def test_initiate_cot_recipe(self, mock_socketio):
        response = initate_cot("Can you find a recipe?")
        self.assertIsNone(response)  # Assuming this returns None and calls socketio.emit
        mock_socketio.emit.assert_called_with('show_loader', {'message': 'Loading...'})

    @patch('retriever.cotpromptswithLangchain.check_if_multiple_product_requested')
    @patch('retriever.cotpromptswithLangchain.socketio')
    def test_invoke_recipe_module(self, mock_socketio, mock_check):
        global productList
        productList = ["Product1"]
        invoke_recipe_module()
        self.assertTrue(mock_check.called)

    @patch('retriever.cotpromptswithLangchain.getUrlReqbody')
    def test_check_if_multiple_product_requested(self, mock_get_url_reqbody):
        mock_get_url_reqbody.return_value = [{'api1': {'payLoad': {'fields': [{'match': {'regex': 'product1'}}]}}}]
        check_if_multiple_product_requested()
        self.assertIn('product1', productList)

    @patch('retriever.cotpromptswithLangchain.assitent_print')
    @patch('retriever.cotpromptswithLangchain.check_sub_type')
    def test_split_prompt_process(self, mock_check_sub_type, mock_assitent_print):
        global productList
        productList = ['product1', 'product2']
        split_prompt_process()
        mock_assitent_print.assert_called_with("Recipe Finder : you are looking for recipe of product1")
        self.assertTrue(mock_check_sub_type.called)

    @patch('retriever.cotpromptswithLangchain.call_llm_and_ask_que')
    @patch('retriever.cotpromptswithLangchain.assitent_print')
    def test_check_sub_type(self, mock_assitent_print, mock_call_llm):
        mock_call_llm.return_value = [{'response': '{"api1": {"url": "http://example.com", "payLoad": {"fields": []}}}'}]
        global productList
        productList = ['test_product']
        check_sub_type('test_product')
        mock_assitent_print.assert_called()  # Assert that the assistant print function was called

    @patch('retriever.cotpromptswithLangchain.session')
    def test_handle_product_confirmation(self, mock_session):
        mock_session.get.return_value = [{'fields': {'name': 'test_product'}}]
        result = handle_product_confirmation('test_product')
        self.assertIsNone(result)

    @patch('retriever.cotpromptswithLangchain.call_postapi')
    def test_get_ingredients_success(self, mock_call_postapi):
        mock_call_postapi.return_value = {'success': True, 'page': {'records': [{'fields': {'recipe': 'Test Recipe'}}]}}
        global product_id
        product_id = '12345'
        get_ingredients(product_id, 'Get ingredients', 'test_item')
        self.assertTrue(mock_call_postapi.called)

    @patch('retriever.cotpromptswithLangchain.call_llm_and_ask_que')
    @patch('retriever.cotpromptswithLangchain.assitent_print')
    def test_get_recipe(self, mock_assitent_print, mock_call_llm):
        mock_call_llm.return_value = [{'response': '{"api3": {"url": "http://example.com"}}'}]
        global product_id
        product_id = '12345'
        get_recipe(product_id, 'Need recipe', 'test_item')
        mock_assitent_print.assert_called()

if __name__ == '__main__':
    unittest.main()
