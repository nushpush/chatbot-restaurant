// ChatService.test.js
import { createConversationId, getBotResponse, createMessage, createResponse, getChatHistory, getAllConversationName, editMessage, fetchConversationName } from './ChatService'; // Adjust the import based on your file structure
import fetch from 'node-fetch';

jest.mock('node-fetch');

describe('ChatService', () => {
    afterEach(() => {
        jest.clearAllMocks(); // Clear mocks after each test
    });

    test('createConversationId should return conversation ID', async () => {
        const mockResponse = {
            ok: true,
            json: jest.fn().mockResolvedValue({ result: '12345' }),
        };
        fetch.mockResolvedValue(mockResponse);

        const result = await createConversationId('userId', 'workspaceId');
        expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/createConversation'), expect.any(Object));
        expect(result).toBe('12345');
    });

    test('createConversationId should throw an error for failed response', async () => {
        const mockResponse = {
            ok: false,
            json: jest.fn().mockResolvedValue({ message: 'Error' }),
        };
        fetch.mockResolvedValue(mockResponse);

        await expect(createConversationId('userId', 'workspaceId')).rejects.toThrow('Failed to create a new conversation ID.');
    });

    test('getBotResponse should return bot response', async () => {
        const mockResponse = {
            ok: true,
            json: jest.fn().mockResolvedValue({ response: 'Hello from bot' }),
        };
        fetch.mockResolvedValue(mockResponse);

        const result = await getBotResponse('Hello');
        expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/chat'), expect.any(Object));
        expect(result).toEqual({ response: 'Hello from bot' });
    });

    test('getBotResponse should throw an error for failed response', async () => {
        const mockResponse = {
            ok: false,
            json: jest.fn().mockResolvedValue({ message: 'Error' }),
        };
        fetch.mockResolvedValue(mockResponse);

        await expect(getBotResponse('Hello')).rejects.toThrow('Network response was not ok');
    });

    test('createMessage should create a message and return response', async () => {
        const mockResponse = {
            ok: true,
            json: jest.fn().mockResolvedValue({ success: true }),
        };
        fetch.mockResolvedValue(mockResponse);

        const result = await createMessage('conversationId', 'message', 'userId');
        expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/createMessage'), expect.any(Object));
        expect(result).toEqual({ success: true });
    });

    test('createResponse should create a response and return response', async () => {
        const mockResponse = {
            ok: true,
            json: jest.fn().mockResolvedValue({ success: true }),
        };
        fetch.mockResolvedValue(mockResponse);

        const result = await createResponse('messageId', 'response', 'conversationId', 1, 2, 3, 4, 5);
        expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/createResponse'), expect.any(Object));
        expect(result).toEqual({ success: true });
    });

    test('getChatHistory should return chat history', async () => {
        const mockSocket = {
            emit: jest.fn(),
            on: jest.fn((event, callback) => {
                // Simulate chat history response
                const response = { success: true, data: { Messages: [] } };
                callback(response);
            }),
        };
        global.socket = mockSocket; // Mock the socket

        const result = await getChatHistory('conversationId');
        expect(mockSocket.emit).toHaveBeenCalledWith('get_chat_history', { conversationId: 'conversationId' });
        expect(result).toEqual([]); // Adjust based on your expected response
    });

    test('getAllConversationName should return conversation names', async () => {
        const mockResponse = {
            ok: true,
            json: jest.fn().mockResolvedValue({ success: true, data: ['Chat1', 'Chat2'] }),
        };
        fetch.mockResolvedValue(mockResponse);

        const result = await getAllConversationName('userId');
        expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/getAllChat'), expect.any(Object));
        expect(result).toEqual(['Chat1', 'Chat2']);
    });

    test('editMessage should edit a message and return result', async () => {
        const mockResponse = {
            ok: true,
            json: jest.fn().mockResolvedValue({ success: true }),
        };
        fetch.mockResolvedValue(mockResponse);

        const result = await editMessage('messageId', 'New message', 'userId');
        expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/editMessage'), expect.any(Object));
        expect(result).toEqual({ success: true });
    });

    test('fetchConversationName should return conversation name', async () => {
        const mockResponse = {
            ok: true,
            json: jest.fn().mockResolvedValue({ data: 'Conversation Name' }),
        };
        fetch.mockResolvedValue(mockResponse);

        const result = await fetchConversationName('conversationId');
        expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/getChatNameForCurrentId'), expect.any(Object));
        expect(result).toBe('Conversation Name');
    });
});

