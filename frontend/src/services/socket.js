import io from 'socket.io-client';

let socket = null;

export const socketService = {
  connect: () => {
    
    if (socket?.connected) {
      console.log('🔄 Reusing existing WebSocket connection');
      return socket;
    }


    if (socket && !socket.connected) {
      console.log('🔌 Reconnecting existing socket');
      socket.connect();
      return socket;
    }


    if (!socket) {
      console.log('🆕 Creating new WebSocket connection');
      socket = io('http://localhost:5000', {
        transports: ['websocket'],
        autoConnect: true,
        reconnection: true,  
        reconnectionAttempts: 5,
        reconnectionDelay: 1000,
      });

      socket.on('connect', () => {
        console.log('✅ WebSocket connected:', socket.id);
      });

      socket.on('disconnect', (reason) => {
        console.log('❌ WebSocket disconnected:', reason);
      });

      socket.on('connect_error', (error) => {
        console.error('🔴 WebSocket connection error:', error.message);
      });
    }

    return socket;
  },

  joinSession: (sessionId) => {
    if (!socket) {
      console.warn('⚠️ Socket not initialized, cannot join session');
      return;
    }

    const join = () => {
      socket.emit('join_session', { session_id: sessionId });
      console.log(`📍 Joining: session_${sessionId}`);
    };


    if (socket.connected) {
      join();
    } else {
      socket.once('connect', join);
    }
  },

  leaveSession: (sessionId) => {
    if (socket?.connected) {
      socket.emit('leave_session', { session_id: sessionId });
      console.log(`📤 Left session room: session_${sessionId}`);
    }
  },

  onSessionUpdate: (callback) => {
    if (socket) {
      console.log('👂 Listening for session_update events');
      socket.on('session_update', callback);
    }
  },

  offSessionUpdate: () => {
    if (socket) {
      console.log('🔇 Stopped listening for session_update');
      socket.off('session_update');
    }
  },

  onSessionEnded: (callback) => {  
    if (socket) {
      console.log('👂 Listening for session_ended events');
      socket.on('session_ended', callback);
    }
  },

  offSessionEnded: () => {  
    if (socket) {
      console.log('🔇 Stopped listening for session_ended');
      socket.off('session_ended');
    }
  },

  disconnect: () => {
    if (socket) {
      console.log('🔌 Disconnecting WebSocket');
      socket.removeAllListeners();
      socket.disconnect();
      socket = null;
    }
  },

  off: (event) => {
    if (socket) {
      console.log(`🔇 Removing listener: ${event}`);
      socket.off(event);
    }
  },

 emit: (event, data) => {
    if (socket && socket.connected) {
      console.log(`📤 Emitting: ${event}`, data);
      socket.emit(event, data);
    } else {
      console.warn('⚠️ Socket not connected');
    }
  },

  on: (event, callback) => {
    if (socket) {
      console.log(`👂 Listening for: ${event}`);
      socket.on(event, callback);
    }
  },



  getSocket: () => socket

};
