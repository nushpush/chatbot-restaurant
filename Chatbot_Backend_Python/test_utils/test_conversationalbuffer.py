import unittest
from utils.conversationalbuffer import update_history

class TestConversationalBuffer(unittest.TestCase):

    def test_update_history_within_limit(self):
        # Test case when the history array has less than 10 items
        history_array = ["old message 1", "old message 2"]
        new_history = "new message"
        
        updated_history = update_history(new_history, history_array)
        
        self.assertEqual(len(updated_history), 3)
        self.assertEqual(updated_history[-1], new_history)
    
    def test_update_history_exceeds_limit(self):
        # Test case when the history array has exactly 10 items, the oldest should be removed
        history_array = [f"old message {i}" for i in range(1, 11)]  # 10 messages
        new_history = "new message"
        
        updated_history = update_history(new_history, history_array)
        
        self.assertEqual(len(updated_history), 10)
        self.assertEqual(updated_history[-1], new_history)  # Last message should be the new one
        self.assertNotIn("old message 1", updated_history)   # Oldest message should be removed
    
    def test_update_history_empty_history_array(self):
        # Test case when the history array is empty
        history_array = []
        new_history = "first message"
        
        updated_history = update_history(new_history, history_array)
        
        self.assertEqual(len(updated_history), 1)
        self.assertEqual(updated_history[-1], new_history)
    
    def test_update_history_single_item(self):
        # Test case when there's only one item in the history array
        history_array = ["initial message"]
        new_history = "second message"
        
        updated_history = update_history(new_history, history_array)
        
        self.assertEqual(len(updated_history), 2)
        self.assertEqual(updated_history[-1], new_history)

    def test_update_history_max_limit(self):
        # Test case when history array has exactly 9 items, the new one should fit without removing any
        history_array = [f"old message {i}" for i in range(1, 10)]  # 9 messages
        new_history = "new message"
        
        updated_history = update_history(new_history, history_array)
        
        self.assertEqual(len(updated_history), 10)
        self.assertEqual(updated_history[-1], new_history)
        self.assertIn("old message 1", updated_history)  # The first message should still be there

if __name__ == '__main__':
    unittest.main()
