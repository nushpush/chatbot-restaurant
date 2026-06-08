import unittest
from unittest.mock import patch, Mock
import requests
from services.llm_service import call_llm, evaluate_llm_response

class TestLLMService(unittest.TestCase):

    @patch('services.llm_service.requests.post')
    def test_call_llm_success(self, mock_post):
        # Arrange
        prompt = "What is AI?"
        response = "AI is"
        expected_llm_response = "AI is the simulation of human intelligence by machines."

        # Mock the response object
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "response": expected_llm_response
            }
        }
        mock_response.raise_for_status = Mock()  # No exception raised
        mock_post.return_value = mock_response

        # Act
        llm_response = call_llm(prompt, response)

        # Assert
        self.assertEqual(llm_response, expected_llm_response)
        mock_post.assert_called_once_with(
            "https://genaiazurellmapp.azurewebsites.net/api/v1/chat",
            data={"content": f"{response} {prompt}", "model": "gpt-4-vision"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

    @patch('services.llm_service.requests.post')
    def test_call_llm_request_exception(self, mock_post):
        # Arrange
        mock_post.side_effect = requests.exceptions.RequestException("API request failed")

        # Act
        llm_response = call_llm("What is AI?", "AI is")

        # Assert
        self.assertIn('Error sending request', llm_response)
        mock_post.assert_called_once()

    @patch('services.llm_service.requests.post')
    def test_call_llm_http_error(self, mock_post):
        # Arrange
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Internal Server Error")
        mock_post.return_value = mock_response

        # Act
        llm_response = call_llm("What is AI?", "AI is")

        # Assert
        self.assertIn('Error sending request', llm_response)
        mock_post.assert_called_once()

    @patch('services.llm_service.requests.post')
    def test_evaluate_llm_response_success(self, mock_post):
        # Arrange
        content = "What is AI?"
        final_response = "AI is the simulation of human intelligence by machines."
        expected_evaluation_data = [{
            "flesch_kincaid_grade_level/v1/score": 10.5,
            "ari_grade_level/v1/score": 8.2,
            "answer_similarity/v1/score": 0.95,
            "answer_correctness/v1/score": 0.9,
            "answer_relevance/v1/score": 0.85
        }]

        # Mock the response object
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "flesch_kincaid_grade_level/v1/score": 10.5,
                "ari_grade_level/v1/score": 8.2,
                "answer_similarity/v1/score": 0.95,
                "answer_correctness/v1/score": 0.9,
                "answer_relevance/v1/score": 0.85
            }
        ]
        mock_response.raise_for_status = Mock()  # No exception raised
        mock_post.return_value = mock_response

        # Act
        evaluation_response = evaluate_llm_response(content, final_response)

        # Assert
        self.assertEqual(evaluation_response, expected_evaluation_data)
        mock_post.assert_called_once_with(
            'https://genaiazurellmapp.azurewebsites.net/api/v1/llmevaluate',
            json={
                "inputs": [content],
                "response": [final_response]
            },
            headers={"Content-Type": "application/json"}
        )

    @patch('services.llm_service.requests.post')
    def test_evaluate_llm_response_request_exception(self, mock_post):
        # Arrange
        mock_post.side_effect = requests.exceptions.RequestException("API request failed")

        # Act
        evaluation_response = evaluate_llm_response("What is AI?", "AI is the simulation of human intelligence.")

        # Assert
        self.assertIn('Error sending request', evaluation_response)
        mock_post.assert_called_once()

    @patch('services.llm_service.requests.post')
    def test_evaluate_llm_response_http_error(self, mock_post):
        # Arrange
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Internal Server Error")
        mock_post.return_value = mock_response

        # Act
        evaluation_response = evaluate_llm_response("What is AI?", "AI is the simulation of human intelligence.")

        # Assert
        self.assertIn('Error sending request', evaluation_response)
        mock_post.assert_called_once()


if __name__ == '__main__':
    unittest.main()
