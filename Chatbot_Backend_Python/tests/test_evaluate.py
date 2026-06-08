import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import pandas as pd
import asyncio

# Importing the async_llm_evaluate function from your module
from evaluation.evaluate import async_llm_evaluate

class TestAsyncLlmEvaluate(unittest.IsolatedAsyncioTestCase):

    @patch('evaluation.evaluate.request')
    @patch('evaluation.evaluate.mlflow')
    async def test_async_llm_evaluate_success(self, mock_mlflow, mock_request):
        # Mocking request.json to return a valid input and response
        mock_request.json = {
            "inputs": ["What is AI?"],
            "response": ["Artificial Intelligence (AI) is the simulation of human intelligence in machines."]
        }

        # Mocking ground truth processing
        expected_ground_truth = ["Artificial Intelligence (AI) is the simulation of human intelligence in machines."]

        # Mocking the mlflow.evaluate call and the results it would return
        mock_mlflow.evaluate.return_value.tables = {
            "eval_results_table": pd.DataFrame(
                [{"inputs": "What is AI?", "ground_truth": expected_ground_truth[0], "result": "Correct"}]
            )
        }

        # Calling the function
        result = await async_llm_evaluate()

        # Verifying the results are correctly returned as JSON
        self.assertIsInstance(result, str)  # Check if it is JSON string
        json_result = json.loads(result)
        self.assertEqual(json_result[0]['inputs'], "What is AI?")
        self.assertEqual(json_result[0]['ground_truth'], expected_ground_truth[0])

        # Asserting that the mlflow.evaluate function was called once
        mock_mlflow.evaluate.assert_called_once()

    @patch('evaluation.evaluate.request')
    async def test_async_llm_evaluate_invalid_response(self, mock_request):
        # Mocking request.json to return a response that doesn't contain the 'response' key
        mock_request.json = {
            "inputs": ["What is AI?"],
            "response": {}
        }

        with self.assertRaises(TypeError):
            await async_llm_evaluate()

    @patch('evaluation.evaluate.request')
    async def test_async_llm_evaluate_list_response(self, mock_request):
        # Mocking request.json to return a list response
        mock_request.json = {
            "inputs": ["Explain quantum computing."],
            "response": ["Quantum computing is computing using quantum-mechanical phenomena."]
        }

        # Expecting the ground truth to be correctly extracted from the response list
        expected_ground_truth = ["Quantum computing is computing using quantum-mechanical phenomena."]

        with patch('evaluation.evaluate.mlflow') as mock_mlflow:
            # Mocking the mlflow.evaluate call and its return value
            mock_mlflow.evaluate.return_value.tables = {
                "eval_results_table": pd.DataFrame(
                    [{"inputs": "Explain quantum computing.", "ground_truth": expected_ground_truth[0], "result": "Correct"}]
                )
            }

            result = await async_llm_evaluate()

            # Verifying the results are correctly returned as JSON
            self.assertIsInstance(result, str)  # Check if it is JSON string
            json_result = json.loads(result)
            self.assertEqual(json_result[0]['inputs'], "Explain quantum computing.")
            self.assertEqual(json_result[0]['ground_truth'], expected_ground_truth[0])

    @patch('evaluation.evaluate.request')
    @patch('evaluation.evaluate.mlflow')
    async def test_async_llm_evaluate_with_no_inputs(self, mock_mlflow, mock_request):
        # Mocking request.json to return no inputs
        mock_request.json = {
            "inputs": [],
            "response": []
        }

        with self.assertRaises(IndexError):
            await async_llm_evaluate()

    @patch('evaluationevaluate.asyncio.sleep', new_callable=AsyncMock)
    async def test_async_llm_evaluate_sleep(self, mock_sleep):
        # Test to ensure asyncio.sleep is called correctly
        with patch('evaluation.evaluate.mlflow') as mock_mlflow, patch('evaluate.request') as mock_request:
            # Mocking request.json to return inputs and response
            mock_request.json = {
                "inputs": ["What is AI?"],
                "response": ["Artificial Intelligence (AI) is the simulation of human intelligence in machines."]
            }

            # Mocking mlflow.evaluate call
            mock_mlflow.evaluate.return_value.tables = {
                "eval_results_table": pd.DataFrame([{"inputs": "What is AI?", "ground_truth": "AI is..."}])
            }

            await async_llm_evaluate()

            # Verifying that sleep was called
            mock_sleep.assert_called_once_with(2000)

if __name__ == '__main__':
    unittest.main()
