import { chatService } from '../services/Chatservice';
import { environment } from '../environment/environment';

// Mocking fetch and socket.io client
global.fetch = jest.fn();
jest.mock('socket.io-client', () => ({
  io: () => ({
    emit: jest.fn(),
    on: jest.fn()
  })
}));

describe('Chatservice', () => {
  afterEach(() => {
    jest.clearAllMocks(); // Clear mocks after each test
  });

  describe('createConversationId', () => {
    it('should successfully create a conversation ID', async () => {
      const mockResponse = { result: 'conversation123' };
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const userId = 'user1';
      const workspaceId = 'workspace1';

      const result = await chatService.createConversationId(userId, workspaceId);

      expect(fetch).toHaveBeenCalledWith(`${environment.baseUrl}/createConversation`, expect.any(Object));
      expect(result).toBe('conversation123');
    });

    it('should throw an error when the response is not ok', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ message: 'Error' })
      });

      const userId = 'user1';
      const workspaceId = 'workspace1';

      await expect(chatService.createConversationId(userId, workspaceId)).rejects.toThrow('Failed to create a new conversation ID.');
    });
  });

  describe('getBotResponse', () => {
    it('should get bot response successfully', async () => {
      const mockResponse = { response: 'Hello' };
      const userMessage = 'Hi';
      const formData = new FormData();
      formData.append('content', userMessage);
      
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await chatService.getBotResponse(userMessage);

      expect(fetch).toHaveBeenCalledWith(`${environment.baseUrl}/chat`, expect.any(Object));
      expect(result).toEqual(mockResponse);
    });

    it('should throw an error when the response is not ok', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ message: 'Error' })
      });

      await expect(chatService.getBotResponse('Hi')).rejects.toThrow('Network response was not ok');
    });
  });

  describe('createMessage', () => {
    it('should successfully create a message', async () => {
      const mockResponse = { result: 'message123' };
      const conversationId = 'conversation123';
      const message = 'Hello!';
      const userId = 'user1';

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await chatService.createMessage(conversationId, message, userId);

      expect(fetch).toHaveBeenCalledWith(`${environment.baseUrl}/createMessage`, expect.any(Object));
      expect(result).toBe(mockResponse);
    });

    it('should throw an error if creating message fails', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ message: 'Error' })
      });

      await expect(chatService.createMessage('conversation123', 'Hello!', 'user1')).rejects.toThrow('Failed to createmessage');
    });
  });

  describe('getChatHistory', () => {
    it('should get chat history successfully', async () => {
      const mockSocketResponse = {
        success: true,
        data: {
          Messages: [
            {
              content: 'Hi',
              message_id: 'msg1',
              created_at: '2024-10-21T00:00:00Z',
              Responses: [
                {
                  response: 'Hello',
                  response_id: 'resp1',
                  created_at: '2024-10-21T00:01:00Z',
                  vote: 1,
                },
              ],
            },
          ],
        },
      };

      const conversationId = 'conversation123';
      const socket = require('socket.io-client').io();
      socket.on.mockImplementationOnce((event, callback) => {
        if (event === 'chat_history_response') {
          callback(mockSocketResponse);
        }
      });

      const result = await chatService.getChatHistory(conversationId);

      expect(socket.emit).toHaveBeenCalledWith('get_chat_history', { conversationId });
      expect(result).toEqual([
        {
          text: 'Hi',
          sender: 'user',
          message_id: 'msg1',
          created_at: '2024-10-21T00:00:00Z',
        },
        {
          text: 'Hello',
          sender: 'bot',
          doc_ref: undefined,
          message_id: 'msg1',
          response_id: 'resp1',
          created_at: '2024-10-21T00:01:00Z',
          vote: 1,
        },
      ]);
    });

    it('should throw an error if chat history fails', async () => {
      const socket = require('socket.io-client').io();
      socket.on.mockImplementationOnce((event, callback) => {
        if (event === 'chat_history_response') {
          callback({ success: false, message: 'Failed' });
        }
      });

      await expect(chatService.getChatHistory('conversation123')).rejects.toThrow('Failed to fetch chat history: Failed');
    });
  });

  describe('addVote', () => {
    it('should successfully add a vote', async () => {
      const mockSocketResponse = { success: true, response: { message: 'Voted successfully' } };
      const responseId = 'resp1';
      const vote = 1;
      const socket = require('socket.io-client').io();

      socket.on.mockImplementationOnce((event, callback) => {
        if (event === 'vote_updated') {
          callback(mockSocketResponse);
        }
      });

      const result = await chatService.addVote(responseId, vote);

      expect(socket.emit).toHaveBeenCalledWith('vote_response', { responseId, vote });
      expect(result).toEqual(mockSocketResponse);
    });

    it('should throw an error if adding vote fails', async () => {
      const socket = require('socket.io-client').io();
      socket.on.mockImplementationOnce((event, callback) => {
        if (event === 'vote_updated') {
          callback({ success: false, message: 'Vote failed' });
        }
      });

      await expect(chatService.addVote('resp1', 1)).rejects.toThrow('Failed to add vote');
    });
  });

  // Add other test cases similarly based on the service methods...
});
