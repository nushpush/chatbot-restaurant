import unittest
from unittest.mock import patch, MagicMock
from guardrail.food_guardrails import is_food_related

class TestFoodGuardrails(unittest.TestCase):

    @patch('guardrail.food_guardrails.classifier')
    def test_is_food_related_positive_case(self, mock_classifier):
        # Mock the classifier output for a food-related sentence
        mock_classifier.return_value = {
            'labels': ["recipe creation", "sustainable practices", "menu refinement"],
            'scores': [0.9, 0.7, 0.6]
        }
        sentence = "I want to improve this recipe."
        result = is_food_related(sentence)

        # Assert that the function returns True for a food-related sentence
        self.assertTrue(result)

    @patch('guardrail.food_guardrails.classifier')
    def test_is_food_related_negative_case(self, mock_classifier):
        # Mock the classifier output for a non-food-related sentence
        mock_classifier.return_value = {
            'labels': ["technology", "sports", "finance"],
            'scores': [0.9, 0.8, 0.7]
        }
        sentence = "Let's discuss artificial intelligence."
        result = is_food_related(sentence)

        # Assert that the function returns False for a non-food-related sentence
        self.assertFalse(result)

    @patch('guardrail.food_guardrails.classifier')
    def test_is_food_related_low_confidence(self, mock_classifier):
        # Mock the classifier output for a food-related sentence but with low confidence
        mock_classifier.return_value = {
            'labels': ["recipe creation", "sustainable practices", "menu refinement"],
            'scores': [0.4, 0.3, 0.2]
        }
        sentence = "This dish looks great!"
        result = is_food_related(sentence)

        # Assert that the function returns False due to low confidence scores
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
