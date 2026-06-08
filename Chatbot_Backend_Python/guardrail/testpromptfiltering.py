import unittest
from unittest.mock import patch, MagicMock
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import TextCategory, AnalyzeTextOptions

from guardrail.prompt_filtering import analyze_content

class TestAnalyzeContent(unittest.TestCase):

    @patch('guardrail.prompt_filtering.ContentSafetyClient')
    def test_analyze_content(self, mock_content_safety_client):
        # Mocking the client instance
        mock_client_instance = mock_content_safety_client.return_value

        # Mocking the response of analyze_text
        mock_response = MagicMock()

        # Creating a mock category analysis response
        mock_response.categories_analysis = [
            MagicMock(category=TextCategory.HATE, confidence=0.9),
            MagicMock(category=TextCategory.SELF_HARM, confidence=0.7),
            MagicMock(category=TextCategory.SEXUAL, confidence=0.6),
            MagicMock(category=TextCategory.VIOLENCE, confidence=0.8),
        ]

        # Setting the return value of analyze_text
        mock_client_instance.analyze_text.return_value = mock_response

        # Call the analyze_content function
        result = analyze_content("This is a test content")

        # Assertions to ensure each category result is correct
        self.assertEqual(result['hate_result'].category, TextCategory.HATE)
        self.assertEqual(result['hate_result'].confidence, 0.9)
        self.assertEqual(result['self_harm_result'].category, TextCategory.SELF_HARM)
        self.assertEqual(result['self_harm_result'].confidence, 0.7)
        self.assertEqual(result['sexual_result'].category, TextCategory.SEXUAL)
        self.assertEqual(result['sexual_result'].confidence, 0.6)
        self.assertEqual(result['violence_result'].category, TextCategory.VIOLENCE)
        self.assertEqual(result['violence_result'].confidence, 0.8)

if __name__ == '__main__':
    unittest.main()
