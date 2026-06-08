import unittest
from unittest.mock import patch, MagicMock
from azure.core.exceptions import HttpResponseError
from guardrail.prompt_filtering import analyze_content
from azure.ai.contentsafety.models import TextCategory, AnalyzeTextOptions

class TestPromptFiltering(unittest.TestCase):

    @patch('guardrail.prompt_filtering.ContentSafetyClient')
    @patch('guardrail.prompt_filtering.AzureKeyCredential')
    def test_analyze_content_positive_case(self, mock_credential, mock_client):
        # Mock the response of the content safety client
        mock_client_instance = mock_client.return_value
        mock_client_instance.analyze_text.return_value = MagicMock(
            categories_analysis=[
                MagicMock(category=TextCategory.HATE, confidence_score=0.9),
                MagicMock(category=TextCategory.SELF_HARM, confidence_score=0.1),
                MagicMock(category=TextCategory.SEXUAL, confidence_score=0.3),
                MagicMock(category=TextCategory.VIOLENCE, confidence_score=0.6),
            ]
        )

        content = "This is a test content"
        result = analyze_content(content)

        # Assert that the correct results are returned based on the mock
        self.assertEqual(result['hate_result'].category, TextCategory.HATE)
        self.assertEqual(result['self_harm_result'].category, TextCategory.SELF_HARM)
        self.assertEqual(result['sexual_result'].category, TextCategory.SEXUAL)
        self.assertEqual(result['violence_result'].category, TextCategory.VIOLENCE)

    @patch('guardrail.prompt_filtering.ContentSafetyClient')
    @patch('guardrail.prompt_filtering.AzureKeyCredential')
    def test_analyze_content_http_error(self, mock_credential, mock_client):
        # Mock the client to raise an HttpResponseError
        mock_client_instance = mock_client.return_value
        mock_client_instance.analyze_text.side_effect = HttpResponseError("Request failed")

        content = "This content will raise an error"
        
        # Assert that an HttpResponseError is raised
        with self.assertRaises(HttpResponseError):
            analyze_content(content)

    @patch('guardrail.prompt_filtering.ContentSafetyClient')
    @patch('guardrail.prompt_filtering.AzureKeyCredential')
    def test_analyze_content_missing_category(self, mock_credential, mock_client):
        # Mock the client response with missing categories
        mock_client_instance = mock_client.return_value
        mock_client_instance.analyze_text.return_value = MagicMock(
            categories_analysis=[
                MagicMock(category=TextCategory.SEXUAL, confidence_score=0.3),
                MagicMock(category=TextCategory.VIOLENCE, confidence_score=0.6),
            ]
        )

        content = "This content has limited categories"
        result = analyze_content(content)

        # Assert that some categories are missing in the results
        self.assertNotIn('hate_result', result)
        self.assertNotIn('self_harm_result', result)
        self.assertEqual(result['sexual_result'].category, TextCategory.SEXUAL)
        self.assertEqual(result['violence_result'].category, TextCategory.VIOLENCE)


if __name__ == '__main__':
    unittest.main()
