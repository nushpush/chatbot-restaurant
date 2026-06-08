import React, { useState, useEffect, useRef, useCallback } from "react";
import "./Chatbot.css";
import botAvatar from "../assets/images/MessageBot.svg";
import closeIcon from "../assets/images/Side Menu.svg";
import maximizeIcon from "../assets/images/GenAI.svg";
import UserAvatar from "../assets/images/UserIcon.svg";
import restoreIcon from "../assets/images/maximizeIcon.svg";
import hamburgericon from "../assets/images/HamburgerIcon.png";
import Loader from "../Loader/Loader";
import minimize from "../assets/images/minimize 1.png";
import sendDisabledIcon from "../assets/images/Send-disable 1.png";
import sendEnabledIcon from "../assets/images/Send-enable 1.png";
import ChatHistory from "./Chathistory";
import { environment } from "../environment/environment"
// import editIcon from "../assets/images/editIcon.png";
import { chatService } from "../services/Chatservice";
// import { fetchAndSetChatNames } from "../utilities/chatServiceUtilities";
// import likeIcon from "../assets/images/like (1).png";
// import dislikeIcon from "../assets/images/dont-like.png";
// import reloadIcon from "../assets/images/reload.png";
// import Afterlike from "../assets/images/liked.png";
// import afterDislikeIcon from "../assets/images/disliked.png";
import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";
// import { sendMessage, onMessage } from "../services/socket_service.js";
import io from "socket.io-client";
import BouncingDotsLoader from "../Loader/BouncingDotLoader";
// import { typeMessage } from "../utilities/messageUtilities";
import sanitizeHtml from "sanitize-html";
// import { environment } from "../environment/environment"
 
// const socket = io("http://localhost:5000");
const ragas = 'http://localhost:5000/api/v1/llmevaluate';
const userId = localStorage.getItem('userId');
const socket = io(`${environment.baseUrl}`, {
  query: {
      user_id: userId  // Include user_id in the connection options
  }
});
function Chatbot({ userId }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);
  const [currentTime, setCurrentTime] = useState("");
  const [hoverText, setHoverText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [expandedMessages, setExpandedMessages] = useState({});
  const [isMinimized, setIsMinimized] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [activeConversationId, setactiveConversationId] = useState(null);
  const [newChatInitiate, setNewChatInitiate] = useState(0);
  const [isNewChatDisabled, setIsNewChatDisabled] = useState(false);
  // const [minimizedConversationId, setMinimizedConversationId] = useState(null);
  const [editMessageId, setEditMessageId] = useState(null);
  const [editContent, setEditContent] = useState("");
  const [chatHistory, setChatHistory] = useState({});
  const [displayedConversationName, setDisplayedConversationName] =
    useState("New chat");
  const [typingConversationId, setTypingConversationId] = useState(null);
  const textareaRef = useRef(null);
  const [likedMessages, setLikedMessages] = useState({});
  const [dislikedMessages, setDislikedMessages] = useState({});
  const [activeMessage, setActiveMessage] = useState(null);
  // const [activeResponse,setActiveResponse] =useState(null)
  const [lastUserMessage, setLastUserMessage] = useState('');
  const [selectedAgent, setSelectedAgent] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isSecondMessageDisplayed, setIsSecondMessageDisplayed] = useState(false);
  const messageListRef = useRef(null);
  const [queue, setQueue] = useState([]);
  const [isDotLoading, setIsDotLoading] = useState(false);
  const [isTypingMessage, setIsTypingMessage] = useState(false);
  const [clickedId, setClickedId] = useState(null);
  // const [showButtons, setShowButtons] = useState(false);

  // const [isUserScrolling, setIsUserScrolling] = useState(false);

  // let userId = userId;
  console.log("user------id--------"+ userId)
  let workspaceId = 1;

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      // First message with typing indicator
      showTypingIndicator(
        "Hi Chef! How can I inspire your menu today?",
        300, // Delay for first message
        () => {
          // Second message will only show after the first message finishes typing
          showTypingIndicator(
            "What information are you looking for? Please use the navigation below or type in the text box.",
            300, // Delay for second message
            () => {
              // After second message, update the state to display the buttons
              setIsSecondMessageDisplayed(true);
            }
          );
        }
      );
    }
  }, [isOpen, messages.length]);
  

  const showTypingIndicator = useCallback(
    (finalMessage, initialDelay, callback) => {
      console.log("finaleMEssage", finalMessage);
      setIsTypingMessage(true);
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: "", sender: "bot", typing: true },
      ]);
      setIsTyping(true);
      setTimeout(() => {
        let charIndex = -1;
        const messageLength = finalMessage.length;
        // Dynamically adjust the typing speed based on message length
        const dynamicTypingSpeed = messageLength > 100 ? 10 : 35;
        const typeCharacter = () => {
          charIndex++;
          if (charIndex < finalMessage.length) {
            const appendCharacter = (message, char) => {
  return { ...message, text: message.text + char };
};

const updateMessages = (messages, char) => {
  return messages.map((msg) => {
    return msg.typing ? appendCharacter(msg, char) : msg;
  });
};

setMessages((prevMessages) => updateMessages(prevMessages, finalMessage[charIndex]));

            setTimeout(typeCharacter, dynamicTypingSpeed); // Continue typing with a small delay
          } else {
            setIsTyping(false);
            setMessages((prevMessages) => {
              const updatedMessages = prevMessages.filter((msg) => !msg.typing); // Remove the typing indicator
              const newMessages = [
                ...updatedMessages,
                {
                  text: finalMessage,
                  sender: "bot",
                  createdAt: new Date().toISOString(),
                  status: "active",
                },
              ];

              console.log("Updated Messages:", newMessages); // Log the updated messages array

              return newMessages;
            });
            if (callback) {
              callback(); // Trigger the callback for the next message
            }
          }
          setIsTypingMessage(false);
        };

        typeCharacter(); // Start typing characters
      }, initialDelay);
    },
    []
  );

  useEffect(() => {
    const handleMessage = async(data) => {
      console.log("Received data:", data);

      if (data.message === "Loading...") {
        // Only add loading message if no typing is in progress
        setIsDotLoading(true);
        setMessages((prevQueue) => [
          ...prevQueue,
          {
            text: "",
            sender: "bot",
            isLoading: true,
            id: new Date().getTime(),
            status: "active",
          }, // Add a loading message
        ]);

        console.log("isDotLoading insidehandlemessage", isDotLoading);
      } else if (data.message === "Hideloader") {
        setIsDotLoading(false);
        setMessages((prevQueue) =>
          prevQueue.map((msg) =>
            msg.isLoading
              ? { ...msg, isLoading: false, text: "", status: "edited" }
              : msg
          )
        );
      } else {
        const sanitizedMessage = sanitizeHtml(data.message);
        console.log("Sanitized message:", sanitizedMessage);

        
        
 try {
          const evaluationBody = {
            inputs: [lastUserMessage], // Replace this with dynamic question if needed
            response: [sanitizedMessage]  // The actual response from the bot
          };

          const evalResponse = await fetch(ragas, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(evaluationBody),
          });

          const evalResult = await evalResponse.json();
		  console.log('Evaluation result:', evalResult);
          const ratingText = `Ratings -<ul>
              <li>Latency: ${evalResult[0]["latency"]}</li>
              <li>Answer_Correctness: ${evalResult[0]["answer_correctness/v1/score"]}</li>
              <li>Answer_Similarity: ${evalResult[0]["answer_similarity/v1/score"]}</li>
              <li>Answer_Relevance: ${evalResult[0]["answer_relevance/v1/score"]}</li>
              <li>Flesch_kincaid_grade_level: ${evalResult[0]["flesch_kincaid_grade_level/v1/score"]}</li>
              <li>Ari_grade_level: ${evalResult[0]["ari_grade_level/v1/score"]}</li>
            </ul>`;
              const combinedText = `${sanitizedMessage} ${ratingText}`
              // const combinedText = `${sanitizedMessage}`
          // Update messages with the evaluation scores
          setMessages((prevQueue) => [
            ...prevQueue,
            {
              text: combinedText,
              sender: 'bot',
              id: new Date().getTime(),
              isLoading: false,

            }
          ]);
        } 
        catch (error) {
          console.error('Error fetching evaluation result:', error);
        }       
              
        
        setQueue((prevQueue) => [
          ...prevQueue,
          {
            text: sanitizedMessage,
            sender: "bot",
            id: new Date().getTime(),
            isLoading: false,
          },
        ]);
      }
    };

    socket.on("response", handleMessage);
    socket.on("agentresponse", handleMessage);
    socket.on("show_loader", handleMessage); // Listen for loader events

    return () => {
      socket.off("response", handleMessage);
      socket.off("show_loader", handleMessage);
      socket.off("agentresponse", handleMessage);
    };
  }, [lastUserMessage]);

  const processQueue = () => {
    if (queue.length === 0 || isTyping) return;
    const [firstMessage, ...remainingQueue] = queue;

    showTypingIndicator(firstMessage.text, 0, () => {
      setQueue(remainingQueue);
    });
  };

  useEffect(() => {
    const intervalId = setInterval(processQueue, 100);
    return () => clearInterval(intervalId);
  }, [processQueue]);

  useEffect(() => {
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
    }
  }, [messages, messageListRef]);

  useEffect(() => {}, [currentConversationId]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.selectionStart = textareaRef.current.selectionEnd =
        textareaRef.current.value.length;
      textareaRef.current.focus();
    }
  }, [editMessageId]);

  useEffect(() => {
    if (isOpen) {
      const now = new Date();
      const hours = now.getHours() % 12 || 12; // Convert to 12-hour format
      const minutes = now.getMinutes().toString().padStart(2, "0");
      const ampm = now.getHours() >= 12 ? "pm" : "am";
      const timeString = `Today, ${hours}:${minutes} ${ampm}`;
      setCurrentTime(timeString);
    }
  }, [isOpen]);
  // const selectedWorkspace = useSelector(
  //   (state) => state.workspace.selectedWorkspace.employeeRoles
  // );
  const typeConversationName = (fullName, setDisplayedConversationName) => {
    setDisplayedConversationName(""); // Reset the displayed name to ensure it starts from empty
    let index = -1;
    const interval = setInterval(() => {
      setDisplayedConversationName((prev) => {
        if (index < fullName.length) {
          return prev + fullName[index];
        } else {
          clearInterval(interval);
          return prev;
        }
      });

      index++;
    }, 30); // Adjust the speed as necessary
  };

// Function to handle conversation creation
  const createConversation = (userId, workspaceId) => {
    return new Promise((resolve, reject) => {
      // Emit a request to the server to create a new conversation
      socket.emit("create_conversation", {
        user_id: userId,
        workspace_id: workspaceId,
      });

      // Listen for the conversation_created event
      socket.on("conversation_created", (response) => {
        const { conversationId } = response;
        console.log(
          "Conversation created successfully. conversationId is:",
          conversationId
        );
        resolve(conversationId); // Return the conversationId when created
      });

      // Handle any error in conversation creation
      socket.on("conversation_creation_error", (error) => {
        console.error("Failed to create conversation:", error);
        reject(error);
      });
    });
  };

  const createMessage = (userMessage, conversationId, userId) => {
    return new Promise((resolve, reject) => {
      socket.off("message_created");
      socket.emit("create_message", {
        message: userMessage,
        conversationId: conversationId,
        user_id: userId,
      });
      socket.on("message_created", (response) => {
        const { messageId, conversationId, belongsToAfterEdit } = response;
        console.log("Message sent successfully:", response);

        // Update messages with the newly created messageId and other details
        setMessages((prevMessages) => {
          return prevMessages.map((msg) =>
            msg.text === userMessage && !msg.message_id
              ? {
                  ...msg,
                  message_id: messageId,
                  conversationId: conversationId,
                  status: "active",
                  belongs_to_after_edit: belongsToAfterEdit,
                }
              : msg
          );
        });
        console.log("messageID is", messageId);
        resolve(messageId);
      });
      socket.on("message_creation_error", (error) => {
        console.error("failed to craete message:", error);
        reject(error);
      });
    });
  };

  const createResponse = (messageId, responseText, conversationId,flesch_kincaid_grade_level,ari_grade_level,answer_similarity,answer_correctness,answer_relevance) => {
  console.log("messageID is", messageId, "responseText is", responseText, "conversationId is", conversationId);
 
  return new Promise((resolve, reject) => {
      socket.off('response_created');
      // Emit a request to the server to create a new response
      socket.emit('create_response', {
          messageId: messageId,
          response: responseText,
          conversationId: conversationId,
          flesch_kincaid_grade_level: flesch_kincaid_grade_level,
          ari_grade_level: ari_grade_level,
          answer_similarity: answer_similarity,
          answer_correctness: answer_correctness,
          answer_relevance: answer_relevance

      });

      // Listen for the response_created event
      socket.on('response_created', (response) => {
          const { success, message, data } = response;
          if (success) {
              console.log("Response created successfully:", data);
              resolve(data);  // Return the created response data
          } else {
              reject(message);
          }
      });

      // Handle any error in response creation
      socket.on('response_creation_error', (error) => {
          console.error("Failed to create response:", error);
          reject(error);
      });
  });
};

const fetchConversationName = (conversationId) => {
  return new Promise((resolve, reject) => {
    // Emit the event to request the conversation name
    socket.emit('get_chatname_for_current_id', { conversationId });

    // Listen for the response
    socket.on('conversation_found', (data) => {
      if (data.success) {
        resolve(data.data);  // Resolve with the conversation name
      } else {
        reject(data.error);  // Reject with the error message
      }
    });

    socket.on('conversation_not_found', (error) => {
      reject(error.error);  // Reject with the error message
    });

    socket.on('get_chat_history_error', (error) => {
      reject(error.error);  // Reject with the error message
    });
  });
};

  // Function to handle message submission
  const handleMessageSubmit = async () => {
    console.log("selectedAgent is", selectedAgent);
    let conversationId = currentConversationId;
    let isNewConversation = false;
    // Check if the input is empty
    if (inputValue.trim() === "") return;
  
    const userMessage = inputValue;
    setInputValue("");  // Clear input field
  
    // Add user message to the UI
    let newMessage = {
        text: userMessage,
        sender: "user",
        createdAt: new Date().toISOString(),
        conversationId: conversationId,
        messageId: 0,
        status: 'active',
        version: 1,
        belongsTo: null,
    };
  
    setMessages((prevMessages) => [...prevMessages, newMessage]);
  
    try {
        // If new chat is initiated or no conversation ID, create a new conversation
        if (newChatInitiate === 1 || !conversationId) {
            conversationId = await createConversation(userId, workspaceId);
            setCurrentConversationId(conversationId);
            setTypingConversationId(conversationId);
            setNewChatInitiate(0);
            setIsNewChatDisabled(false);
            setDisplayedConversationName("New chat");
            isNewConversation = true;
        }
        console.log("conversationid id", conversationId);
        // Now that we have the conversationId, send the message to the server
        const messageId= await createMessage(userMessage, conversationId, userId);
        console.log("messageID is", messageId);
        // Emit the message to the agent
        socket.emit('message', {
            input: userMessage,
            agent: selectedAgent,
            conversationId , // Use the new or existing conversationId
            userId,
            messageId
          });
          
          socket.on('response', async (data) => {
            console.log("Bot response received:", data);
            // Handle the bot response
            const sanitizedMessage = sanitizeHtml(data.message);
            const botResponse = {
              text: sanitizedMessage,
              sender: "bot",
              responseId: 0,  
              messageId:messageId, 
              status: 'active',
            };
      console.log("sanitisedMessage",sanitizedMessage)
      console.log("botResponse",botResponse)
            // Update the UI with the bot's response
            //  setMessages((prevMessages) => [...prevMessages, botResponse]);
            console.log("botconversation",conversationId)
            // Create the response in the backend
            const evaluationBody = {
              inputs: [lastUserMessage], // Replace this with dynamic question if needed
              response: [sanitizedMessage]  // The actual response from the bot
            };
  
  
            const evalResponse = await fetch(ragas, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(evaluationBody),
            });
  
            const evalResult = await evalResponse.json();
            const flesch_kincaid_grade_level=evalResult[0]?.["flesch_kincaid_grade_level/v1/score"] || 0;
            const ari_grade_level=evalResult[0]?.["ari_grade_level/v1/score"] || 0;
            const answer_correctness=evalResult[0]?.["answer_correctness/v1/score"] || 0;
            const answer_relevance=evalResult[0]?.["answer_relevance/v1/score"] || 0;
            const answer_similarity=evalResult[0]?.["answer_similarity/v1/score"] || 0;
            const createResponseResult = await createResponse(messageId, sanitizedMessage, conversationId,flesch_kincaid_grade_level,ari_grade_level,answer_similarity,answer_correctness,answer_relevance);
            console.log("Created response", createResponseResult)
            if (!createResponseResult) {
              throw new Error("Failed to create response");
            }
      
            const responseData = createResponseResult.data;
            console.log("responseData",responseData)
            // Update the bot response with the actual responseId and other details
            // setMessages((prevMessages) => {
            //   return prevMessages.map((msg) =>
            //     msg.text === sanitizedMessage && msg.sender === "bot" && msg.responseId === 0
            //       ? { ...msg, responseId: responseData.responseId, version: responseData.version, status: responseData.status }
            //       : msg
            //   );
            // });
          });
  
  
        // Clear the selected agent after message submission
        setSelectedAgent('');
        setLastUserMessage(userMessage);
    } catch (error) {
        console.error("Error during message submission:", error);
    }
  };

  // Function to send message to the server

  const handleAgentChange = (e) => {
    const selectedAgent = e.target.value;
    setSelectedAgent(selectedAgent);
    console.log("selectedAgent", selectedAgent);
    // Send a greeting message based on the selected agent
    const greetingMessage =
      selectedAgent === "recipe"
        ? "Hello! I'm here to help you with recipes. What recipe are you looking for?"
        : "Hello! I'm here to assist with ingredient information. What do you need help with?";

    const botMessage = {
      text: greetingMessage,
      sender: "bot",
      createdAt: new Date().toISOString(),
      status: "active",
      greet: "agent-greeting",
    };
    // setMessages((prevMessages) => [...prevMessages, botMessage]);
    setMessages((prevMessages) => {
      // Filter out any previous greeting message
      const updatedMessages = prevMessages.filter(
        (message) => message.greet !== "agent-greeting"
      );
      // Add the new greeting message
      return [...updatedMessages, botMessage];
    });
  };
  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleMessageSubmit();
    }
  };
  const toggleChatbot = async () => {
    if (isOpen) {
      setMessages([]);
      setIsSidebarOpen(false);
      // setIsMaximized(false);
      setIsOpen(false);
      setCurrentConversationId(null);
      setClickedId(null)
      setIsSecondMessageDisplayed(false)
    } else {
      setCurrentConversationId(currentConversationId);
      setIsMinimized(false);
      setIsMaximized(false);

    }
    try {
      const response = await fetch(
        "https://genaiazurellmapp.azurewebsites.net/api/v1/resethistory",
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error("Network response was not ok " + response.statusText);
      }
      // const data = await response.json();
    } catch (error) {
      console.error("There was a problem with the fetch operation:", error);
    }
    setIsOpen(!isOpen);
  };

  const toOpenChatbot = () => {
    if (isOpen) {
      setMessages([]);
      setIsSidebarOpen(false);
      setIsMaximized(false);
      setCurrentConversationId(null);
    } else {
      setCurrentConversationId(currentConversationId);
      setIsMinimized(false);
      setIsMaximized(false);
    }
    setIsOpen(!isOpen);
  };

  const toggleMaximize = () => {
    setIsMaximized(!isMaximized);
    setIsMinimized(false);
    setIsSidebarOpen(false);
  };

  const toggleMinimize = () => {
    if (!isMinimized) {
      setCurrentConversationId(currentConversationId);
    } else {
      setCurrentConversationId(currentConversationId);
    }
    setIsMinimized(!isMinimized);
    setIsOpen(false);
    setIsSidebarOpen(false);
  };

  const handleChatHistoryClick = async () => {
    console.log("current conversation-----------",currentConversationId)
    setClickedId(currentConversationId)
    if (!isMaximized) {
      setIsMaximized(true);
      setIsSidebarOpen(true);
      if(currentConversationId)
        {
          const message = await chatService.getChatHistory(currentConversationId);
          console.log("message -------------",message)
          setMessages(message);
        }
    } else {
      if(currentConversationId)
      {
        const message = await chatService.getChatHistory(currentConversationId);
        console.log("message -------------",message)
        setMessages(message);
      }
      setIsSidebarOpen(!isSidebarOpen);
    }
  };

  const handleMouseEnter = (text) => {
    setHoverText(text);
  };

  const handleMouseLeave = () => {
    setHoverText("");
  };

  const handleDrag = (e) => {
    const popup = e.target.closest(".popup-container");
    let posX = e.clientX - popup.offsetLeft;
    let posY = e.clientY - popup.offsetTop;

    const mouseMoveHandler = (e) => {
      popup.style.left = `${e.clientX - posX}px`;
      popup.style.top = `${e.clientY - posY}px`;
    };

    const mouseUpHandler = () => {
      document.removeEventListener("mousemove", mouseMoveHandler);
      document.removeEventListener("mouseup", mouseUpHandler);
    };

    document.addEventListener("mousemove", mouseMoveHandler);
    document.addEventListener("mouseup", mouseUpHandler);
  };

  const getChatContentClass = () => {
    let className = "chat-content";
    if (isSidebarOpen) {
      className += " with-sidebar";
    } else if (isMaximized) {
      className += " maximized";
    }
    return className;
  };

  const toggleReadMore = (index) => {
    setIsMaximized(true);
    setExpandedMessages((prevState) => ({
      ...prevState,
      [index]: !prevState[index],
    }));
  };

  const handleGetChatHistory = async (conversationId) => {
    try {
      const fetchMessage = await chatService.getChatHistory(conversationId);
      setMessages(fetchMessage);
    } catch (error) {
      throw error;
    }
  };
  const handleEditMessage = (message) => {
    setEditMessageId(message.messageId);
    setEditContent(message.text);
  };
  const handleCancelEdit = () => {
    setEditMessageId(null);
    setEditContent("");
  };
  const handleSaveEditMessage = async () => {
    setActiveMessage("");
    try {
      const editResult = await chatService.editMessage(
        editMessageId,
        editContent,
        userId
      );
      if (editResult.success) {
        setIsLoading(true);
        const newMessageRecord = editResult.data;
        const newMessage = {
          messageId: newMessageRecord.messageId,
          text: newMessageRecord.content,
          sender: "user",
          version: newMessageRecord.version,
          belongsTo: newMessageRecord.belongsToAfterEdit,
          status: newMessageRecord.status,
        };
        setMessages((prevMessages) => {
          const updatedMessages = prevMessages.map((msg) =>
            msg.messageId === editMessageId ? { ...msg, status: "edited" } : msg
          );
          return [...updatedMessages, newMessage];
        });
        // setMessages((prevMessages) => [...prevMessages, newMessage]);
        const modelResponse = await chatService.getBotResponse(editContent);
        const ratingNewText = `Ratings -<ul>
      <li>Flesch Kincaid Grade Level: ${modelResponse.rating[0]["flesch_kincaid_grade_level/v1/score"]}</li>
      <li>ARI Grade Level: ${modelResponse.rating[0]["ari_grade_level/v1/score"]}</li>
      <li>Answer Similarity: ${modelResponse.rating[0]["answer_similarity/v1/score"]}</li>
      <li>Answer Correctness: ${modelResponse.rating[0]["answer_correctness/v1/score"]}</li>
      <li>Answer Relevance: ${modelResponse.rating[0]["answer_relevance/v1/score"]}</li>
    </ul>`;
        const combinedText = `${modelResponse.response} ${ratingNewText}`;
        // const botResponseText = modelResponse.response.trim();
        const createResponse = await chatService.createResponse(
          newMessageRecord.messageId,
          modelResponse.response,
          currentConversationId,
          modelResponse.rating[0]["flesch_kincaid_grade_level/v1/score"],
          modelResponse.rating[0]["ari_grade_level/v1/score"],
          modelResponse.rating[0]["answer_similarity/v1/score"],
          modelResponse.rating[0]["answer_correctness/v1/score"],
          modelResponse.rating[0]["answer_relevance/v1/score"]
        );
        if (!createResponse) {
          throw new Error("Failed to create response");
        }
        const responseData = createResponse.data;
        const botResponse = {
          messageId: newMessageRecord.messageId,
          text: combinedText,
          sender: "bot",
          createdAt: new Date().toISOString(),
          conversationId: currentConversationId,
          responseId: responseData.responseId,
          status: "active",
          version: responseData.version,
        };
        // Add the bot response to messages
        setMessages((prevMessages) => [...prevMessages, botResponse]);
        setActiveMessage(newMessage);
        setEditMessageId(null);
        setEditContent("");
      }
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };
  const handleVote = async (responseId, voteType) => {
    const newLikedMessages = { ...likedMessages };
    const newDislikedMessages = { ...dislikedMessages };

    if (voteType === true) {
      if (newLikedMessages[responseId] !== true) {
        newLikedMessages[responseId] = true;
        newDislikedMessages[responseId] = false;
        setLikedMessages(newLikedMessages);
        setDislikedMessages(newDislikedMessages);
      }
    } else {
      // If the vote is for "dislike"
      if (newDislikedMessages[responseId] !== true) {
        newLikedMessages[responseId] = false;
        newDislikedMessages[responseId] = true;
        setLikedMessages(newLikedMessages);
        setDislikedMessages(newDislikedMessages);
      }
    }

    try {
      // Perform the API call
      await chatService.addVote(responseId, voteType);
    } catch (error) {
      // Rollback the UI state in case of an error
      console.error("Failed to add vote", error);
      // Revert the state changes
      if (voteType === true) {
        setLikedMessages((prev) => ({
          ...prev,
          [responseId]: false,
        }));
        setDislikedMessages((prev) => ({
          ...prev,
          [responseId]: false,
        }));
      } else {
        setLikedMessages((prev) => ({
          ...prev,
          [responseId]: false,
        }));
        setDislikedMessages((prev) => ({
          ...prev,
          [responseId]: false,
        }));
      }
    }
  };

  const handleReloadResponse = async (message_response) => {
    setIsLoading(true);
    try {
      const userMessage = messages.find(
        (msg) =>
          msg.messageId === message_response.messageId && msg.sender === "user"
      );
      if (!userMessage) {
        console.error("User message not found for this response");
        return;
      }
      setMessages((prevMessages) => {
        const updatedResponses = prevMessages.map((msg) =>
          msg.responseId === message_response.responseId && msg.sender === "bot"
            ? { ...msg, status: "edited" }
            : msg
        );
        return updatedResponses;
      });
      const botResponse = await chatService.getBotResponse(userMessage.text);
      const ratingText = `Ratings -<ul>
      <li>Flesch Kincaid Grade Level: ${botResponse.rating[0]["flesch_kincaid_grade_level/v1/score"]}</li>
      <li>ARI Grade Level: ${botResponse.rating[0]["ari_grade_level/v1/score"]}</li>
      <li>Answer Similarity: ${botResponse.rating[0]["answer_similarity/v1/score"]}</li>
      <li>Answer Correctness: ${botResponse.rating[0]["answer_correctness/v1/score"]}</li>
      <li>Answer Relevance: ${botResponse.rating[0]["answer_relevance/v1/score"]}</li>
    </ul>`;
      const combinedText = `${botResponse.response} ${ratingText}`;
      // const createResponse = await chatService.createResponse(messageData.messageId,response.response, conversationId,response.rating[0]["flesch_kincaid_grade_level/v1/score"],
      // response.rating[0]["ari_grade_level/v1/score"],
      // response.rating[0]["answer_similarity/v1/score"],
      // response.rating[0]["answer_correctness/v1/score"],
      // response.rating[0]["answer_relevance/v1/score"]);
      // const response=await chatService.regenerateResponse(message_response.responseId, botResponse.response);
      const response = await chatService.regenerateResponse(
        message_response.responseId,
        botResponse.response,
        botResponse.rating[0]["flesch_kincaid_grade_level/v1/score"],
        botResponse.rating[0]["ari_grade_level/v1/score"],
        botResponse.rating[0]["answer_similarity/v1/score"],
        botResponse.rating[0]["answer_correctness/v1/score"],
        botResponse.rating[0]["answer_relevance/v1/score"]
      );
      const responseData = response.data;
      const regenerateResponse = {
        messageId: responseData.messageId,
        text: combinedText,
        sender: "bot",
        createdAt: new Date().toISOString(),
        conversationId: currentConversationId,
        responseId: responseData.responseId,
        status: "active",
        version: responseData.version,
      };
      setMessages((prevMessages) => {
        return [...prevMessages, regenerateResponse];
      });
    } catch (error) {
      console.error("Error reloading response:", error);
    } finally {
      setIsLoading(false);
    }
  };
  const getTotalVersions = (message) => {
    if (message.sender === "user") {
      if (message.belongsTo !== null && message.belongsTo !== undefined) {
        const relatedMessages = messages.filter(
          (msg) => msg.belongsTo === message.belongsTo && msg.sender === "user"
        );
        return relatedMessages.length + 1;
      } else {
        const relatedMessages = messages.filter(
          (msg) => msg.belongsTo === message.messageId && msg.sender === "user"
        );
        return relatedMessages.length + 1;
      }
    } else if (message.sender === "bot") {
      if (message.version) {
        const relatedResponses = messages.filter(
          (msg) => msg.messageId === message.messageId && msg.sender === "bot"
        );
        return relatedResponses.length;
      }
    }
    return 1;
  };
  const handlePreviousResponseVersion = (currentResponse) => {
    const relatedResponses = messages.filter(
      (msg) =>
        msg.messageId === currentResponse.messageId && msg.sender === "bot"
    );
    const sortedVersions = [...relatedResponses].sort(
      (a, b) => a.version - b.version
    );
    const currentIndex = sortedVersions.findIndex(
      (res) => res.responseId === currentResponse.responseId
    );
    if (currentIndex > 0) {
      // Navigate to the previous version
      const previousVersion = sortedVersions[currentIndex - 1];
      // setActiveResponse(previousVersion);
      setMessages((prevMessages) =>
        prevMessages.map((res) =>
          res.responseId === currentResponse.responseId
            ? { ...res, status: "edited" }
            : res.responseId === previousVersion.responseId
            ? { ...res, status: "active" }
            : res
        )
      );
    }
  };
  const handleNextResponseVersion = (currentResponse) => {
    const relatedResponses = messages.filter(
      (msg) =>
        msg.messageId === currentResponse.messageId && msg.sender === "bot"
    );

    const sortedVersions = [...relatedResponses].sort(
      (a, b) => a.version - b.version
    );
    const currentIndex = sortedVersions.findIndex(
      (res) => res.responseId === currentResponse.responseId
    );

    if (currentIndex >= 0 && currentIndex < sortedVersions.length - 1) {
      const nextVersion = sortedVersions[currentIndex + 1];
      // setActiveResponse(nextVersion);
      setMessages((prevMessages) =>
        prevMessages.map((res) =>
          res.responseId === currentResponse.responseId
            ? { ...res, status: "edited" }
            : res.responseId === nextVersion.responseId
            ? { ...res, status: "active" }
            : res
        )
      );
    }
  };

  const renderResponseVersionNavigation = (response) => {
    const totalVersions = getTotalVersions(response);
    const currentVersion = response.version || 1;
    const versionDisplay =
      totalVersions > 1 ? `${currentVersion}/${totalVersions}` : null;
    if (!versionDisplay && totalVersions <= 1) return null;
    return (
      <div className="response-navigation-container">
        {/* <button
          className="response-navigation-button"
          onClick={() => handlePreviousResponseVersion(response)}
          disabled={response.version === 1}
        >
          {"<"}
        </button>
        <span>{versionDisplay}</span>
        <button
          className="response-navigation-button-right"
          onClick={() => handleNextResponseVersion(response)}
          disabled={response.version === totalVersions}
        >
          {">"} */}
        {/* </button> */}
      </div>
    );
  };

  const renderEditOptions = (message, index) => {
    return hoverText === index && message.sender === "user" ? (
      <div className="editpen-container">
        {/* <img
          // src={editIcon}
          alt="editpen"
          className="editpen"
          onClick={() => handleEditMessage(message)}
        /> */}
      </div>
    ) : null;
  };

  const renderVersionNavigation = (message, totalVersions) => {
    const currentVersion = message.version || 1;
    const versionDisplay =
      message.sender === "user" && totalVersions > 1
        ? `${currentVersion}/${totalVersions}`
        : null;
    if (!versionDisplay) return null;
    return (
      <div className="message-navigation-container">
        <button
          className="version-navigation-button"
          onClick={() => handlePreviousVersion(message)}
          disabled={message.version === 1}
        >
          {"<"}
        </button>
        <span>{versionDisplay}</span>
        <button
          className="version-navigation-button"
          onClick={() => handleNextVersion(message)}
          disabled={message.version === totalVersions}
        >
          {">"}
        </button>
      </div>
    );
  };
  const renderResponseIcons = (message, index) => {
    // const likeStatus = message.vote
    // const hasUserVoted = message.vote !== undefined;
    // const isUpvoted = hasUserVoted && message.vote === true;
    // const isDownvoted = hasUserVoted && message.vote === false;
    const isLiked = likedMessages[message.responseId]
    const isDisliked = dislikedMessages[message.responseId]
    // const isExpanded = expandedMessages[index];
    if (message.sender !== "bot" || message.initial) return null;
    const relatedResponses = messages.filter(
      (msg) =>
        (msg.sender === "bot" && msg.status === "active") ||
        msg.belongsTo === message.messageId
    );
    const latestResponse = relatedResponses[relatedResponses.length - 1];
    const latestResponseVersion = messages.filter(
      (msg) =>
        msg.messageId === latestResponse.messageId && msg.sender === "bot"
    );

    const sortedVersions = [...latestResponseVersion].sort(
      (a, b) => a.version - b.version
    );
    const hasMultipleVersions = sortedVersions[sortedVersions.length - 1];
    const isLatestResponse =
      latestResponse?.responseId === message.responseId &&
      hasMultipleVersions?.responseId === message.responseId;
    const showIcons = isLatestResponse || hoverText === index;
    return (
      <div
        className="response-icons"
        onMouseEnter={() => setHoverText(index)}
        onMouseLeave={() => setHoverText("")}
      >
        {message.sender === "bot" && renderResponseVersionNavigation(message)}
        <div
          className={`icon-group ${
            message.sender === "bot" && renderResponseVersionNavigation(message)
              ? "with-navigation"
              : ""
          }`}
        >
          {/* {showIcons && (
          <>
            <img
              src={isLiked ? Afterlike : likeIcon}
              alt="like"
              className="like-icon"
              onClick={() => handleVote(message.responseId, true)}
            />
            <img
              src={isDisliked ? afterDislikeIcon : dislikeIcon}
              alt="don't like"
              className="dislike-icon"
              onClick={() => handleVote(message.responseId, false)}
            />
            {isLatestResponse && (
              <img
                src={reloadIcon}
                alt="reload"
                className="reload-icon"
                onClick={() => handleReloadResponse(message)}
              />
            )}
          </>
        )} */}
        </div>
      </div>
    );
  };
  
//   const renderResponseIcons=(message,index)=>{
//     console.log("message in renderResponseIcons",message)
//     console.log("message_id in renderResponseIcons",message.message_id)
//     const likeStatus = message.vote
//     const hasUserVoted = message.vote !== undefined;
//     const isUpvoted = hasUserVoted && message.vote === true;
//     const isDownvoted = hasUserVoted && message.vote === false;
 
//     console.log("likeStatus in renderResponseIcons",likeStatus)
//     const isLiked = likedMessages[message.response_id] || isUpvoted;
//     const isDisliked = dislikedMessages[message.response_id] || isDownvoted;
//     // const isExpanded = expandedMessages[index];
//    if ( message.sender !== "bot" || message.initial) return null;
//     // const relatedResponses = messages.filter(
//     //   msg =>  (msg.sender === 'bot' && msg.status=== 'active') || msg.belongs_to_after_edit === message.message_id );
//     // console.log("relatedResponses in renderResponseIcons",relatedResponses)
//     // const latestResponse = relatedResponses[relatedResponses.length - 1];
//     // const latestResponseVersion =messages.filter(
//     //   msg=>(msg.message_id === latestResponse.message_id) && msg.sender ==='bot'
//     // )
 
//     // const sortedVersions = [...latestResponseVersion].sort((a, b) => a.version - b.version);
//     // const hasMultipleVersions =sortedVersions[sortedVersions.length - 1];
//     // const isLatestResponse = latestResponse?.response_id === message.response_id && hasMultipleVersions?.response_id=== message.response_id;
//     const showIcons =  hoverText === index;
//     return(
//       <div className="response-icons"
//       onMouseEnter={() => setHoverText(index)}
//       onMouseLeave={() => setHoverText("")}>
//          {message.sender === 'bot' && renderResponseVersionNavigation(message)}
//          <div className={`icon-group ${message.sender === 'bot' && renderResponseVersionNavigation(message) ? 'with-navigation' : ''}`}>
//          {showIcons && (
//           <>
//             <img
//               src={isLiked ? Afterlike : likeIcon}
//               alt="like"
//               className="like-icon"
//               onClick={() => handleVote(message.response_id, true)}
//             />
//             <img
//               src={isDisliked ? afterDislikeIcon : dislikeIcon}
//               alt="don't like"
//               className="dislike-icon"
//               onClick={() => handleVote(message.response_id, false)}
//             />
//             {/* {isLatestResponse && (
//               <img
//                 src={reloadIcon}
//                 alt="reload"
//                 className="reload-icon"
//                 onClick={() => handleReloadResponse(message)}
//               />
//             )} */}
//           </>
//         )}
//       </div>
//     </div>
//   );
// };
  
  
  const handleNextVersion = (currentMessage) => {
    let relatedMessages = [];
    if (currentMessage.belongsTo === null) {
      // For the original message, find all messages with belongsTo equal to currentMessage.messageId
      relatedMessages = messages.filter(
        (msg) =>
          (msg.belongsTo === currentMessage.messageId ||
            msg.messageId === currentMessage.messageId) &&
          msg.sender === "user"
      );
    } else {
      // For subsequent versions, find all messages related to the original message
      relatedMessages = messages.filter(
        (msg) =>
          (msg.belongsTo === currentMessage.belongsTo ||
            msg.messageId === currentMessage.belongsTo) &&
          msg.sender === "user"
      );
    }
    const sortedVersions = [...relatedMessages].sort(
      (a, b) => a.version - b.version
    );
    const currentIndex = sortedVersions.findIndex(
      (msg) => msg.messageId === currentMessage.messageId
    );
    if (currentIndex >= 0) {
      const nextVersion = sortedVersions[currentIndex + 1];
      const relatedResponse = messages.filter(
        (msg) => msg.messageId === nextVersion.messageId && msg.sender === "bot"
      );
      const latestResponse = relatedResponse[relatedResponse.length - 1];
      // const nonLatestResponses = relatedResponse.filter(msg => msg.responseId !== latestResponse.responseId);
      setActiveMessage(nextVersion);
      setMessages((prevMessages) =>
        prevMessages.map((msg) => {
          return msg.messageId === currentMessage.messageId
            ? { ...msg, status: "edited" }
            : msg.messageId === nextVersion.messageId &&
              msg.responseId === latestResponse.responseId
            ? { ...msg, status: "active" }
            : msg.messageId === nextVersion.messageId && msg.sender === "user"
            ? { ...msg, status: "active" }
            : msg;
        })
      );
    }
  };
  const handlePreviousVersion = (currentMessage) => {
    const relatedMessages = messages.filter(
      (msg) =>
        (msg.belongsTo === currentMessage.belongsTo ||
          msg.messageId === currentMessage.belongsTo) &&
        msg.sender === "user"
    );
    const sortedVersions = [...relatedMessages].sort(
      (a, b) => a.version - b.version
    );
    const currentIndex = [...sortedVersions].findIndex(
      (msg) => msg.messageId === currentMessage.messageId
    );
    if (currentIndex > 0) {
      const previousVersion = sortedVersions[currentIndex - 1];
      const relatedResponse = messages.filter(
        (msg) =>
          msg.messageId === previousVersion.messageId && msg.sender === "bot"
      );
      // const latestResponse = [...relatedResponse].sort((a, b) => a.version - b.version)[0];
      const latestResponse = relatedResponse[relatedResponse.length - 1];
      setActiveMessage(previousVersion);
      setMessages((prevMessages) =>
        prevMessages.map((msg) => {
          return msg.messageId === currentMessage.messageId
            ? { ...msg, status: "edited" }
            : // : msg.responseId === latestResponse.responseId
            // ? { ...msg, status: 'active' }
            // : msg.messageId === previousVersion.messageId
            //   ? { ...msg, status: 'active' }
            //   : msg
            msg.messageId === previousVersion.messageId &&
              msg.responseId === latestResponse.responseId
            ? { ...msg, status: "active" }
            : msg.messageId === previousVersion.messageId &&
              msg.sender === "user"
            ? { ...msg, status: "active" }
            : msg;
        })
      );
    }
  };
  const renderMessageText = (message, isExpanded, index) => {
    if (message.isLoading) {
      return (
        <div className="message-text-wrapper typing">
          <BouncingDotsLoader /> {/* Display the loader */}
        </div>
      );
    }
    const words = message.text.split(" ");
    const isLongMessage = words.length > 71;
    const displayText =
      isExpanded || isMaximized || !isLongMessage
        ? message.text
        : message.text.split(" ").slice(0, 71).join(" ") + "...";
    const readMoreLabel = isExpanded || isMaximized ? " " : "Read More";
    const formattedText = displayText
      .replace(
        /(Response from private|Response from OpenAI)/g,
        "<br><br><strong>$1</strong>"
      )
      .replace(/(Ratings)/g, "<br><strong>$1</strong>");
    // const showRadioButtons=message.initial
    return (
      <div className="message-text-wrapper" autoFocus>
        <span className="message-text">
          <ReactMarkdown rehypePlugins={[rehypeRaw]}>
            {formattedText}
          </ReactMarkdown>
        </span>
        {isLongMessage && (
          <span className="read-more" onClick={() => toggleReadMore(index)}>
            {readMoreLabel}
          </span>
        )}
      </div>
    );
  };
  const handleButtonClick = async (buttonText, agent) => {
    // Add user's message to the messages array
    setMessages([...messages, { sender: "user", text: buttonText }]);
    setIsSecondMessageDisplayed(false);
    setSelectedAgent(agent);

    try {
      let conversationId = currentConversationId; // Check if conversationId already exists

      // If no conversationId exists, create a new conversation
      if (!conversationId || newChatInitiate === 1) {
        conversationId = await createConversation(userId, workspaceId);
        setCurrentConversationId(conversationId); // Save conversationId in state
        setTypingConversationId(conversationId); // Track typing if necessary
        setNewChatInitiate(0); // Reset new chat flag
        setIsNewChatDisabled(false); // Enable new chat if previously disabled
        setDisplayedConversationName("New chat"); // Set displayed conversation name
      }

      console.log("conversationId is:", conversationId);

      // Create the user's message
      const messageId = await createMessage(buttonText, conversationId, userId);
      console.log("Message created with ID:", messageId);

      // Send the button click data to the server along with conversation ID
      socket.emit("buttonclick", {
        input: buttonText,
        agent: agent,
        conversationId: conversationId,
      });

      // Listen for the bot's response from the server
      socket.on("agentresponse", async (data) => {
        console.log("Bot response received:", data);

        // Sanitize the bot's response for safe HTML rendering
        const sanitizedMessage = sanitizeHtml(data.message);
        // Create the response in the backend
        const createResponseResult = await createResponse(
          messageId,
          sanitizedMessage,
          conversationId
        );
        if (!createResponseResult) {
          throw new Error("Failed to create response");
        }
      });
    } catch (error) {
      console.error("Error in handleButtonClick:", error);
    }
  };

  const renderMessage = (message, index) => {
    const isActiveMessage = activeMessage?.messageId === message.messageId;
    if (message.status !== "active" && !isActiveMessage) {
      return null;
    }
    if (message.sender === "bot") {
      const activeResponses = message.status === "edited";
      if (activeResponses) {
        return null;
      }
    }
    const isExpanded = expandedMessages[index];
    const totalVersions = getTotalVersions(message);
    return (
      <div
        key={index}
        className="message-box"
        onMouseEnter={() => setHoverText(index)}
        onMouseLeave={() => setHoverText("")}
      >
        <div className="message-container">
          <div className={`message ${message.sender}`}>
            {renderEditOptions(message, index)}
            {message.sender === "bot" && (
              <img src={botAvatar} alt="bot avatar" className="bot-avatar" />
            )}
            {message.sender === "user" && (
              <img src={UserAvatar} alt="user avatar" className="user-avatar" />
            )}
            <div className="message-content">
              {editMessageId === message.messageId &&
              message.sender === "user" ? (
                <>
                  <textarea
                    ref={textareaRef}
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    className="edit-textarea"
                    autoFocus
                  />
                  <div className="edit-buttons">
                    <button onClick={handleCancelEdit} className="cancel">
                      Cancel
                    </button>
                    <button onClick={handleSaveEditMessage}>Send</button>
                  </div>
                </>
              ) : (
                renderMessageText(message, isExpanded, index)
              )}
              {/* {renderVersionNavigation(message,totalVersions)} */}
            </div>
            <div className="icon">{renderResponseIcons(message, index)}</div>
          </div>
        </div>
       
        {index === 1 && isSecondMessageDisplayed && clickedId === null && (
          <div className="button-container">
            <button
              className="chat-button full-width"
              onClick={() => handleButtonClick("Show me today's menu", "menu")}
            >
              Show me today's menu
            </button>
            <div className="button-row">
              <button
                className="chat-button half-width"
                onClick={() =>
                  handleButtonClick("Search for a recipe", "recipe")
                }
              >
                Search for a recipe
              </button>
              <button
                className="chat-button half-width"
                onClick={() =>
                  handleButtonClick(
                    "Ideas for ingredient substitute",
                    "ingredient"
                  )
                }
              >
                Ideas for ingredient substitute
              </button>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div>
      <div
        className="message-icon"
        data-testid="message-icon"
        onMouseEnter={() => handleMouseEnter("Gen Ai Assistant")}
        onMouseLeave={handleMouseLeave}
        onClick={toOpenChatbot}
      >
        <img src={botAvatar} alt="Bot Avatar" />
        {hoverText && <div className="hover-text">{hoverText}</div>}
      </div>
      {isOpen && !isMinimized && (
        <div className={`popup-container${isMaximized ? " maximized" : ""}`}>
          <div className="popup">
            <div className="header" onMouseDown={handleDrag}>
              <span className="hamburger">
              <img src={hamburgericon} alt="hamburger1"className="hamburger1" onClick={handleChatHistoryClick} />
              </span>
              <span className="title">Gen AI Assistant</span>
              <div className="header-buttons">
                <button className="toggle-button" onClick={toggleMinimize}>
                  <img
                    className="minimize-btn"
                    src={minimize}
                    alt="minimize icon"
                  />
                </button>
                <button className="toggle-maximize" onClick={toggleMaximize}>
                  <img
                    className="maximise-btn"
                    src={isMaximized ? restoreIcon : maximizeIcon}
                    alt="maximize icon"
                  />
                </button>
                <button className="toggle-button" onClick={toggleChatbot}>
                  <img className="close-btn" src={closeIcon} alt="closeIcon" />
                </button>
              </div>
            </div>

            {!isSidebarOpen && <div className="subheader"></div>}
            <div className={getChatContentClass()}>
              {!isSidebarOpen && (
                <p className="chat-history" onClick={handleChatHistoryClick}>
                  Chat History
                </p>
              )}

              {isSidebarOpen ? (
                <ChatHistory
                  isSidebarOpen={isSidebarOpen}
                  setIsSidebarOpen={setIsSidebarOpen}
                  isMaximized={isMaximized}
                  userId={userId}
                  getChatHistory={handleGetChatHistory}
                  setCurrentConversationId={setCurrentConversationId}
                  isNewChatDisabled={isNewChatDisabled}
                  setIsNewChatDisabled={setIsNewChatDisabled}
                  setNewChatInitiate={setNewChatInitiate}
                  setMessages={setMessages}
                  setEditMessageId={setEditMessageId}
                  chatHistory={chatHistory}
                  setChatHistory={setChatHistory}
                  displayedConversationName={displayedConversationName} // Pass the displayed conversation name
                  typingConversationId={typingConversationId}
                  clickedId={clickedId} // Pass clickedId to ChatHistory
                  setClickedId={setClickedId}
                  setIsSecondMessageDisplayed={setIsSecondMessageDisplayed}
                  setactiveConversationId = {setactiveConversationId}
                  activeConversationId ={activeConversationId}
                  
                  
                />
              ) : null}
              {(!isSidebarOpen || messages.length > 0) && (
                <>
                  <div
                    className={`current-time ${
                      isSidebarOpen ? "with-sidebar" : ""
                    }`}
                  >
                    {currentTime}
                  </div>
                  <div
                    className={`message-list ${
                      isSidebarOpen ? "with-sidebar" : ""
                    }`}
                    ref={messageListRef}
                  >
                    {messages.map((message, index) =>
                      renderMessage(message, index)
                    )}
                  </div>
                </>
              )}
              {isSidebarOpen && messages.length === 0 && (
                <div className="assistant-heading">Gen Ai Assistant</div>
              )}
              {isLoading && <Loader />}
            </div>
            <div
              className={`message-input ${isSidebarOpen ? "with-sidebar" : ""}`}
            >
              <textarea
                type="text"
                placeholder="Type here ..."
                value={inputValue}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                // disabled={isLoading}
                disabled={isDotLoading}
              />
              <img
                src={
                  inputValue.trim() === "" ? sendDisabledIcon : sendEnabledIcon
                }
                alt="Send"
                className={`send-icon ${
                  inputValue.trim() === "" ? "disabled" : ""
                }`}
                onClick={handleMessageSubmit}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Chatbot;
