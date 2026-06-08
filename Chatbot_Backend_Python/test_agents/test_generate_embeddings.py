import unittest
from unittest.mock import patch, MagicMock
import json
from agents.generate_embeddings import generate_embeddings, preprocess_text, main

class TestGenerateEmbeddings(unittest.TestCase):

    @patch('agents.generate_embeddings.client.embeddings.create')
    def test_generate_embeddings_success(self, mock_create):
        # Mock the response from the AzureOpenAI client
        mock_response = MagicMock()
        mock_response.data = [{"embedding": [0.1, 0.2, 0.3]}]
        mock_create.return_value = mock_response

        text_chunk = "Sample text"
        embedding = generate_embeddings(text_chunk)

        # Validate the embedding
        self.assertEqual(embedding, [0.1, 0.2, 0.3])
        mock_create.assert_called_once_with(input=[text_chunk], model="genai4swemodernizationembeddingmodel")

    @patch('agents.generate_embeddings.client.embeddings.create')
    def test_generate_embeddings_failure(self, mock_create):
        # Simulate an exception during embedding generation
        mock_create.side_effect = Exception("Error generating embeddings")

        text_chunk = "Sample text"
        embedding = generate_embeddings(text_chunk)

        # Check if it handles the exception and returns None
        self.assertIsNone(embedding)

    def test_preprocess_text(self):
        input_text = '{"key": "value"}'
        expected_output = '{"key":"value"}'
        processed_text = preprocess_text(input_text)

        # Assert that the text is preprocessed correctly
        self.assertEqual(processed_text, expected_output)

    @patch('agents.generate_embeddings.redis_client')
    @patch('agents.generate_embeddings.generate_embeddings')
    @patch('agents.generate_embeddings.preprocess_text')
    def test_main_success(self, mock_preprocess, mock_generate, mock_redis):
        # Setup mock values for the test
        mock_preprocess.return_value = '{"processed": "text"}'
        mock_generate.return_value = [0.1, 0.2, 0.3]

        # Mock Redis client behavior
        mock_redis.exists.return_value = False

        sample_api_response = '{"page": {"records": [{"id": 1, "text": "Sample text"}]}}'
        user_id = "user_123"

        # Run the main function
        main(api_response=sample_api_response, user_id=user_id)

        # Assert Redis set method is called with the correct values
        mock_redis.set.assert_called_once_with(
            user_id, json.dumps([{
                "chunk_id": "chunk_1",
                "parent_id": "ica_responses",
                "title": "Document Title",
                "chunk": '{"processed":"text"}',
                "vector": [0.1, 0.2, 0.3],
                "last_modified": "2024-09-03T00:00:00Z"
            }])
        )

    @patch('agents.generate_embeddings.redis_client')
    @patch('agents.generate_embeddings.generate_embeddings')
    @patch('agents.generate_embeddings.preprocess_text')
    def test_main_with_existing_redis(self, mock_preprocess, mock_generate, mock_redis):
        # Setup mock values for the test
        mock_preprocess.return_value = '{"processed": "text"}'
        mock_generate.return_value = [0.1, 0.2, 0.3]

        # Mock Redis client behavior, simulate existing records
        existing_record = [{
            "chunk_id": "chunk_2",
            "parent_id": "existing_data",
            "title": "Existing Title",
            "chunk": "existing_chunk",
            "vector": [0.4, 0.5, 0.6],
            "last_modified": "2024-09-02T00:00:00Z"
        }]
        mock_redis.exists.return_value = True
        mock_redis.get.return_value = json.dumps(existing_record)

        sample_api_response = '{"page": {"records": [{"id": 1, "text": "Sample text"}]}}'
        user_id = "user_123"

        # Run the main function
        main(api_response=sample_api_response, user_id=user_id)

        # Check if Redis set is called with merged results
        expected_results = [{
            "chunk_id": "chunk_1",
            "parent_id": "ica_responses",
            "title": "Document Title",
            "chunk": '{"processed":"text"}',
            "vector": [0.1, 0.2, 0.3],
            "last_modified": "2024-09-03T00:00:00Z"
        }] + existing_record

        mock_redis.set.assert_called_once_with(user_id, json.dumps(expected_results))

    @patch('agents.generate_embeddings.redis_client')
    def test_main_invalid_api_response(self, mock_redis):
        # Test case for invalid API response
        invalid_api_response = 'Invalid JSON'
        user_id = "user_123"

        with self.assertLogs() as captured:
            main(api_response=invalid_api_response, user_id=user_id)
            # Check if the error was logged
            self.assertIn("Error processing API response", captured.output[0])

# Run the tests
if __name__ == '__main__':
    unittest.main()
