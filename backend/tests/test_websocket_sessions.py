from app import create_app


def test_websocket_join_session():
    app, socketio = create_app()
    app.config.update({"TESTING": True})

    client = socketio.test_client(app)
    assert client.is_connected()

    client.emit("join_session", {"session_id": 123})

    socketio.emit("session_update", {"status": "ok"}, to="session_123")
    received = client.get_received()

    assert any(message["name"] == "session_update" for message in received)
    client.disconnect()


def test_websocket_broadcast_update():
    app, socketio = create_app()
    app.config.update({"TESTING": True})

    client_a = socketio.test_client(app)
    client_b = socketio.test_client(app)

    client_a.emit("join_session", {"session_id": 55})
    client_b.emit("join_session", {"session_id": 55})

    socketio.emit("session_update", {"client_id": 7}, to="session_55")

    received_a = client_a.get_received()
    received_b = client_b.get_received()

    assert any(message["name"] == "session_update" for message in received_a)
    assert any(message["name"] == "session_update" for message in received_b)

    client_a.disconnect()
    client_b.disconnect()
