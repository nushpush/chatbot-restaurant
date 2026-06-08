// test/mockSocket.js
const EventEmitter = require('events');

class MockSocket extends EventEmitter {
  emit(event, data) {
    this.emit(event, data); // Simulate emitting event
  }
}

module.exports = MockSocket;
