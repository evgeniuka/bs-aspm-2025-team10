from flask_socketio import emit

def emit_session_update(socketio, session_id, client_id, updated_data):
    room = f"session_{session_id}"
    socketio.emit('session_update', {
        'session_id': session_id,
        'client_id': client_id,
        'updated_data': updated_data
    }, to=room)