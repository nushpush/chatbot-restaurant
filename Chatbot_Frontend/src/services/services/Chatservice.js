
import { environment } from "../environment/environment"
import { io } from 'socket.io-client';
const socket = io(`${environment.baseUrl}`);
const createConversationId =async(userId,workspaceId)=>{
    try{
        const response = await fetch (`${environment.baseUrl}/createConversation`,{
            method:'POST',
            headers: {
              'Content-Type':'application/json'
            },
            body: JSON.stringify({
                user_id:userId,
                workspace_id:workspaceId
            }),
            });
           
            const data = await response.json();
            console.log("response",data)
            if (!response.ok) {
              throw new Error('Failed to create a new conversation ID.');
            }
            return data.result;
          } catch (error) {
            console.error('Error creating conversation:', error);
            throw error;
          }
}

// const getBotResponse = async (userMessage ,selectedWorkspace)=>{
//     const formData = new FormData();
//     formData.append('content', userMessage);
//     formData.append('model','genailllmpocmodel');
//     formData.append('workspace', selectedWorkspace);
//     try{
//       const chatResponse = await fetch(`${environment.baseUrl}/chat`,{
//         method: 'POST',
//         body: formData,
//       });
//       if(!chatResponse.ok){
//         throw new Error('Network response was not ok');
//       }
//       console.log("chatResponse",chatResponse)
//       return await chatResponse.json()
//     }
//     catch(error){
//        console.log('Error getting bot response:',error);
//        throw error;
//     }
// }
const getBotResponse = async (userMessage)=>{
  const formData = new FormData();
  formData.append('content', userMessage);
 
  try{
    const chatResponse = await fetch(`${environment.baseUrl}/chat`,{
      method: 'POST',
      body: formData,
    });
    if(!chatResponse.ok){
      throw new Error('Network response was not ok');
    }
    console.log("chatResponse",chatResponse)
    return await chatResponse.json()
  }
  catch(error){
     console.log('Error getting bot response:',error);
     throw error;
  }
}

 const createMessage = async(conversationId,message,userId)=>{
  try{
    console.log("inservicfile",conversationId,message,userId)
     const addMessage = await fetch(`${environment.baseUrl}/createMessage`,{
        method: 'POST',
        headers: {
            'Content-Type':'application/json',
        },
        body: JSON.stringify({
            conversationId:conversationId,
            message:message,
            userId:userId
        }),
     });
     if(!addMessage.ok){
        throw new Error('Failed to createmessage');
     }
     return await addMessage.json();
  }
  catch(error){
     console.log("Error creating message",error);
     throw error;
  }
}


// const createResponse = async (messageId, response, conversationId, ratings) => {
//   try {
//       const saveResponse = await fetch(`${environment.baseUrl}/createResponse`, {
//           method: 'POST',
//           headers: {
//               'Content-Type': 'application/json'
//           },
//           body: JSON.stringify({
//               messageId: messageId,
//               response: response,
//               conversationId: conversationId,
//               flesch_kincaid_grade_level: ratings["flesch_kincaid_grade_level/v1/score"],
//               ari_grade_level: ratings["ari_grade_level/v1/score"],
//               answer_similarity: ratings["answer_similarity/v1/score"],
//               answer_correctness: ratings["answer_correctness/v1/score"],
//               answer_relevance: ratings["answer_relevance/v1/score"],
//               doc_ref: ['sample_doc_ref'],
//               input_token: null,
//               output_token: null,
//           }),
//       });

//       if (!saveResponse.ok) {
//           throw new Error('Failed to create the response');
//       }

//       return await saveResponse.json();
//   } catch (error) {
//       throw error;
//   }
// };







const createResponse = async (messageId,response,conversationId,flesch_kincaid_grade_level,ari_grade_level,answer_similarity,answer_correctness,answer_relevance)=>{
    try{
        const saveResponse = await fetch(`${environment.baseUrl}/createResponse`,{
            method: 'POST',
            headers:{
                'Content-Type':'application/json'
            },
            body: JSON.stringify({
                messageId:messageId,
                response:response,
                conversationId:conversationId,
                flesch_kincaid_grade_level:flesch_kincaid_grade_level,
                ari_grade_level:ari_grade_level,
                answer_similarity:answer_similarity,
                answer_correctness:answer_correctness,
                 answer_relevance:answer_relevance,
            }),
        });
        if(!saveResponse.ok){
            throw new Error('Failed to create the response')
        }
        
        return await saveResponse.json();
    }
    catch(error){
         throw error;
    }
};



// const getChatHistory =async (conversationId)=>{
//     try{
//     //   setIsLoading(true)
//       const response = await fetch(`${environment.baseUrl}/getChatHistory/${conversationId}`, {
//         method: 'GET',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//       });
//       const result = await response.json();
//       console.log("dataingetchathistory", result);
//     //   setIsLoading(false);
//       if (result.success) {
//         // return result.data.Messages.flatMap(message => [
//         //   { text: message.content, sender: 'user',
//         //     messageId: message.messageId, 
//         //    version: message.version, 
//         //    belongsTo: message.belongsToAfterEdit,
//         //    createdAt: message.createdAt,
//         //    status:message.status
//         //   },
//         //   message.Response ? { 
//         //     text: message.Response.response, 
//         //     sender: 'bot', 
//         //     doc_ref: message.Response.doc_ref, 
//         //     messageId: message.Response.messageId,
//         //     responseId:message.Response.responseId ,
//         //     status:message.status,
//         //     version: message.Response.version
//         //   } : []
//         // ]);
//         const messages = result.data.Messages.flatMap(message => {
//           // User message
//           const userMessage = {
//             text: message.content,
//             sender: 'user',
//             messageId: message.messageId,
//             version: message.version,
//             belongsTo: message.belongsToAfterEdit,
//             createdAt: message.createdAt,
//             status: message.status
//           };
  
//           // Bot responses
//           const botResponses = message.Responses.map(response => {
//           //   const ratingText = response.flesch_kincaid_grade_level || response.ari_grade_level || response.answer_similarity || response.answer_correctness || response.answer_relevance
//           //   ? `Ratings - Flesch Kincaid Grade Level: ${response.flesch_kincaid_grade_level ?? 'N/A'}, 
//           //   ARI Grade Level: ${response.ari_grade_level ?? 'N/A'}, 
//           //   Answer Similarity: ${response.answer_similarity ?? 'N/A'}, 
//           //   Answer Correctness: ${response.answer_correctness ?? 'N/A'}, 
//           //   Answer Relevance: ${response.answer_relevance ?? 'N/A'}`
//           //   : ''
//           // // Combine response text with rating text
//           // const combinedText = `${response.response} ${ratingText}`
//           const ratingItems = [
//             `Flesch Kincaid Grade Level: ${response.flesch_kincaid_grade_level ?? 'N/A'}`,
//             `ARI Grade Level: ${response.ari_grade_level ?? 'N/A'}`,
//             `Answer Similarity: ${response.answer_similarity ?? 'N/A'}`,
//             `Answer Correctness: ${response.answer_correctness ?? 'N/A'}`,
//             `Answer Relevance: ${response.answer_relevance ?? 'N/A'}`
//           ].filter(item => !item.includes('N/A')) 
//             .map(item => `<li>${item}</li>`)
//             .join('');
          
//           // Construct the rating text with a heading
//           const ratingText = ratingItems.length > 0
//             ? `<strong>Ratings:</strong><ul>${ratingItems}</ul>`
//             : '';
        
//           // Combine the response text with the formatted rating text
//           const combinedText = `${response.response} ${ratingText}`
//           return{
//             text: combinedText,
//             sender: 'bot',
//             doc_ref: response.doc_ref,
//             messageId: response.messageId,
//             responseId: response.responseId,
//             status: response.status,
//             version: response.version
//         }});
//         console.log("botresponseinservice",botResponses)
//           return [userMessage, ...botResponses];
//         });
//        console.log("messageisservice",messages)
//         return messages;
//         // setMessages(messages);
//       } else {
//         console.error('Failed to fetch chat history:', result.message);
//        throw new Error(result.message)
//       }
//     }
//     catch(error){
//       console.log("errorinchathistory",error)
//       throw error;
//     }
//   }


const getChatHistory = async (conversationId) => {
  try {
      // Fetch chat history via WebSocket
      socket.emit('get_chat_history', { conversationId });

      // Listen for chat history response
      return new Promise((resolve, reject) => {
          socket.on('chat_history_response', (result) => {
              console.log("Data in getChatHistory:", result);

              if (result.success) {
                  // Process messages and responses
                  const messages = result.data.Messages.flatMap(message => {
                      // User message
                      const userMessage = {
                          text: message.content,
                          sender: 'user',
                          message_id: message.message_id,
                          created_at: message.created_at,
                          belongs_to_after_edit : message.belongs_to_after_edit,
                          // responses: message.responses.map(response => ({
                          //     text: response.response,
                          //     sender: 'bot',
                          //     responseId: response.response_id,
                          //     createdAt: response.created_at,
                          // }))
                      };

                      // Bot responses
                      const botResponses = message.Responses.map(response => {
                          return {
                              text: response.response,
                              sender: 'bot',
                              doc_ref: response.doc_ref,
                              message_id: response.message_id,
                              response_id: response.response_id,
                              created_at: response.created_at,
                              vote : response.vote
                          };
                      });

                      return [userMessage, ...botResponses];
                  });

                  console.log("Processed messages:", messages);
                  resolve(messages);
              } else {
                  console.error('Failed to fetch chat history:', result.message);
                  reject(new Error(result.message));
              }
          });
      });
  } catch (error) {
      console.error("Error in getChatHistory:", error);
      throw error;
  }
};


 
  

const getAllConversationName = async( userId)=>{
    try{
         const response = await fetch(`${environment.baseUrl}/getAllChat/${userId}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        console.log('userId',userId)
        const conversationDetails = await response.json()
        console.log('datahistory',conversationDetails)
       if(conversationDetails.success){
        return conversationDetails.data;
       }else{
        console.error('Failed to fetch all the chat names :',conversationDetails.message)
        throw new Error(conversationDetails.message)
       }
    }
    catch(error){
      console.log("errorinchathistory",error)
      throw error;
    }
  }
const editMessage = async (messageId, newMessage, userId) => {
    try {
      const response = await fetch(`${environment.baseUrl}/editMessage`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messageId,
          newMessage,
          userId,
        }),
      });
      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Error editing message:', error);
      throw error;
    }
  };

 const fetchConversationName = async (conversationId) => {
    try {
      console.log("conversationIDinfetchConversationName",conversationId)
      const response = await fetch(`${environment.baseUrl}/getChatNameForCurrentId/${conversationId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      console.log("response",response)
      const conversationName = await response.json()
      console.log("conversationName",conversationName)
      return conversationName.data; // Adjust according to the API response structure
    } catch (error) {
      console.error('Error fetching conversation name:', error);
      return null;
    }
  };

  const DeleteConversation = async (conversationId) => {
    try {
      const response = await fetch(`${environment.baseUrl}/softDeleteConversation/${conversationId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Error deleting conversation:', error);
      throw error;
    }
  };

  const addVote = async (responseId, vote) => {
    try {
      // const response = await fetch(`${environment.baseUrl}/addVote`, {
      //   method: 'PUT',
      //   headers: {
      //     'Content-Type': 'application/json',
      //   },
      //   body: JSON.stringify({
      //     responseId,
      //     vote
 
      //   }),
      // });
      // return response.data;
      socket.emit('vote_response', { responseId, vote });
      socket.on('vote_updated', (response) => {
        return response;
      });
    } catch (error) {
      console.error("Failed to add vote", error);
      throw error;
    }
  };

  
  const regenerateResponse = async (responseId, newResponse,flesch_kincaid_grade_level,ari_grade_level,answer_similarity,answer_correctness,answer_relevance) => {
    try {
      const regenerate_response = await fetch(`${environment.baseUrl}/regenerateResponse`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          responseId,
          newResponse,
          doc_ref:['sample_doc_ref'],
          input_token:null,
          output_token:null,
          flesch_kincaid_grade_level:flesch_kincaid_grade_level,
          ari_grade_level:ari_grade_level,
          answer_similarity:answer_similarity,
          answer_correctness:answer_correctness,
          answer_relevance:answer_relevance,   
        }),
      });
      const result = await regenerate_response.json();
      console.log("regenerate_response",result)
      return result;
    } catch (error) {
      console.error('Error editing message:', error);
      throw error;
    }
  };

 



const formatDate = (createdAt) => {
  const date = new Date(createdAt);
  const dd = String(date.getDate()).padStart(2, '0');
  const mm = String(date.getMonth() + 1).padStart(2, '0');
  const yyyy = date.getFullYear();
  return `${dd}.${mm}.${yyyy}`;
};
 const fetchAndSetChatNames = async (userId, setChatHistory) => {
  try {
    console.log("fetchAndSetChatNames")
    console.log("useridinfetchandSetnames",userId)
    socket.emit('get_all_chats', { userId });

    socket.on('get_all_chats_response', (response) => {
      console.log("get_all_chats_response",response)
      if (response.success) {
        const chatName = response.data;
        console.log("chatnames", chatName);
        const groupedData = chatName.reduce((acc, conversation) => {
          const date = formatDate(conversation.updatedAt); // Format date function
          if (!acc[date]) {
            acc[date] = [];
          }
          acc[date].push(conversation);
          return acc;
        }, {});
        console.log("groupedData",groupedData)
        setChatHistory(groupedData);
      } else {
        console.error("Error fetching chat names", response.error);
      }
    });
  } catch (error) {
    console.error("Socket error fetching chat names", error);
  }
};

export const chatService = {
    createConversationId,
    getBotResponse,
    createMessage,
    createResponse,
    getChatHistory,
    getAllConversationName,
    editMessage,
    fetchConversationName,
    DeleteConversation,
    addVote,
    regenerateResponse,
    fetchAndSetChatNames     
  };