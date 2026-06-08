import unittest
from unittest.mock import patch, MagicMock
from agents.recipe_agent import RecipeAgent, RecipeTool
import os

class TestRecipeAgent(unittest.TestCase):

    def setUp(self):
        # Initialize the RecipeAgent object before each test
        self.recipe_agent = RecipeAgent()
        self.query = "Find me a recipe with chicken and rice"
    
    @patch("agents.recipe_agent.cotpromptswithLangchain.initate_cot")
    def test_get_recipe(self, mock_initate_cot):
        # Test that the get_recipe method returns the expected response
        
        # Define mock behavior for initiate_cot method
        mock_initate_cot.return_value = "Recipe found: Chicken and Rice"

        # Call the method under test
        result = self.recipe_agent.get_recipe(self.query)
        
        # Assertions to check if the result matches the expected output
        self.assertEqual(result, "Recipe found: Chicken and Rice")
        mock_initate_cot.assert_called_once_with(self.query)

    @patch("agents.recipe_agent.cotpromptswithLangchain.initate_cot")
    def test_get_recipe_empty_query(self, mock_initate_cot):
        # Test that an empty query returns a relevant response
        
        # Define mock behavior
        mock_initate_cot.return_value = "No recipe found for empty query"

        # Call the method with an empty query
        result = self.recipe_agent.get_recipe("")

        # Assertions to check the behavior with an empty query
        self.assertEqual(result, "No recipe found for empty query")
        mock_initate_cot.assert_called_once_with("")

    @patch("agents.recipe_agent.openai.ChatCompletion.create")
    def test_get_recipe_openai_interaction(self, mock_openai_create):
        # Test that OpenAI API call is made correctly for recipe generation
        
        # Set up mock OpenAI API call return value
        mock_openai_create.return_value.choices = [MagicMock(message={"content": "Recipe: Chicken Alfredo"})]

        # Call the method
        response = self.recipe_agent.get_recipe(self.query)

        # Assertions
        self.assertEqual(response, "Recipe: Chicken Alfredo")
        mock_openai_create.assert_called_once()

    @patch("agents.recipe_agent.cotpromptswithLangchain.initate_cot")
    def test_recipe_tool_run_called_correctly(self, mock_initate_cot):
        # Test that the RecipeTool's run method is called correctly
        
        # Set up mock return value for cotpromptswithLangchain.initate_cot
        mock_initate_cot.return_value = "Recipe found: Spaghetti Bolognese"
        
        # Call the method
        result = self.recipe_agent.get_recipe("Spaghetti Bolognese recipe")
        
        # Check that the result is as expected
        self.assertEqual(result, "Recipe found: Spaghetti Bolognese")
        
        # Verify that the RecipeTool's _run method was called
        mock_initate_cot.assert_called_once_with("Spaghetti Bolognese recipe")


if __name__ == '__main__':
    unittest.main()
