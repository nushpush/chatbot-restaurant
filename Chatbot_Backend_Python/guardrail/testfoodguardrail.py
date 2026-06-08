import unittest
from unittest.mock import patch

# Adjust the import based on where your module is located
from guardrail.food_guardrails import is_food_related

class TestIsFoodRelated(unittest.TestCase):
    @patch('guardrail.food_guardrails.classifier')  # Mocking the classifier with correct path
    def test_food_related_sentence(self, mock_classifier):
        # Mock the output of the classifier for a food-related sentence
        mock_classifier.return_value = {
            'labels': ['recipe creation', 'sustainable practices', 'menu refinement'],
            'scores': [0.7, 0.6, 0.4]  # One of the scores above 0.5
        }

        sentence = "How can I make a sustainable chicken recipe?"
        result = is_food_related(sentence)
        self.assertTrue(result)

    @patch('guardrail.food_guardrails.classifier')  # Mocking the classifier with correct path
    def test_non_food_related_sentence(self, mock_classifier):
        # Mock the output of the classifier for a non-food-related sentence
        mock_classifier.return_value = {
            'labels': ['technology', 'sports', 'music'],
            'scores': [0.3, 0.2, 0.1]  # All scores below 0.5
        }

        sentence = "How to build a website using Python?"
        result = is_food_related(sentence)
        self.assertFalse(result)

    @patch('guardrail.food_guardrails.classifier')  # Mocking the classifier with correct path
    def test_low_confidence_food_related_sentence(self, mock_classifier):
        # Mock the output of the classifier for a low-confidence food-related sentence
        mock_classifier.return_value = {
            'labels': ['recipe creation', 'sustainable practices', 'menu refinement'],
            'scores': [0.4, 0.3, 0.2]  # All scores below 0.5
        }

        sentence = "How can I create a delicious recipe?"
        result = is_food_related(sentence)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
