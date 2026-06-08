import unittest
from unittest.mock import patch, Mock
import requests
from services.auth_service import get_auth_token


class TestAuthService(unittest.TestCase):

    @patch('services.auth_service.requests.post')
    def test_get_auth_token_success(self, mock_post):
        # Arrange
        expected_token = "mock_auth_token"

        # Mock the response object
        mock_response = Mock()
        mock_response.json.return_value = {"authToken": expected_token}
        mock_response.raise_for_status = Mock()  # No exception raised
        mock_post.return_value = mock_response

        # Act
        auth_token = get_auth_token()

        # Assert
        self.assertEqual(auth_token, expected_token)
        mock_post.assert_called_once_with(
            " https://dcponazure-account01.azurewebsites.net/api/v1/accounts/authenticate/",
            json={
                "credentials": {
                    "username": "manusha",
                    "password": "manusha"
                },
                "typeCodes": ["PERSON"]
            },
            headers={
                "Content-Type": "application/json",
                "X-TENANT": "QSR",
                "X-USER-ID": "manusha"
            }
        )

    @patch('services.auth_service.requests.post')
    def test_get_auth_token_no_token(self, mock_post):
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {}  # No auth token in response
        mock_response.raise_for_status = Mock()  # No exception raised
        mock_post.return_value = mock_response

        # Act
        auth_token = get_auth_token()

        # Assert
        self.assertIsNone(auth_token)
        mock_post.assert_called_once()

    @patch('services.auth_service.requests.post')
    def test_get_auth_token_request_exception(self, mock_post):
        # Arrange
        mock_post.side_effect = requests.exceptions.RequestException("Request failed")

        # Act
        auth_token = get_auth_token()

        # Assert
        self.assertIsNone(auth_token)
        mock_post.assert_called_once()

    @patch('services.auth_service.requests.post')
    def test_get_auth_token_http_error(self, mock_post):
        # Arrange
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
        mock_post.return_value = mock_response

        # Act
        auth_token = get_auth_token()

        # Assert
        self.assertIsNone(auth_token)
        mock_post.assert_called_once()


if __name__ == '__main__':
    unittest.main()
