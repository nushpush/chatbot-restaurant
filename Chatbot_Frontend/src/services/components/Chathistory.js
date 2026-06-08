
import React, {useState,  useEffect } from 'react';
import './Chathistory.css';
import Arrowback from '../assets/images/Arrow back 1.png';
import NewChat from '../assets/images/edit.png';
import {chatService} from '../services/Chatservice'
// import {fetchAndSetChatNames} from '../utilities/chatServiceUtilities'
import ThreedotIcon from '../assets/images/moreIcon.png'
import ConversationDelete from './Chatdelete.js';
import DeleteIcon from '../assets/images/delete.png';

function Chathistory  ({ 
  isSidebarOpen, 
  setIsSidebarOpen,
  userId,
  getChatHistory,
  setCurrentConversationId,
  isNewChatDisabled,
  setIsNewChatDisabled,
  setNewChatInitiate,
  setMessages,
  setEditMessageId,
  chatHistory, 
  setChatHistory, 
  displayedConversationName,
  typingConversationId,
  clickedId,
  setClickedId,
  setIsSecondMessageDisplayed,
  setactiveConversationId,
  activeConversationId
})  {
  // const[chatHistory,setChatHistory]=useState([])
  // const[clickedId,setClickedId]=useState(null);
  const [hoveredConversationId, setHoveredConversationId] = useState(null);
  const [showDeleteOptionId, setShowDeleteOptionId] = useState(null)
  const [showModal, setShowModal] = useState(false);
  const [currentConversation, setCurrentConversation] = useState(null);
  
  const [currentConversationName, setCurrentConversationName] = useState('');
  useEffect(() => {
    const fetchData = async () => {
      await chatService.fetchAndSetChatNames(userId, setChatHistory);
    };
    fetchData();
  }, [userId, setChatHistory]);
  
  useEffect(() => {
    if ( currentConversation) {
      const fetchConversationName = async () => {
        try {
          const name = await chatService.fetchConversationName(currentConversation);
          setCurrentConversationName(name);
        } catch (error) {
          console.error('Failed to fetch conversation name:', error);
        }
      };
      
      fetchConversationName();
    }
  }, [currentConversation]);
  
  const handleNewChatClick = async () => {
    if (!isNewChatDisabled) {
      setNewChatInitiate(1);
      setIsNewChatDisabled(true);
      setCurrentConversationId(null);
      setMessages([]);
      setIsSidebarOpen(false)
      setClickedId(null);
      setEditMessageId(null)
      setShowDeleteOptionId(null);
    }
  };
  const handlebackNewChat = async () => {
    if(activeConversationId){
    const message = await chatService.getChatHistory(activeConversationId);
    console.log("message", message);
    setMessages(message);
    setClickedId(activeConversationId);
    }
    else{
      setNewChatInitiate(1);
      setIsNewChatDisabled(true);
      setCurrentConversationId(null);
      setMessages([]);
      setIsSidebarOpen(false)
      setClickedId(null);
      setEditMessageId(null)
      setShowDeleteOptionId(null);
      setIsSecondMessageDisplayed(false)
    }
  };

  
  const handleHistory = async (conversationId) => {
    setIsSidebarOpen(true);
    await getChatHistory(conversationId); // Call getChatHistory function with conversationId
    setCurrentConversationId(conversationId);
    setNewChatInitiate(0);
    setIsNewChatDisabled(false);
    setClickedId(conversationId);
    setEditMessageId(null); 
    setShowDeleteOptionId(null);
    const name = await chatService.fetchConversationName(conversationId);
    setCurrentConversation(name);
  };
  const handleThreeDotClick = (conversationId, e) => {
    e.stopPropagation();
    setShowDeleteOptionId(prevId => (prevId === conversationId ? null : conversationId));
  };
  const handleDeleteConversation = (conversationId) => {
    setShowModal(true);
    setCurrentConversation(conversationId);
    setShowDeleteOptionId(null);
    setClickedId(null);
  };
  const handleConfirmDelete = async () => {
    if (currentConversation) {
      try {
        const response = await chatService.DeleteConversation(currentConversation);
        if(response.success===true){
          chatService.fetchAndSetChatNames(userId, setChatHistory);
          setMessages([]);
        }
      } catch (error) {
        console.error('Failed to delete conversation:', error);
      } finally {
        setShowModal(false); // Close the modal after deletion
        setCurrentConversation(null); // Reset the current conversation
      }
    }
  };
  // const getConversationName = async(conversationId) => {
  //   for (const date of Object.keys(chatHistory)) {
  //     const conversation = chatHistory[date].find(c => c.conversationId === conversationId);
  //     if (conversation) {
  //       return conversation.conversationName;
  //     }
  //   }
  //   return '';
  // };
  return (
    <div className={`sidebar ${isSidebarOpen ? 'open' : ''}`}>
      <div className="sidebar-header">
      <img src={Arrowback} alt="right-arrow" className="right-arrow" onClick={handlebackNewChat}/>
      <img src={NewChat} alt="new chat" className={` new-chat ${isNewChatDisabled ? 'disabled' : ''}`} onClick={handleNewChatClick} />
        <span className="sidebar-title">Chat History</span>
        <div>
        </div>
      </div>
      <div className="sidebar-content">
     
    {Object.keys(chatHistory).map((date, index) => (
          <div key={index} className='date-group'>
            <div className='date'>{date}</div>
            {chatHistory[date].map((conversation, subIndex) => (
              <div key={subIndex} className={`history-content ${clickedId === conversation.conversationId ? 'clicked': ''}`} onClick={() => handleHistory(conversation.conversationId)}
              onMouseEnter={() => {
                setHoveredConversationId(conversation.conversationId);
              }}
              onMouseLeave={() => {
                setHoveredConversationId(null);
              }}
              >
               <span className='conversation-name'>
                 {typingConversationId === conversation.conversationId
                ? displayedConversationName
                : conversation.conversationName}
                </span>
                {(hoveredConversationId === conversation.conversationId || clickedId === conversation.conversationId) && (
                <div className='three-dot-container'>
                  <img 
                    src={ThreedotIcon} 
                    alt='options' 
                    className='three-dot-icon'
                    onClick={(e) => handleThreeDotClick(conversation.conversationId, e)}
                  />
                  {showDeleteOptionId === conversation.conversationId && (
                    <div className='delete-option' onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteConversation(conversation.conversationId);
                    }}>
                      <img src={DeleteIcon} alt='deleteIcon' className='delete-icon'/>&nbsp;<span className='delete-text'>
                      Delete
                      </span>
                     
                    </div>
                  )}
                </div>
              )}
              </div>
            ))}
          </div>
        ))}
      
       <ConversationDelete
        show={showModal}
        onClose={() => setShowModal(false)}
        onConfirm={handleConfirmDelete}
      conversationName = {currentConversationName}
      />
      </div>
    </div>
  );
};

export default Chathistory;
