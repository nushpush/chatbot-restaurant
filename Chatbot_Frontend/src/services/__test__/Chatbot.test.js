import React from 'react';
import '../__mocks__/svgMock.js';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Chatbot from '../components/Chatbot';
import socketIOClient from 'socket.io-client';
import '@testing-library/jest-dom';
import { chatService } from '../services/Chatservice';

// Mock socket.io-client
jest.mock('socket.io-client');
const mockedSocket = {
  emit: jest.fn(),
  on: jest.fn(),
  off: jest.fn(),
};
socketIOClient.mockReturnValue(mockedSocket);

// Mock chatService methods
jest.mock('../services/Chatservice', () => ({
  getChatHistory: jest.fn(),
  addVote: jest.fn(),
  getBotResponse: jest.fn(),
  editMessage: jest.fn(),
  regenerateResponse: jest.fn(),
}));

describe("Chatbot component", () => {
  let messages, setActiveMessage, setMessages;

  // Mock localStorage
  beforeAll(() => {
    global.localStorage = {
      getItem: jest.fn(() => 'testUserId'), // Simulate a value for localStorage.getItem
      setItem: jest.fn(),
      removeItem: jest.fn(),
      clear: jest.fn(),
    };
  });

  beforeEach(() => {
    mockedSocket.on.mockClear();
    mockedSocket.off.mockClear();
    messages = [{ text: 'Hello' }, { text: 'Hi' }];
    setActiveMessage = jest.fn();
    setMessages = jest.fn();
  });

  afterAll(() => {
    // Cleanup mock to prevent affecting other tests
    global.localStorage = undefined;
  });

  test("renders initial chatbot interface", () => {
    render(<Chatbot userId="testUser" />);
    expect(screen.getByAltText("Bot Avatar")).toBeInTheDocument();
    expect(screen.getByAltText("User Avatar")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Type a message...")).toBeInTheDocument();
  });

  test("shows initial typing indicator message on open", async () => {
    render(<Chatbot userId="testUser" />);
    fireEvent.click(screen.getByAltText("Bot Avatar")); // Simulate opening the chatbot

    await waitFor(() => {
      expect(screen.getByText("Hi Chef! How can I inspire your menu today?")).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(
        screen.getByText("What information are you looking for? Please use the navigation below or type in the text box.")
      ).toBeInTheDocument();
    });
  });

  test("sends a message and receives bot response", async () => {
    render(<Chatbot userId="testUser" />);

    const input = screen.getByPlaceholderText("Type a message...");
    fireEvent.change(input, { target: { value: "Hello" } });
    fireEvent.keyPress(input, { key: "Enter", code: "Enter" });

    // Expect user message to appear in chat
    await waitFor(() => {
      expect(screen.getByText("Hello")).toBeInTheDocument();
    });

    // Simulate receiving a bot response via socket
    mockedSocket.on.mock.calls.forEach(([event, callback]) => {
      if (event === "response") {
        callback({ message: "Hello, how can I help you today?" });
      }
    });

    // Expect bot message to appear in chat
    await waitFor(() => {
      expect(screen.getByText("Hello, how can I help you today?")).toBeInTheDocument();
    });
  });

  test("handles loading and evaluation result", async () => {
    render(<Chatbot userId="testUser" />);

    // Simulate bot sending a loading message
    mockedSocket.on.mock.calls.forEach(([event, callback]) => {
      if (event === "show_loader") {
        callback({ message: "Loading..." });
      }
    });

    await waitFor(() => {
      expect(screen.getByText("Loading...")).toBeInTheDocument();
    });

    // Simulate bot sending evaluation result
    mockedSocket.on.mock.calls.forEach(([event, callback]) => {
      if (event === "response") {
        callback({
          message: "Here is the evaluation.",
          evaluation: {
            latency: "0.5s",
            answer_correctness: 0.9,
          },
        });
      }
    });

    await waitFor(() => {
      expect(screen.getByText("Here is the evaluation.")).toBeInTheDocument();
      expect(screen.getByText("Latency: 0.5s")).toBeInTheDocument();
      expect(screen.getByText("Answer Correctness: 0.9")).toBeInTheDocument();
    });
  });

  test("toggles maximize and minimize states", async () => {
    render(<Chatbot userId="testUser" />);
    
    const maximizeButton = screen.getByAltText("Maximize");
    fireEvent.click(maximizeButton);

    expect(screen.getByAltText("Restore")).toBeInTheDocument();

    fireEvent.click(screen.getByAltText("Restore"));
    expect(screen.getByAltText("Maximize")).toBeInTheDocument();
  });

  test("displays and updates typing indicator for long messages", async () => {
    render(<Chatbot userId="testUser" />);

    // Simulate typing indicator with a long message
    mockedSocket.on.mock.calls.forEach(([event, callback]) => {
      if (event === "response") {
        callback({
          message: "This is a long response message from the bot to simulate typing...",
        });
      }
    });

    await waitFor(() => {
      expect(screen.getByText(/This is a long response/)).toBeInTheDocument();
    });
  });

  test("sanitizes incoming message HTML", async () => {
    render(<Chatbot userId="testUser" />);

    mockedSocket.on.mock.calls.forEach(([event, callback]) => {
      if (event === "response") {
        callback({
          message: "<script>alert('xss')</script>Safe message",
        });
      }
    });

    await waitFor(() => {
      expect(screen.queryByText("alert('xss')")).not.toBeInTheDocument();
      expect(screen.getByText("Safe message")).toBeInTheDocument();
    });
  });

// Assuming we have jest.fn() mocks or spyOn for asynchronous methods like getChatHistory, createResponse, editMessage, regenerateResponse, addVote, etc.

  test("handleAgentChange sets selected agent and greeting message", () => {
    render(<Chatbot />);
    const dropdown = screen.getByRole("combobox");

    fireEvent.change(dropdown, { target: { value: "recipe" } });
    expect(screen.getByText(/help you with recipes/i)).toBeInTheDocument();

    fireEvent.change(dropdown, { target: { value: "ingredient" } });
    expect(screen.getByText(/assist with ingredient information/i)).toBeInTheDocument();
  });

  test("handleKeyDown submits message on Enter key press", () => {
    render(<Chatbot />);
    const input = screen.getByPlaceholderText("Type a message");

    fireEvent.change(input, { target: { value: "Hello, chatbot!" } });
    fireEvent.keyDown(input, { key: "Enter", code: "Enter" });

    expect(screen.getByText("Hello, chatbot!")).toBeInTheDocument();
  });

  test("toggleChatbot opens and closes chatbot, resets history", async () => {
    render(<Chatbot />);
    const toggleButton = screen.getByText(/Open Chat/i);

    fireEvent.click(toggleButton); // Open chatbot
    expect(screen.getByRole("chat-popup")).toBeInTheDocument();

    fireEvent.click(toggleButton); // Close chatbot
    expect(screen.queryByRole("chat-popup")).not.toBeInTheDocument();
  });

  test("toggleMaximize toggles between maximized and minimized states", () => {
    render(<Chatbot />);
    const maximizeButton = screen.getByRole("button", { name: "Maximize" });

    fireEvent.click(maximizeButton);
    expect(screen.getByRole("chat-popup")).toHaveClass("maximized");

    fireEvent.click(maximizeButton);
    expect(screen.getByRole("chat-popup")).not.toHaveClass("maximized");
  });

  test("toggleMinimize minimizes chat window and hides popup", () => {
    render(<Chatbot />);
    const minimizeButton = screen.getByRole("button", { name: "Minimize" });

    fireEvent.click(minimizeButton);
    expect(screen.queryByRole("chat-popup")).not.toBeVisible();
  });

  test("handleChatHistoryClick loads chat history and toggles sidebar", async () => {
    chatService.getChatHistory.mockResolvedValue([{ text: "Previous chat message" }]);
    render(<Chatbot />);
    const historyButton = screen.getByText("Chat History");

    fireEvent.click(historyButton);
    expect(await screen.findByText("Previous chat message")).toBeInTheDocument();
  });

  test("handleVote sets like or dislike and calls API", async () => {
    render(<Chatbot />);
    const voteButton = screen.getByText("Like");

    fireEvent.click(voteButton);
    expect(chatService.addVote).toHaveBeenCalledWith(expect.any(String), true);
  });

  test("handleReloadResponse reloads bot response with updated text and ratings", async () => {
    const mockMessage = { messageId: "123", text: "User query" };
    chatService.getBotResponse.mockResolvedValue({ response: "Updated bot response", rating: [{ "flesch_kincaid_grade_level/v1/score": 5 }] });
    chatService.regenerateResponse.mockResolvedValue({ data: "new response data" });
    render(<Chatbot />);
    
    await handleReloadResponse(mockMessage);
    expect(screen.getByText(/Updated bot response/i)).toBeInTheDocument();
  });
  
  test("handleEditMessage sets message for editing", () => {
    render(<Chatbot />);
    const editButton = screen.getByText("Edit");

    fireEvent.click(editButton);
    expect(screen.getByRole("textbox")).toHaveValue("Existing message text");
  });

  test("handleCancelEdit clears edit state", () => {
    render(<Chatbot />);
    const cancelEditButton = screen.getByText("Cancel Edit");

    fireEvent.click(cancelEditButton);
    expect(screen.getByRole("textbox")).toHaveValue("");
  });

  test("handleSaveEditMessage saves edits and updates messages list", async () => {
    chatService.editMessage.mockResolvedValue({ success: true, data: { messageId: "123", text: "Edited message" } });
    render(<Chatbot />);
    const saveButton = screen.getByText("Save");

    fireEvent.click(saveButton);
    expect(await screen.findByText("Edited message")).toBeInTheDocument();
  });
  
    
  
  test('handleNextVersion should activate the next message version and update statuses correctly', () => {
    const currentMessage = messages[0];
    const { rerender } = render(
      <Chatbot
      messages={messages}
      currentMessage={currentMessage}
      setMessages={setMessages}
      setActiveMessage={setActiveMessage}
    />
    );

    const instance = screen.getByText("Hello");
    fireEvent.click(instance);
    rerender(<Chatbot messages={messages} />);

    expect(setActiveMessage).toHaveBeenCalledWith(messages[1]);
    expect(setMessages).toHaveBeenCalledWith(expect.any(Function));
  });

  test('handlePreviousVersion should activate the previous message version and update statuses correctly', () => {
    const currentMessage = messages[1];
    const { rerender } = render(
      <Chatbot
      messages={messages}
      currentMessage={currentMessage}
      setMessages={setMessages}
      setActiveMessage={setActiveMessage}
    />
    );

    const instance = screen.getByText("Hi");
    fireEvent.click(instance);
    rerender(<Chatbot messages={messages} />);

    expect(setActiveMessage).toHaveBeenCalledWith(messages[0]);
    expect(setMessages).toHaveBeenCalledWith(expect.any(Function));
  });

  test('renderMessageText should correctly render long text with "Read More" label', () => {
    const longMessage = { text: "A ".repeat(72), isLoading: false };
    render(<Chatbot renderMessageText={(message) => renderMessageText(longMessage, false, 1)} />);
    expect(screen.getByText("Read More")).toBeInTheDocument();
  });

  test('renderMessageText should display full text if isExpanded is true', () => {
    const longMessage = { text: "A ".repeat(72), isLoading: false };
    render(<Chatbot renderMessageText={(message) => renderMessageText(longMessage, true, 1)} />);
    expect(screen.queryByText("Read More")).not.toBeInTheDocument();
  });

  test('handleButtonClick should send the message to the server and update the conversation state', async () => {
    render(<Chatbot messages={messages} setMessages={setMessages} />);
    
    const button = screen.getByText("Show me today's menu");
    fireEvent.click(button);

    await waitFor(() => {
      expect(mockedSocket.emit).toHaveBeenCalledWith("buttonclick", expect.objectContaining({
        input: "Show me today's menu"
      }));
    });
    expect(setMessages).toHaveBeenCalledWith(expect.any(Function));
  });

  test('renderMessage should not render messages with non-active status unless they are activeMessage', () => {
    const inactiveMessage = { ...messages[0], status: "edited" };
    render(<Chatbot messages={[inactiveMessage]} activeMessage={null} />);
    
    expect(screen.queryByText("Hello")).not.toBeInTheDocument();
  });

  test('renderMessage should render active messages and show avatars correctly', () => {
    render(<Chatbot messages={messages} activeMessage={messages[0]} />);
    
    expect(screen.getByText("Hello")).toBeInTheDocument();
    expect(screen.getByAltText("user avatar")).toBeInTheDocument();
    expect(screen.getByAltText("bot avatar")).toBeInTheDocument();
  });
  test("displays error message on bot response failure", async () => {
    mockedSocket.on.mock.calls.forEach(([event, callback]) => {
      if (event === "response") {
        callback({ error: "Failed to get response" });
      }
    });
    render(<Chatbot userId="testUser" />);
    fireEvent.change(screen.getByPlaceholderText("Type a message..."), { target: { value: "Test" } });
    fireEvent.keyPress(screen.getByPlaceholderText("Type a message..."), { key: "Enter", code: "Enter" });
  
    await waitFor(() => {
      expect(screen.getByText("Failed to get response")).toBeInTheDocument();
    });
  });

  test("shows loading indicator when bot response is delayed", async () => {
    mockedSocket.on.mock.calls.forEach(([event, callback]) => {
      if (event === "response") {
        setTimeout(() => callback({ message: "Delayed response" }), 3000);
      }
    });
    render(<Chatbot userId="testUser" />);
    fireEvent.change(screen.getByPlaceholderText("Type a message..."), { target: { value: "Hello" } });
    fireEvent.keyPress(screen.getByPlaceholderText("Type a message..."), { key: "Enter", code: "Enter" });
  
    expect(screen.getByText("Typing...")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("Delayed response")).toBeInTheDocument();
    });
  });

  test("disables buttons during message processing", async () => {
    render(<Chatbot userId="testUser" />);
    const input = screen.getByPlaceholderText("Type a message...");
    fireEvent.change(input, { target: { value: "Loading test" } });
    fireEvent.keyPress(input, { key: "Enter", code: "Enter" });
  
    expect(screen.getByRole("button", { name: "Send" })).toBeDisabled();
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Send" })).not.toBeDisabled();
    });
  });

  test("sanitizes HTML with embedded scripts in bot response", async () => {
    mockedSocket.on.mock.calls.forEach(([event, callback]) => {
      if (event === "response") {
        callback({ message: "<a href='http://malicious.com'>Click me</a><script>alert('XSS')</script>" });
      }
    });
    render(<Chatbot userId="testUser" />);
    await waitFor(() => {
      expect(screen.getByText("Click me")).toBeInTheDocument();
      expect(screen.queryByText("alert('XSS')")).not.toBeInTheDocument();
    });
  });

  test("reconnects socket and resumes communication after disconnection", async () => {
    mockedSocket.on.mock.calls.forEach(([event, callback]) => {
      if (event === "disconnect") {
        callback();
      }
      if (event === "connect") {
        callback();
      }
    });
    render(<Chatbot userId="testUser" />);
    mockedSocket.emit("disconnect");
    await waitFor(() => {
      expect(mockedSocket.emit).toHaveBeenCalledWith("connect");
    });
  });

  test("does not send empty message", () => {
    render(<Chatbot userId="testUser" />);
    const input = screen.getByPlaceholderText("Type a message...");
    fireEvent.change(input, { target: { value: "" } });
    fireEvent.keyPress(input, { key: "Enter", code: "Enter" });
  
    expect(mockedSocket.emit).not.toHaveBeenCalledWith("userMessage", expect.anything());
  });
});
