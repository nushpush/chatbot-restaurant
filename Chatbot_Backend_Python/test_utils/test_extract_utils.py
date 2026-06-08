import unittest
from unittest.mock import patch, Mock
import sys
import os
import requests

# Ensure the parent directory (project root) is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import extract_utils

class TestExtractUtils(unittest.TestCase):

    def test_extract_req_body_valid_input(self):
        response_text = """
        Here is a URL: https://example.com/api/v1/resource
        ```json
        {
            "key": "value"
        }
        ```
        """
        expected_output = [
            {"url": "https://example.com/api/v1/resource", "payload": {"key": "value"}}
        ]
        result = extract_utils.extract_req_body(response_text)
        self.assertEqual(result, expected_output)

    def test_extract_req_body_invalid_json(self):
        response_text = """
        Here is a URL: https://example.com/api/v1/resource
        ```json
        {
            key: "value"  # Missing quotes around the key
        }
        ```
        """
        expected_output = [
            {"url": "https://example.com/api/v1/resource", "payload": None}
        ]
        result = extract_utils.extract_req_body(response_text)
        self.assertEqual(result, expected_output)

    def test_extract_req_body_no_payload(self):
        response_text = """
        Here is a URL: https://example.com/api/v1/resource
        """
        expected_output = [
            {"url": "https://example.com/api/v1/resource", "payload": None}
        ]
        result = extract_utils.extract_req_body(response_text)
        self.assertEqual(result, expected_output)

    def test_extract_req_body_no_urls(self):
        response_text = """
        ```json
        {
            "key": "value"
        }
        ```
        """
        expected_output = []
        result = extract_utils.extract_req_body(response_text)
        self.assertEqual(result, expected_output)

    def test_extract_req_body_empty_input(self):
        response_text = ""
        expected_output = []
        result = extract_utils.extract_req_body(response_text)
        self.assertEqual(result, expected_output)

    @patch('utils.extract_utils.requests.post')
    def test_getUrlReqbody_success(self, mock_post):
        # Mock the response of the requests.post call
        mock_response = Mock()
        mock_response.json.return_value = {
            "result": "Here is a URL: https://example.com/api/v1/resource\n```json\n{\"key\": \"value\"}\n```"
        }
        mock_post.return_value = mock_response

        user_prompt = "Find the best restaurant nearby"
        expected_output = [
            {"url": "https://example.com/api/v1/resource", "payload": {"key": "value"}}
        ]
        result = extract_utils.getUrlReqbody(user_prompt)
        self.assertEqual(result, expected_output)

    @patch('utils.extract_utils.requests.post')
    def test_getUrlReqbody_api_error(self, mock_post):
        # Simulate a request exception
        mock_post.side_effect = requests.exceptions.RequestException("API request failed")
        
        user_prompt = "Find the best restaurant nearby"
        expected_output = {"error": "Error sending request: API request failed"}
        result = extract_utils.getUrlReqbody(user_prompt)
        self.assertEqual(result, expected_output)


if __name__ == '__main__':
    unittest.main()
