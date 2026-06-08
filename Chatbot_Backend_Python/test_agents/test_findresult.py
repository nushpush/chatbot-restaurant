import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import json
from agents.findresult import (
    generate_embeddings, search_by_embedding, cosine_similarity, 
    retrieve_most_similar, save_results_to_file, llm_response, chunk_text
)

class TestFindResult(unittest.TestCase):

    @patch('agents.findresult.AzureOpenAI.embeddings.create')
    def test_generate_embeddings(self, mock_create):
        mock_create.return_value = MagicMock(data=[{'embedding': [0.1, 0.2, 0.3]}])
        result = generate_embeddings("sample text")
        self.assertEqual(result, [0.1, 0.2, 0.3])

    @patch('agents.findresult.SearchClient.search')
    def test_search_by_embedding(self, mock_search):
        mock_search.return_value = [{'chunk_id': '123', 'score': 0.95}]
        embedding = [0.1, 0.2, 0.3]
        search_by_embedding(embedding)
        mock_search.assert_called_once()

    def test_cosine_similarity(self):
        vec_a = np.array([1, 0, 0])
        vec_b = np.array([0, 1, 0])
        result = cosine_similarity(vec_a, vec_b)
        self.assertAlmostEqual(result, 0.0)

        vec_c = np.array([1, 1, 0])
        vec_d = np.array([1, 1, 0])
        result = cosine_similarity(vec_c, vec_d)
        self.assertAlmostEqual(result, 1.0)

    @patch('agents.findresult.redis_client.get')
    def test_retrieve_most_similar(self, mock_redis_get):
        # Sample embeddings and stored data
        mock_redis_get.return_value = json.dumps([{
            "vector": [0.1, 0.2, 0.3],
            "chunk": "sample chunk"
        }])
        query_embedding = [0.1, 0.2, 0.3]
        user_id = 'test_user'
        result = retrieve_most_similar(query_embedding, user_id, top_k=1)
        self.assertEqual(result[0]['chunk'], "sample chunk")

    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('agents.findresult.json.dump')
    def test_save_results_to_file(self, mock_json_dump, mock_open):
        results = [{'result': 'test_result'}]
        save_results_to_file(results, 'output.json')
        mock_open.assert_called_with('output.json', 'w')
        mock_json_dump.assert_called_with(results, mock_open(), indent=4)

    @patch('agents.findresult.requests.post')
    def test_llm_response(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": {"response": "test_response"}}
        mock_post.return_value = mock_response
        result = llm_response("test prompt")
        self.assertEqual(result, "test_response")

    def test_chunk_text(self):
        text = "This is a long text that needs to be chunked."
        max_chunk_size = 10
        chunks = list(chunk_text(text, max_chunk_size))
        self.assertEqual(len(chunks), 4)
        self.assertEqual(chunks[0], "This is a ")
        self.assertEqual(chunks[1], "long text ")
        self.assertEqual(chunks[2], "that needs")
        self.assertEqual(chunks[3], " to be chu")
