import io from 'socket.io-client';

let socket = null;

export const socketService = {
  connect: () => {
    if (!socket) {
      socket = io('http://localhost:5000', {
        transports: ['websocket'],
        autoConnect: true
      });
      
      socket.on('connect', () => {
        console.log('✅ WebSocket connected:', socket.id);
      });
      
      socket.on('disconnect', () => {
        console.log('❌ WebSocket disconnected');
      });
    }
    return socket;
  },

  joinSession: (sessionId) => {
    if (socket) {
      socket.emit('join_session', { session_id: sessionId });
      console.log(`📍 Joined session room: session_${sessionId}`);
    }
  },

  leaveSession: (sessionId) => {
    if (socket) {
      socket.emit('leave_session', { session_id: sessionId });
      console.log(`📤 Left session room: session_${sessionId}`);
    }
  },

  onSessionUpdate: (callback) => {
    if (socket) {
      socket.on('session_update', callback);
    }
  },

  offSessionUpdate: () => {
    if (socket) {
      socket.off('session_update');
    }
  },

  disconnect: () => {
    if (socket) {
      socket.disconnect();
      socket = null;
    }
  }
};
