// import { io } from 'socket.io-client';

// const SOCKET_URL = 'http://localhost:5000';  // Update this URL to your Flask server's address

// const socket = io(SOCKET_URL, {
//   transports: ['websocket'],
// });
// socket.on('connect', () => {
//   console.log('Socket connected:', socket.id);
// });
// export const sendMessage = (message) => {
//   socket.emit('message', { input: message });
// };

// export const onMessage = (callback) => {
//   console.log("callback function:", callback);
//   socket.on('response', (data) => {
//     console.log("Received data from server:", data);
//     if (data.message) {
//       callback(data.message);
//     } else {
//       console.warn("No 'message' field in received data:", data);
//     }
//   });
// };
