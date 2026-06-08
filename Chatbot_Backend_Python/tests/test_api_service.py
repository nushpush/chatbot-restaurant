import unittest
from unittest.mock import patch, Mock
import requests
from services.api_service import call_ica_db


class TestApiService(unittest.TestCase):

    @patch('services.api_service.requests.post')
    def test_call_ica_db_success(self, mock_post):
        # Arrange
        url = "https://api.example.com/db"
        payload = {"query": "SELECT * FROM table"}
        token = "test_token"

        # Mock the response
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success", "data": "some data"}
        mock_response.raise_for_status = Mock()  # No exception raised
        mock_post.return_value = mock_response

        # Act
        result = call_ica_db(url, payload, token)

        # Assert
        self.assertEqual(result, {"status": "success", "data": "some data"})
        mock_post.assert_called_once_with(
            url, 
            json=payload, 
            headers={
                "Content-Type": "application/json",
                "X-TENANT": "QSR",
                "X-USER-ID": "manusha",
                "X-AUTHORIZATION": token
            }
        )

    @patch('services.api_service.requests.post')
    def test_call_ica_db_raises_exception(self, mock_post):
        # Arrange
        url = "https://api.example.com/db"
        payload = {"query": "SELECT * FROM table"}
        token = "test_token"

        # Mock an exception when calling the API
        mock_post.side_effect = requests.exceptions.RequestException("API request failed")

        # Act
        result = call_ica_db(url, payload, token)

        # Assert
        self.assertIsNone(result)
        mock_post.assert_called_once_with(
            url,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-TENANT": "QSR",
                "X-USER-ID": "manusha",
                "X-AUTHORIZATION": token
            }
        )

    @patch('services.api_service.requests.post')
    def test_call_ica_db_invalid_status_code(self, mock_post):
        # Arrange
        url = "https://api.example.com/db"
        payload = {"query": "SELECT * FROM table"}
        token = "test_token"

        # Mock a response with a status code indicating an error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
        mock_post.return_value = mock_response

        # Act
        result = call_ica_db(url, payload, token)

        # Assert
        self.assertIsNone(result)
        mock_post.assert_called_once_with(
            url,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-TENANT": "QSR",
                "X-USER-ID": "manusha",
                "X-AUTHORIZATION": token
            }
        )


if __name__ == '__main__':
    unittest.main()
